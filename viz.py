"""
SIDUMKM — pembentuk geometri grafik (SVG dihitung di server, tanpa library chart).
Setiap fungsi mengembalikan koordinat siap pakai di template Jinja.
"""
import math

SINGKATAN_BULAN = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "Mei", "06": "Jun",
    "07": "Jul", "08": "Agu", "09": "Sep", "10": "Okt", "11": "Nov", "12": "Des",
}


def nama_bulan(ym):
    if not ym or "-" not in str(ym):
        return ym
    return SINGKATAN_BULAN.get(str(ym).split("-")[1], str(ym))


def ringkas(nilai):
    nilai = float(nilai or 0)
    if abs(nilai) >= 1_000_000_000:
        return f"{nilai / 1_000_000_000:.1f} M"
    if abs(nilai) >= 1_000_000:
        return f"{nilai / 1_000_000:.0f} jt"
    if abs(nilai) >= 1_000:
        return f"{nilai / 1_000:.0f} rb"
    return f"{nilai:.0f}"


# ------------------------------------------------------------------ meter
def meter(nilai, cx=130, cy=116, r=100):
    """Busur skor 0-100, penanda nilai (jarum) dan garis ambang sukses 50."""
    nilai = max(0.0, min(100.0, float(nilai or 0)))

    def titik(skala, radius=r):
        rad = math.radians(180 - skala * 1.8)
        return (cx + radius * math.cos(rad), cy - radius * math.sin(rad))

    a, b = titik(0), titik(100)
    jj = (cx, cy)
    j1, j2 = (cx, cy), titik(nilai, r * 0.93)
    m1, m2 = titik(50, r * 0.80), titik(50, r * 0.99)
    return {
        "d": f"M {a[0]:.1f} {a[1]:.1f} A {r} {r} 0 0 1 {b[0]:.1f} {b[1]:.1f}",
        "offset": round(100 - nilai, 2), "nilai": nilai, "cx": cx, "cy": cy, "r": r,
        "jarum": {"x1": f"{j1[0]:.1f}", "y1": f"{j1[1]:.1f}", "x2": f"{j2[0]:.1f}", "y2": f"{j2[1]:.1f}"},
        "titik_udang": f"{j2[0]:.1f},{j2[1]:.1f}",
        "ambang": {"x1": f"{m1[0]:.1f}", "y1": f"{m1[1]:.1f}", "x2": f"{m2[0]:.1f}", "y2": f"{m2[1]:.1f}"},
        "ujung_kiri": {"x": f"{a[0]:.1f}", "y": f"{a[1] + 20:.1f}"},
        "ujung_kanan": {"x": f"{b[0]:.1f}", "y": f"{b[1] + 20:.1f}"},
    }


# ------------------------------------------------------------------ radar
def radar(deret, cx=200, cy=170, r=108):
    """deret = [(label, nilai 0..100)] -> geometri jaring laba-laba 3 pilar."""
    n = max(len(deret), 3)

    def titik(fraksi, indeks):
        rad = math.radians(-90 + indeks * 360 / n)
        return (cx + r * fraksi * math.cos(rad), cy + r * fraksi * math.sin(rad))

    cincin = []
    for fr in (0.25, 0.5, 0.75, 1.0):
        cincin.append(" ".join("%s,%s" % (f"{x:.1f}", f"{y:.1f}") for x, y in
                               (titik(fr, i) for i in range(n))))

    poligon = " ".join(f"{x:.1f},{y:.1f}" for x, y in
                       (titik(min(1.0, max(0.10, v / 100)), i) for i, (_, v) in enumerate(deret)))

    sumbu, label = [], []
    for i, (nama, nilai) in enumerate(deret):
        x, y = titik(1.0, i)
        lx, ly = titik(1.20, i)
        sumbu.append({"x2": f"{x:.1f}", "y2": f"{y:.1f}"})
        label.append({
            "x": f"{lx:.1f}", "y": f"{ly:.1f}", "nama": nama, "nilai": nilai,
            "anchor": "middle" if abs(lx - cx) < 8 else ("start" if lx > cx else "end"),
        })
    return {"cx": cx, "cy": cy, "r": r, "lebar": cx * 2, "tinggi": cy * 2 + 34,
            "cincin": cincin, "poligon": poligon, "sumbu": sumbu, "label": label}


# ------------------------------------------------------------------ garis
def garis(seri, lebar=640, tinggi=212, kiri=62, kanan=16, atas=16, bawah=32):
    """
    seri = [(nama, [(bulan 'YYYY-MM', nilai), ...])]
    Mengembalikan grid, polyline, area, dan sumbu X.
    """
    semua = [v for _, titik_tupel in seri for _, v in titik_tupel]
    if not semua:
        return None
    maks = max(semua) or 1
    orde = 10 ** int(math.log10(maks))
    batas = math.ceil(maks / orde) * orde
    n = max(len(p) for _, p in seri)
    rentang = max(1, n - 1)

    def x(i):
        return kiri + i * (lebar - kiri - kanan) / rentang

    def y(v):
        return tinggi - bawah - (v / batas) * (tinggi - atas - bawah)

    grid = [{"y": f"{y(batas * k / 4):.1f}", "label": ringkas(batas * k / 4)} for k in range(5)]

    jalur = []
    for idx, (nama, titik_tupel) in enumerate(seri):
        pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, (_, v) in enumerate(titik_tupel))
        area = (f"M {x(0):.1f},{tinggi - bawah} L " +
                " L ".join(f"{x(i):.1f},{y(v):.1f}" for i, (_, v) in enumerate(titik_tupel)) +
                f" L {x(len(titik_tupel) - 1):.1f},{tinggi - bawah} Z")
        jalur.append({
            "nama": nama, "points": pts, "area": area if idx == 0 else "",
            "titik": [{"cx": f"{x(i):.1f}", "cy": f"{y(v):.1f}", "nilai": v,
                       "bulan": nama_bulan(b)} for i, (b, v) in enumerate(titik_tupel)],
        })

    sumbu_x = [{"x": f"{x(i):.1f}", "label": nama_bulan(b)} for i, (b, _) in enumerate(seri[0][1])]
    return {"lebar": lebar, "tinggi": tinggi, "kiri": kiri, "grid": grid, "jalur": jalur,
            "sumbu_x": sumbu_x, "dasar": tinggi - bawah, "batas": batas}


# ------------------------------------------------------------------ kolom
def kolom(nilai_list, label_list=None, lebar=640, tinggi=150, bawah=26, atas=10, batas=100):
    """Batang riwayat skor 0-100."""
    n = max(len(nilai_list), 1)
    jarak = (lebar - 20) / n
    lebar_batang = max(4, min(34, jarak * 0.6))
    bars = []
    for i, v in enumerate(nilai_list):
        t = max(2.0, (float(v) / batas) * (tinggi - atas - bawah))
        x = 10 + i * jarak + (jarak - lebar_batang) / 2
        bars.append({"x": f"{x:.1f}", "y": f"{tinggi - bawah - t:.1f}",
                     "w": f"{lebar_batang:.1f}", "h": f"{t:.1f}",
                     "nilai": v, "label": (label_list[i] if label_list and i < len(label_list) else "")})
    return {"lebar": lebar, "tinggi": tinggi, "dasar": tinggi - bawah, "bars": bars,
            "garis_ambang": f"{tinggi - bawah - (50 / batas) * (tinggi - atas - bawah):.1f}"}


# ------------------------------------------------------------ batang acuan
def batang(deret):
    """deret = [(label, nilai, pembanding, warna)] -> data tabel batang horizontal."""
    batas = max([max(a, b) for _, a, b, _ in deret] + [1]) or 1
    return [{"label": l, "anda": a, "acuan": b, "warna": w,
             "lebar": max(2.0, a / batas * 100), "lebar_acuan": max(2.0, b / batas * 100)}
            for l, a, b, w in deret]
