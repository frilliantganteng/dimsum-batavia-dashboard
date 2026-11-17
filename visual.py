"""Fungsi visualisasi (matplotlib/seaborn) - dipakai oleh Streamlit & makalah."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import analisis as an

MERAH, EMAS, ABU, HIJAU = "#B3261E", "#E0A526", "#9A9189", "#2E7D5B"
PALET = ["#B3261E", "#E0A526", "#2E7D5B", "#7A4E2D", "#D9693A",
         "#4F7CAC", "#8E6BBF", "#C98A8A", "#6B8E23", "#5C5C5C"]
plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titleweight": "bold"})


def _bar_h(ax, serie, fmt, tertinggi=MERAH, terendah=EMAS):
    s = serie.sort_values()
    warna = [ABU] * len(s)
    warna[-1], warna[0] = tertinggi, terendah
    ax.barh(s.index, s.values, color=warna)
    for y, v in enumerate(s.values):
        ax.text(v, y, " " + fmt(v), va="center", fontsize=9)
    ax.set_xlim(0, s.max() * 1.18)
    ax.margins(y=0.04)


def fig_jumlah_per_mitra(df):
    fig, ax = plt.subplots(figsize=(8, 4.6))
    _bar_h(ax, an.jumlah_per_mitra(df), lambda v: f"{int(v)}")
    ax.set_title("Jumlah Transaksi per Mitra")
    ax.set_xlabel("Jumlah transaksi (merah = tertinggi, kuning = terendah)")
    fig.tight_layout()
    return fig


def fig_tren_bulanan(df):
    t = an.tren_bulanan(df)
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.plot(t.index, t.values, marker="o", color=MERAH, lw=2.2)
    ax.fill_between(range(len(t)), t.values, alpha=.10, color=MERAH)
    for i, v in enumerate(t.values):
        ax.annotate(int(v), (i, v), textcoords="offset points", xytext=(0, 7),
                    ha="center", fontsize=9)
    ax.set_ylim(0, t.max() * 1.2)
    ax.set_title("Tren Jumlah Transaksi Bulanan")
    ax.set_ylabel("Jumlah transaksi")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    fig.tight_layout()
    return fig


def fig_persentase(df):
    s = an.jumlah_per_mitra(df)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    w, _ = ax.pie(s.values, colors=PALET[:len(s)], startangle=90, counterclock=False,
                  wedgeprops=dict(width=.42, edgecolor="white"))
    ax.legend(w, [f"{n} ({v / s.sum() * 100:.1f}%)" for n, v in s.items()],
              loc="center left", bbox_to_anchor=(1, .5), frameon=False)
    ax.text(0, 0, f"{s.sum():,}\ntransaksi".replace(",", "."), ha="center", va="center",
            fontweight="bold")
    ax.set_title("Kontribusi Mitra terhadap Total Transaksi")
    fig.tight_layout()
    return fig


def fig_nominal_per_mitra(df):
    s = an.nominal_per_mitra(df) / 1e6
    fig, ax = plt.subplots(figsize=(8, 4.6))
    _bar_h(ax, s, lambda v: f"Rp {v:,.1f} jt".replace(",", "."), tertinggi=HIJAU)
    ax.set_title("Total Nominal Transaksi Berhasil per Mitra")
    ax.set_xlabel("Total nominal (juta rupiah)")
    fig.tight_layout()
    return fig


def fig_heatmap(df):
    h = an.heatmap_data(df)
    fig, ax = plt.subplots(figsize=(9, 3.8))
    sns.heatmap(h, cmap="YlOrRd", annot=True, fmt="d", linewidths=.5,
                cbar_kws={"label": "Jumlah transaksi"}, ax=ax, annot_kws={"size": 8})
    ax.set_title("Heatmap Aktivitas Transaksi (Hari x Jam)")
    ax.set_xlabel("Jam")
    ax.set_ylabel("")
    ax.tick_params(axis="y", rotation=0)
    fig.tight_layout()
    return fig


def fig_status(df):
    tot = df["status"].value_counts().reindex(["Berhasil", "Pending", "Gagal"], fill_value=0)
    spm = an.status_per_mitra(df)
    pct = spm.div(spm.sum(axis=1), axis=0) * 100
    pct = pct.sort_values("Berhasil")
    warna = {"Berhasil": HIJAU, "Pending": EMAS, "Gagal": MERAH}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1, 1.6]})
    a1.pie(tot.values, labels=[f"{k}\n{v / tot.sum() * 100:.1f}%" for k, v in tot.items()],
           colors=[warna[k] for k in tot.index], startangle=90, counterclock=False,
           wedgeprops=dict(width=.45, edgecolor="white"))
    a1.set_title("Status Transaksi Keseluruhan")
    left = 0 * pct["Berhasil"]
    for st in ["Berhasil", "Pending", "Gagal"]:
        a2.barh(pct.index, pct[st], left=left, color=warna[st], label=st)
        left = left + pct[st]
    a2.set_xlim(0, 100)
    a2.set_xlabel("Persentase transaksi (%)")
    a2.set_title("Komposisi Status per Mitra")
    a2.legend(ncol=3, loc="lower center", bbox_to_anchor=(.5, -.28), frameon=False)
    fig.tight_layout()
    return fig
