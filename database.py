"""
SIDUMKM — lapisan database (SQLite)
Skema 7 tabel sesuai rancangan sistem: users, business_profile, financial_records,
business_plans, marketing_activities, scores, reference_stats.
"""
import sqlite3
from pathlib import Path

from scoring import hitung_skor_umkm

DB_PATH = Path(__file__).resolve().parent / "sidumkm.db"

SKEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    usia INTEGER,
    education INTEGER,
    owner_gender INTEGER,
    toko_slug TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS business_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    nama_usaha TEXT,
    jenis_usaha TEXT,
    initial_capital INTEGER DEFAULT 0,
    financial_record_keeping INTEGER DEFAULT 0,
    internet_usage INTEGER DEFAULT 0,
    business_plan INTEGER DEFAULT 0,
    marketing_effort INTEGER DEFAULT 1,
    partnership INTEGER DEFAULT 0,
    parent_business_experience INTEGER DEFAULT 0,
    industry_experience REAL DEFAULT 0,
    professional_advice INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS financial_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tanggal DATE NOT NULL,
    jenis TEXT NOT NULL CHECK (jenis IN ('masuk','keluar')),
    kategori TEXT NOT NULL,
    jumlah REAL NOT NULL,
    keterangan TEXT
);
CREATE INDEX IF NOT EXISTS idx_fin_user ON financial_records(user_id, tanggal);

CREATE TABLE IF NOT EXISTS business_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    judul TEXT,
    target_omzet REAL DEFAULT 0,
    modal_usaha REAL DEFAULT 0,
    strategi_pemasaran TEXT,
    produk_utama TEXT,
    analisis_risiko TEXT,
    deadline DATE,
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS marketing_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    nama_produk TEXT NOT NULL,
    harga REAL DEFAULT 0,
    deskripsi TEXT,
    foto_teks TEXT,
    link_katalog TEXT,
    aktif INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skor_keberhasilan REAL,
    status TEXT,
    kategori TEXT,
    skor_keuangan REAL,
    skor_perencanaan REAL,
    skor_pemasaran REAL,
    rekomendasi TEXT,
   calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reference_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    indikator TEXT NOT NULL,
    kode TEXT NOT NULL,
    ambang TEXT,
    nilai_berhasil REAL,
    nilai_tidak_berhasil REAL,
    selisih REAL,
    korelasi REAL,
    bobot INTEGER,
    keterangan TEXT
);
"""


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = db()
    conn.executescript(SKEMA)
    # migrasi ringan: kolom untuk hapus bertahap-bisa-batal + jejak verifikasi
    punya = {r["name"] for r in conn.execute("PRAGMA table_info(financial_records)")}
    if "dihapus_pada" not in punya:
        conn.execute("ALTER TABLE financial_records ADD COLUMN dihapus_pada TEXT")
    punya_p = {r["name"] for r in conn.execute("PRAGMA table_info(business_profile)")}
    if "verifikasi_otomatis" not in punya_p:
        conn.execute("ALTER TABLE business_profile ADD COLUMN verifikasi_otomatis TEXT DEFAULT ''")
    conn.commit()
    conn.close()


# ------------------------------------------------- ringkasan per pengguna
def ambil_profil(conn, user_id):
    row = conn.execute("SELECT * FROM business_profile WHERE user_id=?", (user_id,)).fetchone()
    return dict(row) if row else None


def ringkasan_modul(conn, user_id):
    """Indikator turunan dari tabel transaksi / rencana / katalog, dipakai scoring."""
    fin = conn.execute(
        """SELECT
             COUNT(*)                                                        AS n,
             COALESCE(SUM(CASE WHEN jenis='masuk'  THEN jumlah END), 0)      AS masuk,
             COALESCE(SUM(CASE WHEN jenis='keluar' THEN jumlah END), 0)      AS keluar,
             COUNT(DISTINCT CASE WHEN tanggal >= date('now','-30 days') THEN tanggal END)
                                                                            AS hari_catat,
             COUNT(DISTINCT CASE WHEN tanggal >= date('now','-30 days') THEN 1 END)
                                                                            AS aktif
           FROM financial_records WHERE user_id=? AND dihapus_pada IS NULL""",
        (user_id,),
    ).fetchone()

    net = (fin["masuk"] or 0) - (fin["keluar"] or 0)
    margin = (net / fin["masuk"]) if fin["masuk"] else 0.0

    plan = conn.execute(
        "SELECT * FROM business_plans WHERE user_id=? ORDER BY id DESC LIMIT 1", (user_id,)
    ).fetchone()

    omzet_bulan_ini = conn.execute(
        """SELECT COALESCE(SUM(jumlah),0) AS total FROM financial_records
           WHERE user_id=? AND jenis='masuk' AND dihapus_pada IS NULL
             AND strftime('%Y-%m',tanggal)=strftime('%Y-%m','now')""",
        (user_id,),
    ).fetchone()["total"]

    kelengkapan = 0
    progress = 0.0
    if plan:
        kelengkapan = sum(
            1 for k in ("target_omzet", "modal_usaha", "strategi_pemasaran",
                        "produk_utama", "analisis_risiko")
            if plan[k] not in (None, "", 0)
        )
        if plan["target_omzet"]:
            progress = min(100.0, 100.0 * omzet_bulan_ini / plan["target_omzet"])
        else:
            progress = plan["progress"] or 0

    produk = conn.execute(
        "SELECT COUNT(*) AS n FROM marketing_activities WHERE user_id=? AND aktif=1", (user_id,)
    ).fetchone()["n"]

    return {
        "jumlah_transaksi": fin["n"] or 0,
        "masuk": fin["masuk"] or 0,
        "keluar": fin["keluar"] or 0,
        "net": net,
        "margin": margin,
        "hari_catat_30hari": fin["hari_catat"] or 0,
        "target_omzet": plan["target_omzet"] if plan else 0,
        "punya_deadline": bool(plan and plan["deadline"]),
        "kelengkapan_isian": kelengkapan,
        "progress_target": progress,
        "jumlah_produk": produk,
        "omzet_bulan_ini": omzet_bulan_ini,
        "rencana": dict(plan) if plan else None,
    }


def simpan_skor(conn, user_id, profil, modul):
    """Hitung ulang skor, simpan sebagai riwayat, kembalikan hasilnya."""
    import json

    hasil = hitung_skor_umkm(profil, modul)
    from scoring import generate_rekomendasi

    rekomendasi = generate_rekomendasi(profil, modul)
    conn.execute(
        """INSERT INTO scores (user_id, skor_keberhasilan, status, kategori,
                               skor_keuangan, skor_perencanaan, skor_pemasaran, rekomendasi)
           VALUES (?,?,?,?,?,?,?,?)""",
        (user_id, hasil["skor"], hasil["status"], hasil["kategori"],
         hasil["pilar"]["keuangan"], hasil["pilar"]["perencanaan"],
         hasil["pilar"]["pemasaran"], json.dumps(rekomendasi)),
    )
    conn.commit()
    hasil["rekomendasi"] = rekomendasi
    return hasil


def riwayat_skor(conn, user_id, jumlah_riwayat=30):
    """Riwayat skor terbaru (untuk garis tren di dashboard)."""
    rows = conn.execute(
        """SELECT skor_keberhasilan, calculated_at FROM scores
           WHERE user_id=? ORDER BY id DESC LIMIT ?""",
        (user_id, jumlah_riwayat),
    ).fetchall()
    return [(r["calculated_at"], r["skor_keberhasilan"]) for r in reversed(rows)]


def tren_omzet(conn, user_id, bulan=6):
    """Omzet & biaya 6 bulan terakhir per YYYY-MM, untuk line chart dashboard."""
    rows = conn.execute(
        """SELECT strftime('%Y-%m',tanggal) AS bulan,
                  COALESCE(SUM(CASE WHEN jenis='masuk'  THEN jumlah END),0) AS masuk,
                  COALESCE(SUM(CASE WHEN jenis='keluar' THEN jumlah END),0) AS keluar
           FROM financial_records
           WHERE user_id=? AND tanggal >= date('now', ?)
           GROUP BY bulan ORDER BY bulan ASC""",
        (user_id, f"-{int(bulan)} months"),
    ).fetchall()
    return [dict(r) for r in rows]


# ------------------------------------------------- pembuat saran otomatis
def statistik_saran(conn, user_id):
    """Nominal & kategori paling umum — dipakai chip sekali-klik di form transaksi."""
    baris = conn.execute(
        """SELECT jenis, kategori, COUNT(*) AS n, SUM(jumlah) AS total
           FROM financial_records
           WHERE user_id=? AND dihapus_pada IS NULL AND tanggal >= date('now','-120 days')
           GROUP BY jenis, kategori ORDER BY n DESC LIMIT 6""",
        (user_id,)).fetchall()
    nominal = conn.execute(
        """SELECT jenis, ROUND(AVG(jumlah), -3) AS rata, COUNT(*) n
           FROM financial_records WHERE user_id=? AND dihapus_pada IS NULL
           GROUP BY jenis""",
        (user_id,)).fetchall()
    aktif = conn.execute(
        """SELECT COUNT(DISTINCT tanggal) AS hari, MAX(tanggal) AS terakhir
           FROM financial_records WHERE user_id=? AND dihapus_pada IS NULL
             AND tanggal >= date('now','-7 days')""",
        (user_id,)).fetchone()
    rata = {r["jenis"]: int(r["rata"] or 0) for r in nominal}
    return {
        "sering": [{"jenis": b["jenis"], "kategori": b["kategori"], "n": b["n"],
                    "jumlah": int((b["total"] or 0) / max(1, b["n"]))} for b in baris],
        "nominal_masuk": rata.get("masuk", 0),
        "nominal_keluar": rata.get("keluar", 0),
        "hari_terakhir": aktif["terakhir"] or "",
        "hari_aktif_minggu": aktif["hari"] or 0,
    }


def nominal_umum(user_id_saran, jenis, nilai_simpan=0):
    """3 nominal preset untuk chip cepat, pembulatan ke Rp500 terdekat."""
    dasar = nilai_simpan or {"masuk": 25_000, "keluar": 10_000}.get(jenis, 10_000)
    bulat = max(500, int(round(dasar / 500.0) * 500))
    return [bulat, bulat * 2, max(500, int(round(bulat / 2 / 500.0) * 500))]


def skeleton_rencana(conn, user_id, omzet_bulan=None):
    """
    Draf rencana bisnis satu halaman, diisi dari perilaku, bukan dari pertanyaan.
    Pengguna tinggal menyetujui / mengoreksi.
    """
    mod = ringkasan_modul(conn, user_id)
    saran = statistik_saran(conn, user_id)
    # basis = uang masuk bulan ini; kalau belum lengkap, rata-rata per bulan aktif
    bulan_aktif = max(1, len({str(t)[:7] for t in conn.execute(
        "SELECT tanggal FROM financial_records WHERE user_id=? AND dihapus_pada IS NULL",
        (user_id,))}) if True else 1)
    omzet = float(omzet_bulan or max(mod["masuk"] / bulan_aktif, mod["omzet_bulan_ini"]))
    langkah = 100_000 if omzet >= 5_000_000 else 10_000
    target = int(round(omzet * 1.10 / langkah) * langkah) if omzet else 0
    produk = conn.execute(
        """SELECT nama_produk, harga FROM marketing_activities
           WHERE user_id=? AND aktif=1 ORDER BY id LIMIT 1""", (user_id,)).fetchone()
    kategori_masuk = next((s for s in saran["sering"] if s["jenis"] == "masuk"), None)
    strategi = ("Posting foto produk di WhatsApp/Instagram 2x seminggu dan titipkan daftar harga "
                "ke 3 warung tetangga. Catat setiap penjualan di buku kas.")
    return {
        "judul": "Rencana 3 bulan ke depan",
        "target_omzet": target,
        "modal_usaha": int(round((mod["keluar"] or 0) / bulan_aktif / 10_000) * 10_000),
        "produk_utama": produk["nama_produk"] if produk else "",
        "strategi_pemasaran": strategi,
        "analisis_risiko": "Harga bahan baku naik; penjualan sepi di minggu pertama bulan.",
        "kategori_andalan": kategori_masuk["kategori"] if kategori_masuk else "Penjualan",
    }


def urungkan_hapus(conn, user_id):
    """Batalkan penghapusan terakhir (soft-delete)."""
    row = conn.execute(
        """SELECT id FROM financial_records
           WHERE user_id=? AND dihapus_pada IS NOT NULL
           ORDER BY dihapus_pada DESC LIMIT 1""", (user_id,)).fetchone()
    if not row:
        return False
    conn.execute("UPDATE financial_records SET dihapus_pada=NULL WHERE id=?", (row["id"],))
    conn.commit()
    return True
