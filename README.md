# SIDUMKM — Sistem Informasi Dashboard UMKM

Prototipe **Sistem Pendukung Keputusan (SPK) berbasis web** untuk pelaku UMKM, dengan
pendekatan **rule-based scoring** (bukan machine learning). Bobot, ambang, dan kalimat
rekomendasi diturunkan dari hasil olahan 250 data UMKM: pencatatan keuangan (r = 0,568),
rencana bisnis (r = 0,450), usaha pemasaran (r = 0,239), dan pemanfaatan internet (r = 0,191).

## Cara menjalankan

```bash
pip install -r requirements.txt      # Flask + Werkzeug
python seed.py --reset               # bangun SQLite + 250 UMKM + akun demo
python app.py                        # http://localhost:3000
```

Untuk deployment, atur `SIDUMKM_SECRET_KEY` ke nilai acak yang panjang. Jika tidak diatur,
aplikasi membuat kunci sementara saat dijalankan.

Saat aplikasi dibuka pertama kali, tampil **mode sederhana** (bahasa sehari-hari untuk pelaku usaha).
Klik "Ubah ke bahasa teknis" di kanan atas untuk menampilkan istilah bobot / korelasi / rule-based —
gunakannya untuk screenshot naskah. Preferensi ini per sesi (`session["mode"]`).

Akun demo: **demo@umkm.id** / **demo1234** (sudah berisi ±6 bulan arus kas, katalog produk,
dan riwayat skor). 250 akun hasil seed memakai sandi `umkm123`.

## Struktur

```
app.py                routing Flask, aksi sekali-klik /tindak, mode bahasa, API /api/skor
scoring.py            RULE-BASED SCORING ENGINE + business rules (inti sistem)
database.py           skema 7 tabel + agregasi indikator turunan
seed.py               250 profil UMKM, statistik acuan, akun demo
viz.py                geometri SVG (meter, radar, garis, kolom, batang) dihitung di server
validasi/audit_label_derasif.py  pemeriksaan independen atas dataset olahan (label derivatif,
                        korelasi vs bobot, kondisional dua arah, kontrol label acak)
templates/            10 halaman Jinja
static/css/           design system "Buku Kas" + elemen signature (meter & stempel)
static/js/catat.js    form catat sekali-klik (pilih jenis, nominal chip,Enter = simpan)
static/js/rupiah.js   format ribuan saat mengetik
static/js/buku.js     animasi skor, saring buku kas
static/manifest.webmanifest + sw.js  → PWA, halaman inti tetap dibuka tanpa sinyal
sidumkm.db            SQLite (dibuat oleh seed.py)
```

## Model data (7 tabel)

`users` · `business_profile` · `financial_records` · `business_plans` ·
`marketing_activities` · `scores` (riwayat + rekomendasi JSON) · `reference_stats` (aturan dari dataset)

## Halaman

| Rute | Isi |
|---|---|
| `/masuk`, `/daftar` | autentikasi; pendaftaran hanya menanyakan data yang tidak bisa disimpulkan sistem (14 isian → kalimat, bukan angka) |
| `/dashboard` | meter Skor_Keberhasilan, stempel status, radar 3 pilar, arus kas 6 bulan, posisi vs 250 UMKM, daftar rekomendasi prioritas, riwayat skor |
| `/keuangan` | Pilar 1 — form catat sekali-klik (tekan tombol, ketik angka, siap), preset dari riwayat, buku kas, hapus yang bisa dibatalkan, laporan & grafik bulanan |
| `/rencana` | Pilar 2 — business plan; `?draf=1` membuka formulir yang sudah terisi dari catatan uang pengguna |
| `/pemasaran` | Pilar 3 — katalog produk, halaman publik, tombol share WhatsApp |
| `/toko/<slug>` | mini-website katalog (tanpa login) |
| `/profil` | kontribusi 8 indikator ke skor + edit profil |
| `/acuan` | tabel statistik 250 UMKM, sebaran skor, logika scoring |
| `/api/skor` | JSON hasil scoring engine |

## Mesin penilaian

```
skor = 25·catatan_keuangan + 20·rencana_bisnis + 15·(pemasaran-1)/6 + 10·internet
     + 10·normalisasi(modal) + 10·min(pengalaman,20)/20 + 5·kemitraan + 5·(saran-1)/6
status = "Berhasil" jika skor >= 50
```

Skor per pilar (0–100) dihitung dari data operasional yang sebenarnya: konsistensi
pencatatan 30 hari, kelengkapan butir rencana, capaian target dari omzet riil, dan jumlah
produk di katalog. Setiap penyimpanan data memicu perhitungan ulang dan mencatat riwayat
di tabel `scores`.

## Lapisan "permudah" (logika backend demi kegunaan pengguna awam)

| Mekanisme | Fungsi | Lokasi |
|---|---|---|
| Verifikasi indikator dua arah | `financial_record_keeping`, `business_plan`, `internet_usage` tidak lagi dipercaya dari centang user, tapi dinyalakan **dan dipadamkan** dari bukti perilaku (isi buku kas, kelengkapan rencana, katalog aktif). Alasannya ditulis dengan bahasa manusia, contoh: "Pencatatan keuangan saya aktifkan karena buku Anda sudah berisi 13 catatan." | `scoring.verifikasi_insilik()` dipanggil `app.hasil_terkini()` |
| Satu langkah berikutnya | Daftar rekomendasi diurut `(prioritas, BIAYA_MENIT)` lalu hanya langkah termurah-waktu yang jadi kartu utama; sisanya masuk daftar lipat | `scoring.langkah_terbaik()`, `BIAYA_MENIT` |
| Aksi sekali klik (`/tindak`) | Tombol di dashboard benar-benar mengerjakan tindakannya: `catat` menyimpan transaksi hari ini, `bagikan` menyalakan status online, `rencana`/`produk` membuka halaman dengan draf siap pakai | `app.tindak()` |
| Preset dari riwayat | Chip nominal & daftar "Sering Anda catat" diambil dari kategori/nominal yang paling sering dipakai pengguna itu | `database.statistik_saran()`, `nominal_umum()` |
| Draf rencana otomatis | `/rencana?draf=1` mengisi judul, target omzet (rata-rata uang masuk +10%), modal, produk unggulan, strategi, risiko, tenggat — pengguna tinggal mengoreksi | `database.skeleton_rencana()` |
| Hapus bisa dibatalkan | Transaksi tidak di-hard-delete: kolom `dihapus_pada` + tombol "Batalkan hapusan terakhir" | `database.urungkan_hapus()` |
| Kalimat → angka | Form pendaftaran hanya menawarkan kalimat ("Promosi seminggu sekali", "Rp 5 juta - Rp 10 juta"), angka 1-7 dan rupiah dihitung server | `PILIHAN_PEMASARAN`, `PILIHAN_SARAN`, `PILIHAN_MODAL`, `nilai_dari_kata()`, `modal_dari_pilihan()` |
| Umpan balik sebab-akibat | Setiap penyimpanan memunculkan "Naik 25 poin, sekarang 48,2/100" dan meter di rail/dashboard ikut bergerak ulang | `app.delta_skor()` + animasi `buku.js` |
| Dua gaya bahasa | `mode=sederhana` (default, untuk pelaku UMKM) dan `mode=riset` (istilah bobot/korelasi/rule-based, untuk naskah & screenshot) — `GET /mode/riset` | `session["mode"]`, `mode_aktif()`, label di `muk.html`/`dashboard.html` |
| PWA offline | Manifest + service worker + ikon: halaman inti dan aset tersimpan cache, aplikasi bisa dipasang di HP dan tetap terbuka saat sinyal hilang | `/manifest.webmanifest`, `/sw.js`, `static/img/` |
| Angka manusiawi | Input uang menerima "12.000"/"12,000"/"12000", membulatkan otomatis (Rp500 / Rp1.000), Enter = simpan | `static/js/catat.js`, `rupiah.js`, `app._ambil_nominal()` |

Kaidah yang dipakai: **sistem yang menghitung, bukan pengguna yang mengetik angka.** Setiap pertanyaan yang bisa dijawab sendiri oleh perilaku pengguna, dihapus dari formulir.

## Catatan untuk naskah jurnal

Sistem ini layak diklaim sebagai DSS rule-based: seluruh keputusan dapat dilacak ke satu
indikator dan satu aturan (`scoring.py:generate_rekomendasi`), tidak ada bobot hasil
training laten, dan `reference_stats` menyimpan angka acuan yang sama dengan yang dipakai
di bab hasil analisis. Untuk pengujian black-box, setiap rute dan simpanan skor bisa
dijalankan lewat `python -m unittest` atau manual dengan akun demo.


## Lapisan "permudah" (UX untuk pengguna awam)

Ditambahkan setelah tinjauan kegunaan, semuanya di sisi server supaya tampilan tetap tipis:

| Mekanisme | Lokasi | Efek bagi pengguna |
|---|---|---|
| Verifikasi indikator dari perilaku | `scoring.verifikasi_insilik()` dipanggil `app.hasil_terkini()` | `catatan keuangan`, `rencana bisnis`, `internet` tidak ditanya dua kali — sistem menyalakannya sendiri dari isi buku kas/rencana/katalog, dan menjelaskan alasannya di dashboard |
| Satu tindakan terpilih | `scoring.langkah_terbaik()` (dampak ÷ `BIAYA_MENIT`) | dashboard memperlihatkan satu tombol "kerjakan ini dulu"; sisanya masuk daftar lipat |
| Aksi sekali klik | `POST /tindak` (`catat`, `rencana`, `produk`, `bagikan`) | tombol dari dashboard benar-benar menyimpan catatan/mengaktifkan status, bukan hanya membuka form |
| Preset dari riwayat | `database.statistik_saran()`, `nominal_umum()` | chip nominal & tombol "sering Anda catat" memakai angka milik pengguna sendiri |
| Hapus bisa dibatalkan | kolom `financial_records.dihapus_pada` + `database.urungkan_hapus()` | tidak ada dialog konfirmasi yang menakutkan; ada tombol "Batalkan hapusan terakhir" |
| Draf rencana otomatis | `database.skeleton_rencana()` (`/rencana?draf=1`) | target omzet, modal, dan produk terisi dari catatan; pengguna tinggal menyetujui |
| Bahasa sederhana ↔ riset | `session["mode"]`, rute `/mode/<nama>` | istilah bobot/korelasi/threshold disembunyikan dari pelaku usaha, tinggal diklik untuk keperluan naskah & screenshot |
| Catatan sebab-akibat | `app.delta_skor()` | setiap simpan memunculkan "Naik 25 poin, sekarang 48,2/100" |
| Pamitan input teknis | `PILIHAN_PEMASARAN`, `PILIHAN_SARAN`, `PILIHAN_MODAL` | pendaftaran memakai kalimat ("Promosi seminggu sekali"), angka 1–7 dihitung di server |
| Format rupiah manusiawi | `static/js/catat.js`, `rupiah.js` | mengetik `12000` tampil `12.000`, pembulatan Rp500/Rp1.000, Enter = simpan |
| PWA | `/manifest.webmanifest`, `/sw.js`, ikon PNG | bisa dipasang di HP, halaman inti & aset tetap terbuka saat sinyal hilang |
| Aksesibilitas | `static/css/app.css` bagian terakhir | target sentuh ≥44px, teks form 16px (tanpa zoom paksa iOS), kontras 4,5:1, `aria-current`, `role="status"`, focus ring 3px |
