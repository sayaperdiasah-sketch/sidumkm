# Hasil uji black-box SIDUMKM

| Kode | Kasus uji | Hasil yang diharapkan | Hasil sesungguhnya | Keterangan | Keputusan |
|---|---|---|---|---|---|
| BB-01 | Akses /dashboard tanpa login | Diarahkan ke halaman masuk | sesuai harapan | HTTP 200 | LULUS |
| BB-02 | Login dengan sandi salah | Ditolak, pesan menjelaskan tanpa membocorkan kredensial | sesuai harapan | Email atau sandi tidak dikenali. Periksa kembali, atau gunakan | LULUS |
| BB-03 | Login akun terdaftar | Masuk ke dashboard | sesuai harapan | HTTP 200 | LULUS |
| BB-04 | Reproduksi indeks pada 250 baris data penelitian | Skor mesin == Skor_Keberhasilan CSV | sesuai harapan | 250/250 baris cocok | LULUS |
| BB-05 | Profil memenuhi semua atribut | Skor 100 | sesuai harapan | skor=100.0 | LULUS |
| BB-06 | Atribut pembukuan dilepas dari profil sempurna | Skor turun tepat 25 poin (bobot terbesar) | sesuai harapan | 100 - 75.0 = 25.0 | LULUS |
| BB-07 | Baris hasil impor dataset tidak diubah nilanya oleh aplikasi | Flag kuesioner tetap; hanya dilaporkan bila bertentangan | sesuai harapan | Di kuesioner catatan keuangan tercatat tidak ada, ta... | LULUS |
| BB-08b | Skor bergerak setelah aksi sekali-klik | Pesan memuat perubahan poin | sesuai harapan | 55.92 -> 55.92; Catatan Transport Rp467.500 masuk  | LULUS |
| BB-08 | Tombol sekali-klik 'Catat sekarang' di dashboard | Satu baris buku kas terbentuk tanpa membuka formulir | sesuai harapan | total baris=217; pesan: Catatan Transport Rp467.500 masuk ke buku ka... | LULUS |
| BB-09 | Input nominal ditulis '12.500' (titik ribuan) | Tersimpan 12500 | sesuai harapan | tersimpan=12,500 | LULUS |
| BB-10 | Hapus satu baris lalu tekan 'Batalkan hapusan terakhir' | Jumlah baris pulih, tanpa dialog konfirmasi browser | sesuai harapan | 218 -> 217 -> 218 | LULUS |
| BB-11 | Membuka /rencana?draf=1 bagi pengguna tanpa rencana | Formulir terisi otomatis dari riwayat arus kas | sesuai harapan | banner draf + target terisi | LULUS |
| BB-12 | Menekan 'Bagikan tautan' pada katalog | Status jualan online aktif + usaha pemasaran naik satu tingkat | sesuai harapan | internet=1, pemasaran=5 | LULUS |
| BB-13 | Mengubah mode bahasa pada halaman | Istilah teknis muncul hanya di mode riset | sesuai harapan | pergantian leksikon terverifikasi | LULUS |
| BB-14 | Menampilkan hasil perhitungan ke mesin luar (/api/skor) | JSON berisi skor, status, tiga pilar, dan rekomendasi | sesuai harapan | skor=58.42, pilar=[77.5, 71.7, 0.0] | LULUS |
| BB-15 | Sembilan rute utama + berkas PWA | Semua merespons 200/302 | sesuai harapan | tidak ada rute yang gagal | LULUS |

Total 16 kasus: LULUS 16, GAGAL 0.
