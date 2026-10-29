# Ringkasan validasi dataset UMKM

- Sampel: **250** UMKM, 12 atribut input, tanpa missing, tanpa duplikat baris.

- **Catatan metode (wajib dibaca):** dataset TIDAK memuat kolom outcome keberhasilan.
  Label `status_keberhasilan` pada berkas olahan dihasilkan dari
  `Skor_Keberhasilan >= 50` yang dijumlahkan dari 8 atribut yang sama. Dengan begitu,
  korelasi fitur-vs-label bukan temuan empiris melainkan konsekuensi definisi bobot.


## 1. Audit label (bukti sirkularitas)

| fitur | bobot | r_dgn_label | r_tanpa_dirinya | selisih_r |
|---|---|---|---|---|
| Financial_Record_Keeping | 25 | 0.568 | -0.018 | 0.585 |
| Business_Plan | 20 | 0.45 | -0.0 | 0.45 |
| Marketing_Norm | 15 | 0.239 | 0.023 | 0.217 |
| Internet_Usage | 10 | 0.199 | -0.037 | 0.236 |
| Initial_Capital | 10 | 0.241 | 0.033 | 0.208 |
| Experience_Norm | 10 | 0.136 | 0.013 | 0.123 |
| Partnership | 5 | -0.034 | -0.104 | 0.07 |
| Advice_Norm | 5 | 0.096 | 0.002 | 0.094 |
| LABEL ACAK (pembanding) | 0 | -0.087 |  |  |

> Bila bobot sebuah fitur dihapus dari rumus skor, korelasinya dengan label runtuh ke ~0.
> Label acak dengan base rate identik juga memberi r mendekati 0 — itu pembanding jujurnya.


## 2. Kontribusi tiap bobot terhadap ragam indeks (deskriptif)

| indikator | bobot | variasi_sumber_persen | kovarian_dgn_skor_persen |
|---|---|---|---|
| Financial_Record_Keeping | 25 | 44.6 | 44.2 |
| Business_Plan | 20 | 28.5 | 31.2 |
| Initial_Capital | 10 | 7.1 | 8.1 |
| Marketing_Norm | 15 | 7.1 | 7.3 |
| Internet_Usage | 10 | 7.0 | 5.3 |
| Experience_Norm | 10 | 2.7 | 2.8 |
| Advice_Norm | 5 | 0.9 | 0.7 |
| Partnership | 5 | 1.8 | 0.5 |

## 3. Sebaran atribut

| atribut | keterangan | jenis | mean | std | proporsi_persen |
|---|---|---|---|---|---|
| Age | Usia pemilik (tahun) | num | 39.76 | 12.806 |  |
| Education | Pendidikan: 1 SD, 2 SMP, 3 SMA, 4 Sarjana, 5 Pascasarjana | kat | 2.876 | 1.407 |  |
| Initial_Capital | Kecukupan modal awal: 1 memadai, 0 tidak | bin | 0.516 | 0.501 | 51.6 |
| Financial_Record_Keeping | Kualitas pencatatan keuangan: 1 baik, 0 buruk | bin | 0.488 | 0.501 | 48.8 |
| Internet_Usage | Penggunaan internet: 1 ya, 0 tidak | bin | 0.44 | 0.497 | 44.0 |
| Business_Plan | Perencanaan bisnis: 1 ada, 0 tidak | bin | 0.524 | 0.5 | 52.4 |
| Marketing_Effort | Usaha pemasaran (Likert 1-7) | lik | 3.996 | 1.993 |  |
| Partnership | Kemitraan: 1 ya, 0 tidak | bin | 0.46 | 0.499 | 46.0 |
| Parent_Business_Experience | Pengalaman usaha orang tua: 1 pernah, 0 tidak | bin | 0.44 | 0.497 | 44.0 |
| Industry_Experience | Pengalaman industri pemilik (tahun) | num | 9.76 | 6.165 |  |
| Owner_Gender | Jenis kelamin: 1 laki-laki, 0 perempuan | bin | 0.564 | 0.497 | 56.4 |
| Professional_Advice | Konsultasi profesional (Likert 1-7) | lik | 4.14 | 2.079 |  |

## 4. Hubungan antar-atribut (uji yang sah)

| pasangan | chi2 | p_value | cramers_v | kategori |
|---|---|---|---|---|
| Initial_Capital × Financial_Record_Keeping | 0.14 | 0.713 | 0.023 | independen |
| Initial_Capital × Internet_Usage | 1.18 | 0.277 | 0.069 | independen |
| Initial_Capital × Business_Plan | 9.1 | 0.003 | 0.191 | berelasi |
| Initial_Capital × Partnership | 0.95 | 0.33 | 0.062 | independen |
| Initial_Capital × Parent_Business_Experience | 0.0 | 0.947 | 0.004 | independen |
| Initial_Capital × Owner_Gender | 0.1 | 0.749 | 0.02 | independen |
| Financial_Record_Keeping × Internet_Usage | 0.09 | 0.764 | 0.019 | independen |
| Financial_Record_Keeping × Business_Plan | 0.02 | 0.885 | 0.009 | independen |
| Financial_Record_Keeping × Partnership | 5.96 | 0.015 | 0.154 | berelasi |
| Financial_Record_Keeping × Parent_Business_Experience | 1.74 | 0.187 | 0.084 | independen |
| Financial_Record_Keeping × Owner_Gender | 0.03 | 0.86 | 0.011 | independen |
| Internet_Usage × Business_Plan | 0.3 | 0.585 | 0.035 | independen |
| Internet_Usage × Partnership | 0.24 | 0.627 | 0.031 | independen |
| Internet_Usage × Parent_Business_Experience | 0.55 | 0.457 | 0.047 | independen |
| Internet_Usage × Owner_Gender | 0.4 | 0.527 | 0.04 | independen |
| Business_Plan × Partnership | 0.1 | 0.753 | 0.02 | independen |
| Business_Plan × Parent_Business_Experience | 0.0 | 0.972 | 0.002 | independen |
| Business_Plan × Owner_Gender | 0.02 | 0.875 | 0.01 | independen |
| Partnership × Parent_Business_Experience | 0.99 | 0.319 | 0.063 | independen |
| Partnership × Owner_Gender | 0.12 | 0.728 | 0.022 | independen |
| Parent_Business_Experience × Owner_Gender | 4.81 | 0.028 | 0.139 | berelasi |

Hanya 3 dari 21 pasangan atribut yang berelasi (p ≤ 0,05), semuanya lemah (Cramer's V < 0,20):

| pasangan | chi2 | p_value | cramers_v | kategori |
|---|---|---|---|---|
| Initial_Capital × Business_Plan | 9.1 | 0.003 | 0.191 | berelasi |
| Financial_Record_Keeping × Partnership | 5.96 | 0.015 | 0.154 | berelasi |
| Parent_Business_Experience × Owner_Gender | 4.81 | 0.028 | 0.139 | berelasi |

Hubungan yang tersisa jauh lebih lemah daripada yang dibutuhkan untuk claiming
'faktor penentu keberhasilan'.


## 5. Kalibrasi ambang indeks

| ambang | jumlah_berhasil | persen_berhasil | prediksi_sama_dengan_label_skrip |
|---|---|---|---|
| 20.0 | 234.0 | 93.6 | 138.0 |
| 25.0 | 222.0 | 88.8 | 150.0 |
| 30.0 | 208.0 | 83.2 | 164.0 |
| 35.0 | 193.0 | 77.2 | 179.0 |
| 40.0 | 170.0 | 68.0 | 202.0 |
| 45.0 | 144.0 | 57.6 | 228.0 |
| 50.0 | 122.0 | 48.8 | 250.0 |
| 55.0 | 98.0 | 39.2 | 226.0 |
| 60.0 | 77.0 | 30.8 | 205.0 |
| 65.0 | 61.0 | 24.4 | 189.0 |
| 70.0 | 36.0 | 14.4 | 164.0 |
| 75.0 | 24.0 | 9.6 | 152.0 |
| 80.0 | 11.0 | 4.4 | 139.0 |

Ambang 50 menghasilkan 122 UMKM 'Berhasil' (48.8%).
