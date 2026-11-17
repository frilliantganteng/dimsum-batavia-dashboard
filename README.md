# Dimsum Batavia – Dashboard Analisis Transaksi Mitra
Projek UTS Data Science.

## Menjalankan
    pip install -r requirements.txt
    streamlit run app.py

Dataset bawaan: `data_transaksi_mitra.csv` (simulasi). Untuk data riil, unggah CSV lewat sidebar
dengan kolom: id_transaksi, tanggal, mitra, produk, qty, harga_satuan, total_nominal,
metode_pembayaran, status (kolom `kota` opsional).
Dataset dapat dibuat ulang dengan `python generate_data.py`.
