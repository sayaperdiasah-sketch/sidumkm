# -*- coding: utf-8 -*-
"""
Pemeriksaan independen terhadap hasil olahan dataset UMKM (250 baris).
Tujuan: memastikan angka yang akan masuk naskah benar-benar temuan,
bukan artefak dari cara label dibuat.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

pd.set_option("display.width", 130)
pd.set_option("display.max_columns", None)

CARA = [Path(__file__).resolve().parents[i] / "uploads/umkm_clean.csv" for i in range(1, 5)]
CSV = sys.argv[1] if len(sys.argv) > 1 else next((str(c) for c in CARA if c.exists()), "umkm_clean.csv")
print("memakai berkas:", CSV)
df = pd.read_csv(CSV)
y = df["status_keberhasilan"].astype(int)

print("BAGIAN A — apakah label berdiri sendiri?")
print("label = 1 jika Skor_Keberhasilan >= 50, dan Skor_Keberhasilan dihitung dari 8 fitur yang sama")
ulang = (df["Skor_Keberhasilan"] >= 50).astype(int)
print(f"   akurasi label terhadap rumus  : {(ulang == y).mean() * 100:.1f}%")
print(f"   base rate 'Berhasil'          : {y.mean() * 100:.1f}% ({y.sum()} dari {len(df)})")
print(f"   skor terendah/tertinggi       : {df['Skor_Keberhasilan'].min():.1f} / {df['Skor_Keberhasilan'].max():.1f}")

print("\nBAGIAN B — korelasi asli (pearson) vs angka yang dipakai di naskah")
fitur = [c for c in df.columns if c not in
         ("Skor_Keberhasilan", "status_keberhasilan", "Age_Group", "Education_Label")]
r_asli = df[fitur + ["status_keberhasilan"]].corr()["status_keberhasilan"].drop("status_keberhasilan")
banding = pd.DataFrame({
    "r_sebenarnya": r_asli.round(3),
    "selisih_rerata": (df[y == 1][fitur].mean() - df[y == 0][fitur].mean()).round(3),
})
print(banding.sort_values("r_sebenarnya", ascending=False).to_string())
print("   catatan: untuk fitur biner, selisih_rerata x100 = poin persentase (mis. 0,568 -> 56,8 poin)")

print("\nBAGIAN C — dua arah kondisional (sering tertukar di naskah)")
for f in ["Financial_Record_Keeping", "Business_Plan", "Internet_Usage", "Partnership", "Initial_Capital"]:
    a = y[df[f] == 1].mean() * 100
    b = y[df[f] == 0].mean() * 100
    c = df.loc[y == 1, f].mean() * 100
    d = df.loc[y == 0, f].mean() * 100
    print(f"   {f:28s} P(sukses|punya)={a:5.1f}%  P(sukses|tidak)={b:5.1f}%   ||   P(punya|sukses)={c:5.1f}%  P(punya|gagal)={d:5.1f}%")

print("\nBAGIAN D — apakah r mencerminkan kekuatan data atau besar bobot?")
bobot = {"Financial_Record_Keeping": 25, "Business_Plan": 20, "Marketing_Norm": 15,
         "Internet_Usage": 10, "Initial_Capital": 10, "Experience_Norm": 10,
         "Partnership": 5, "Advice_Norm": 5}
for f, w in bobot.items():
    skor_tanpa = df["Skor_Keberhasilan"] - df[f] * w
    r_lengkap = np.corrcoef(df[f], y)[0, 1]
    r_tanpa = np.corrcoef(df[f], (skor_tanpa >= 50).astype(int))[0, 1]
    print(f"   {f:28s} bobot={w:>2} | r dgn label={r_lengkap:+.3f} | r dgn label TANPA dirinya={r_tanpa:+.3f} (turun {r_lengkap - r_tanpa:+.3f})")
print("   -> kalau korelasi 'hilang' saat fitur dikeluarkan dari rumus label,")
print("      hubungannya bukan temuan empiris: itu definisi.")

print("\nBAGIAN E — uji statistik yang sah pada label derivatif ini")
from scipy import stats
chi2, p, _, _ = stats.chi2_contingency(pd.crosstab(df.Financial_Record_Keeping, y))
print(f"   chi-square catatan_keuangan x label : chi2={chi2:.1f} p={p:.2e}  (signifikan, tapi tautologis)")
# bandingkan dengan label acak sebagai kontrol negatif
rng = np.random.default_rng(7)
yacak = rng.binomial(1, y.mean(), len(df))
c2, p2, _, _ = stats.chi2_contingency(pd.crosstab(df.Financial_Record_Keeping, yacak))
pred = (df.Skor_Keberhasilan >= 50).astype(int)
print(f"   label ACAK dengan base rate sama    : akurasi rumus={(pred == yacak).mean() * 100:.1f}%, chi2={c2:.1f} p={p2:.3f}")
ts = stats.pearsonr(df.Financial_Record_Keeping, yacak)
print(f"   r dengan label acak                 : {ts[0]:+.3f} (p={ts[1]:.3f})  <- ini pembanding yang jujur")

print("\nBAGIAN F — apa yang MASIH bisa diklaim dari dataset ini")
koomen = pd.crosstab(df.Financial_Record_Keeping, df.Business_Plan)
print("   hubungan antar FITUR (bebas dari label derivatif):")
print(koomen.to_string())
korel3 = df[["Financial_Record_Keeping", "Business_Plan", "Internet_Usage", "Marketing_Effort",
             "Initial_Capital", "Industry_Experience"]].corr().round(2)
print(korel3.to_string())

print("\nBAGIAN G — model warkop (berkas lain di folder yang sama)")
stat = pd.read_pickle("/workspace/6b761e99-ceda-4f0b-bcc8-c7cabc3534ef/work/uploads/model_stats.pkl")
print("   model_stats.pkl:", {k: round(v, 3) for k, v in stat.items()})
print("   RandomForestRegressor 119 MB ikut diunggah -> ada target lain (omzet?) yang bukan turunan rumus")
