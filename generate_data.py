"""Membuat dataset simulasi transaksi mitra Dimsum Batavia (Jan-Okt 2026).

Dataset sengaja dibuat "kotor" (duplikat, nilai kosong, penulisan tidak seragam)
agar tahap Data Cleaning pada makalah bisa didemonstrasikan.
Jalankan:  python generate_data.py
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

MITRA = {  # nama: (kota, bobot jumlah transaksi, rata-rata porsi/transaksi, peluang gagal)
    "Dimsum Kota Tua":  ("Jakarta Barat",   0.17, 4,  0.04),
    "Kedai Sentosa":    ("Tangerang",       0.14, 5,  0.05),
    "Warung Bahari":    ("Bekasi",          0.12, 4,  0.05),
    "Resto Naga Emas":  ("Jakarta Utara",   0.10, 14, 0.03),
    "Kantin Mawar":     ("Depok",           0.10, 5,  0.06),
    "Toko Pelangi":     ("Bogor",           0.09, 6,  0.05),
    "Kafe Teratai":     ("Jakarta Selatan", 0.08, 7,  0.04),
    "Depot Lestari":    ("Semarang",        0.07, 8,  0.07),
    "Warung Harmoni":   ("Pekalongan",      0.06, 5,  0.14),
    "Gerai Sinar Jaya": ("Cirebon",         0.07, 6,  0.08),
}
PRODUK = {
    "Siomay Ayam": 18000, "Hakau Udang": 24000, "Bakpao Daging": 15000,
    "Lumpia Kulit Tahu": 16000, "Xiao Long Bao": 28000,
    "Cakar Ayam Saus": 20000, "Bakpao Coklat": 13000, "Pangsit Goreng": 14000,
}
BAYAR = ["Transfer Bank", "QRIS", "Tunai", "Virtual Account"]
FAKTOR_BULAN = {1: .80, 2: .85, 3: 1.15, 4: 1.00, 5: 1.05,
                6: 1.10, 7: 1.20, 8: 1.30, 9: 1.15, 10: 1.25}
FAKTOR_HARI = [.85, .80, .85, .90, 1.10, 1.45, 1.40]  # Senin..Minggu
JAM = np.arange(9, 22)
BOBOT_JAM = np.array([2, 4, 8, 9, 6, 4, 4, 5, 8, 10, 9, 5, 2], float)

N = 1600
tanggal_pool = pd.date_range("2026-01-01", "2026-10-31", freq="D")
w = np.array([FAKTOR_BULAN[d.month] * FAKTOR_HARI[d.dayofweek] for d in tanggal_pool])
tgl = rng.choice(tanggal_pool, size=N, p=w / w.sum())
jam = rng.choice(JAM, size=N, p=BOBOT_JAM / BOBOT_JAM.sum())
menit = rng.integers(0, 60, size=N)
waktu = pd.to_datetime(tgl) + pd.to_timedelta(jam, "h") + pd.to_timedelta(menit, "m")

nama = list(MITRA)
mitra = rng.choice(nama, size=N, p=np.array([MITRA[m][1] for m in nama]) / sum(MITRA[m][1] for m in nama))
produk = rng.choice(list(PRODUK), size=N)
qty = np.array([max(1, rng.poisson(MITRA[m][2])) for m in mitra])
harga = np.array([PRODUK[p] for p in produk])

status = []
for m in mitra:
    pg, pp = MITRA[m][3], 0.07
    status.append(rng.choice(["Berhasil", "Pending", "Gagal"], p=[1 - pg - pp, pp, pg]))

df = pd.DataFrame({
    "id_transaksi": [f"DB-{i:05d}" for i in range(1, N + 1)],
    "tanggal": waktu,
    "mitra": mitra,
    "kota": [MITRA[m][0] for m in mitra],
    "produk": produk,
    "qty": qty,
    "harga_satuan": harga,
    "total_nominal": qty * harga,
    "metode_pembayaran": rng.choice(BAYAR, size=N, p=[.35, .40, .10, .15]),
    "status": status,
}).sort_values("tanggal").reset_index(drop=True)
df["id_transaksi"] = [f"DB-{i:05d}" for i in range(1, N + 1)]

# ---- injeksi data kotor ----
idx = rng.choice(N, 30, replace=False)
for k, i in enumerate(idx):
    df.loc[i, "mitra"] = [df.loc[i, "mitra"].upper(), df.loc[i, "mitra"].lower(), "  " + df.loc[i, "mitra"] + " "][k % 3]
for i in rng.choice(N, 12, replace=False):
    df.loc[i, "status"] = rng.choice([df.loc[i, "status"].upper(), df.loc[i, "status"].lower() + " "])
df.loc[rng.choice(N, 9, replace=False), "total_nominal"] = np.nan
df.loc[rng.choice(N, 14, replace=False), "metode_pembayaran"] = np.nan
df = pd.concat([df, df.sample(18, random_state=7)], ignore_index=True)  # duplikat

df.to_csv("data_transaksi_mitra.csv", index=False)
print("Dataset dibuat:", df.shape)
