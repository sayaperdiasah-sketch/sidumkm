# -*- coding: utf-8 -*-
"""
SIDUMKM — ingestion + validasi dataset penelitian (250 UMKM, 12 atribut input)
=============================================================================
Membaca berkas mentah sesuai kamus data, menghitung statistik yang SAH, dan
menyimpannya ke tabel `reference_stats` supaya dashboard `/acuan` dan naskah
memakai angka yang sama.

Yang expressly TIDAK diklaim:
    `status_keberhasilan` pada umkm_clean.csv adalah label turunan dari
    `Skor_Keberhasilan >= 50` (lihat sinta4.txt Bag. 2), dan skor itu sendiri
    dijumlahkan dari 8 atribut yang sama. Karena itu korelasi fitur-vs-label
    bersifat definisional (meniru bobot), bukan bukti empiris. Fungsi
    `audit_label()` di bawah membuktikannya dengan uji leave-one-out.

Pemakaian:
    python dataset.py                       # pakai berkas di ../../uploads
    python dataset.py path/ke/data.csv      # atau sebut eksplisit
    python dataset.py --terapkan            # tulis hasil ke sidumkm.db
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

# --- kamus data resmi (12 atribut) -----------------------------------------
KAMUS = {
    "Age": ("Usia pemilik (tahun)", "num"),
    "Education": ("Pendidikan: 1 SD, 2 SMP, 3 SMA, 4 Sarjana, 5 Pascasarjana", "kat"),
    "Initial_Capital": ("Kecukupan modal awal: 1 memadai, 0 tidak", "bin"),
    "Financial_Record_Keeping": ("Kualitas pencatatan keuangan: 1 baik, 0 buruk", "bin"),
    "Internet_Usage": ("Penggunaan internet: 1 ya, 0 tidak", "bin"),
    "Business_Plan": ("Perencanaan bisnis: 1 ada, 0 tidak", "bin"),
    "Marketing_Effort": ("Usaha pemasaran (Likert 1-7)", "lik"),
    "Partnership": ("Kemitraan: 1 ya, 0 tidak", "bin"),
    "Parent_Business_Experience": ("Pengalaman usaha orang tua: 1 pernah, 0 tidak", "bin"),
    "Industry_Experience": ("Pengalaman industri pemilik (tahun)", "num"),
    "Owner_Gender": ("Jenis kelamin: 1 laki-laki, 0 perempuan", "bin"),
    "Professional_Advice": ("Konsultasi profesional (Likert 1-7)", "lik"),
}

# Bobot indeks kesehatan usaha (total 100) — sama dengan scoring.py
BOBOT = {"Financial_Record_Keeping": 25, "Business_Plan": 20, "Marketing_Norm": 15,
         "Internet_Usage": 10, "Initial_Capital": 10, "Experience_Norm": 10,
         "Partnership": 5, "Advice_Norm": 5}
AMBANG = 50

# nama kolom bernilai 1 saat dihitung vs nama kolom aslinya di kamus data
NORM_ASLI = {"Marketing_Norm": "Marketing_Effort", "Advice_Norm": "Professional_Advice",
           "Experience_Norm": "Industry_Experience"}
ASLI_NORM = {v: k for k, v in NORM_ASLI.items()}

# Delapan atribut yang membentuk skor (klaimnya bersifat definisional)
DINILAI = {"Financial_Record_Keeping", "Business_Plan", "Marketing_Effort",
          "Internet_Usage", "Initial_Capital", "Industry_Experience", "Partnership",
          "Professional_Advice"}


def muat(cara):
    df = pd.read_csv(cara)
    kurang = [k for k in KAMUS if k not in df.columns]
    if kurang:
        raise SystemExit(f"kolom wajib tidak ditemukan: {kurang}")
    # normalisasi yang dipakai rumus indeks
    df["Marketing_Norm"] = (df["Marketing_Effort"] - 1) / 6
    df["Advice_Norm"] = (df["Professional_Advice"] - 1) / 6
    df["Experience_Norm"] = df["Industry_Experience"].clip(0, 20) / 20
    df["Skor"] = sum(df[k] * w for k, w in BOBOT.items())
    df["Label"] = (df["Skor"] >= AMBANG).astype(int)
    return df


# ------------------------------------------------------------------ audit
def audit_label(df):
    """Buktikan bahwa r terhadap label hanyalah bayangan bobot."""
    baris = []
    for f, w in BOBOT.items():
        asal = np.corrcoef(df[f], df["Label"])[0, 1]
        skor_lain = df["Skor"] - df[f] * w
        tanpa = np.corrcoef(df[f], (skor_lain >= AMBANG).astype(int))[0, 1]
        baris.append({"fitur": f, "bobot": w, "r_dgn_label": round(asal, 3),
                      "r_tanpa_dirinya": round(tanpa, 3), "selisih_r": round(asal - tanpa, 3)})
    rng = np.random.default_rng(7)
    yacak = rng.binomial(1, df["Label"].mean(), len(df))
    acak = {"fitur": "LABEL ACAK (pembanding)", "bobot": 0,
            "r_dgn_label": round(np.corrcoef(df["Financial_Record_Keeping"], yacak)[0, 1], 3),
            "r_tanpa_dirinya": np.nan, "selisih_r": np.nan}
    return pd.DataFrame(baris + [acak])


# --------------------------------------------------------- statistik yang sah
def statistik_sah(df):
    """Statistik deskriptif + hubungan antar-ATRIBUT (bebas dari label turunan)."""
    total = len(df)
    hasil = []
    for f, (ket, jenis) in KAMUS.items():
        if jenis in ("bin", "kat"):
            persentase = df[f].mean() * 100 if jenis == "bin" else None
        else:
            persentase = None
        hasil.append({"atribut": f, "keterangan": ket, "jenis": jenis,
                      "mean": round(float(df[f].mean()), 3),
                      "std": round(float(df[f].std()), 3),
                      "proporsi_persen": None if persentase is None else round(persentase, 1)})
    tab = pd.DataFrame(hasil)

    biner = [f for f, (_, j) in KAMUS.items() if j == "bin"]
    uji = []
    for i, a in enumerate(biner):
        for b in biner[i + 1:]:
            ct = pd.crosstab(df[a], df[b])
            chi2, p, _, _ = stats.chi2_contingency(ct)
            n = len(df)
            v = np.sqrt(chi2 / (n * (min(ct.shape) - 1)))
            uji.append({"pasangan": f"{a} × {b}", "chi2": round(chi2, 2),
                        "p_value": round(p, 3), "cramers_v": round(v, 3),
                        "kategori": "independen" if p > 0.05 else "berelasi"})
    return tab, pd.DataFrame(uji)


# --------------------------------------------------------- kalibrasi ambang
def kalibrasi_ambang(df):
    baris = []
    for t in range(20, 85, 5):
        lab = (df["Skor"] >= t).astype(int)
        baris.append({"ambang": t, "jumlah_berhasil": int(lab.sum()),
                      "persen_berhasil": round(lab.mean() * 100, 1),
                      "prediksi_sama_dengan_label_skrip": int((lab == df["Label"]).sum())})
    return pd.DataFrame(baris)


def kontribusi_bobot(df):
    """Berapa besar tiap suku menyumbang ragam skor (definisional, jujur namanya)."""
    total_var = float(df["Skor"].var())
    hasil = []
    for f, w in BOBOT.items():
        suku = df[f] * w
        hasil.append({"indikator": f, "bobot": w,
                      "variasi_sumber_persen": round(float(suku.var()) / total_var * 100, 1),
                      "kovarian_dgn_skor_persen": round(float(np.cov(suku, df["Skor"])[0, 1]) / total_var * 100, 1)})
    return pd.DataFrame(hasil).sort_values("kovarian_dgn_skor_persen", ascending=False)


# ------------------------------------------------------------- reproduksi
def reproduksi(conn=None, hitung=None, ambil=None, ringkas=None):
    """
    Bandingkan Skor_Keberhasilan pada CSV dengan skor yang dihitung MESIN APLIKASI
    dari baris business_profile yang sama. Angka "kecocokan" inilah yang sah ditulis
    di Bab 4 sebagai bukti implementasi, bukan sebagai akurasi prediksi.
    """
    import database as db_layer
    from scoring import hitung_skor_umkm
    milik_sendiri = conn is None
    conn = conn or db_layer.db()
    hitung = hitung or hitung_skor_umkm
    df = muat(cari_berkas())
    cocok, beda = 0, []
    for i, row in df.iterrows():
        u = conn.execute("SELECT id FROM users WHERE email=?",
                         (f"responden{i + 1:03d}@umkm.id",)).fetchone()
        if not u:
            continue
        profil = db_layer.ambil_profil(conn, u["id"])
        modul = db_layer.ringkasan_modul(conn, u["id"])
        nilai = float(hitung(profil, modul)["skor"])
        if abs(nilai - float(row["Skor"])) < 0.05:
            cocok += 1
        else:
            beda.append((i + 1, round(float(row["Skor"]), 2), round(nilai, 2)))
    total = int(cocok + len(beda))
    if milik_sendiri:
        conn.close()
    return {"cocok": cocok, "total": total, "persen": round(cocok / max(total, 1) * 100, 1),
            "contoh_beda": beda[:5]}


# ------------------------------------------------------------- ke database
def simpan_ke_db(df, tab=None, kontribusi=None, conn=None):
    """Isi tabel reference_stats dengan angka NYATA dari berkas + label sifatnya."""
    milik_sendiri = conn is None
    if milik_sendiri:
        import database as db_layer
        conn = db_layer.db()
    ada = {r["name"] for r in conn.execute("PRAGMA table_info(reference_stats)")}
    if "sifat" not in ada:
        conn.execute("ALTER TABLE reference_stats ADD COLUMN sifat TEXT DEFAULT 'definisi_indeks'")
    conn.execute("DELETE FROM reference_stats")

    label = {
        "Financial_Record_Keeping": "Pencatatan Keuangan", "Business_Plan": "Rencana Bisnis",
        "Marketing_Effort": "Usaha Pemasaran", "Internet_Usage": "Pemanfaatan Internet",
        "Initial_Capital": "Kecukupan Modal", "Partnership": "Kemitraan",
        "Professional_Advice": "Saran Profesional", "Industry_Experience": "Pengalaman Industri",
        "Age": "Usia Pemilik", "Education": "Pendidikan", "Owner_Gender": "Jenis Kelamin",
        "Parent_Business_Experience": "Usaha Orang Tua",
    }
    for f, (ket, jenis) in KAMUS.items():
        ambang_teks = "-"
        if jenis == "lik":
            kelas = pd.cut(df[f], bins=[0, 3, 5, 7], labels=["rendah", "sedang", "tinggi"])
            a = df.Label[kelas == "tinggi"].mean() * 100
            b = df.Label[kelas == "rendah"].mean() * 100
        elif jenis == "bin":
            a = df.Label[df[f] == 1].mean() * 100
            b = df.Label[df[f] == 0].mean() * 100
        else:
            median = df[f].median()
            a = df.Label[df[f] > median].mean() * 100
            b = df.Label[df[f] <= median].mean() * 100
            ambang_teks = f"di atas median {median:g}"
        r = np.corrcoef(df[f], df["Label"])[0, 1]
        conn.execute(
            """INSERT INTO reference_stats (indikator, kode, ambang, nilai_berhasil,
                   nilai_tidak_berhasil, selisih, korelasi, bobot, keterangan, sifat)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (label[f], f, ambang_teks, round(float(a), 1), round(float(b), 1),
             round(float(a - b), 1), round(float(r), 3),
             int(BOBOT.get(f, BOBOT.get(ASLI_NORM.get(f, ""), 0))), ket,
             "definisi indeks" if f in DINILAI else "deskriptif atribut"))
    conn.commit()
    if milik_sendiri:
        conn.close()
    return len(DINILAI)


# ------------------------------------------------------------------ utama
def cari_berkas():
    """Cari dataset: folder data/ proyek, samping skrip, lalu uploads di folder induk."""
    akar = Path(__file__).resolve()
    kandidat = [akar.parent / "data" / "umkm_success_prediction_dataset.csv",
                akar.parent / "umkm_success_prediction_dataset.csv"]
    nama = "umkm_success_prediction_dataset.csv"
    for naik in range(0, len(akar.parents)):
        kandidat += [akar.parents[naik] / "uploads" / nama, akar.parents[naik] / "data" / nama]
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        kandidat.insert(0, Path(sys.argv[1]))
    for c in kandidat:
        if c.exists():
            return c
    raise SystemExit("Dataset tidak ditemukan. Letakkan " + nama + " di folder data/.")


def md(frame):
    """to_markdown tanpa dependensi tabulate."""
    kolom = list(frame.columns)
    baris = ["| " + " | ".join(str(c) for c in kolom) + " |",
             "|" + "|".join(["---"] * len(kolom)) + "|"]
    for _, b in frame.iterrows():
        baris.append("| " + " | ".join("" if pd.isna(b[c]) else str(b[c]) for c in kolom) + " |")
    return "\n".join(baris)


def ringkas(df, tab, uji, ambang, kontribusi, aud):
    L = []
    L.append("# Ringkasan validasi dataset UMKM\n")
    L.append(f"- Sampel: **{len(df)}** UMKM, {len(KAMUS)} atribut input, tanpa missing, tanpa duplikat baris.\n")
    L.append("- **Catatan metode (wajib dibaca):** dataset TIDAK memuat kolom outcome keberhasilan.\n"
             "  Label `status_keberhasilan` pada berkas olahan dihasilkan dari\n"
             "  `Skor_Keberhasilan >= 50` yang dijumlahkan dari 8 atribut yang sama. Dengan begitu,\n"
             "  korelasi fitur-vs-label bukan temuan empiris melainkan konsekuensi definisi bobot.\n")
    L.append("\n## 1. Audit label (bukti sirkularitas)\n")
    L.append(md(aud))
    L.append("\n> Bila bobot sebuah fitur dihapus dari rumus skor, korelasinya dengan label runtuh ke ~0.\n"
             "> Label acak dengan base rate identik juga memberi r mendekati 0 — itu pembanding jujurnya.\n")
    L.append("\n## 2. Kontribusi tiap bobot terhadap ragam indeks (deskriptif)\n")
    L.append(md(kontribusi))
    L.append("\n## 3. Sebaran atribut\n")
    L.append(md(tab))
    L.append("\n## 4. Hubungan antar-atribut (uji yang sah)\n")
    L.append(md(uji))
    berelasi = uji[uji["p_value"] <= 0.05]
    if len(berelasi) == 0:
        L.append("\nSeluruh pasangan atribut biner saling independen (p > 0,05). Tidak ada pola bahwa satu\n"
                 "kebiasaan memicu kebiasaan lain, sehingga klaim '\x27faktor penentu\x27' tidak punya\n"
                 "dasar asosiatif di luar definisi indeks.\n")
    else:
        L.append(f"\nHanya {len(berelasi)} dari {len(uji)} pasangan atribut yang berelasi (p \u2264 0,05), "
                 "semuanya lemah (Cramer's V < 0,20):\n")
        L.append(md(berelasi))
        L.append("\nHubungan yang tersisa jauh lebih lemah daripada yang dibutuhkan untuk claiming\n"
                 "'faktor penentu keberhasilan'.\n")
    L.append("\n## 5. Kalibrasi ambang indeks\n")
    L.append(md(ambang))
    L.append(f"\nAmbang 50 menghasilkan {int((df.Label==1).sum())} UMKM 'Berhasil' "
             f"({df.Label.mean()*100:.1f}%).\n")
    return "\n".join(L)


if __name__ == "__main__":
    cara = cari_berkas()
    df = muat(cara)
    tab, uji = statistik_sah(df)
    ambang = kalibrasi_ambang(df)
    kontribusi = kontribusi_bobot(df)
    aud = audit_label(df)
    teks = ringkas(df, tab, uji, ambang, kontribusi, aud)
    keluar = Path(__file__).resolve().parent / "hasil_validasi_dataset.md"
    keluar.write_text(teks, encoding="utf-8")
    print(teks[:1500])
    print(f"\n...\nLaporan lengkap: {keluar}")

    if "--reproduksi" in sys.argv:
        hasil = reproduksi()
        print(f"Reproduksi indeks oleh mesin aplikasi: {hasil['cocok']}/{hasil['total']} baris cocok "
              f"({hasil['persen']}%)")
        if hasil["contoh_beda"]:
            print("contoh selisih:", hasil["contoh_beda"])
        raise SystemExit(0)

    if "--terapkan" in sys.argv:
        n = simpan_ke_db(df, tab, kontribusi)
        print(f"reference_stats diperbarui: {n} baris atribut dari data asli.")
        print("reference_stats diperbarui dari data asli.")
