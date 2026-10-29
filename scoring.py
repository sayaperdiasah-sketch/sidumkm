"""
SIDUMKM — Rule-Based Scoring Engine
===================================
Pengganti model machine learning. Seluruh bobot, threshold, dan business rule
diturunkan dari hasil analisis 250 data UMKM (lihat `ATURAN_ACUAN`).

Fungsi utama:
    hitung_skor_umkm(profil, modul)  -> dict skor total + skor per pilar
    generate_rekomendasi(profil, modul) -> list rekomendasi berprioritas
"""

# ----- Bobot indikator (total = 100) -------------------------------------
BOBOT = {
    "financial_record_keeping": 25,   # faktor terkuat, r = 0.568
    "business_plan": 20,              # faktor kedua,   r = 0.450
    "marketing_effort": 15,           # r = 0.239
    "internet_usage": 10,
    "initial_capital": 10,
    "industry_experience": 10,
    "partnership": 5,
    "professional_advice": 5,
}

THRESHOLD_BERHASIL = 50

# Ambang batas bandungan modal awal -> nilai ternormalisasi 0..1
JANGKAUAN_MODAL = [
    (1_000_000, 0.20),
    (5_000_000, 0.45),
    (10_000_000, 0.65),
    (50_000_000, 0.85),
    (float("inf"), 1.00),
]

# ----- Nilai statistik acuan (hasil olahan dataset 250 UMKM) --------------
# Dipakai text business rule di dashboard, bukan untuk dihitung ulang.
ATURAN_ACUAN = {
    "financial_record_keeping": {"berhasil": 77.9, "tidak": 21.1, "selisih": 56.8, "r": 0.568},
    "business_plan": {"berhasil": 70.2, "tidak": 25.2, "selisih": 45.0, "r": 0.450},
    "marketing_effort": {"berhasil": 63.6, "tidak": 38.1, "selisih": 25.5, "r": 0.239},
    "internet_usage": {"berhasil": 60.0, "tidak": 40.0, "selisih": 20.0, "r": 0.191},
    "industry_experience": {"berhasil": 57.4, "tidak": 42.2, "selisih": 15.2, "r": 0.148},
}


# ----- Normalisasi ---------------------------------------------------------
def normalisasi_marketing(nilai):
    """marketing_effort 1..7 -> 0..1"""
    return max(0.0, min(1.0, (int(nilai or 1) - 1) / 6))


def normalisasi_saran(nilai):
    """professional_advice 1..7 -> 0..1"""
    return max(0.0, min(1.0, (int(nilai or 1) - 1) / 6))


def normalisasi_pengalaman(tahun):
    """industry_experience (tahun), dibatasi 20 -> 0..1"""
    return max(0.0, min(1.0, float(tahun or 0) / 20))


def normalisasi_modal(rupiah):
    for batas, nilai in JANGKAUAN_MODAL:
        if float(rupiah or 0) <= batas:
            return nilai
    return 1.0


# ----- Skor per pilar (0..100) --------------------------------------------
def skor_keuangan(profil, modul):
    """Pilar 1 — dikunci oleh konsistensi pencatatan, bukan hanya ada/tidaknya."""
    konsisten = min(1.0, modul.get("hari_catat_30hari", 0) / 20)          # 20 hari cukup
    volume = min(1.0, modul.get("jumlah_transaksi", 0) / 40)
    untung = 1.0 if modul.get("net", 0) > 0 else (0.4 if modul.get("net", 0) == 0 else 0.0)
    margin = max(0.0, min(1.0, (modul.get("margin", 0) or 0) / 0.30))     # margin 30% = penuh
    return round(
        35 * (1 if profil["financial_record_keeping"] else 0)
        + 25 * konsisten
        + 15 * volume
        + 15 * untung
        + 10 * margin,
        1,
    )


def skor_perencanaan(profil, modul):
    """Pilar 2 — kelengkapan rencana + pencapaian target."""
    ada = 1.0 if profil["business_plan"] else (0.45 if modul.get("target_omzet") else 0.0)
    lengkap = min(1.0, modul.get("kelengkapan_isian", 0) / 4)
    capaian = max(0.0, min(1.0, (modul.get("progress_target", 0) or 0) / 100))
    deadline = 1.0 if modul.get("punya_deadline") else 0.0
    return round(35 * ada + 25 * lengkap + 25 * capaian + 15 * deadline, 1)


def skor_pemasaran(profil, modul):
    """Pilar 3 — usaha pemasaran, kehadiran online, dan isi katalog."""
    usaha = normalisasi_marketing(profil["marketing_effort"])
    online = 1.0 if profil["internet_usage"] else 0.0
    katalog = min(1.0, modul.get("jumlah_produk", 0) / 8)
    mitra = normalisasi_saran(profil["professional_advice"])
    return round(40 * usaha + 25 * online + 20 * katalog + 15 * mitra, 1)


# ----- Skor utama ----------------------------------------------------------
def hitung_skor_umkm(profil, modul=None):
    """
    Menghitung Skor Keberhasilan UMKM (0-100) dari 8 indikator.
    `profil` = baris business_profile, `modul` = data isian ketiga pilar.
    """
    modul = modul or {}
    skor = (
        profil["financial_record_keeping"] * BOBOT["financial_record_keeping"]
        + profil["business_plan"] * BOBOT["business_plan"]
        + normalisasi_marketing(profil["marketing_effort"]) * BOBOT["marketing_effort"]
        + profil["internet_usage"] * BOBOT["internet_usage"]
        + normalisasi_modal(profil["initial_capital"]) * BOBOT["initial_capital"]
        + normalisasi_pengalaman(profil["industry_experience"]) * BOBOT["industry_experience"]
        + profil["partnership"] * BOBOT["partnership"]
        + normalisasi_saran(profil["professional_advice"]) * BOBOT["professional_advice"]
    )
    skor = round(max(0.0, min(100.0, skor)), 2)

    pilar = {
        "keuangan": skor_keuangan(profil, modul),
        "perencanaan": skor_perencanaan(profil, modul),
        "pemasaran": skor_pemasaran(profil, modul),
    }
    pilar_total = round(sum(pilar.values()) / 3, 1)

    return {
        "skor": skor,
        "pilar": pilar,
        "pilar_total": pilar_total,
        "status": "Berhasil" if skor >= THRESHOLD_BERHASIL else "Perlu Perbaikan",
        "kategori": (
            "Sangat Baik" if skor >= 75
            else "Baik" if skor >= 60
            else "Cukup" if skor >= 45
            else "Perlu Perbaikan"
        ),
    }


# ----- Business rules ------------------------------------------------------


# ===========================================================================
# Lapisan "permudah pengguna" — sistem yang berpikir, bukan bertanya
# Semua pemetaan di bawah dipakai form pendaftaran/dashboard supaya pelaku UMKM
# cukup memilih kalimat, bukan mengisi angka teknis.
# ===========================================================================

# Kalimat -> nilai 1..7 (user tidak pernah melihat angka 1-7)
PILIHAN_PEMASARAN = {
    1: "Tidak pernah promosi",
    2: "Promosi setahun sekali",
    3: "Promosi beberapa bulan sekali",
    4: "Promosi sebulan sekali",
    5: "Promosi seminggu sekali",
    6: "Promosi hampir tiap hari",
    7: "Promosi tiap hari + pasang iklan",
}
PILIHAN_SARAN = {
    1: "Belum pernah bertanya ke siapa pun",
    2: "Ngobrol dengan sesama pedagang",
    3: "Pernah ikut sosialisasi dinas",
    4: "Rutin didamping pendamping UMKM",
    5: "Rutin konsultasi bank / koperasi",
    6: "Pernah dibina inkubator usaha",
    7: "Punya akuntan / konsultan tetap",
}
# Kalimat -> nilai rupiah (untuk jangkauan modal)
PILIHAN_MODAL = {
    1: ("Kurang dari Rp 1 juta", 500_000),
    2: ("Rp 1 juta - Rp 5 juta", 2_500_000),
    3: ("Rp 5 juta - Rp 10 juta", 7_500_000),
    4: ("Rp 10 juta - Rp 50 juta", 25_000_000),
    5: ("Lebih dari Rp 50 juta", 75_000_000),
}

# Biaya waktu (menit) tiap tindakan — dipakai untuk memilih SATU langkah
BIAYA_MENIT = {
    "Keuangan": 1, "Pemasaran": 3, "Perencanaan": 6, "Edukasi": 90, "Kemitraan": 90,
    "Pertahankan": 1,
}

# Kalimat awam tanpa istilah skor/bobot/indikator
PENGANTAR_AWAM = {
    "catat": "Yuk, catat pemasukan pertama. Cukup ketik uangnya, tombolnya sudah disediakan.",
    "rutin": "Catatannya masih jarang. Sekali tulis hari ini sudah menolong nilai usaha Anda.",
    "rencana": "Buat rencana satu halaman. Isian sudah saya isi dari catatan penjualan Anda, tinggal perbaiki lalu simpan.",
    "produk": "Tambah foto produk ke katalog supaya lebih banyak orang tahu Anda jualan apa.",
    "internet": "Buat tautan katalog lalu kirim ke WhatsApp pelanggan. Satu tombol, langsung jadi.",
    "alami": "Pengalaman bisa ditambah lewat pelatihan. Tidak mengubah nilai hari ini, jadi kerjakan kalau sempat.",
    "mitra": "Bergabung dengan komunitas usaha. Efeknya kecil tapi menahan penjualan supaya tidak macet.",
    "jaga": "Semua sudah baik. Tugas Anda tinggal mempertahankan catatan setiap hari.",
}


def nilai_dari_kata(pilihan, kata, cadangan=1):
    """Balikkan kalimat pilihan user ke angka 1..7 yang dipakai mesin skor."""
    for angka, teks in pilihan.items():
        if teks == kata:
            return angka
    try:
        return max(1, min(7, int(kata)))
    except (TypeError, ValueError):
        return cadangan


def modal_dari_pilihan(kode):
    try:
        return PILIHAN_MODAL[int(kode)][1]
    except (KeyError, TypeError, ValueError):
        return 0


def verifikasi_insilik(profil, modul):
    """
    Tiga indikator yang tadinya diisi sendiri oleh pengguna (self-report) diverifikasi
    dari perilaku nyata — dua arah: dinyalakan kalau buktinya ada, padamkan kalau buktinya hilang.
    Mengembalikan (profil_terkoreksi, daftar_alasan_manusiawi).
    """
    alasan = []
    profil = dict(profil)

    ada_catatan = modul.get("jumlah_transaksi", 0) >= 1
    if profil["financial_record_keeping"] != int(ada_catatan):
        profil["financial_record_keeping"] = int(ada_catatan)
        alasan.append("Pencatatan keuangan "
                      + ("saya aktifkan" if ada_catatan else "saya nonaktifkan")
                      + f" karena buku Anda {'sudah berisi ' + str(modul['jumlah_transaksi']) + ' catatan' if ada_catatan else 'kosong lagi'}.")

    ada_rencana = modul.get("kelengkapan_isian", 0) >= 2
    if profil["business_plan"] != int(ada_rencana):
        profil["business_plan"] = int(ada_rencana)
        alasan.append("Rencana bisnis " + ("terhitung aktif" if ada_rencana else "belum terhitung")
                      + f" — {'butir target dan strategi sudah terisi' if ada_rencana else 'mininal dua butir harus terisi'}.")

    ada_online = modul.get("jumlah_produk", 0) >= 1
    if profil["internet_usage"] != int(ada_online):
        profil["internet_usage"] = int(ada_online)
        alasan.append("Status jualan online " + ("aktif" if ada_online else "lepas")
                      + f" karena katalog Anda {'bisa dibuka lewat tautan' if ada_online else 'tidak punya produk aktif'}.")

    return profil, alasan


def langkah_terbaik(rekomendasi):
    """
    Pilih SATU tindakan dengan dampak terbesar per menit usaha.
    Daftar panjang membuat pengguna awam bingung; satu tombol menyelesaikannya.
    """
    urut = {"TINGGI": 0, "SEDANG": 1, "RENDAH": 2}
    def skor_prioritas(r):
        return (urut.get(r["prioritas"], 9), BIAYA_MENIT.get(r["modul"], 30))
    if not rekomendasi:
        return None
    return sorted(rekomendasi, key=skor_prioritas)[0]

PRIORITAS_ORDER = {"TINGGI": 0, "SEDANG": 1, "RENDAH": 2}
PRIORITAS_LABEL = {"TINGGI": "merah", "SEDANG": "kuning", "RENDAH": "hijau"}


def generate_rekomendasi(profil, modul=None):
    """
    Rekomendasi dashboard. Tiap butir membawa:
      kode       -> aksi sekali-klik yang bisa dikerjakan mesin
      ajakan     -> kalimat perintah manusiawi (tanpa istilah skor/bobot)
      waktu_menit-> perkiraan usaha, dipakai mesin memilih SATU langkah terdekat
    """
    modul = modul or {}
    a = ATURAN_ACUAN
    out = []

    TOMBOL = {
        "catat": "Catat sekarang", "rencana": "Buka draf rencana saya",
        "produk": "Tambah produk", "bagikan": "Buatkan tautan katalog",
        "edukasi": "Lihat pilihannya", "mitra": "Lihat pilihannya", "jaga": "Lanjut",
    }

    def tambah(kode, prioritas, modul_nama, judul, ajakan, pesan, dampak, tautan, angka, waktu):
        out.append({
            "kode": kode, "prioritas": prioritas, "modul": modul_nama, "ikon": angka,
            "judul": judul, "ajakan": ajakan, "pesan": pesan, "dampak": dampak,
            "tautan": tautan, "waktu_menit": waktu, "tombol": TOMBOL.get(kode, "Lanjutkan"),
            # tindak hanya bisa dikerjakan mesin untuk empat kode ini; sisanya berupa tautan
            "langsung": kode in ("catat", "rencana", "produk", "bagikan"),
        })

    if not profil["financial_record_keeping"]:
        tambah("catat", "TINGGI", "Keuangan", "Mulai catatan keuangan",
              PENGANTAR_AWAM["catat"],
              (f"UMKM dengan catatan keuangan baik memiliki peluang sukses "
               f"{a['financial_record_keeping']['berhasil']}% vs "
               f"{a['financial_record_keeping']['tidak']}% jika tidak."),
              f"+{a['financial_record_keeping']['selisih']} poin peluang sukses", "/keuangan", "buku", 1)
    elif modul.get("hari_catat_30hari", 0) < 10:
        tambah("catat", "SEDANG", "Keuangan", "Catatan belum rutin",
              PENGANTAR_AWAM["rutin"],
              (f"Baru {modul.get('hari_catat_30hari', 0)} hari tercatat dalam 30 hari terakhir."),
              "+15 poin skor pilar Keuangan", "/keuangan", "buku", 1)

    if not profil["business_plan"]:
        tambah("rencana", "TINGGI", "Perencanaan", "Buat rencana usaha",
              PENGANTAR_AWAM["rencana"],
              (f"UMKM dengan rencana bisnis memiliki peluang sukses "
               f"{a['business_plan']['berhasil']}% vs {a['business_plan']['tidak']}% jika tidak."),
              f"+{a['business_plan']['selisih']} poin peluang sukses", "/rencana", "papan", 6)

    if profil["marketing_effort"] <= 3:
        tambah("produk", "SEDANG", "Pemasaran", "Tambah produk ke katalog",
              PENGANTAR_AWAM["produk"],
              (f"Pemasaran tinggi (6-7) berhasil {a['marketing_effort']['berhasil']}% vs "
               f"rendah (1-3) {a['marketing_effort']['tidak']}%."),
              f"+{a['marketing_effort']['selisih']} poin peluang sukses", "/pemasaran", "megafon", 3)

    if not profil["internet_usage"]:
        tambah("bagikan", "SEDANG", "Pemasaran", "Pasang katalog di internet",
              PENGANTAR_AWAM["internet"],
              (f"UMKM yang memanfaatkan internet berhasil "
               f"{a['internet_usage']['berhasil']}% vs {a['internet_usage']['tidak']}%."),
              f"+{a['internet_usage']['selisih']} poin peluang sukses", "/pemasaran", "jaring", 2)

    if modul.get("jumlah_produk", 0) < 3 and profil["internet_usage"]:
        tambah("produk", "RENDAH", "Pemasaran", "Lengkapi katalog",
              PENGANTAR_AWAM["produk"],
              "Katalog dengan lebih dari 8 produk membuat skor pilar Pemasaran penuh.",
              "+20 poin skor pilar Pemasaran", "/pemasaran", "keranjang", 3)

    if profil["industry_experience"] < 5:
        tambah("edukasi", "RENDAH", "Edukasi", "Ikut pelatihan usaha",
              PENGANTAR_AWAM["alami"],
              (f"Pengalaman di bawah 5 tahun berpeluang sukses "
               f"{a['industry_experience']['tidak']}%; selisihnya "
               f"{a['industry_experience']['selisih']} poin."),
              f"+{a['industry_experience']['selisih']} poin peluang sukses", "/acuan", "bintang", 90)

    if not profil["partnership"]:
        tambah("mitra", "RENDAH", "Kemitraan", "Bergabung ke komunitas usaha",
              PENGANTAR_AWAM["mitra"],
              "Bobot kemitraan memang kecil (5 poin) tetapi menahan pemasaran agar tidak stagnan.",
              "+5 poin skor", "/pemasaran", "simpul", 90)

    if not out:
        tambah("jaga", "RENDAH", "Pertahankan", "Semua sudah baik",
              PENGANTAR_AWAM["jaga"],
              "Tugas Anda tinggal mempertahankan catatan setiap hari.",
              "Skor bertahan", "/keuangan", "ceklis", 1)

    for r in out:
        r["warna"] = PRIORITAS_LABEL.get(r["prioritas"], "hijau")
    out.sort(key=lambda r: PRIORITAS_ORDER.get(r["prioritas"], 9))

    return out

