"""
SIDUMKM — Seeder database
Membuat skema, 250 profil UMKM (turunan sebaran dataset penelitian),
tabel statistik acuan, dan satu akun demo berisi transaksi/rencana/katalog.

Jalankan:  python seed.py --reset
"""
import math
import random
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

from werkzeug.security import generate_password_hash

import database as db_layer
from scoring import ATURAN_ACUAN, BOBOT

random.seed(250)

NAMA_DEPAN = ["Budi", "Siti", "Agus", "Dewi", "Rina", "Joko", "Endang", "Tono", "Wati", "Slamet",
              "Nur", "Ayu", "Fitri", "Dedi", "Yanti", "Hendra", "Rina", "Sulastri", "Bayu", "Intan",
              "Kartika", "Rudi", "Mega", "Taufik", "Lilis", "Wawan", "Eti", "Nana", "Dadan", "Ismail"]
NAMA_BELAKANG = ["Santoso", "Wijaya", "Lestari", "Pratama", "Halim", "Maulida", "Setiawan", "Rahayu",
                 "Kusuma", "Hidayat", "Permata", "Utami", "Gunawan", "Saputra", "Anggraini", "Firmansyah"]

JENIS_USAHA = (
    [("Kuliner", 94), ("Ritel / Sembako", 40), ("Jasa", 18), ("Fashion & Konveksi", 12),
     ("Kerajinan", 9), ("Layanan Digital", 5)]
)

PENDIDIKAN = {1: "SD", 2: "SMP", 3: "SMA", 4: "D1-D3", 5: "S1", 6: "S2"}

KATEGORI_MASUK = ["Penjualan", "Penjualan daring", "Titip di warung", "Jasa servis"]
KATEGORI_KELUAR = ["Bahan baku", "Listrik & air", "Sewa tempat", "Gaji karyawan", "Kemasan",
                   "Kuota internet", "Transport", "Listrik"]


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def slugify(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")


# ------------------------------------------------------------------ profil
def buat_profil():
    jenis = random.choices([j for j, _ in JENIS_USAHA], weights=[w for _, w in JENIS_USAHA])[0]
    usia = random.randint(21, 60)
    pendidikan = random.choices([1, 2, 3, 4, 5, 6], weights=[4, 14, 47, 14, 19, 2])[0]
    exp = max(0, round(random.gauss(7, 5.5), 1))
    modal = random.choices(
        [500_000, 2_000_000, 4_000_000, 8_000_000, 15_000_000, 30_000_000, 75_000_000],
        weights=[16, 24, 20, 15, 12, 8, 5])[0]
    modal = int(modal * random.uniform(0.8, 1.35))
    frk = 1 if random.random() < 0.42 else 0
    bp = 1 if random.random() < 0.55 else 0
    mar = int(round(sigmoid(random.gauss(-0.4 + 1.1 * frk + 0.8 * bp, 1.1)) * 6)) + 1
    inter = 1 if random.random() < (0.20 + 0.09 * mar) else 0
    mitra = 1 if random.random() < 0.33 else 0
    ortu = 1 if random.random() < 0.29 else 0
    saran = int(round(sigmoid(random.gauss(-1.0 + 0.9 * frk, 1.0)) * 6)) + 1

    p_sukses = sigmoid(
        -2.05 + 1.55 * frk + 0.95 * bp + 0.30 * (mar - 3.5)
        + 0.42 * inter + 0.22 * (1 if exp >= 5 else 0)
        + 0.18 * (1 if modal >= 5_000_000 else 0) + 0.25 * mitra
    )
    sukses = 1 if random.random() < p_sukses else 0

    nama = f"{random.choice(NAMA_DEPAN)} {random.choice(NAMA_BELAKANG)}"
    return {
        "nama": nama,
        "email": f"{slugify(nama)}.{random.randint(100, 999)}@umkm.id",
        "usia": usia,
        "education": pendidikan,
        "owner_gender": random.choices([1, 2], weights=[52, 48])[0],
        "nama_usaha": random.choice(["Usaha ", "Toko ", "Warung ", "CV ", "Dapur "]) +
                      random.choice(["Makmur", "Berkah", "Sari Rasa", "Jaya", "Keluarga",
                                     "Tiga Putra", "Sederhana", "Sumber Rejeki", "Ayunda",
                                     "Mandiri", "Cahaya", "Rasa Nusantara"]),
        "jenis_usaha": jenis,
        "initial_capital": modal,
        "financial_record_keeping": frk,
        "internet_usage": inter,
        "business_plan": bp,
        "marketing_effort": mar,
        "partnership": mitra,
        "parent_business_experience": ortu,
        "industry_experience": exp,
        "professional_advice": saran,
        "_sukses": sukses,
    }


# ------------------------------------------------------------------ transaksi
def bulan_ke(n_ke_belakang):
    """Bulan pertama `n` bulan ke belakang (tanpa bug lompat 31 hari)."""
    tahun, bulan = date.today().year, date.today().month
    total = (tahun * 12 + (bulan - 1)) - n_ke_belakang
    return date(total // 12, total % 12 + 1, 1)


def isi_operasional(conn, user_id, frk, mar, inter, sukses, bulan=4, rapat=0.35):
    """Riwayat arus kas + rencana bisnis + katalog produk untuk satu pengguna."""
    hari_skrg = date.today()
    # hari tercatat per bulan: pencatatan baik -> rutin, pencatatan buruk -> jarang
    catatan = random.randint(12, 24) if frk else random.randint(1, 6)
    catatan = max(1, int(catatan * rapat)) if rapat != 1.0 else catatan
    skala = (1.4 if sukses else 0.75) * (1 + 0.12 * mar)

    for b in range(bulan):
        awal_bulan = bulan_ke(bulan - 1 - b)
        for _ in range(catatan):
            if awal_bulan.month == hari_skrg.month and awal_bulan.year == hari_skrg.year:
                hari = random.randint(1, max(1, hari_skrg.day))
            else:
                hari = random.randint(1, 28)
            tgl = awal_bulan.replace(day=min(28, hari)).isoformat()
            if tgl > hari_skrg.isoformat():
                continue
            conn.execute(
                "INSERT INTO financial_records (user_id,tanggal,jenis,kategori,jumlah,keterangan) VALUES (?,?,?,?,?,?)",
                (user_id, tgl, "masuk", random.choice(KATEGORI_MASUK),
                 int(random.randint(120_000, 900_000) * skala), "Pembelian pelanggan"))
            for _ in range(random.randint(1, 3)):
                conn.execute(
                    "INSERT INTO financial_records (user_id,tanggal,jenis,kategori,jumlah,keterangan) VALUES (?,?,?,?,?,?)",
                    (user_id, tgl, "keluar", random.choice(KATEGORI_KELUAR),
                     int(random.randint(40_000, 380_000) * skala), "Pengeluaran usaha"))

    if mar >= 4:
        produk_n = random.randint(3, 9)
        for i in range(produk_n):
            conn.execute(
                """INSERT INTO marketing_activities
                   (user_id,nama_produk,harga,deskripsi,foto_teks,link_katalog,aktif)
                   VALUES (?,?,?,?,?,?,1)""",
                (user_id,
                 f"Produk unggulan {i + 1}",
                 random.randint(15, 350) * 1000,
                 "Dijual langsung dari lokasi usaha, bisa pesan lewat WhatsApp.",
                 "★" * random.randint(3, 5),
                 f"/toko/{user_id}"))
    if sukses or random.random() < 0.5:
        conn.execute(
            """INSERT INTO business_plans
               (user_id,judul,target_omzet,modal_usaha,strategi_pemasaran,produk_utama,
                analisis_risiko,deadline,progress) VALUES (?,?,?,?,?,?,?,?,?)""",
            (user_id, "Rencana setahun berjalan",
             random.randint(8, 45) * 1_000_000, random.randint(4, 30) * 1_000_000,
             "Broadcast WhatsApp mingguan, titip di warung tetangga, dan foto produk setiap Jumat.",
             "Paket hemat keluarga",
             "Kenaikan harga bahan baku dan modal kerja yang macet.",
             (hari_skrg + timedelta(days=random.randint(20, 220))).isoformat(),
             random.randint(15, 85)))


# ------------------------------------------------------------------ acuan
def isi_reference_stats(conn):
    meta = [
        ("financial_record_keeping", "Pencatatan Keuangan", "Ada catatan rutin", ATURAN_ACUAN["financial_record_keeping"]),
        ("business_plan", "Rencana Bisnis", "Punya business plan", ATURAN_ACUAN["business_plan"]),
        ("marketing_effort", "Usaha Pemasaran", "Skor 6-7", ATURAN_ACUAN["marketing_effort"]),
        ("internet_usage", "Pemanfaatan Internet", "Gunakan online", ATURAN_ACUAN["internet_usage"]),
        ("industry_experience", "Pengalaman Industri", "≥ 5 tahun", ATURAN_ACUAN["industry_experience"]),
    ]
    for kode, ind, amb, v in meta:
        conn.execute(
            """INSERT INTO reference_stats
               (indikator,kode,ambang,nilai_berhasil,nilai_tidak_berhasil,selisih,korelasi,bobot,keterangan)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (ind, kode, amb, v["berhasil"], v["tidak"], v["selisih"], v["r"],
             BOBOT[kode],
             "Selisih peluang sukses (persentase poin) antara pelaku dengan/tanpa indikator ini "
             "pada 250 UMKM."))
    for kode, ind, ket in [
        ("initial_capital", "Modal Awal", "Bobot dari sebaran modal 250 UMKM, dibin per jangkauan."),
        ("partnership", "Kemitraan", "Menjadi mitra/pemasok atau bergabung komunitas usaha."),
        ("professional_advice", "Saran Profesional", "Konsultasi ke dinas, bank, atau pendamping."),
    ]:
        conn.execute(
            """INSERT INTO reference_stats
               (indikator,kode,ambang,nilai_berhasil,nilai_tidak_berhasil,selisih,korelasi,bobot,keterangan)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (ind, kode, "-", None, None, None, None, BOBOT[kode], ket))


# ------------------------------------------------------------------ main
def jalankan(reset=False):
    if reset and db_layer.DB_PATH.exists():
        db_layer.DB_PATH.unlink(missing_ok=True)
        for extra in ("-wal", "-shm"):
            p = Path(str(db_layer.DB_PATH) + extra)
            p.unlink(missing_ok=True)

    db_layer.init_db()
    conn = db_layer.db()
    if conn.execute("SELECT COUNT(*) n FROM users").fetchone()["n"] > 0:
        print("Database sudah berisi data, lewati seed (pakai --reset untuk bangun ulang).")
        return

    profiles = [buat_profil() for _ in range(250)]
    for p in profiles:
        cur = conn.execute(
            "INSERT INTO users (nama,email,password,usia,education,owner_gender,toko_slug) VALUES (?,?,?,?,?,?,?)",
            (p["nama"], p["email"], generate_password_hash("umkm123"), p["usia"],
             p["education"], p["owner_gender"], None))
        uid = cur.lastrowid
        conn.execute(
            """INSERT INTO business_profile
               (user_id,nama_usaha,jenis_usaha,initial_capital,financial_record_keeping,
                internet_usage,business_plan,marketing_effort,partnership,
                parent_business_experience,industry_experience,professional_advice)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (uid, p["nama_usaha"], p["jenis_usaha"], p["initial_capital"],
             p["financial_record_keeping"], p["internet_usage"], p["business_plan"],
             p["marketing_effort"], p["partnership"], p["parent_business_experience"],
             p["industry_experience"], p["professional_advice"]))
        conn.execute("UPDATE users SET toko_slug=? WHERE id=?", (f"toko-{uid}", uid))
        isi_operasional(conn, uid, p["financial_record_keeping"], p["marketing_effort"],
                        p["internet_usage"], p["_sukses"], bulan=4, rapat=0.35)
        if random.random() < 0.25:
            prof = db_layer.ambil_profil(conn, uid)
            mod = db_layer.ringkasan_modul(conn, uid)
            db_layer.simpan_skor(conn, uid, prof, mod)

    # ---- akun demo lengkap -------------------------------------------------
    cur = conn.execute(
        """INSERT INTO users (nama,email,password,usia,education,owner_gender,toko_slug)
           VALUES (?,?,?,?,?,?,?)""",
        ("Budi Santoso", "demo@umkm.id", generate_password_hash("demo1234"), 34, 3, 1, "toko-demo"))
    uid = cur.lastrowid
    conn.execute(
        """INSERT INTO business_profile
           (user_id,nama_usaha,jenis_usaha,initial_capital,financial_record_keeping,internet_usage,
            business_plan,marketing_effort,partnership,parent_business_experience,
            industry_experience,professional_advice) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (uid, "Dapur Sari Rasa", "Kuliner", 6_500_000, 1, 1, 0, 4, 0, 1, 3.5, 3))
    isi_operasional(conn, uid, frk=1, mar=4, inter=1, sukses=1, bulan=6, rapat=1.0)
    conn.execute("DELETE FROM business_plans WHERE user_id=?", (uid,))
    conn.execute("DELETE FROM marketing_activities WHERE user_id=?", (uid,))
    produk = [("Nasi Uduk Komplit", 18_000, "Porsi pagi dengan ayam goreng + sambal terasi."),
              ("Keripik Kentang 250gr", 22_000, "Kemasan standing pouch, tahan 3 bulan."),
              ("Sambal Buatan Sendiri 200ml", 25_000, "Sambal bawang siap masak, tanpa pengawet."),
              ("Nasi Kucing Frozen (isi 6)", 60_000, "Tinggal panaskan, cocok untuk stok kulkas."),
              ("Paket Katering Harian", 35_000, "3 kotak nasi + lauk, antar radius 3 km."),
              ("Rempeyek Kacang 500gr", 20_000, "Digoreng setiap Selasa dan Jumat.")]
    for i, (n, h, d) in enumerate(produk):
        conn.execute(
            """INSERT INTO marketing_activities
               (user_id,nama_produk,harga,deskripsi,foto_teks,link_katalog,aktif) VALUES (?,?,?,?,?,?,1)""",
            (uid, n, h, d, "★" * (4 if i % 2 else 5), f"/toko/toko-demo"))

    # skor riwayat agar garis tren dashboard terisi
    prof = db_layer.ambil_profil(conn, uid)
    mod = db_layer.ringkasan_modul(conn, uid)
    for i, delta in enumerate([-11, -8, -6, -3, -2, 0]):
        conn.execute(
            """INSERT INTO scores (user_id,skor_keberhasilan,status,kategori,skor_keuangan,
                                   skor_perencanaan,skor_pemasaran,rekomendasi,calculated_at)
               VALUES (?,?,?,?,?,?,?,?, datetime('now', ?))""",
            (uid, max(0, round(prof["financial_record_keeping"] * 25 + prof["business_plan"] * 20
                               + ((prof["marketing_effort"] - 1) / 6) * 15 + prof["internet_usage"] * 10
                               + 0.65 * 10 + min(prof["industry_experience"], 20) / 20 * 10 + delta, 2)),
             "Perlu Perbaikan", "Cukup", mod["hari_catat_30hari"] * 2, 25, 60, "[]",
             f"-{25 - i * 4} days"))

    isi_reference_stats(conn)
    conn.commit()

    total = conn.execute("SELECT COUNT(*) n FROM users").fetchone()["n"]
    trx = conn.execute("SELECT COUNT(*) n FROM financial_records").fetchone()["n"]
    print(f"Seed selesai: {total} pengguna, {trx} transaksi, DB di {db_layer.DB_PATH}")
    conn.close()


if __name__ == "__main__":
    jalankan(reset="--reset" in sys.argv)
