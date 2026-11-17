"""Dimsum Batavia - Dashboard Analisis & Visualisasi Data Transaksi Mitra.
Jalankan:  streamlit run app.py
"""
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

import analisis as an
import visual as vz

st.set_page_config(page_title="Dimsum Batavia | Dashboard Mitra", page_icon="🥟", layout="wide")

st.markdown("""
<style>
.hero{background:linear-gradient(120deg,#B3261E 0%,#7A1712 100%);color:#FFF4E0;
      padding:1.6rem 2rem;border-radius:18px;margin-bottom:1rem}
.hero h1{margin:0;font-size:2.1rem;color:#FFF4E0}
.hero p{margin:.3rem 0 0;opacity:.9}
div[data-testid="stMetric"]{background:#fff;border:1px solid #EAD9C3;border-radius:14px;padding:.8rem 1rem}
.insight{background:#F6EBDD;border-left:5px solid #B3261E;padding:.7rem 1rem;border-radius:8px;margin-top:.4rem}
</style>
<div class="hero">
  <h1>🥟 Dimsum Batavia</h1>
  <p>Dashboard Analisis &amp; Visualisasi Data Transaksi Mitra · Proyek UTS Data Science</p>
</div>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def muat(sumber):
    raw = an.load_raw(sumber) if sumber is not None else an.load_raw()
    kurang = [k for k in an.KOLOM_WAJIB if k not in raw.columns]
    if kurang:
        raise ValueError("Kolom wajib tidak ada: " + ", ".join(kurang))
    return an.clean(raw)


# ---------- Sidebar ----------
st.sidebar.header("⚙️ Pengaturan Data")
berkas = st.sidebar.file_uploader("Unggah CSV transaksi (opsional)", type="csv")
try:
    df_all, log = muat(berkas)
except Exception as e:
    st.sidebar.error(f"Gagal membaca berkas: {e}")
    st.stop()
if berkas is None:
    st.sidebar.caption("Memakai dataset simulasi bawaan (data_transaksi_mitra.csv).")

st.sidebar.header("🔎 Filter")
tmin, tmax = df_all["tanggal"].min().date(), df_all["tanggal"].max().date()
rentang = st.sidebar.date_input("Rentang tanggal", (tmin, tmax), min_value=tmin, max_value=tmax)
daftar_mitra = sorted(df_all["mitra"].unique())
pilih_mitra = st.sidebar.multiselect("Mitra", daftar_mitra, default=daftar_mitra)
pilih_status = st.sidebar.multiselect("Status", ["Berhasil", "Pending", "Gagal"],
                                      default=["Berhasil", "Pending", "Gagal"])

df = df_all.copy()
if isinstance(rentang, tuple) and len(rentang) == 2:
    df = df[(df["tanggal"].dt.date >= rentang[0]) & (df["tanggal"].dt.date <= rentang[1])]
df = df[df["mitra"].isin(pilih_mitra) & df["status"].isin(pilih_status)]

if df.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

# ---------- KPI ----------
r = an.ringkasan(df)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Transaksi", f"{r['total_transaksi']:,}".replace(",", "."))
k2.metric("Omzet (Berhasil)", an.rp(r["omzet"]))
k3.metric("Rata-rata Nilai Transaksi", an.rp(r["rata_nilai"]))
k4.metric("Tingkat Keberhasilan", f"{r['tingkat_berhasil']:.1f}%")


def tampil(fig, catatan=None):
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    if catatan:
        st.markdown(f"<div class='insight'>💡 {catatan}</div>", unsafe_allow_html=True)


jml = an.jumlah_per_mitra(df)
nom = an.nominal_per_mitra(df)
tren = an.tren_bulanan(df)
spm = an.status_per_mitra(df)
gagal_pct = (spm["Gagal"] / spm.sum(axis=1) * 100).sort_values(ascending=False)
h = an.heatmap_data(df)
hari_top = h.sum(axis=1).idxmax()
jam_top = int(h.sum(axis=0).idxmax())

tabs = st.tabs(["📊 Jumlah per Mitra", "📈 Tren Bulanan", "🥧 Persentase", "💰 Nominal",
                "🔥 Heatmap", "✅ Status", "🗂️ Data & Cleaning", "👥 Tim"])

with tabs[0]:
    tampil(vz.fig_jumlah_per_mitra(df),
           f"<b>{jml.index[0]}</b> paling banyak bertransaksi ({jml.iloc[0]}), "
           f"sedangkan <b>{jml.index[-1]}</b> paling sedikit ({jml.iloc[-1]}).")
with tabs[1]:
    tampil(vz.fig_tren_bulanan(df),
           f"Puncak transaksi pada <b>{tren.idxmax()}</b> ({tren.max()} transaksi); "
           f"terendah pada <b>{tren.idxmin()}</b> ({tren.min()}).")
with tabs[2]:
    tampil(vz.fig_persentase(df),
           f"{jml.index[0]} menyumbang {jml.iloc[0] / jml.sum() * 100:.1f}% dari seluruh transaksi.")
with tabs[3]:
    tampil(vz.fig_nominal_per_mitra(df),
           f"<b>{nom.index[0]}</b> memiliki total nominal terbesar ({an.rp(nom.iloc[0])}), "
           f"meski jumlah transaksinya tidak selalu paling banyak.")
with tabs[4]:
    tampil(vz.fig_heatmap(df),
           f"Aktivitas tertinggi terjadi pada hari <b>{hari_top}</b> dan sekitar pukul <b>{jam_top}:00</b>.")
with tabs[5]:
    tampil(vz.fig_status(df),
           f"Persentase gagal tertinggi: <b>{gagal_pct.index[0]}</b> ({gagal_pct.iloc[0]:.1f}%). "
           "Perlu dievaluasi bersama mitra terkait.")
with tabs[6]:
    st.subheader("Log Data Cleaning")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Baris awal", log["baris_awal"])
    c2.metric("Teks diseragamkan", log["teks_diseragamkan"])
    c3.metric("Duplikat dihapus", log["duplikat_dihapus"])
    c4.metric("Nominal diisi ulang", log["nominal_diisi"])
    c5.metric("Baris akhir", log["baris_akhir"])
    st.subheader("Data Transaksi (terfilter)")
    st.dataframe(df.drop(columns=["periode"]), use_container_width=True, height=360)
    st.download_button("⬇️ Unduh data terfilter (CSV)",
                       df.drop(columns=["periode"]).to_csv(index=False).encode("utf-8"),
                       "transaksi_terfilter.csv", "text/csv")
with tabs[7]:
    st.subheader("Kelompok Proyek UTS Data Science")
    st.table(pd.DataFrame({
        "No": [1, 2, 3],
        "Nama": ["Muhammad Frilliant Ilyas", "Amar Bin Munif Dahbul", "Daffa Sidqi Irfada"],
        "NIM": ["25.240.0018", "25.240.0056", "25.240.0017"],
    }).set_index("No"))
    st.caption("Data pada dashboard ini adalah data simulasi untuk keperluan pembelajaran.")
