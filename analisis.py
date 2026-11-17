"""Modul pengolahan data transaksi mitra Dimsum Batavia."""
from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).parent / "data_transaksi_mitra.csv"
HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
NAMA_BULAN = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun",
              7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"}
KOLOM_WAJIB = ["id_transaksi", "tanggal", "mitra", "produk", "qty",
               "harga_satuan", "total_nominal", "metode_pembayaran", "status"]


def load_raw(sumber=DATA_PATH):
    return pd.read_csv(sumber)


def clean(raw):
    """Pembersihan data. Mengembalikan (dataframe bersih, log perubahan)."""
    df = raw.copy()
    log = {"baris_awal": len(df)}

    # 1. Seragamkan teks (spasi berlebih & huruf besar/kecil)
    df["mitra"] = df["mitra"].str.strip().str.title()
    df["status"] = df["status"].str.strip().str.title()
    log["teks_diseragamkan"] = int((raw["mitra"] != df["mitra"]).sum()
                                   + (raw["status"] != df["status"]).sum())

    # 2. Hapus duplikat berdasarkan id_transaksi
    sebelum = len(df)
    df = df.drop_duplicates(subset="id_transaksi", keep="first")
    log["duplikat_dihapus"] = sebelum - len(df)

    # 3. Tipe data
    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
    df = df.dropna(subset=["tanggal", "mitra", "status"])

    # 4. Nilai kosong: nominal dihitung ulang (qty x harga), metode bayar diberi label
    log["nominal_diisi"] = int(df["total_nominal"].isna().sum())
    df["total_nominal"] = df["total_nominal"].fillna(df["qty"] * df["harga_satuan"])
    log["metode_kosong_diisi"] = int(df["metode_pembayaran"].isna().sum())
    df["metode_pembayaran"] = df["metode_pembayaran"].fillna("Tidak Diketahui")

    # 5. Fitur turunan untuk analisis
    df["periode"] = df["tanggal"].dt.to_period("M")
    df["bulan"] = df["tanggal"].dt.month.map(NAMA_BULAN) + " " + df["tanggal"].dt.year.astype(str)
    df["hari"] = pd.Categorical(df["tanggal"].dt.dayofweek.map(dict(enumerate(HARI))),
                                categories=HARI, ordered=True)
    df["jam"] = df["tanggal"].dt.hour

    df = df.sort_values("tanggal").reset_index(drop=True)
    log["baris_akhir"] = len(df)
    return df, log


def ringkasan(df):
    ok = df[df["status"] == "Berhasil"]
    return {
        "total_transaksi": len(df),
        "transaksi_berhasil": len(ok),
        "omzet": float(ok["total_nominal"].sum()),
        "rata_nilai": float(ok["total_nominal"].mean()) if len(ok) else 0.0,
        "tingkat_berhasil": len(ok) / len(df) * 100 if len(df) else 0.0,
    }


def jumlah_per_mitra(df):
    return df.groupby("mitra").size().sort_values(ascending=False).rename("jumlah")


def nominal_per_mitra(df):
    ok = df[df["status"] == "Berhasil"]
    return ok.groupby("mitra")["total_nominal"].sum().sort_values(ascending=False)


def tren_bulanan(df):
    t = df.groupby("periode").size()
    t.index = [f"{NAMA_BULAN[p.month]} {p.year}" for p in t.index]
    return t


def heatmap_data(df):
    return (df.groupby(["hari", "jam"], observed=False).size()
              .unstack(fill_value=0).reindex(HARI))


def status_per_mitra(df):
    return (pd.crosstab(df["mitra"], df["status"])
              .reindex(columns=["Berhasil", "Pending", "Gagal"], fill_value=0))


def rp(x):
    """Format rupiah: 12.345.678"""
    return "Rp " + f"{x:,.0f}".replace(",", ".")
