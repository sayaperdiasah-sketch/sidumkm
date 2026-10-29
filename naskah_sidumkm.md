# SIDUMKM — Sistem Pendukung Keputusan Berbasis Web dengan Penilaian Beraturan untuk UMKM

> **Draf naskah untuk jurnal SINTA 4** · berkas kerja. Bagian bertanda `[ISI ...]`
> wajib diisi penulis (identitas, afiliasi, rujukan lokal). Angka-angka dalam naskah ini
> dibangkitkan ulang oleh `dataset.py`, `validasi/uji_hitam.py`, dan `seed.py`.

> **Cat panjang badan naskah (untuk editor):** bagian 3–7 saat ini ±5.950 kata. Untuk artikel
> 6–8 halaman jurnal SINTA, pangkas dengan urutan: gabungkan Subbab 4.1–4.2 jadi satu subbab
> (hemat ±250 kata), pindahkan rincian teknis Subbab 5.5 poin (4)–(6) ke Lampiran (hemat ±300),
> kurangi Tabel 4 menjadi enam baris indeks saja (sisanya ke Lampiran), dan lipat dua narasi
> Subbab 6.8 (hemat ±400). Table & figures: 9 tabel + 3 gambar sudah melebihi kebiasaan 5–6 —
> hapus Tabel 3 dan salin isinya ke dalam narasi 6.1.

**Struktur berkas ini**
1. Judul & identitas
2. Abstrak (ID) / Abstract (EN)
3. Pendahuluan
4. Landasan teori
5. Metode penelitian
6. Hasil dan pembahasan
7. Kesimpulan
8. Daftar pustaka
9. Lampiran A — perintah reproduksi; Lampiran B — daftar fitur & rute

---

## 1. Judul dan identitas

**Judul (utama).** SIDUMKM: Sistem Pendukung Keputusan Berbasis Web dengan Penilaian Beraturan
dan Verifikasi Indikator Otomatis pada Usaha Mikro, Kecil, dan Menengah

**Alternatif bila editor meminta penekanan berbeda**
- *Rancang Bangun Indeks Kesehatan Usaha UMKM Berbasis Web dengan Pendekatan Rule-Based Scoring*
- *Antarmuka Sederhana untuk Pengguna Minim Literasi Digital: Studi Implementasi SPK pada 250 UMKM*

**Penulis.** [ISI nama penulis, NIM, program studi] · **Penulis korespondensi:** [ISI email]
**Afiliasi.** [ISI institusi, kota, negara] · **ORCID:** [ISI bila ada]
**Bidang.** Ilmu Komputer / Sistem Informasi — Sistem Pendukung Keputusan, Pengembangan Sistem

---

## 2. Abstrak

Usaha mikro dan kecil sering kali tidak kekurangan niat untuk mengelola usahanya, melainkan
kekurangan alat yang memberi tahu apa yang harus dikerjakan lebih dulu. Penelitian ini bertujuan
merancang dan membangun **SIDUMKM**, sebuah sistem pendukung keputusan (SPK) berbasis web yang
menilai kesehatan usaha mikro, kecil, dan menengah (UMKM) dengan pendekatan penilaian beraturan
(*rule-based scoring*) di atas indeks delapan komponen berbobot yang bobotnya ditetapkan secara
terdokumentasi dengan merujuk sebaran 250 data UMKM. Sistem dibangun menggunakan Flask (Python) dengan basis data SQLite berelasi
berisi tujuh tabel inti, dan diuji secara black-box serta melalui reproduksi indeks pada
seluruh baris data. Hasil pengujian menunjukkan seluruh indikator sistem berjalan sesuai
spesifikasi pada 16 kasus uji black-box (LULUS 16 dari 16), indeks yang dihitung mesin aplikasi
identik dengan indeks pada berkas data sebanyak 250 dari 250 baris (100%), dan ambang keputusan
50 mengklasifikasikan 48,8% UMKM pada data penelitian sebagai “berhasil”. Berbeda dari SPK pada
umumnya yang berhenti pada perhitungan nilai, sistem ini menambahkan lapisan kemudahan berupa
verifikasi indikator otomatis dari perilaku pencatatan, penyajian satu tindakan terdekat berbasis
perbandingan dampak terhadap waktu pengerjaan, isian cepat yang terisi dari riwayat pengguna,
penghapusan yang dapat dibatalkan, serta dwi-bahasa antarmuka (sehari-hari dan teknis). Dampak
lapisan ini terlihat pada penurunan beban masukan pengguna: tiga dari delapan atribut tidak lagi
ditanyakan karena disimpulkan dari bukti dalam sistem. Simpulan, SPK berbasis aturan yang
transparan dan hemat ketikan layak diimplementasikan untuk pendampingan UMKM; validasi lanjutan
pada lapangan dan pengujian kegunaan dengan pengguna asli masih perlu dilakukan.

**Kata kunci:** sistem pendukung keputusan; UMKM; penilaian beraturan; indeks kesehatan usaha;
antarmuka pengguna; pengujian black-box

> **Catatan penulis (hapus sebelum submit):** abstrak di atas sebaiknya dipangkas ke 150–250 kata
> mengikuti format jurnal tujuan, dan satu kueri angka kontribusi UMKM pada pendahuluan perlu
> diambil dari sumber resmi (BPS/Kemenkop UKM) — lihat bagian *Pendahuluan*.

**Abstract (EN).** Micro and small enterprises rarely lack the willingness to manage their
businesses; what is missing is a tool that tells them what to do first. This study designs and
builds **SIDUMKM**, a web-based decision support system (DSS) that assesses the health of micro,
small, and medium enterprises using rule-based scoring on a six-component weighted index derived
from 250 MSME records. The system was built with Flask (Python) and a relational SQLite database
of seven core tables, and was evaluated through black-box testing and index reproduction over the
entire dataset. All sixteen black-box test cases passed, the scores computed by the application
reproduced the scores in the data file for 250 of 250 records (100%), and a threshold of 50
classified 48.8% of the sampled enterprises as "successful". Unlike conventional DSSs that stop
at computing a value, the system adds a usability layer comprising automatic indicator
verification from recording behaviour, presentation of a single nearest action chosen by impact
per unit of effort, input fields pre-filled from the user's own history, undoable deletion, and a
dual-language interface (everyday and technical). Three of the eight attributes are no longer
asked from the user because they are inferred from evidence inside the system. A transparent,
low-input rule-based DSS is thus practical for MSME mentoring; further field validation and
usability testing with real users remain necessary.

**Keywords:** decision support system; MSMEs; rule-based scoring; enterprise health index;
user interface; black-box testing

---

## 3. Pendahuluan

Usaha mikro, kecil, dan menengah (UMKM) menyerap sebagian besar tenaga kerja Indonesia dan
menyumbang proporsi produk domestik bruto yang besar [ISI: angka terbaru BPS/Kemenkop UKM beserta
tahun dan tautan sumber]. Pada skala yang sama, kematian usaha mikro lebih sering dipicu oleh
manajemen sehari-hari yang tidak tercatat daripada oleh ketidakmampuan memproduksi. Dua kebiasaan
yang secara konsisten muncul pada literature pendampingan usaha adalah pembukuan yang tertib dan
perencanaan tertulis; keduanya murah dijalankan, tetapi justru paling sering diabaikan.

Persoalannya, pelaku UMKM umumnya tidak kekurangan alat pencatat, melainkan kekurangan alat yang
berkata apa yang harus dikerjakan lebih dulu. Aplikasi kasir, buku tulis, grup percakapan, dan
laporan dinas tersedia, tetapi semuanya meminta pengguna yang memahami bahwa pembukuan berkaitan
dengan kelayakan kredit, atau bahwa target penjualan harus ditetapkan sebelum dikejar. Namun ketika
sebuah sistem memaparkan banyak indikator sekaligus kepada pengguna yang baru pertama kali membuka
aplikasi, yang terjadi umumnya bukan pengambilan keputusan, melainkan penundaan: pengguna menutup
layar karena tidak tahu mana yang harus diklik lebih dulu.

Pendekatan berbasis aturan (*rule-based*) menarik untuk konteks ini karena tiga alasan. Pertama,
keputusannya dapat dijelaskan butir demi butir, suatu hal yang tidak diberikan model machine
learning kotak hitam kepada pemilik warung. Kedua, bobot dapat ditetapkan dari hasil analisis
terhadap data lapangan dan didokumentasikan sebagai aturan, sehingga pengulangan penelitian
menjadi mungkin. Ketiga, tanpa proses *training*, sistem tetap dapat dibangun, diuji, dan
dipahami oleh penulis maupun penguji.

Penelitian ini merancang dan membangun **SIDUMKM**, sebuah sistem pendukung keputusan berbasis
web untuk penilaian kesehatan UMKM. Empat hal yang menjadi kontribusi naskah:

1. **Indeks kesehatan usaha berbobot** dengan enam komponen yang pembobotannya diturunkan dari
   hasil pengolahan 250 data UMKM, disusun dengan prosedur penjumlahan tertimbang sehingga nilainya
   dapat ditelusuri ke tiap butirnya.
2. **Lapisan kemudahan pakai** yang memindahkan beban berpikir dari pengguna ke sistem: tiga
   indikator disimpulkan otomatis dari perilaku pencatatan (bukan ditanyakan dan bisa di-self-claim),
   skala Likert 1–7 diganti kalimat, arus kas dicatat dengan satu ketukan, dan tindakan terdekat
   dipilihkan oleh mesin berdasarkan dampak per satuan waktu.
3. **Dwi-bahasa antarmuka** (*sehari-hari* dan *teknis*) dalam satu basis kode, sehingga aplikasi yang
   sama dapat dipakai pendamping lapangan dan dibedah penyusun naskah tanpa saling mengganggu.
4. **Evaluasi ganda** berupa pengujian black-box atas seluruh fungsi dan verifikasi reproduksi
   indeks pada 250 baris data, disertai pembahasan jujur mengenai batas penafsiran angka
   korelasi yang dihasilkan oleh label berbentuk indeks.

Batasan yang perlu dibaca sejak awal: label “berhasil” pada data penelitian ini adalah indeks yang
dihitung dari delapan atribut yang sama, bukan hasil pengukuran keberhasilan usaha di lapangan
secara terpisah. Karena itu naskah ini **tidak mengklaim hubungan sebab akibat** antaratribut
maupun akurasi prediksi. Yang diklaim adalah: (a) rumus indeks dapat direproduksi persis oleh sistem, (b) aturan keputusan dapat dijelaskan dan diverifikasi, serta (c) lapisan kemudahan yang
diusulkan terbukti menurunkan beban masukan pengguna sekaligus memperbaiki kejelasan tindakan
berikutnya.

Rumusan masalah: (1) bagaimana merancang SPK berbasis web yang menghitung kesehatan UMKM dengan
aturan terbuka; (2) bagaimana mengurangi beban masukan bagi pengguna minim literasi digital tanpa
mengorbankan ketepatan perhitungan; dan (3) bagaimana sistem dievaluasi secara fungsional dan
reproduktif. Tujuan penelitian menjawab ketiga hal tersebut. Sistematika penulisan mengikuti pola
pendahuluan, landasan teori, metode, hasil dan pembahasan, serta kesimpulan.

---

## 4. Landasan teori

### 4.1 Sistem pendukung keputusan

Sistem pendukung keputusan adalah sistem interaktif yang membantu pengambil keputusan
memanfaatkan data dan model untuk mengatur suatu situasi yang tidak terstruktur sepenuhnya
(Power, 2002). Turban, Aronson, dan Liang menekankan komponen pembentuknya: basis data, basis
model, dan antarmuka pengguna, dengan tambahan pengetahuan dari pemakai pada siklus pemakaian.
Dalam praktiknya, SPK untuk usaha mikro hampir selalu mengambil bentuk penilaian berbobot
terhadap sekumpulan kriteria, karena keputusan yang diminta adalah “apa yang perlu diperbaiki”,
bukan mencari alternatif optimal di antara sekian pilihan.

Sifat yang paling relevan untuk konteks penelitian ini adalah **keterjelasan**: pengguna
mikro tidak akan menerima angka yang tidak dapat dibongkar. Karena itu sistem tidak memakai model
prediksi kotak hitam, melainkan aturan berbobot yang setiap poinnya dapat ditelusuri ke satu
butir masukan. Pendekatan serupa lazim dipakai pada penelitian SPK UMKM di Indonesia, misalnya
penentuan kelayakan mikro kredit dan prioritas pembinaan [ISI: 2–4 penelitian terdahulu sejenis
yang akan Anda sitasi, usahakan 5 tahun terakhir dan berasal dari jurnal target].

### 4.2 Indeks komposit dan penjumlahan tertimbang

Penilaian multi-atribut dengan penjumlahan tertimbang (*simple additive weighting*, SAW)
menghitung nilai tiap alternatif sebagai jumlah hasil kali antara bobot dan skor atribut yang
telah ternormalisasi (Hwang & Yoon, 1981). Bentuk bakunya ada di bawah ini, dan menjadi dasar
indeks kesehatan usaha pada penelitian ini:

```
A_i = Σ_j  w_j · r_ij ,   dengan r_ij hasil normalisasi atribut j pada responden i
```

Fishburn (1967) menunjukkan bahwa penambahan tertimbang sahih jika atribut saling independen
secara preferensi; MacCrimmon (1968) melengkapi argumen bahwa pembobotan eksplisit justru
membantu pengambil keputusan melihat asumsinya. Karena data penelitian ini hanya berukuran 12
atribut dan sebagian besar biner, normalisasi yang dipakai adalah pemetaan rentang (skala Likert
1–7 menjadi 0–1, pengalaman industri yang dipotong pada 20 tahun menjadi 0–1) dan nilai biner
apa adanya, lalu semua dikalikan total bobot 100.

Perlu ditegaskan sejak bagian teori: indeks semacam ini adalah **alat ukur formatif**. Ia
mendefinisikan keberhasilan menurut aturan yang dipilih penyusunnya, bukan mengungkap hubungan
sebab di lapangan. Konsekuensi penafsirannya dibahas pada Subbab 6.2.

### 4.3 Skala Likert dan batas pengukuran persepsi

Tiga atribut pada data penelitian diukur dengan skala Likert 1–7, yaitu usaha pemasaran,
frekuensi konsultasi profesional, dan (sebagai konsekuensi) dua turunannya setelah normalisasi.
Likert (1932) merancang skala semacam ini untuk mengukur sikap melalui pernyataan verbal, bukan
besaran fisik; akibatnya jarak antar titik skala tidak setara dan penilaian diri rentan bias
kecenderungan tengah serta bias kesopanan.

Dua konsekuensi desain bagi sistem. Pertama, **skala tidak ditampilkan mentah** kepada pengguna:
angka 1–7 diterjemahkan menjadi kalimat berfrekuensi (“sebulan sekali”, “hampir tiap hari”,
“tiap hari plus iklan”) dan pemetaan balik ke angka dilakukan server, sehingga yang masuk ke basis
data tetap 1–7 sesuai kamus variabel tetapi yang dilihat pengguna adalah perilaku konkret. Kedua,
atribut yang **bisa dibuktikan** jangan ditanyakan: tiga indikator dinilai ulang dari bukti
pencatatan agar tidak bergantung pada klaim pengguna.

### 4.4 Kemudahan pakai untuk pengguna minim literasi digital

Davis (1989) memisahkan penerimaan teknologi menjadi manfaat yang dipersepsikan dan kemudahan
yang dipersepsikan; untuk pengguna dengan literasi digital rendah, variabel kedua biasanya yang
menentukan pemakaian berkelanjutan. Davis mendefinisikan kemudahan sebagai “bebas dari usaha”,
dan pada produk nyata beban itu hadir dalam bentuk jumlah ketikan, jumlah pilihan yang harus
dibaca, dan ketidakjelasan langkah berikut.

Karena itu rancangan antarmuka pada penelitian ini mengikuti empat kaidah: (i) satu aksi
per layar untuk tugas inti, (ii) nilai bawaan yang dapat dikoreksi lebih baik daripada kolom
kosong yang harus diisi, (iii) umpan balik sebab–akibat setelah setiap penyimpanan, dan
(iv) pemulihan tanpa hukuman (tindakan berat seperti menghapus dapat dibatalkan). Kaidah ini
dilengkapi persyaratan aksesibilitas minimum WCAG 2.1: target sentuh minimal 44×44 piksel
(kriteria 2.5.5), rasio kontras teks kecil minimal 4,5:1 (kriteria 1.4.3), tautan yang
menjelaskan tujuannya, indikator fokus keyboard yang terlihat, dan pesan status yang dapat
dibacakan teknologi bantu melalui atribut `role="status"` (W3C, 2018).

### 4.5 Aplikasi web progresif (PWA) pada jaringan terbatas

Pendampingan UMKM banyak berlangsung di lokasi dengan koneksi tidak stabil. PWA menutup celah
tersebut tanpa aplikasi toko: sebuah *manifest* mendeklarasikan ikon, warna tema, dan mode tampilan
terpisah, sedangkan *service worker* menyimpan salinan halaman inti beserta asetnya pada cache
sehingga halaman tetap terbentuk saat jaringan hilang, lalu mengambil versi baru ketika pulih
(Dean & Grove, 2016). Pada sistem ini pola yang dipakai adalah *network-first* dengan cadangan
cache, dipilih karena nilai indeks harus mengikuti data terbaru; halaman ringkasan, catat uang,
dan seluruh aset statis termasuk dalam daftar pra-simpan.

Keputusan ini juga memengaruhi arsitektur: berkas *manifest* dan *service worker* disajikan dari
akar situs, bukan dari folder aset, karena cakupan (scope) *service worker* mengikuti lokasi
berkasnya.

---

## 5. Metode penelitian

### 5.1 Jenis dan alur penelitian

Penelitian ini termasuk jenis penelitian dan pengembangan (*research and development*) dengan
model prototipe, karena luaran yang dituju adalah sistem yang dapat diuji dan diulang, bukan
pengujian hipotesis lapangan. Tahapan yang dijalankan:

```
1) Pengumpulan & pemeriksaan data   →  2) Pengolahan (normalisasi, pembobotan, indeks)
        ↓                                        ↓
5) Evaluasi (black-box, reproduksi      3) Perancangan SPK (arsitektur, skema, aturan)
   indeks, kegunaan)                            ↓
        ← 6) Perbaikan berdasar temuan  ←  4) Implementasi (Flask + SQLite + antarmuka)
```

Tahap 1 dan 2 dikerjakan lebih dulu dan hasilnya menjadi masukan penetapan bobot pada tahap 3.
Tahap 4 menghasilkan sistem dengan 16 rute HTTP, dan tahap 5 dieksekusi otomatis melalui dua
skrip yang disertakan bersama naskah (Lampiran A), sehingga seluruh angka pada Bab 6 dapat
dibangkitkan ulang. Penelitian sejenis di Indonesia umumnya memakai alur pengembangan yang sama,
misalnya model ADDIE atau waterfall untuk sistem recommendations [ISI: sitasi bila pembimbing
meminta pembanding metode].

### 5.2 Data dan kamus variabel

Sumber data adalah berkas *umkm_success_prediction_dataset.csv* berisi 250 baris usaha dengan 12 atribut [ISI: sumber data — kuesioner sendiri (lokasi, periode, teknik sampling) atau sumber
publik beserta tautan dan lisensinya; bagian ini wajib diuraikan karena reviewer pasti
menanyakannya]. Pemeriksaan mutu data menghasilkan temuan berikut: tidak ada nilai kosong pada
seluruh kolom, tidak ada baris duplikat utuh, rentang nilai sesuai kamus (usia 18–60, pengalaman
industri 0–20, dua skala Likert 1–7, delapan atribut biner 0/1).

**Tabel 1. Kamus variabel dan sebaran deskriptif (n = 250).**

| Variabel | Tipe | Kode / satuan | Proporsi atau rerata (n=250) |
|---|---|---|---|
| `Age` | numerik | tahun | rerata 39,76 (SD 12,81), rentang 18–60 |
| `Education` | kategorik ordinal | 1 SD, 2 SMP, 3 SMA, 4 Sarjana, 5 Pascasarjana | rerata 2,88 (SD 1,41); SD 60 (24,0%), Sarjana 56 (22,4%), SMA 50 (20,0%), SMP 45 (18,0%), Pascasarjana 39 (15,6%) |
| `Initial_Capital` | biner | 1 = memadai, 0 = tidak memadai | 51,6% memadai |
| `Financial_Record_Keeping` | biner | 1 = pembukuan baik, 0 = buruk | 48,8% baik |
| `Internet_Usage` | biner | 1 = memanfaatkan internet | 44,0% |
| `Business_Plan` | biner | 1 = punya rencana tertulis | 52,4% |
| `Marketing_Effort` | Likert 1–7 | tinggi nilai = sering promosi | rerata 4,00 (SD 1,99); median 4 |
| `Partnership` | biner | 1 = punya kemitraan | 46,0% |
| `Parent_Business_Experience` | biner | 1 = orang tua pernah berusaha | 44,0% |
| `Industry_Experience` | numerik | tahun, dipotong pada 20 untuk normalisasi | rerata 9,76 (SD 6,17) |
| `Owner_Gender` | biner | 1 = laki-laki, 0 = perempuan | 56,4% laki-laki |
| `Professional_Advice` | Likert 1–7 | frekuensi konsultasi profesional | rerata 4,14 (SD 2,08) |

Catatan penting: `Education` hanya berkod 1–5 (tidak ada kode 6) dan `Owner_Gender` memakai 0/1,
bukan 1/2. `Initial_Capital` diukur sebagai **kecukupan**, bukan nominal rupiah. Ketiga hal ini
sengaja ditegaskan karena rancangan awal prototipe sempat memperlakukan modal sebagai rentang
rupiah dan jenis kelamin sebagai dua kode pertama, dan kesalahan semantik semacam ini tidak akan
tampak di antarmuka tetapi membuat angka laporan menyimpang dari data aslinya.

### 5.3 Konstruksi indeks kesehatan usaha

Indeks disusun dengan prosedur penambahan tertimbang seperti pada Persamaan (1). Delapan atribut
ikut dinilai; empat atribut lain (`Age`, `Education`, `Owner_Gender`, `Parent_Business_Experience`) disimpan sebagai data pendamping untuk segmentasi dan tidak diberi
bobot, karena tidak ada dasar teoretis maupun empiris yang cukup untuk memasukkannya ke dalam
indeks.

**Tabel 2. Bobot dan cara normalisasi.**

| Atribut | Bobot | Normalisasi ke 0–1 |
|---|---|---|
| Pencatatan keuangan | 25 | nilai biner apa adanya |
| Rencana bisnis | 20 | nilai biner apa adanya |
| Usaha pemasaran | 15 | (skala − 1) ÷ 6 |
| Pemanfaatan internet | 10 | nilai biner apa adanya |
| Kecukupan modal awal | 10 | nilai biner apa adanya |
| Pengalaman industri | 10 | min(tahun, 20) ÷ 20 |
| Kemitraan | 5 | nilai biner apa adanya |
| Saran profesional | 5 | (skala − 1) ÷ 6 |
| **Jumlah** | **100** | |

Persamaan (2) menyatakan rumus yang diimplementasikan pada `scoring.py`:

```
SKOR = FRK·25 + BP·20 + ((ME−1)/6)·15 + INT·10 + CAP·10
       + (min(EXP,20)/20)·10 + PART·5 + ((PA−1)/6)·5
status = "Berhasil"  jika SKOR ≥ 50  else  "Perlu Perbaikan"
```

Bobot ditetapkan secara **judgement terdokumentasi**, bukan hasil optimasi: urutan besarnya
mengikuti arah dan besar perbedaan proporsi label antarkelompok atribut (Tabel 4) serta
pertimbangan bahwa pembukuan adalah prasyarat bagi perencanaan dan pemasaran yang terukur.
Pemilihan ambang 50 dibahas pada Subbab 6.5. Selain skor total, sistem menghitung tiga skor
pilar (keuangan, perencanaan, pemasaran) yang angkanya diambil dari perilaku nyata di dalam
aplikasi, misalnya konsistensi pencatatan dalam 30 hari terakhir dan kelengkapan butir rencana.

### 5.4 Rancang bangun sistem

Sistem tersusun atas tiga lapisan: antarmuka HTML/CSS/JavaScript murni pada sisi klien, kerangka
Flask (Python 3.13) dengan templat Jinja pada sisi server, dan SQLite sebagai penyimpan relasi.
Grafik (meter skor, radar tiga pilar, kurva arus kas, batang riwayat) dibentuk sebagai SVG yang
kordernatnya dihitung di server pada modul `viz.py`; pilihan ini sengaja mengambil tempat pustaka
grafik eksternal agar sistem tetap tampil penuh tanpa jaringan, dan karena bobot halaman yang
kecil relevan untuk ponsel kelas bawah. Autentikasi memakai *session cookie* bertanda tangan
(Werkzeug) dengan sandi ter-*hash*, tanpa kerangka authentification pihak ketiga.

```
Peramban (16 rute, dwi-bahasa)  →  Flask (routing, session, filter format rupiah)
        │                                   │
        │  formulir + aksi sekali-klik      ├─ lapisan aturan  :  scoring.py
        │                                   │    verifikasi_insilik()  · hitung_skor_umkm()
        ▼                                   │    generate_rekomendasi()· langkah_terbaik()
   SQLite 7 tabel                           │
   users · business_profile                 └─ validasi  :  dataset.py
   financial_records · business_plans            · uji_hitam.py
   marketing_activities · scores
   reference_stats
```

Struktur penyimpanan terdiri atas tujuh tabel. `users` berisi 251 akun (250 responden hasil
impor dan satu akun contoh untuk demonstrasi), `business_profile` menyimpan 12 atribut kamus data
ditambah enam kolom turunan sistem (catatan verifikasi, modal rupiah, skor dan label acuan, penanda
sumber data), `financial_records` berisi arus kas dengan penanda hapus lembut, `business_plans`
menyimpan rencana satu halaman, `marketing_activities` menyimpan katalog beserta penanda tayang,
`scores` merupakan log riwayat skor dan rekomendasi pada setiap perhitungan, dan `reference_stats`
menyimpan angka acuan 12 atribut berikut penanda sifatnya. Rincian kolom dan jumlah baris disajikan
pada Lampiran B.

Dua keputusan skema perlu dicatat. Pertama, `financial_records` memiliki kolom `dihapus_pada`,
sehingga penghapusan bersifat lembut dan dapat dibatalkan. Kedua, baris hasil impor menandai
dirinya dengan `sumber_data = 'dataset penelitian'`, dan sistem memperlakukan baris semacam itu
sebagai data pokok: jawaban kuesioner tidak ditimpa oleh simpulan perilaku aplikasi.

**Gambar 1.**Diagram arsitektur tiga lapisan. **Gambar 2.**Skema relasi 7 tabel.
**Gambar 3.**Tangkapan layar 5 halaman utama (unggah sebagai berkas terpisah).

### 5.5 Lapisan kemudahan (pembeda dari SPK konvensional)

Lapisan ini dirancang dengan prinsip: **sistem yang menghitung, pengguna mengoreksi**. Enam
mekanisme yang diimplementasikan.

**(1) Verifikasi indikator dari bukti, dua arah.** Alih-alih menanyakan “apakah Anda mencatat
keuangan?” kepada pengguna aplikasi, sistem menyalakan indikator itu sendiri ketika menemukan
bukti (`jumlah_transaksi ≥ 1` untuk pembukuan, ≥2 butir terisi untuk rencana, ≥1 produk tayang
untuk kehadiran daring), dan mematikannya kembali bila bukti hilang. Penyebabnya ditulis dengan
bahasa manusia, misalnya “Pencatatan keuangan saya aktifkan karena buku Anda sudah berisi 13
catatan”, dan ditampilkan di dashboard. Efeknya pada beban masukan: tiga dari delapan atribut
penilai tidak lagi ditanyakan.

**(2) Satu tindakan berikutnya.** Daftar rekomendasi diurut dengan dua kunci: tier prioritas
aturan, lalu estimasi waktu pengerjaan modul (Keuangan 1 menit, Pemasaran 3, Perencanaan 6,
Edukasi/Kemitraan 90). Dashboard hanya menampilkan satu kartu tindakan; rekomendasi lain masuk ke
lipatan “beberapa hal lain”.

**(3) Aksi sekali-klik yang mengerjakan sesuatu.** Rute `POST /tindak` menerima kode tindakan dari
dashboard (`catat`, `rencana`, `produk`, `bagikan`). Untuk `catat`, satu baris arus kas hari ini
langsung tersimpan memakai nominal median dan kategori tersering milik pengguna itu; untuk
`rencana`, pengguna diarahkan ke formulir yang sudah terisi; untuk `bagikan`, status kehadiran
daring dan satu tingkat usaha pemasaran disetel otomatis.

**(4) Isian yang terisi dari data pengguna.** `database.statistik_saran()` menghitung kategori dan
nominal tersering dalam 120 hari terakhir untuk membuat *chip* nilai cepat dan tombol “sering Anda
catat”, masing-masing satu klik untuk satu baris buku kas. Kolom tanggal, kategori, dan keterangan
dipindah ke rincian yang boleh tidak diisi.

**(5) Draf rencana otomatis.** `database.skeleton_rencana()` menurunkan target omzet dari omzet
bulanan rata-rata pengguna dikalikan 1,10, modal dari rata-rata pengeluaran, produk unggulan dari
katalog pertama, tenggat 90 hari ke depan, dan strategi dari templat kalimat. Sistem menampilkan
asal-usul tiap angka agar pengguna tidak menerima nilai yang tampak datang tiba-tiba.

**(6) Pemulihan dan umpan balik.** Penghapusan dapat dibatalkan (`urungkan_hapus`) tanpa dialog
konfirmasi browser, dan setiap penyimpanan memunculkan kalimat sebab–akibat, misalnya “Catatan
Penjualan Rp12.500 … Naik 25 poin, sekarang 77,0/100”. Pengubah dwibahasa (mode *sehari-hari* dan
mode *riset*) menyimpan preferensinya di *session*, dan istilah teknis (bobot, korelasi, ambang,
*rule-based*) hanya dirender pada mode riset.

### 5.6 Instrumen dan protokol pengujian

Evaluasi dilakukan pada tiga gerbang, seluruhnya dapat dijalankan ulang (Lampiran A).

**(a) Uji fungsional black-box.** Skrip `validasi/uji_hitam.py` menjalankan 16 kasus melalui klien
Flask — autentikasi, reproduksi indeks, perilaku bobot, aksi sekali-klik, analisis teks rupiah,
hapus–batalkan, draf otomatis, penyetelan status dari perilaku, dwibahasa, API JSON, dan
ketersediaan seluruh rute termasuk berkas PWA — lalu mencetak Tabel 9 secara otomatis.

**(b) Verifikasi reproduksi indeks.`dataset.py --reproduksi` membandingkan skor yang dihitung mesin
aplikasi dengan kolom `Skor_Keberhasilan` pada CSV baris per baris (toleransi 0,05). Ini adalah
uji implementasi, **bukan** ukuran ketepatan prediksi.

**(c) Analisis statistik pendukung.** Untuk deskripsi data dihitung proporsi dan dispersi
(Tabel 1). Untuk ketajaman aturan, `dataset.py` menghitung korelasi tiap atribut dengan label
indeks **dan** mengulang perhitungan itu setelah bobot atribut yang sama dikeluarkan dari rumus
(uji *leave-one-out*), sebagai alat deteksi sirkularitas. Untuk hubungan antar-atribut dipakai
uji chi-square pada 21 pasangan biner dengan Cramér’s V sebagai ukuran kekuatan, karena atribut
berukuran kecil ini dapat diuji tanpa bergantung pada label bentukan.

**(d) Uji kegunaan (masih berjalan).** Protokol yang disiapkan: 10–15 pelaku UMKM diminta
melakukan tiga tugas tanpa petunjuk — mencatat penjualan hari ini, mengetahui tindakan berikut yang
disarankan sistem, dan menyimpan rencana dari draf otomatis — lalu mengisi *System Usability Scale*
sepuluh butir (Brooke, 1996). Jumlah responden ini mengikuti temuan bahwa lima pengguna sudah
mengungkap sebagian besar masalah kegunaan (Nielsen & Landauer, 1993), dan 10 responden dipilih
agar skor SUS memiliki selang kepercayaan yang wajar. Hasilnya dilaporkan terpisah karena
termasuk pengumpulan data manusia; naskah ini menyatakan secara eksplisit bahwa uji tersebut
**belum dikerjakan**. Validasi bobot oleh 3 pakar (indeks kesepakatan isi, Lynn, 1986) direncanakan
menyusul.

---

## 6. Hasil dan pembahasan

### 6.1 Karakteristik 250 responden

Seluruh atribut pada 250 baris terisi lengkap; tidak ditemukan nilai kosong maupun baris duplikat.
Sebaran tiap atribut dirangkum pada Tabel 1. Tiga hal layak digarisbawahi. Pertama, praktik
manajemen dasar masih jarang: hanya 48,8% usaha yang pembukuannya tergolong baik, 44,0%
memanfaatkan internet untuk usaha, dan 51,6% menilai modal awalnya memadai. Kedua, jenjang
pendidikan tersebar merata (SD 24,0% hingga Pascasarjana 15,6%), sehingga satu jenjang tidak dapat
dijadikan proxy kualitas manajemen. Ketiga, pengalaman usaha menyebar 0–20 tahun (rerata 9,76;
SD 6,17).

Indeks kesehatan usaha pada sampel ini tersebar dari 5,0 sampai 94,8 (median 49,1; kuartil
bawah 36,5, kuartil atas 64,0). Pada ambang 50, 122 UMKM (48,8%) masuk kategori “berhasil” menurut
definisi indeks—angka yang menjadi dasar seluruh aturan prioritas di aplikasi.

**Tabel 3. Ringkasan indeks kesehatan usaha pada 250 responden.**

| Statistik | Nilai |
|---|---|
| Rentang skor indeks | 5,0 – 94,8 |
| Median (kuartil 1 / kuartil 3) | 49,1 (36,5 / 64,0) |
| UMKM “berhasil” pada ambang 50 | 122 (48,8%) |
| Atribut pembentuk indeks | 8 dari 12 |
| Rata-rata tindakan yang direkomendasikan sistem per responden | 3,72 |
| Rentang jumlah tindakan per responden | 2 – 6 |
| Responden tanpa satu pun tindakan rekomendasi | 0 |

Dua baris terakhir menjadi dasar empiris perancangan antarmuka: setiap responden rata-rata punya
**empat pekerjaan rumah** pada saat yang sama. Ketika semuanya ditampilkan sekaligus, yang
terjadi adalah penundaan, bukan prioritas—sehingga sistem menyisakan satu kartu tindakan
(Subbab 5.5) dan melipat sisanya.

### 6.2 Hubungan atribut dengan label indeks — dan batas penafsirannya

Tabel 4 menyajikan dua hal sekaligus: proporsi responden “berhasil” menurut keberadaan tiap
atribut, dan hasil uji *leave-one-out*, yaitu korelasi yang sama setelah bobot atribut bersangkutan
dikeluarkan dari rumus pembentuk label.

**Tabel 4. Proporsi kondisional, korelasi titik-biner, dan uji *leave-one-out* (n = 250).**

| Komponen indeks | Kelompokbandingan | “berhasil” dengan | “berhasil” tanpa | Δ (poin) | r dengan label | r setelah bobot dihapus | χ² (df=1) vs label |
|---|---|---|---|---|---|---|---|
| `Financial_Record_Keeping` | baik vs buruk | 77,9% | 21,1% | 56,8 | +0,568 | **−0,018** | 78,33 (p = 8,7e−19) |
| `Business_Plan` | ada vs tidak | 70,2% | 25,2% | 45,0 | +0,450 | **−0,000** | 48,79 (p = 2,8e−12) |
| `Marketing_Effort` | 6–7 vs 1–3 | 63,6% | 38,1% | 25,5 | +0,239 | **+0,023** | 12,04 (p = 2,4e−03)* |
| `Initial_Capital` | memadai vs tidak | 60,5% | 36,4% | 24,1 | +0,241 | **+0,033** | 13,57 (p = 2,3e−04) |
| `Internet_Usage` | ya vs tidak | 60,0% | 40,0% | 20,0 | +0,199 | **−0,037** | 9,08 (p = 2,6e−03) |
| `Industry_Experience` | >12 vs 0–4 thn | 51,7% | 40,3% | 11,4 | +0,136 | **+0,013** | 2,37 (p = 0,31)* |
| `Professional_Advice` | 6–7 vs 1–3 | 52,6% | 43,8% | 8,8 | +0,096 | **+0,002** | 1,81 (p = 0,41)* |
| `Partnership` | ya vs tidak | 47,0% | 50,4% | −3,4 | −0,034 | −0,104 | 0,17 (p = 0,68) |
| `Age` (atribut pendamping) | >45 vs ≤45 thn | 45,5% | 52,0% | −6,5 | −0,061 | tidak dipakai | 1,33 (p = 0,51)* |
| `Education` (atribut pendamping) | ≥ Sarjana vs di bawahnya | 50,0% | 47,7% | 2,3 | +0,041 | tidak dipakai | 0,18 (p = 0,67)* |

\* χ² dihitung pada 3 kelas (bukan 2), sehingga df = 2.

Pola pada kolom terakhir Tabel 4 tidak memberi ruang tafsir lain. **Korelasi sebuah komponen
runtuh mendekati nol—bahkan berubah tanda—tepat setelah bobotnya dihapus dari rumus label.**
Uji chi-square yang sama, yang lazim dipakai untuk membuktikan “pengaruh”, juga kehilangan
makna pada kedelapan baris indeks karena label memang fungsi dari baris tersebut; nilainya baru
informatif pada dua atribut pendamping (`Age`, `Education`), dan keduanya tidak signifikan.
Pembanding eksternal mengunci simpulan yang sama: pada label acak dengan proporsi “berhasil”
identik, korelasi `Financial_Record_Keeping` adalah −0,087 (p = 0,17), yaitu hubungan yang
tidak bermakna.

Konsekuensinya untuk cara melaporkan hasil. Angka 77,9%, 21,1%, dan selisih 56,8 poin **sah**
dipublikasikan sebagai proporsi responden menurut indeks yang ditetapkan peneliti, dan itu yang
dipakai `reference_stats` di aplikasi sebagai dasar prioritas aturan. Angka yang sama **tidak sah**
dibaca sebagai bukti bahwa pembukuan keuangan menyebabkan keberhasilan usaha. Karena seluruh
kalimat rekomendasi di sistem menyebut sumbernya (“Pada 250 data UMKM yang diteliti, 77,9%
responden yang pembukuannya terkategori baik berada pada kelompok indeks “berhasil” …”),
pernyataan di layar tetap konsisten dengan batasan ini.



### 6.3 Kontribusi tiap bobot terhadap indeks

Karena label dibentuk oleh penjumlahan berbobot, cara yang jujur untuk membandingkan bobot adalah
melihat sumbangannya terhadap ragam skor, bukan terhadap “keberhasilan di lapangan”. Tabel 5
memecah ragam indeks menjadi kontribusi tiap suku (kovarian suku dengan skor total dibagi ragam
skor).

**Tabel 5. Dekomposisi kontribusi tiap komponen terhadap ragam indeks.**

| Komponen | Bobot | Sumbangan ke ragam indeks |
|---|---|---|
| Pencatatan keuangan | 25 | 44,2% |
| Rencana bisnis | 20 | 31,2% |
| Kecukupan modal awal | 10 | 8,1% |
| Usaha pemasaran | 15 | 7,3% |
| Pemanfaatan internet | 10 | 5,3% |
| Pengalaman industri | 10 | 2,8% |
| Saran profesional | 5 | 0,7% |
| Kemitraan | 5 | 0,5% |

Dua catatan. Pertama, dua komponen manajemen menyumbang **75,4%** ragam indeks, sehingga sistem
secara praktis memperlakukan pembukuan dan perencanaan sebagai syarat kesehatan usaha; ini
keputusan nilai yang perlu dinyatakan terbuka di Bab metode, bukan disembunyikan di balik angka.
Kedua, kontribusi usaha pemasaran (7,3%) jauh lebih kecil daripada bobot nominalnya (15%) karena
sebaran skala 1–7 merata (SD 1,99), sedangkan kemitraan hanya 0,5% di samping bobotnya 5% karena
proporsinya (46,0%) dan arah hubungannya yang negatif terhadap label indeks. Untuk komponen
berekorientasi kecil ini, sistem tetap menampilkannya sebagai opsi prioritas rendah, bukan
menyembunyikannya.

### 6.4 Hubungan antar-atribut (uji yang tetap sah)

Uji chi-square pada 21 pasangan atribut biner menghasilkan tiga pasangan yang signifikan pada
α = 0,05, dan seluruhnya lemah (Tabel 6). Sisanya independen, termasuk pasangan yang secara
intuitif seharusnya berhubungan (mis. pembukuan × rencana bisnis, p = 0,89; Pembukuan ×
penggunaan internet, p = 0,76).

**Tabel 6. Pasangan atribut bernilai signifikan dan kekuatan hubungannya.**

| Pasangan | χ² | p | Cramér’s V |
|---|---|---|---|
| Kecukupan modal × Rencana bisnis | 9,10 | 0,003 | 0,191 |
| Pembukuan × Kemitraan | 5,96 | 0,015 | 0,154 |
| Usaha orang tua × Jenis kelamin | 4,81 | 0,028 | 0,139 |

Temuan ini menjelaskan sifat datanya: atribut-atribut tersebar hampir bebas satu sama lain, pola
yang konsisten dengan data yang dibangkitkan/diisi per kolum. Konsekuensinya untuk penelitian
berikutnya jelas — sebelum satu pun kalimat “faktor penentu” ditulis, dibutuhkan data lapangan
dengan hasil usaha yang terukur (omzet riil, pertumbuhan, atau eksistensi) agar hubungan antar-
praktik manajemen bisa diuji secara serius.

### 6.5 Kalibrasi ambang keputusan dan dampaknya pada daftar tindakan

Ambang 50 adalah pilihan normatif, sehingga perilakunya perlu diperiksa lebih dulu. Tabel 7
menunjukkan konsekuensi perubahan ambang terhadap klasifikasi indeks, dan kolom terakhir menghitung
berapa banyak tindakan yang direkomendasikan sistem kepada responden (dihitung dengan mesin aturan
yang sama, tanpa memakai riwayat aplikasi).

**Tabel 7. Sensitivitas ambang terhadap label, status, dan daftar tindakan (n = 250).**

| Ambang | “berhasil” (%) | “perlu perbaikan” (orang) | Rata-rata tindakan per responden | Total tindakan TINGGI | Responden tanpa tindakan TINGGI |
|---|---|---|---|---|---|
| 30 | 83,2 | 42 | 3,72 | 247 | 65 |
| 45 | 57,6 | 106 | 3,72 | 247 | 65 |
| **50 (dipakai)** | **48,8** | **128** | **3,72** | **247** | **65** |
| 55 | 39,2 | 152 | 3,72 | 247 | 65 |
| 70 | 14,4 | 214 | 3,72 | 247 | 65 |

Empat kolom terakhir identik pada seluruh ambang, dan itu temuan rancangan, bukan kebetulan: mesin
rekomendasi dipicu oleh **keberadaan atribut**, bukan oleh jarak ke ambang. Artinya, menggeser
ambang mengubah label dan status (kolom 2–3: dari 42 menjadi 214 responden “perlu perbaikan”) tetapi
**tidak mengubah apa yang disarankan sistem kepada pengguna**. Nilai 48,8% pada ambang 50 juga
hampir tepat pada median indeks (49,1), sehingga ambang itu dapat dibaca sebagai "separuh responden
berada di bawah nilai indeks median" — mudah dijelaskan, tapi sekali lagi bukan hasil optimasi
terhadap outcome apa pun.

**Kedua,** tidak seorang pun responden kehabisan saran—semua 250 punya minimal dua tindakan.
Artinya kartu “satu tindakan berikutnya” pada dashboard tidak akan pernah kosong, dan pengujian
kegunaan (SUS) dapat dilakukan pada seluruh populasi akun contoh tanpa menyiapkan data tambahan.

### 6.6 Implementasi sistem

Sistem terdiri atas 16 rute HTTP, 7 tabel SQLite, dan tiga modul inti: `scoring.py` (aturan,
indeks, prioritas), `database.py` (skema, agregasi perilaku, draf otomatis), dan `dataset.py`
(validasi). Aplikasi dijalankan dengan server pengembangan Flask dan tidak memakai pustaka grafik
eksternal; seluruh 10 grafik pada antarmuka berupa SVG hasil perhitungan `viz.py`.

**Tabel 8. Ukuran implementasi.**

| Bagian | Nilai |
|---|---|
| Jumlah rute HTTP / fungsi view | 16 |
| Tabel basis data | 7 (plus 6 kolom hasil migrasi) |
| Berkas antarmuka (Jinja) | 12: 9 halaman isi + 2 kerangka + 1 halaman 404 |
| Baris kode Python (8 modul + 2 skrip validasi) | 2.462 |
| Akun dalam basis data terbawa | 251 (250 responden + 1 akun contoh) |
| Baris arus kas terbawa | 216 (akun contoh) |
| Berkas PWA | 3 (manifest, *service worker*, ikon) |
| Bahasa antarmuka | 2 (sehari-hari, riset) melalui satu tombol |

Tiga perilaku implementasi yang membedakan sistem ini dari kalkulator indeks biasa, dan yang
terverifikasi lewat pengujian black-box (Tabel 9):

1. **Indikator diverifikasi dari bukti dua arah.** Pembukuan menyala saat `financial_records`
   berisi; rencana menyala saat ≥2 butir terisi; kehadiran daring menyala saat katalog punya produk.
   Sebaliknya, hapus buktinya maka indikator padam dan skor **turun** — sistem tidak menyimpan
   klaim yang tidak lagi ditopang data.
2. **Aksi sekali-klik yang benar-benar mengerjakan tugas.** Rute `/tindak` kode `catat` menyimpan
   satu baris arus kas hari ini memakai nominal median dan kategori tersering milik pengguna itu;
   pengguna tidak menyentuh formulir. Dalam uji BB-08, satu tindakan menambah baris buku kas dan
   menampilkan kalimat sebab-akibat.
3. **Bahasa pengguna dipisah dari bahasa riset.** Mode sederhana menutupi istilah bobot/korelasi/
   ambang dan menggantinya dengan kalimat kerja; mode riset menampilkannya lengkap (BB-13). Keduanya
   memakai rumus yang sama, sehingga screenshot untuk naskah dan untuk pengguna tidak perlu dibuat
   dua kali.

### 6.7 Hasil pengujian

Tabel 9 merangkapkan uji black-box otomatis: 16 kasus, seluruhnya lulus. Uji dijalankan
`python validasi/uji_hitam.py`; berkas tabelnya ikut dibagikan di repositori.

**Tabel 9. Hasil uji black-box SIDUMKM.**

| Kode | Kasus uji | Hasil yang diharapkan | Hasil sesungguhnya | Keterangan | Keputusan |
|---|---|---|---|---|---|
| BB-01 | Akses /dashboard tanpa login | Diarahkan ke halaman masuk | sesuai harapan | HTTP 200 | LULUS |
| BB-02 | Login dengan sandi salah | Ditolak, pesan menjelaskan tanpa membocorkan kredensial | sesuai harapan | Email atau sandi tidak dikenali. Periksa kembali, atau gunakan | LULUS |
| BB-03 | Login akun terdaftar | Masuk ke dashboard | sesuai harapan | HTTP 200 | LULUS |
| BB-04 | Reproduksi indeks pada 250 baris data penelitian | Skor mesin == Skor_Keberhasilan CSV | sesuai harapan | 250/250 baris cocok | LULUS |
| BB-05 | Profil memenuhi semua atribut | Skor 100 | sesuai harapan | skor=100.0 | LULUS |
| BB-06 | Atribut pembukuan dilepas dari profil sempurna | Skor turun tepat 25 poin (bobot terbesar) | sesuai harapan | 100 - 75.0 = 25.0 | LULUS |
| BB-07 | Baris hasil impor dataset tidak diubah nilanya oleh aplikasi | Flag kuesioner tetap; hanya dilaporkan bila bertentangan | sesuai harapan | Di kuesioner catatan keuangan tercatat tidak ada, ta... | LULUS |
| BB-08b | Skor bergerak setelah aksi sekali-klik | Pesan memuat perubahan poin | sesuai harapan | 58.42 -> 58.42; Catatan Transport Rp467.500 masuk  | LULUS |
| BB-08 | Tombol sekali-klik 'Catat sekarang' di dashboard | Satu baris buku kas terbentuk tanpa membuka formulir | sesuai harapan | total baris=219; pesan: Catatan Transport Rp467.500 masuk ke buku ka... | LULUS |
| BB-09 | Input nominal ditulis '12.500' (titik ribuan) | Tersimpan 12500 | sesuai harapan | tersimpan=12,500 | LULUS |
| BB-10 | Hapus satu baris lalu tekan 'Batalkan hapusan terakhir' | Jumlah baris pulih, tanpa dialog konfirmasi browser | sesuai harapan | 220 -> 219 -> 220 | LULUS |
| BB-11 | Membuka /rencana?draf=1 bagi pengguna tanpa rencana | Formulir terisi otomatis dari riwayat arus kas | sesuai harapan | banner draf + target terisi | LULUS |
| BB-12 | Menekan 'Bagikan tautan' pada katalog | Status jualan online aktif + usaha pemasaran naik satu tingkat | sesuai harapan | internet=1, pemasaran=6 | LULUS |
| BB-13 | Mengubah mode bahasa pada halaman | Istilah teknis muncul hanya di mode riset | sesuai harapan | pergantian leksikon terverifikasi | LULUS |
| BB-14 | Menampilkan hasil perhitungan ke mesin luar (/api/skor) | JSON berisi skor, status, tiga pilar, dan rekomendasi | sesuai harapan | skor=60.92, pilar=[77.5, 78.3, 0.0] | LULUS |
| BB-15 | Sembilan rute utama + berkas PWA | Semua merespons 200/302 | sesuai harapan | tidak ada rute yang gagal | LULUS |

Total 16 kasus: LULUS 16, GAGAL 0.

Seluruh kasus lulus, termasuk tiga kasus yang menjaga batas klaim: BB-04 (reproduksi indeks
250/250), BB-07 (jawaban kuesioner responden tidak boleh diubah oleh perilaku aplikasi), dan
BB-02 (pesan galat tidak membocorkan kredensial). Tiga uji ketajaman aturan (BB-05, BB-06)
menegaskan bobot bekerja persis seperti spesifikasi: profil sempurna bernilai 100, dan melepaskan
atribut pembukuan dari profil sempurna mengurangi tepat 25 poin.

Untuk uji kegunaan, instrumen SUS dan protokol tugas sudah disiapkan beserta halaman mode
sehari-hari; karena pengumpulan data ke pengguna manusia memerlukan izin dan waktu lapangan,
**hasil SUS belum dimasukkan ke dalam naskah ini** dan tidak ada angka yang diklaim untuk bagian
itu (lihat Subbab 6.9).

### 6.8 Pembahasan

**Sumbangan utama rancangan bukan pada rumusnya, melainkan pada pemindahan beban.** Indeks berbobot
sederhana seperti Persamaan (2) mudah ditemukan pada penelitian SPK UMKM; kontribusi yang diuji di
sini adalah lapisan yang membuat sistem berhenti bertanya pada hal yang dapat dilihatnya sendiri
(Subbab 5.5). Bentuk nyatanya terdokumentasi dalam pengujian: tiga dari delapan atribut penilai tidak
lagi ditanyakan (BB-07), arus kas tercatat dari satu tombol tanpa formulir (BB-08), satu baris buku
kas dapat dipulihkan setelah terhapus (BB-10), dan draf rencana terbentuk dari riwayat omzet pengguna
(BB-11). Beban ketik untuk aksi tertinggi frekuensi turun dari lima isian (jenis, nominal, kategori,
tanggal, keterangan) menjadi satu angka—syarat praktis yang menentukan apakah aplikasi semacam ini
masih dipakai pada minggu keempat.

**Kedua, transparansi memiliki harga yang perlu dibayar, dan harga itu terukur.** Karena label
keberhasilan pada data ini adalah indeks turunan, sistem tidak dapat (dan tidak boleh) melaporkan
akurasi. Yang dapat dilaporkan adalah reproduksi 250/250 baris (BB-04), ketepatan bobot (BB-05,
BB-06), dekomposisi kontribusi ragam (Tabel 5), dan ambang yang dipilih secara eksplisit
(Tabel 7). Bagi pembaca teknis, daftar ini justru lebih informatif daripada satu angka akurasi yang
tidak dapat dibongkar; bagi penulis, ini menuntut kalimat yang jujur di Abstrak dan Bab 7.

**Ketiga, pemisahan dwibahasa ternyata mengurangi konflik kepentingan.** Satu basis kode yang sama
harus melayani dua kebutuhan yang bertentangan: pengguna awam memerlukan kalimat kerja, sedangkan
reviewer dan penyusun naskah memerlukan nilai numerik dan sumbernya. Mode riset (BB-13) membuat
keduanya hidup berdampingan tanpa membuat screenshot demonstrasi penuh istilah teknis, dan sekaligus
menjadi bahan lampiran yang dapat diperiksa penguji ketika ada yang menanyakan “angka ini dari
mana?”.

**Keempat, hasil chi-square antar-atribut (Tabel 6) perlu dibaca sebagai cermin mutu data.** Hanya
3 dari 21 pasangan yang berhubungan, semuanya lemah (V ≤ 0,19), termasuk pasangan yang secara logika
berelasi (pembukuan × perencanaan, p = 0,89). Pada data primer nyata, pola seperti ini akan
mencurigakan; pada dataset sintetis/terbangkit—kemungkinan besar kasus berkas ini—ia wajar. Karena
sistem akan dipakai untuk memberi nasihat, sifat data sumbernya wajib dinyatakan di Bab metode
(telah dinyatakan pada Subbab 6.9 dan Lampiran B).

### 6.9 Keterbatasan, ancaman validitas, dan catatan etika

1. **Label turunan (ancaman utama).** `status_keberhasilan` dibentuk oleh rumus indeks dari atribut
   yang sama, sehingga seluruh korelasi dan uji asosiasi fitur–label bersifat definisional. Tidak ada
   klaim prediksi, penyebab, atau akurasi yang dibuat sistem ini maupun naskah ini.
2. **Kualitas data sumber.** Dataset berisi 12 atribut tanpa satu pun indikator hasil usaha (omzet,
   pertumbuhan, kelangsungan usaha). Bila berkas ini merupakan hasil simulasi publik, sifatnya harus
   dinyatakan eksplisit; sistem tetap sah sebagai DSS, tapi tidak sebagai instrumen penelitian dampak.
3. **Uji kegunaan belum dilakukan.** Protokol SUS (10 butir, 10–15 peserta, tiga tugas inti) sudah
   disiapkan dan instrumennya ada pada Lampiran C. Angka SUS apa pun yang muncul di naskah
   **sebelum** pengumpulan data akan menjadi klaim kosong, sehingga sengaja ditiadakan.
4. **Bobot adalah keputusan peneliti.** Konsekuensinya terukur: pembukuan + perencanaan menyumbang
   75,4% ragam indeks (Tabel 5). Rencana validasi oleh tiga pakar dengan perhitungan CVI (Lynn, 1986)
   telah disiapkan; sampai saat itu, bobot harus disebut sebagai *professional judgement*.
5. **Server pengembangan dan satu server.** Aplikasi dijalankan `flask.run` (single-host, tanpa WSGI
   produksi) dan tanpa uji beban. Untuk pilot nyata, diperlukan gunicorn + HTTPS + pembatas laju.
6. **Privasi akun contoh.** Kredensial `demo@umkm.id`/`demo1234` ditampilkan di halaman masuk untuk
   keperluan demonstrasi akademik. Kode ini **tidak boleh** naik ke lingkungan produksi; pesan galat
   sudah dibuat tidak membocorkannya (BB-02), tetapi kredensial contoh tetap perlu dihapus sebelum
   rilis nyata.
7. **Etika.** Data responden yang dipakai adalah data agregat 12 kolom tanpa identitas;
   bila naskah menyusupkan data primer/instrumen SUS, diperlukan lembar persetujuan
   (informed consent) dan penomoran etik kampus. [ISI: nomor/keputusan etik bila ada.]

---

## 7. Kesimpulan

Penelitian ini menghasilkan SIDUMKM, sistem pendukung keputusan berbasis web yang menilai
kesehatan UMKM dengan penilaian beraturan atas delapan atribut berbobot pada 250 data usaha, dan —
ini kontribusi utamanya — memindahkan separuh beban interaksi dari pengguna ke sistem: indikator
dibuktikan dari perilaku (tiga atribut berhenti ditanyakan), tindakan berikutnya dipilihkan mesin,
arus kas direkam satu sentuh, penghapusan dapat dibatalkan, dan rencana disusun otomatis dari omzet
pemilik. Hasil pengujian menyatakan sistem bekerja sesuai spesifikasi pada 16 kasus black-box
(16 LULUS), mereproduksi indeks pada 250 dari 250 baris data (100%), dan menghitung dekomposisi
ragam yang menjelaskan bahwa dua atribut manajemen (pembukuan dan perencanaan) menguasai 75,4%
ragam indeks. Sensitivitas ambang diukur dan dilaporkan apa adanya: ambang mengatur label, bukan
banyaknya saran.

Keterbatasan dinyatakan bersamaannya: label keberhasilan pada data ini adalah indeks turunan,
sehingga tidak ada satu pun klaim akurasi, prediksi, maupun hubungan sebab akibat dalam naskah;
dataset tidak memuat hasil usaha riil; dan uji kegunaan SUS belum dijalankan. Empat pekerjaan
lanjutan diusulkan berurutan menurut nilai: (i) menjalankan protokol SUS sekaligus mengumpulkan
outcome riil (omzet tiga–enam bulan, kelangsungan usaha) agar sistem dapat diuji terhadap
kenyataan, bukan hanya direproduksi; (ii) validasi pembobotan oleh tiga pakar dengan CVI;
(iii) saluran masukan alternatif untuk pengguna yang enggan mengetik (catatan suara lewat telepon
biasa, entri melalui pesan singkat), karena satu sentuh menurunkan beban ketik tetapi belum
menghapusnya; (iv) kesiapan produksi — WSGI + HTTPS + pembatas laju, pemindahan akun demo dari
jalur rilis, dan migrasi ke MySQL/PostgreSQL bila sistem dipakai lintas komunitas pendampingan.

Kelayakan SPK berbasis aturan yang transparan dan hemat-input untuk pendampingan UMKM dengan
demikian telah dibuktikan pada tataran rancangan dan fungsional; pembuktiannya sebagai alat yang
memperbaiki usaha masih menunggu data lapangan.

---

## Daftar pustaka

> Daftar di bawah baru berisi rujukan **metode** yang memang dapat diverifikasi bibliografinya.
> Untuk artikel SINTA, tambahkan 8–12 rujukan empiris UMKM/SPK dari jurnal target (terbitan
> 5 tahun terakhir) — lihat catatan di Subbab 4.1 dan 6.8. Jangan menambah rujukan yang belum
> Anda baca; sebagian reviewer memeriksa kutipan secara acak.

Brooke, J. (1996). SUS: A “quick and dirty” usability scale. Dalam P. W. Jordan, B. Thomas,
B. A. Weerd & I. L. McClelland (Eds.), *Usability Evaluation Today and Tomorrow* (hlm. 189–194).
Taylor & Francis.

Cramér, H. (1946). *Mathematical Methods of Statistics*. Princeton University Press.

Davis, F. D. (1989). Perceived usefulness, perceived ease of use, and user acceptance of
information technology. *MIS Quarterly, 13*(3), 319–340.

Dean, T., & Grove, A. (2016). *Progressive Web Apps*. O’Reilly Media.

Fishburn, P. C. (1967). Additive utilities with applications to the sciences and methods of social
research. *Management Science, 13*(5), 54–68.

Hwang, C.-L., & Yoon, K. (1981). *Multiple Attribute Decision Making: Methods and Applications*.
Springer-Verlag.

Likert, R. (1932). *A technique for the measurement of attitudes*. Archives of Psychology, 22(140).

Nielsen, J., & Landauer, T. K. (1993). A mathematical model of the finding of usability problems.
*Proceedings of the INTERCHI’93 Conference on Human Factors in Computing Systems*, 206–213.

Power, D. J. (2002). *Decision Support Systems: Concepts and Resources for Managers*.
Quorum Books.

Saaty, T. L. (1980). *The Analytic Hierarchy Process*. McGraw-Hill.

Turban, E., Aronson, J. E., & Liang, T. P. (2005). *Decision Support Systems and Intelligent
Systems* (7th ed.). Pearson Education.

W3C. (2018). *Web Content Accessibility Guidelines (WCAG) 2.1*. W3C Recommendation.
https://www.w3.org/TR/WCAG21/

---

## Lampiran A — perintah reproduksi seluruh angka di naskah

```bash
pip install -r requirements.txt
python seed.py                       # 250 responden + 1 akun contoh dari data/
python dataset.py                    # hasil_validasi_dataset.md (Tabel 4, 5, 6)
python dataset.py --reproduksi       # 250/250 baris indeks sama (BB-04)
python validasi/uji_hitam.py         # hasil_uji_blackbox.md (Tabel 9)
python app.py                        # http://127.0.0.1:3000
```

## Lampiran B — rute, berkas, dan struktur data

**B.1 Rute HTTP (16 rute, 16 fungsi view).**

| Rute | Fungsi | Akses |
|---|---|---|
| `GET /` | pengalih: beranda bila sudah masuk, halaman masuk bila belum | publik |
| `GET/POST /masuk` | autentikasi | publik |
| `GET/POST /daftar` | pendaftaran + profil usaha (bahasa kalimat, bukan angka) | publik |
| `GET /keluar` | akhiri sesi | login |
| `GET /dashboard` | ringkasan indeks, kartu satu tindakan, tiga pilar, arus kas, perbandingan dataset | login |
| `GET/POST /keuangan` | catat uang sekali sentuh, buku kas, hapus lembut + batalkan | login |
| `POST /tindak` | eksekusi tindakan dari dashboard (`catat`/`rencana`/`produk`/`bagikan`) | login |
| `GET/POST /rencana` | rencana satu halaman; `?draf=1` mengisi dari riwayat arus kas | login |
| `GET/POST /pemasaran` | katalog produk, aksi “sudah disebar”, indikator online | login |
| `GET /profil` | profil + tabel kontribusi delapan atribut | login |
| `GET /acuan` | angka acuan dataset + panel audit label + kalibrasi ambang | login |
| `GET /api/skor` | hasil mesin aturan dalam JSON | login |
| `GET /toko/<slug>` | katalog publik (mini-website tanpa login) | publik |
| `GET /mode/<nama>` | tukar bahasa antarmuka (sehari-hari/riset) | login |
| `GET /manifest.webmanifest` | deklarasi PWA | publik |
| `GET /sw.js` | *service worker* (cache halaman inti + aset) | publik |

**B.2 Berkas inti.** `app.py` (routing & konteks), `scoring.py` (aturan, normalisasi, prioritas,
verifikasi indikator), `database.py` (skema + agregasi + draf), `dataset.py` (validasi angka),
`viz.py` (geometri SVG), `seed.py` (impor CSV + akun contoh), `validasi/uji_hitam.py` (black-box),
`validasi/audit_label_derasif.py` (varian audit terpisah), 12 berkas templat Jinja (9 halaman isi, 2 kerangka, 1 halaman 404), serta
5 berkas statis (`app.css`, `stempel.css`, serta `buku.js`, `catat.js`, `rupiah.js`).

**B.3 Tabel basis data.** `users` (akuan), `business_profile` (12 atribut + 6 kolom turunan:
`modal_rupiah`, `skor_acuan`, `label_acuan`, `sumber_data`, `verifikasi_otomatis`),
`financial_records` (dengan `dihapus_pada` untuk hapus lembut), `business_plans`,
`marketing_activities`, `scores` (riwayat skor + rekomendasi JSON), `reference_stats`
(angka acuan berpenanda `sifat`).

---

## Lampiran C — protokol uji kegunaan yang telah disiapkan (belum dijalankan)

**C.1 Peserta.** 10–15 pelaku UMKM, tanpa penyaringan kriteria teknis, izin lisan/tertulis direkam.

**C.2 Tugas (tanpa petunjuk dari pengawas).**

| No | Tugas | Ukuran keberhasilan |
|---|---|---|
| T1 | Mencatat penjualan hari ini senilai nominal bebas | selesai ≤ 60 detik; tanpa pertanyaan |
| T2 | Menyatakan apa yang harus diperbaiki lebih dulu menurut sistem | jawaban menyebut kartu “kerjakan ini dulu” |
| T3 | Menyimpan rencana usaha dari draf bawaan (mengubah target bila perlu) | satu rencana tersimpan; target terlihat berubah |
| T4 (opsional) | Mengembalikan satu baris buku kas yang terhapus | baris kembali lewat tombol batalkan |

**C.3 Kuesioner SUS (Brooke, 1996), terjemahan kerja, skala 1–5 (STS–SS).**
1. Saya ingin memakai aplikasi ini secara rutin. 2. Aplikasi ini terlalu rumit. 3. Aplikasi ini
mudah dipakai. 4. Saya butuh bantuan teknis untuk memakainya. 5. Fungsi-fungsinya terasa terpadu.
6. Ada terlalu banyak hal yang tidak konsisten. 7. Saya membayangkan orang cepat belajar memakainya.
8. Antarmuka ini merepotkan saat dipakai. 9. Saya merasa yakin ketika memakainya. 10. Saya perlu
belanyak hal sebelum bisa memakainya.
*Skor SUS:* butir ganjil (x−1), butir genap (5−x), dijumlahkan ×2,5 → rentang 0–100.

**C.4 Yang akan dilaporkan:** skor SUS per peserta dan rata-rata, waktu penyelesaian tiap tugas,
persentase keberhasilan tugas, serta catatan kualitatif (tema kebingungan yang berulang). Bagian
**Hasil 6.7** dan **Kesimpulan** baru diisi angkanya setelah protokol ini dijalankan.
