"""
SIDUMKM — Sistem Informasi Dashboard UMKM
Sistem Pendukung Keputusan berbasis web dengan pendekatan rule-based scoring.

Jalankan:  python app.py   (default http://localhost:3000)
"""
from datetime import date, datetime, timedelta
import os
from functools import wraps

from flask import (Flask, abort, flash, redirect, render_template, request, session,
                   send_from_directory, url_for)
from flask.json import jsonify
from werkzeug.security import check_password_hash, generate_password_hash

import database as db_layer
from scoring import (ATURAN_ACUAN, BOBOT, PILIHAN_MODAL, PILIHAN_PEMASARAN,
                     PILIHAN_SARAN, generate_rekomendasi, hitung_skor_umkm,
                     langkah_terbaik, modal_dari_pilihan, nilai_dari_kata,
                     verifikasi_insilik)
from viz import batang, garis, kolom, meter, radar
from database import nominal_umum, skeleton_rencana, statistik_saran, urungkan_hapus

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SIDUMKM_SECRET_KEY") or os.urandom(32)


# ---------------------------------------------------------------- filter
def rupiah(nilai, desimal=0):
    try:
        nilai = float(nilai or 0)
    except (TypeError, ValueError):
        return "-"
    negatif = nilai < 0
    teks = f"{abs(nilai):,.{desimal}f}".replace(",", ".")
    return f"{'-' if negatif else ''}Rp{teks}"


def persen(nilai):
    return f"{float(nilai or 0):.1f}%".replace(".0%", "%")


def tanggal_id(isi):
    if not isi:
        return "-"
    nama = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
            "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
    try:
        d = datetime.strptime(str(isi)[:10], "%Y-%m-%d")
    except ValueError:
        return isi
    return f"{d.day} {nama[d.month]} {d.year}"


app.jinja_env.filters["rp"] = rupiah
app.jinja_env.filters["pct"] = persen
app.jinja_env.filters["tgl"] = tanggal_id
app.jinja_env.filters["jml"] = lambda v: f"{float(v or 0):,.0f}".replace(",", ".")


def konek():
    return db_layer.db()


# ---------------------------------------------------------------- auth
def perlu_login(f):
    @wraps(f)
    def pembungkus(*a, **kw):
        if not session.get("uid"):
            flash("Masuk dulu untuk melihat dashboard usaha Anda.")
            return redirect(url_for("masuk"))
        return f(*a, **kw)
    return pembungkus


@app.context_processor
def bawaan():
    """Variabel yang selalu tersedia di template: pengguna aktif + skor ringkas untuk rail."""
    conn = konek()
    user, samping = None, None
    if session.get("uid"):
        user = conn.execute("SELECT * FROM users WHERE id=?", (session["uid"],)).fetchone()
        profil = db_layer.ambil_profil(conn, session["uid"])
        modul = db_layer.ringkasan_modul(conn, session["uid"])
        if profil:
            s = hitung_skor_umkm(profil, modul)
            samping = {"skor": s["skor"], "status": s["status"], "kategori": s["kategori"],
                       "pilar": s["pilar"]}
    total = conn.execute("SELECT COUNT(*) n FROM business_profile WHERE user_id <= 250").fetchone()["n"]
    conn.close()
    return {"pengguna": user, "samping": samping, "tahun": date.today().year,
            "hari_ini": date.today().isoformat(), "total_umkm": total,
            "mode": mode_aktif(), "label_mode": LABEL_MODE}


# ---------------------------------------------------------------- mode & delta
MODE_SEDERHANA = "sederhana"
LABEL_MODE = {MODE_SEDERHANA: "Bahasa sederhana", "riset": "Bahasa riset"}


def mode_aktif():
    return session.get("mode", MODE_SEDERHANA)


def delta_skor(lama, baru):
    """Perubahan skor dalam bahasa Indonesia: koma desimal, satu angka pecahan."""
    sel = round(float(baru) - float(lama), 1)
    angka = f"{float(baru):.1f}".replace(".", ",")
    if sel > 0:
        return f"Naik {f'{sel:.1f}'.replace('.', ',').rstrip('0').rstrip(',')} poin, sekarang {angka}/100."
    if sel < 0:
        turun = abs(sel)
        return (f"Turun {f'{turun:.1f}'.replace('.', ',').rstrip('0').rstrip(',')} poin, "
                f"sekarang {angka}/100.")
    return f"Nilai tetap di {angka}/100."


@app.route("/mode/<nama>")
@perlu_login
def ganti_mode(nama):
    session["mode"] = nama if nama in LABEL_MODE else MODE_SEDERHANA
    return redirect(request.referrer or url_for("dashboard"))


# ---------------------------------------------------------------- stats acuan
_CACHE_ACUAN = None


def statistik_acuan(conn):
    """Rata-rata 250 UMKM di dataset, untuk panel perbandingan."""
    global _CACHE_ACUAN
    if _CACHE_ACUAN:
        return _CACHE_ACUAN
    row = conn.execute(
        """SELECT
             AVG(financial_record_keeping)*100 AS frk,
             AVG(business_plan)*100            AS bp,
             AVG(internet_usage)*100           AS inter,
             AVG(marketing_effort/7.0*100)     AS mar,
             AVG(MIN(industry_experience,20)/20.0*100) AS exp
           FROM business_profile WHERE user_id <= 250""").fetchone()
    _CACHE_ACUAN = {
        "catatan_keuangan": row["frk"], "rencana_bisnis": row["bp"],
        "pemanfaatan_internet": row["inter"], "usaha_pemasaran": row["mar"],
        "pengalaman": row["exp"],
    }
    return _CACHE_ACUAN


def skor_tersimpan(conn, uid):
    row = conn.execute(
        "SELECT * FROM scores WHERE user_id=? ORDER BY id DESC LIMIT 1", (uid,)).fetchone()
    return dict(row) if row else None


def hasil_terkini(conn, uid):
    """
    Profil + ringkasan modul + skor + rekomendasi.
    Tiga indikator diverifikasi dari perilaku (bukan dari centang user) lalu
    disimpan supaya layar Profil & dashboard selalu menunjukkan fakta.
    """
    profil = db_layer.ambil_profil(conn, uid)
    modul = db_layer.ringkasan_modul(conn, uid)
    profil, alasan = verifikasi_insilik(profil, modul)
    if alasan:
        catatan = "; ".join(alasan)
        conn.execute("UPDATE business_profile SET verifikasi_otomatis=? WHERE user_id=?",
                     (catatan, uid))
        conn.commit()
        profil["verifikasi_otomatis"] = catatan
    skor = hitung_skor_umkm(profil, modul)
    rekomendasi = generate_rekomendasi(profil, modul)
    return profil, modul, skor, rekomendasi, alasan


# ---------------------------------------------------------------- halaman
@app.route("/")
def beranda():
    return redirect(url_for("dashboard") if session.get("uid") else url_for("masuk"))


@app.route("/masuk", methods=["GET", "POST"])
def masuk():
    error = None
    if request.method == "POST":
        conn = konek()
        row = conn.execute("SELECT * FROM users WHERE email=?",
                           (request.form["email"].strip().lower(),)).fetchone()
        conn.close()
        if row and check_password_hash(row["password"], request.form["password"]):
            session["uid"] = row["id"]
            return redirect(url_for("dashboard"))
        error = "Email atau sandi tidak dikenali. Coba demo@umkm.id / demo1234."
    return render_template("masuk.html", error=error)


@app.route("/daftar", methods=["GET", "POST"])
def daftar():
    error = None
    f = request.form
    if request.method == "POST":
        email = f["email"].strip().lower()
        conn = konek()
        if conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            error = "Email sudah terdaftar. Silakan masuk saja."
        elif len(f["password"]) < 6:
            error = "Sandi minimal 6 karakter."
        elif not (f.get("nama") or "").strip() or not (f.get("nama_usaha") or "").strip():
            error = "Nama pemilik dan nama usaha wajib diisi."
        else:
            cur = conn.execute(
                """INSERT INTO users (nama,email,password,usia,education,owner_gender,toko_slug)
                   VALUES (?,?,?,?,?,?,?)""",
                (f["nama"], email, generate_password_hash(f["password"]),
                 int(f.get("usia") or 0), int(f.get("education") or 3), int(f.get("owner_gender") or 0), None))
            uid = cur.lastrowid
            conn.execute(
                """INSERT INTO business_profile
                   (user_id,nama_usaha,jenis_usaha,initial_capital,financial_record_keeping,
                    internet_usage,business_plan,marketing_effort,partnership,
                    parent_business_experience,industry_experience,professional_advice)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (uid, f["nama_usaha"], f["jenis_usaha"], modal_dari_pilihan(f.get("modal", 2)),
                 0, 0, 0,  # tiga indikator berikut diisi mesin dari perilaku, bukan ditanya
                 nilai_dari_kata(PILIHAN_PEMASARAN, f.get("pemasaran", ""), 2),
                 1 if f.get("mitra") else 0, int(f.get("ortu") or 0),
                 float(f.get("tahun") or 0),
                 nilai_dari_kata(PILIHAN_SARAN, f.get("saran", ""), 1)))
            conn.execute("UPDATE users SET toko_slug=? WHERE id=?", (f"toko-{uid}", uid))
            modul = db_layer.ringkasan_modul(conn, uid)
            db_layer.simpan_skor(conn, uid, db_layer.ambil_profil(conn, uid), modul)
            conn.commit()
            conn.close()
            session["uid"] = uid
            flash("Profil tersimpan. Kalau ada yang belum lengkap, sistem akan mengaktifkannya sendiri setelah Anda mulai mencatat.")
            return redirect(url_for("dashboard"))
        conn.close()
    nilai = f if request.method == "POST" else {}
    return render_template("daftar.html", error=error, f=nilai,
                           pilihan_modal=sorted(PILIHAN_MODAL.items()),
                           pilihan_pemasaran=sorted(PILIHAN_PEMASARAN.items()),
                           pilihan_saran=sorted(PILIHAN_SARAN.items()))


@app.route("/keluar")
def keluar():
    session.clear()
    return redirect(url_for("masuk"))


@app.route("/dashboard")
@perlu_login
def dashboard():
    uid = session["uid"]
    conn = konek()
    profil, modul, skor, rekomendasi, alasan = hasil_terkini(conn, uid)
    acuan = statistik_acuan(conn)
    tren = db_layer.tren_omzet(conn, uid, bulan=6)
    riwayat = db_layer.riwayat_skor(conn, uid, 24)

    seri = [("Omzet", [(t["bulan"], t["masuk"]) for t in tren]),
            ("Biaya", [(t["bulan"], t["keluar"]) for t in tren])]
    chart = garis(seri)
    jaring = radar([("Keuangan", skor["pilar"]["keuangan"]),
                    ("Rencana", skor["pilar"]["perencanaan"]),
                    ("Pemasaran", skor["pilar"]["pemasaran"])])

    pasangan = [
        ("Pencatatan keuangan", profil["financial_record_keeping"] * 100, acuan["catatan_keuangan"]),
        ("Rencana bisnis", profil["business_plan"] * 100, acuan["rencana_bisnis"]),
        ("Pemanfaatan internet", profil["internet_usage"] * 100, acuan["pemanfaatan_internet"]),
        ("Usaha pemasaran", profil["marketing_effort"] / 7 * 100, acuan["usaha_pemasaran"]),
        ("Pengalaman industri", min(profil["industry_experience"], 20) / 20 * 100, acuan["pengalaman"]),
    ]
    # warna bar mengikuti makna: di atas rata-rata dataset = pandan, di bawah = cabai
    banding = batang([(l, a, b, "hijau" if a >= b else "cabai") for l, a, b in pasangan])
    busur = meter(skor["skor"])
    riwayat_kolom = kolom([r[1] for r in riwayat], [r[0][5:10] for r in riwayat])

    kategori = conn.execute(
        """SELECT kategori, SUM(jumlah) total FROM financial_records
           WHERE user_id=? AND jenis='keluar' AND tanggal>=date('now','-90 days')
           GROUP BY kategori ORDER BY total DESC LIMIT 5""", (uid,)).fetchall()

    berikutnya = langkah_terbaik(rekomendasi)
    lainnya = [r for r in rekomendasi if r is not berikutnya]
    saran = statistik_saran(conn, uid)
    preset = dict(berikutnya) if berikutnya else {}
    if preset:
        preset["nominal"] = nominal_umum(uid, "masuk", saran["nominal_masuk"])[0]
        preset["kategori"] = (saran["sering"][0]["kategori"] if saran["sering"] else "Penjualan")

    konteks = {
        "profil": profil, "modul": modul, "skor": skor, "rekomendasi": rekomendasi,
        "berikutnya": berikutnya, "lainnya": lainnya, "alasan": alasan,
        "saran": saran, "preset": preset, "mode": mode_aktif(), "label_mode": LABEL_MODE,
        "chart": chart, "jaring": jaring, "banding": banding, "riwayat_kolom": riwayat_kolom, "busur": busur,
        "kategori": kategori, "aturan": ATURAN_ACUAN, "bobot": BOBOT,
        "terakhir": skor_tersimpan(conn, uid), "riwayat": riwayat,
        "total_umkm": conn.execute("SELECT COUNT(*) n FROM business_profile WHERE user_id<=250").fetchone()["n"],
    }
    conn.close()
    return render_template("dashboard.html", **konteks)


# ---------------------------------------------------------------- pilar 1
KATEGORI_DEFAULT = {"masuk": "Penjualan", "keluar": "Beli bahan"}


def _ambil_nominal(form, uid, jenis):
    """Nominal: terima '12.000', '12,000', kosong -> rata-rata pengguna."""
    mentah = (form.get("jumlah") or "").strip()
    if mentah:
        bersih = mentah.replace(".", "").replace(",", "").replace("Rp", "").replace(" ", "")
        try:
            return max(0.0, float(bersih or 0))
        except ValueError:
            pass
    saran = statistik_saran(konek(), uid)
    umum = nominal_umum(uid, jenis, saran["nominal_masuk"] if jenis == "masuk" else saran["nominal_keluar"])
    return float(umum[0])


@app.route("/keuangan", methods=["GET", "POST"])
@perlu_login
def keuangan():
    uid = session["uid"]
    conn = konek()
    sebelum = hitung_skor_umkm(*hasil_terkini(conn, uid)[:2])["skor"]

    if request.method == "POST":
        aksi = request.form.get("aksi") or ("hapus" if request.form.get("hapus") else "catat")

        if aksi in ("hapus", "batal"):
            if aksi == "hapus":
                conn.execute("UPDATE financial_records SET dihapus_pada=datetime('now') "
                             "WHERE id=? AND user_id=?", (request.form["hapus"], uid))
                conn.commit()
                flash('Baris dihapus. Salah? Tekan tombol Batalkan di bawah tabel.')
            else:
                urungkan_hapus(conn, uid)
                flash("Baris yang tadi terhapus sudah kembali.")
            return redirect(url_for("keuangan") + "#buku")

        if aksi == "ulangi":
            terakhir = conn.execute(
                """SELECT tanggal, jenis, kategori, jumlah, keterangan FROM financial_records
                   WHERE user_id=? AND dihapus_pada IS NULL ORDER BY id DESC LIMIT 1""",
                (uid,)).fetchone()
            if terakhir:
                conn.execute(
                    """INSERT INTO financial_records (user_id,tanggal,jenis,kategori,jumlah,keterangan)
                       VALUES (?,date('now'),?,?,?,?,?)""",
                    (uid, terakhir["jenis"], terakhir["kategori"], terakhir["jumlah"],
                     (terakhir["keterangan"] or "") + " (diulang)"))
                conn.commit()
                flash("Penjualan kemarin dicatat lagi untuk hari ini.")
            return redirect(url_for("keuangan") + "#buku")

        # aksi == catat : semua field boleh kosong, sistem yang melengkapinya
        jenis = request.form.get("jenis") if request.form.get("jenis") in ("masuk", "keluar") else "masuk"
        jumlah = _ambil_nominal(request.form, uid, jenis)
        kategori = (request.form.get("kategori") or "").strip() or KATEGORI_DEFAULT[jenis]
        tanggal = request.form.get("tanggal") or date.today().isoformat()
        conn.execute(
            """INSERT INTO financial_records (user_id,tanggal,jenis,kategori,jumlah,keterangan)
               VALUES (?,?,?,?,?,?)""",
            (uid, tanggal, jenis, kategori, jumlah,
             (request.form.get("keterangan") or "").strip() or "Catat cepat"))
        if request.form.get("_langsung"):
            session["langsung_terakhir"] = {"jenis": jenis, "jumlah": jumlah, "kategori": kategori}
        conn.commit()

        profil = db_layer.ambil_profil(conn, uid)
        mod = db_layer.ringkasan_modul(conn, uid)
        profil_baru, alasan = verifikasi_insilik(profil, mod)
        for k in ("financial_record_keeping", "business_plan", "internet_usage"):
            if profil_baru[k] != profil[k]:
                conn.execute(f"UPDATE business_profile SET {k}=? WHERE user_id=?", (profil_baru[k], uid))
        sesudah = hitung_skor_umkm(profil_baru, mod)["skor"]
        conn.commit()
        pesan = f"Tersimpan: {jumlah and rupiah(jumlah)} {kategori.lower()}."
        if alasan:
            pesan += " " + alasan[0]
        flash(pesan + " " + delta_skor(sebelum, sesudah))
        return redirect(url_for("keuangan") + "#buku")

    profil, modul, skor, _, alasan = hasil_terkini(conn, uid)
    isi = conn.execute(
        """SELECT * FROM financial_records WHERE user_id=? AND dihapus_pada IS NULL
           ORDER BY tanggal DESC, id DESC LIMIT 120""",
        (uid,)).fetchall()
    bulanan = conn.execute(
        """SELECT strftime('%Y-%m',tanggal) bulan,
                  SUM(CASE WHEN jenis='masuk' THEN jumlah ELSE 0 END) masuk,
                  SUM(CASE WHEN jenis='keluar' THEN jumlah ELSE 0 END) keluar
           FROM financial_records WHERE user_id=? AND dihapus_pada IS NULL
           GROUP BY bulan ORDER BY bulan DESC LIMIT 12""",
        (uid,)).fetchall()
    chart = garis([("Omzet", [(b["bulan"], b["masuk"]) for b in reversed(bulanan)]),
                  ("Biaya", [(b["bulan"], b["keluar"]) for b in reversed(bulanan)])])
    saran = statistik_saran(conn, uid)
    chip = {j: nominal_umum(uid, j, saran["nominal_masuk"] if j == "masuk" else saran["nominal_keluar"])
            for j in ("masuk", "keluar")}
    hasil = {"isi": isi, "bulanan": bulanan, "chart": chart, "profil": profil,
             "modul": modul, "skor": skor, "saldo": modul["net"], "alasan": alasan,
             "saran": saran, "chip": chip, "mode": mode_aktif(),
             "langsung": session.get("langsung_terakhir")}
    conn.close()
    return render_template("keuangan.html", **hasil)


# ---------------------------------------------------------- aksi sekali-klik
@app.route("/tindak", methods=["POST"])
@perlu_login
def tindak():
    """Satu tombol dari dashboard mengerjakan tindakan aslinya, bukan cuma membuka form."""
    kode = request.form.get("kode")
    uid = session["uid"]
    conn = konek()
    profil = db_layer.ambil_profil(conn, uid)
    modul = db_layer.ringkasan_modul(conn, uid)
    sebelum = hitung_skor_umkm(profil, modul)["skor"]

    if kode == "catat":
        saran = statistik_saran(conn, uid)
        jumlah = float(request.form.get("jumlah") or nominal_umum(uid, "masuk", saran["nominal_masuk"])[0])
        kategori = request.form.get("kategori") or (
            saran["sering"][0]["kategori"] if saran["sering"] else "Penjualan")
        conn.execute(
            """INSERT INTO financial_records (user_id,tanggal,jenis,kategori,jumlah,keterangan)
               VALUES (?,date('now'),'masuk',?,?, 'Catat sekali klik')""",
            (uid, kategori, jumlah))
        pesan = f"Catatan {kategori} {rupiah(jumlah)} masuk ke buku kas hari ini."
    elif kode == "bagikan":
        conn.execute("UPDATE business_profile SET internet_usage=1 WHERE user_id=?", (uid,))
        conn.commit()
        flash("Katalog online aktif. Salin tautannya di halaman Produk saya, lalu kirim ke WhatsApp pelanggan.")
        return redirect(url_for("pemasaran"))
    elif kode == "rencana":
        return redirect(url_for("rencana") + "?draf=1")
    elif kode == "produk":
        return redirect(url_for("pemasaran") + "?tambah=1")
    elif kode == "jaga":
        return redirect(url_for("keuangan"))
    else:
        pesan = "Terima kasih, catatan Anda sudah lengkap. Tidak ada pekerjaan tambahan hari ini."
    conn.commit()

    profil_baru, catatan_verifikasi = verifikasi_insilik(db_layer.ambil_profil(conn, uid),
                                                         db_layer.ringkasan_modul(conn, uid))
    if catatan_verifikasi:
        conn.execute("UPDATE business_profile SET verifikasi_otomatis=? WHERE user_id=?",
                     ("; ".join(catatan_verifikasi), uid))
    mod = db_layer.ringkasan_modul(conn, uid)
    conn.execute(
        """UPDATE business_profile SET financial_record_keeping=?, business_plan=?, internet_usage=?
           WHERE user_id=?""",
        (profil_baru["financial_record_keeping"], profil_baru["business_plan"],
         profil_baru["internet_usage"], uid))
    conn.commit()
    sesudah = hitung_skor_umkm(profil_baru, mod)["skor"]
    flash(pesan + " " + delta_skor(sebelum, sesudah))
    conn.close()
    return redirect(url_for("dashboard"))


# ---------------------------------------------------------------- pilar 2
@app.route("/rencana", methods=["GET", "POST"])
@perlu_login
def rencana():
    uid = session["uid"]
    conn = konek()
    if request.method == "POST":
        sebelum = hitung_skor_umkm(*hasil_terkini(conn, uid)[:2])["skor"]
        lama = conn.execute("SELECT id FROM business_plans WHERE user_id=?", (uid,)).fetchone()
        kolom = dict(
            judul=(request.form.get("judul") or "Rencana 3 bulan ke depan").strip(),
            target_omzet=float(request.form.get("target_omzet") or 0),
            modal_usaha=float(request.form.get("modal_usaha") or 0),
            strategi_pemasaran=request.form.get("strategi_pemasaran", ""),
            produk_utama=request.form.get("produk_utama", ""),
            analisis_risiko=request.form.get("analisis_risiko", ""),
            deadline=request.form.get("deadline") or None,
            progress=int(request.form.get("progress") or 0))
        if lama:
            conn.execute(
                """UPDATE business_plans SET judul=:judul, target_omzet=:target_omzet,
                   modal_usaha=:modal_usaha, strategi_pemasaran=:strategi_pemasaran,
                   produk_utama=:produk_utama, analisis_risiko=:analisis_risiko,
                   deadline=:deadline, progress=:progress WHERE id=:id""",
                {**kolom, "id": lama["id"]})
        else:
            conn.execute(
                """INSERT INTO business_plans (user_id, judul, target_omzet, modal_usaha,
                   strategi_pemasaran, produk_utama, analisis_risiko, deadline, progress)
                   VALUES (:uid, :judul, :target_omzet, :modal_usaha, :strategi_pemasaran,
                           :produk_utama, :analisis_risiko, :deadline, :progress)""",
                {"uid": uid, **kolom})
        mod = db_layer.ringkasan_modul(conn, uid)
        profil = db_layer.ambil_profil(conn, uid)
        profil_baru, _ = verifikasi_insilik(profil, mod)
        conn.execute("UPDATE business_profile SET business_plan=?, financial_record_keeping=?, "
                     "internet_usage=? WHERE user_id=?",
                    (profil_baru["business_plan"], profil_baru["financial_record_keeping"],
                     profil_baru["internet_usage"], uid))
        conn.commit()
        sesudah = hitung_skor_umkm(profil_baru, mod)["skor"]
        flash("Rencana tersimpan. " + delta_skor(sebelum, sesudah))
        return redirect(url_for("dashboard"))

    profil, modul, skor, _, alasan = hasil_terkini(conn, uid)
    # ?draf=1 -> sistem menyiapkan isian dari perilaku, pengguna tinggal menyetujui
    draf = None
    if request.args.get("draf") and not modul["rencana"]:
        draf = skeleton_rencana(conn, uid)
    saran = statistik_saran(conn, uid)
    conn.close()
    return render_template("rencana.html", profil=profil, modul=modul, skor=skor,
                           draf=draf, saran=saran, alasan=alasan, mode=mode_aktif(),
                           hari_depan=(date.today() + timedelta(days=90)).isoformat())


# ---------------------------------------------------------------- pilar 3
@app.route("/pemasaran", methods=["GET", "POST"])
@perlu_login
def pemasaran():
    uid = session["uid"]
    conn = konek()
    if request.method == "POST":
        act = request.form.get("aksi")
        if act == "hapus":
            conn.execute("DELETE FROM marketing_activities WHERE id=? AND user_id=?",
                         (request.form["id"], uid))
        elif act == "toggle":
            conn.execute("UPDATE marketing_activities SET aktif=1-aktif WHERE id=? AND user_id=?",
                         (request.form["id"], uid))
        elif act == "usaha":
            conn.execute("UPDATE business_profile SET marketing_effort=?, internet_usage=? "
                         "WHERE user_id=?",
                         (int(request.form["marketing_effort"]),
                          int(request.form.get("internet_usage", 0)), uid))
        elif act == "bagikan":
            # perilaku nyata: tautan katalog disebar -> indikator online + usaha pemasaran naik satu
            profil = db_layer.ambil_profil(conn, uid)
            conn.execute("UPDATE business_profile SET internet_usage=1, marketing_effort=MIN(7, ?) "
                         "WHERE user_id=?", (int(profil["marketing_effort"]) + 1, uid))
            conn.commit()
            flash("Dicatat: katalog Anda sudah disebar. Status jualan online aktif, usaha pemasaran "
                  "naik satu tingkat — sistem menyesuaikan sendiri, bukan Anda yang mengisi.")
            return redirect(url_for("pemasaran"))
        else:
            harga = (request.form.get("harga") or "").strip()
            harga = float(harga.replace(".", "").replace(",", "") or 0)
            nama = (request.form.get("nama_produk") or "").strip()
            if not nama:
                flash("Tulis dulu nama produknya ya — satu kata juga cukup.", "gagal")
                return redirect(url_for("pemasaran") + "?tambah=1")
            conn.execute(
                """INSERT INTO marketing_activities
                   (user_id,nama_produk,harga,deskripsi,foto_teks,link_katalog,aktif)
                   VALUES (?,?,?,?,?,?,1)""",
                (uid, nama, harga,
                 request.form.get("deskripsi", "").strip(),
                 (request.form.get("foto_teks") or "★").strip()[:5] or "★",
                 f"/toko/{request.form.get('slug') or uid}"))
            profil = db_layer.ambil_profil(conn, uid)
            if not profil["internet_usage"]:
                conn.execute("UPDATE business_profile SET internet_usage=1 WHERE user_id=?", (uid,))
                flash('Katalog punya produk pertama, status jualan online saya aktifkan.')
        conn.commit()
        return redirect(url_for("pemasaran"))

    profil, modul, skor, _, _alasan = hasil_terkini(conn, uid)
    produk = conn.execute(
        "SELECT * FROM marketing_activities WHERE user_id=? ORDER BY id DESC", (uid,)).fetchall()
    user = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    return render_template("pemasaran.html", profil=profil, modul=modul, skor=skor,
                           produk=produk, user=user)


@app.route("/manifest.webmanifest")
def manifest():
    return send_from_directory(app.static_folder, "manifest.webmanifest",
                              mimetype="application/manifest+json")


@app.route("/sw.js")
def service_worker():
    # disajikan dari akar supaya cakupannya seluruh aplikasi (butuh untuk mode offline)
    return send_from_directory(app.static_folder, "sw.js", mimetype="application/javascript")


@app.route("/toko/<slug>")
def toko(slug):
    conn = konek()
    user = conn.execute("SELECT * FROM users WHERE toko_slug=?", (slug,)).fetchone()
    if not user:
        try:
            user = conn.execute("SELECT * FROM users WHERE id=?", (int(slug),)).fetchone()
        except ValueError:
            user = None
    if not user:
        conn.close()
        abort(404)
    profil = db_layer.ambil_profil(conn, user["id"])
    produk = conn.execute(
        "SELECT * FROM marketing_activities WHERE user_id=? AND aktif=1 ORDER BY id",
        (user["id"],)).fetchall()
    conn.close()
    return render_template("toko.html", user=user, profil=profil, produk=produk)


# ---------------------------------------------------------------- profil & acuan
@app.route("/profil", methods=["GET", "POST"])
@perlu_login
def profil_halaman():
    uid = session["uid"]
    conn = konek()
    if request.method == "POST":
        angka = ("initial_capital", "marketing_effort", "professional_advice",
                 "parent_business_experience")
        bendera = ("financial_record_keeping", "internet_usage", "business_plan", "partnership")
        for kolom in angka:
            if kolom in request.form:
                conn.execute(f"UPDATE business_profile SET {kolom}=? WHERE user_id=?",
                             (float(request.form[kolom] or 0), uid))
        for kolom in bendera:  # checkbox yang dicentang saja terkirim
            conn.execute(f"UPDATE business_profile SET {kolom}=? WHERE user_id=?",
                         (1 if request.form.get(kolom) else 0, uid))
        if "industry_experience" in request.form:
            conn.execute("UPDATE business_profile SET industry_experience=? WHERE user_id=?",
                         (float(request.form["industry_experience"] or 0), uid))
        for k in ("nama", "nama_usaha", "jenis_usaha"):
            if request.form.get(k):
                if k == "nama":
                    conn.execute("UPDATE users SET nama=? WHERE id=?", (request.form[k], uid))
                else:
                    conn.execute(f"UPDATE business_profile SET {k}=? WHERE user_id=?",
                                 (request.form[k], uid))
        conn.commit()
        flash("Profil diperbarui, skor dihitung ulang.")
        return redirect(url_for("profil_halaman"))
    profil = db_layer.ambil_profil(conn, uid)
    modul = db_layer.ringkasan_modul(conn, uid)
    skor = hitung_skor_umkm(profil, modul)
    kontribusi = [
        ("Pencatatan keuangan", profil["financial_record_keeping"] * BOBOT["financial_record_keeping"],
         BOBOT["financial_record_keeping"]),
        ("Rencana bisnis", profil["business_plan"] * BOBOT["business_plan"], BOBOT["business_plan"]),
        ("Usaha pemasaran", skor["pilar"]["pemasaran"] / 100 * BOBOT["marketing_effort"],
         BOBOT["marketing_effort"]),
        ("Pemanfaatan internet", profil["internet_usage"] * BOBOT["internet_usage"],
         BOBOT["internet_usage"]),
        ("Modal awal", round(profil["initial_capital"] / 50_000_000 * 10, 1), BOBOT["initial_capital"]),
        ("Pengalaman industri", round(min(profil["industry_experience"], 20) / 20 * 10, 1),
         BOBOT["industry_experience"]),
        ("Kemitraan", profil["partnership"] * BOBOT["partnership"], BOBOT["partnership"]),
        ("Saran profesional", round((profil["professional_advice"] - 1) / 6 * 5, 1),
         BOBOT["professional_advice"]),
    ]
    conn.close()
    return render_template("profil.html", profil=profil, skor=skor, kontribusi=kontribusi)


@app.route("/acuan")
@perlu_login
def acuan():
    conn = konek()
    baris = conn.execute("SELECT * FROM reference_stats ORDER BY selisih DESC NULLS LAST").fetchall()
    ringkas = conn.execute(
        """SELECT COUNT(*) n, AVG(financial_record_keeping)*100 frk, AVG(business_plan)*100 bp,
                  AVG(internet_usage)*100 inter, AVG(marketing_effort) mar,
                  AVG(industry_experience) exp, AVG(initial_capital) modal
           FROM business_profile WHERE user_id <= 250""").fetchone()
    skor_pop = conn.execute(
        """SELECT ROUND(skor_keberhasilan/5)*5 b, COUNT(*) n FROM scores
           WHERE user_id<=250 AND id IN (SELECT MAX(id) FROM scores GROUP BY user_id)
           GROUP BY b ORDER BY b""").fetchall()
    distribusi = batang([(f"{r['b']}", r['n'], 0, "tinta") for r in skor_pop])
    conn.close()
    return render_template("acuan.html", baris=baris, ringkas=ringkas, distribusi=distribusi)


# ---------------------------------------------------------------- API
@app.route("/api/skor")
@perlu_login
def api_skor():
    conn = konek()
    profil, modul, skor, rekomendasi, _alasan = hasil_terkini(conn, session["uid"])
    conn.close()
    return jsonify({"user_id": session["uid"], **skor, "rekomendasi": rekomendasi})


@app.errorhandler(404)
def tidak_ditemukan(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    mode_seed = os.environ.get("SIDUMKM_SEED")
    if mode_seed:
        import seed
        seed.jalankan(reset=mode_seed == "reset")
    db_layer.init_db()
    app.run(host="0.0.0.0", port=3000, debug=False, threaded=True)
