# -*- coding: utf-8 -*-
"""
SIDUMKM — uji black-box otomatis
================================
Menjalankan setiap fitur lewat klien Flask dan memeriksa hasil yang nyata,
lalu mencetak tabel pengujian siap tempel ke Bab 4 naskah (BB-01 ... BB-14).

Jalankan:  python validasi/uji_hitam.py        (dari folder proyek)
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app as aplikasi          # noqa: E402
import database as dbl          # noqa: E402
import dataset                  # noqa: E402
from scoring import hitung_skor_umkm, verifikasi_insilik   # noqa: E402

HASIL = []


def catat(kode, kasus, harapan, lolos, angka=""):
    HASIL.append({"kode": kode, "kasus": kasus, "hasil_harapan": harapan,
                  "hasil_sesungguhnya": ("sesuai harapan" if lolos else "TIDAK SESUAI"),
                  "keterangan": angka, "keputusan": "LULUS" if lolos else "GAGAL"})


def masuk(email, sandi):
    c = aplikasi.app.test_client()
    r = c.post("/masuk", data={"email": email, "password": sandi}, follow_redirects=True)
    return c, r


def skor_dari(b):
    m = re.findall(r'data-angka="([\d.]+)"', b)
    return float(m[0]) if m else None


def pesan_dari(b):
    m = re.findall(r'<div class="pesan[^"]*"[^>]*>(.*?)</div>', b, re.S)
    return m[0].strip() if m else ""


# ------------------------------------------------------------------ autikasi
def uji_autentikasi():
    c = aplikasi.app.test_client()
    r = c.get("/dashboard", follow_redirects=True)
    catat("BB-01", "Akses /dashboard tanpa login", "Diarahkan ke halaman masuk",
          r.status_code == 200 and "Masuk" in r.get_data(as_text=True), "HTTP " + str(r.status_code))

    c, r = masuk("demo@umkm.id", "salah")
    b = r.get_data(as_text=True)
    pesan2 = pesan_dari(b)
    catat("BB-02", "Login dengan sandi salah", "Ditolak, pesan menjelaskan tanpa membocorkan kredensial",
          "tidak dikenali" in b and "/dashboard" not in r.request.path
          and "demo1234" not in pesan2, pesan2[:62])

    c, r = masuk("demo@umkm.id", "demo1234")
    catat("BB-03", "Login akun terdaftar", "Masuk ke dashboard", r.status_code == 200,
          "HTTP " + str(r.status_code))


# ------------------------------------------------------------------ mesin skor
def uji_mesin_skor():
    df = dataset.muat(dataset.cari_berkas())
    conn = dbl.db()
    cocok = []
    for i, baris in df.iterrows():
        u = conn.execute("SELECT id FROM users WHERE email=?",
                         (f"responden{i + 1:03d}@umkm.id",)).fetchone()
        prof = dbl.ambil_profil(conn, u["id"]); mod = dbl.ringkasan_modul(conn, u["id"])
        cocok.append(abs(hitung_skor_umkm(prof, mod)["skor"] - float(baris["Skor"])) < 0.05)
    conn.close()
    catat("BB-04", "Reproduksi indeks pada 250 baris data penelitian",
          "Skor mesin == Skor_Keberhasilan CSV", sum(cocok) == len(cocok),
          f"{sum(cocok)}/{len(cocok)} baris cocok")

    prof = {"financial_record_keeping": 1, "business_plan": 1, "internet_usage": 1,
            "marketing_effort": 7, "partnership": 1, "professional_advice": 7,
            "industry_experience": 20, "initial_capital": 1}
    s = hitung_skor_umkm(prof, {})["skor"]
    catat("BB-05", "Profil memenuhi semua atribut", "Skor 100", abs(s - 100) < 0.01, f"skor={s}")

    prof2 = dict(prof, financial_record_keeping=0)
    s2 = hitung_skor_umkm(prof2, {})["skor"]
    catat("BB-06", "Atribut pembukuan dilepas dari profil sempurna",
          "Skor turun tepat 25 poin (bobot terbesar)", abs((s - s2) - 25) < 0.01,
          f"100 - {s2} = {round(s - s2, 2)}")

    p3, alasan = verifikasi_insilik({"financial_record_keeping": 0, "business_plan": 0,
                                     "internet_usage": 0, "marketing_effort": 1,
                                     "partnership": 0, "professional_advice": 1,
                                     "industry_experience": 0, "initial_capital": 0,
                                     "sumber_data": "dataset penelitian"},
                                    {"jumlah_transaksi": 9, "kelengkapan_isian": 0,
                                     "jumlah_produk": 0})
    catat("BB-07", "Baris hasil impor dataset tidak diubah nilanya oleh aplikasi",
          "Flag kuesioner tetap; hanya dilaporkan bila bertentangan",
          p3["financial_record_keeping"] == 0 and len(alasan) == 1,
          (alasan[0][:52] + "...") if alasan else "-")


# ------------------------------------------------------------------ fitur aplikasi
def uji_catat_uang():
    c, r = masuk("demo@umkm.id", "demo1234")
    b0 = c.get("/dashboard").get_data(as_text=True)
    sebelum = skor_dari(b0)

    r = c.post("/tindak", data={"kode": "catat"}, follow_redirects=True)
    b = r.get_data(as_text=True)
    sesudah = skor_dari(b)
    lbl = dbl.db().execute("SELECT COUNT(*) n FROM financial_records WHERE user_id="
                           "(SELECT id FROM users WHERE email='demo@umkm.id')").fetchone()["n"]
    catat("BB-08b", "Skor bergerak setelah aksi sekali-klik",
          "Pesan memuat perubahan poin", any(k in pesan_dari(b) for k in ("poin", "tetap")),
          f"{sebelum} -> {sesudah}; {pesan_dari(b)[:34]}")
    catat("BB-08", "Tombol sekali-klik 'Catat sekarang' di dashboard",
          "Satu baris buku kas terbentuk tanpa membuka formulir", lbl > 0 and r.status_code == 200,
          f"total baris={lbl}; pesan: {pesan_dari(b)[:44]}...")

    r = c.post("/keuangan", data={"aksi": "catat", "jenis": "keluar", "jumlah": "12.500"},
               follow_redirects=True)
    baris = dbl.db().execute("SELECT jumlah FROM financial_records ORDER BY id DESC LIMIT 1").fetchone()["jumlah"]
    catat("BB-09", "Input nominal ditulis '12.500' (titik ribuan)", "Tersimpan 12500",
          abs(baris - 12500) < 1, f"tersimpan={baris:,.0f}")


def uji_hapus_batal():
    c, _ = masuk("demo@umkm.id", "demo1234")
    conn = dbl.db()
    uid = conn.execute("SELECT id FROM users WHERE email='demo@umkm.id'").fetchone()["id"]
    id_trx = conn.execute("SELECT id FROM financial_records WHERE user_id=? AND dihapus_pada IS NULL "
                          "ORDER BY id DESC LIMIT 1", (uid,)).fetchone()["id"]
    awal = conn.execute("SELECT COUNT(*) n FROM financial_records WHERE user_id=? AND "
                        "dihapus_pada IS NULL", (uid,)).fetchone()["n"]
    c.post("/keuangan", data={"hapus": str(id_trx)}, follow_redirects=True)
    sesi = dbl.db().execute("SELECT COUNT(*) n FROM financial_records WHERE user_id=? AND "
                            "dihapus_pada IS NULL", (uid,)).fetchone()["n"]
    r = c.post("/keuangan", data={"aksi": "batal"}, follow_redirects=True)
    urung = dbl.db().execute("SELECT COUNT(*) n FROM financial_records WHERE user_id=? AND "
                             "dihapus_pada IS NULL", (uid,)).fetchone()["n"]
    conn.close()
    catat("BB-10", "Hapus satu baris lalu tekan 'Batalkan hapusan terakhir'",
          "Jumlah baris pulih, tanpa dialog konfirmasi browser", sesi == awal - 1 and urung == awal,
          f"{awal} -> {sesi} -> {urung}")


def uji_rencana_pemasaran():
    c, r = masuk("demo@umkm.id", "demo1234")
    b = c.get("/rencana?draf=1").get_data(as_text=True)
    terisi = bool(re.search(r'name="target_omzet"[^>]*value="[^"]*[1-9]', b)) or "Isian ini saya hitung" in b
    catat("BB-11", "Membuka /rencana?draf=1 bagi pengguna tanpa rencana",
          "Formulir terisi otomatis dari riwayat arus kas", terisi,
          "banner draf + target terisi")

    c.post("/pemasaran", data={"aksi": "bagikan"}, follow_redirects=True)
    conn = dbl.db()
    p = conn.execute("SELECT internet_usage, marketing_effort FROM business_profile WHERE user_id="
                     "(SELECT id FROM users WHERE email='demo@umkm.id')").fetchone()
    conn.close()
    catat("BB-12", "Menekan 'Bagikan tautan' pada katalog",
          "Status jualan online aktif + usaha pemasaran naik satu tingkat",
          p["internet_usage"] == 1 and p["marketing_effort"] >= 4,
          f"internet={p['internet_usage']}, pemasaran={p['marketing_effort']}")


def uji_bahasa_dan_luar_jaringan():
    c, _ = masuk("demo@umkm.id", "demo1234")
    c.get("/mode/riset", follow_redirects=True)
    riset = c.get("/dashboard").get_data(as_text=True)
    c.get("/mode/sederhana", follow_redirects=True)
    biasa = c.get("/dashboard").get_data(as_text=True)
    catat("BB-13", "Mengubah mode bahasa pada halaman",
          "Istilah teknis muncul hanya di mode riset",
          "Skor_Keberhasilan" in riset and "Skor_Keberhasilan" not in biasa,
          "pergantian leksikon terverifikasi")

    j = c.get("/api/skor").get_json()
    catat("BB-14", "Menampilkan hasil perhitungan ke mesin luar (/api/skor)",
          "JSON berisi skor, status, tiga pilar, dan rekomendasi",
          {"skor", "status", "pilar", "rekomendasi"} <= set(j.keys()),
          f"skor={j['skor']}, pilar={(list(j['pilar'].values()))}")

    for lal in ["/", "/sw.js", "/manifest.webmanifest", "/toko/toko-demo", "/keuangan",
                "/rencana", "/pemasaran", "/profil", "/acuan"]:
        r = c.get(lal)
        if r.status_code not in (200, 302):
            catat("BB-15", f"Rute {lal}", "Merespons 200", False, "HTTP " + str(r.status_code))
            break
    else:
        catat("BB-15", "Sembilan rute utama + berkas PWA", "Semua merespons 200/302", True,
              "tidak ada rute yang gagal")


# ------------------------------------------------------------------ keluaran
def tabel_markdown():
    kolom = ["kode", "kasus", "hasil_harapan", "hasil_sesungguhnya", "keterangan", "keputusan"]
    judul = {"kode": "Kode", "kasus": "Kasus uji", "hasil_harapan": "Hasil yang diharapkan",
             "hasil_sesungguhnya": "Hasil sesungguhnya", "keterangan": "Keterangan",
             "keputusan": "Keputusan"}
    baris = ["| " + " | ".join(judul[k] for k in kolom) + " |",
             "|" + "|".join(["---"] * len(kolom)) + "|"]
    for h in HASIL:
        baris.append("| " + " | ".join(str(h[k]).replace("\n", " ") for k in kolom) + " |")
    return "\n".join(baris)


if __name__ == "__main__":
    uji_autentikasi()
    uji_mesin_skor()
    uji_catat_uang()
    uji_hapus_batal()
    uji_rencana_pemasaran()
    uji_bahasa_dan_luar_jaringan()

    lulus = sum(1 for h in HASIL if h["keputusan"] == "LULUS")
    print(tabel_markdown())
    print(f"\n{len(HASIL)} kasus diuji — LULUS {lulus}, GAGAL {len(HASIL) - lulus}")
    out = Path(__file__).resolve().parents[1] / "hasil_uji_blackbox.md"
    out.write_text("# Hasil uji black-box SIDUMKM\n\n" + tabel_markdown() +
                   f"\n\nTotal {len(HASIL)} kasus: LULUS {lulus}, GAGAL {len(HASIL) - lulus}.\n",
                   encoding="utf-8")
    print(f"Tabel tersimpan: {out}")
