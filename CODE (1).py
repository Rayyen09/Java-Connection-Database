import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="PPIC-DSS Input System", layout="wide")
st.title("🧭 Sistem Perencanaan Produksi Terintegrasi (PPIC-DSS)")
st.caption("Versi 2.0 — Input cepat, edit, dan hapus data manual untuk sistem DSS produksi")

# Inisialisasi data session
if "data_produksi" not in st.session_state:
    st.session_state["data_produksi"] = pd.DataFrame(columns=[
        "Buyer", "Order No", "Produk", "Jumlah", "Start Date", "End Date",
        "Lead Time (hari)", "Progress (%)", "Status"
    ])

# ===== Bagian 1: Input Data Cepat =====
st.subheader("📋 Input Data Produksi")

col1, col2, col3 = st.columns(3)
with col1:
    buyer = st.text_input("Nama Buyer", key="buyer_input")
    order_no = st.text_input("Nomor Order", key="order_input")
    produk = st.text_input("Jenis Produk", key="produk_input")
with col2:
    jumlah = st.number_input("Jumlah Pesanan", min_value=1, step=1, key="jumlah_input")
    start_date = st.date_input("Tanggal Mulai", datetime.date.today(), key="start_input")
    end_date = st.date_input("Tanggal Selesai (Rencana)", datetime.date.today(), key="end_input")
with col3:
    lead_time = st.number_input("Lead Time (hari)", min_value=1, step=1, key="lead_input")
    progres = st.slider("Progress Produksi (%)", 0, 100, 0, key="progress_input")
    status = st.selectbox("Status", ["On Time", "Delayed", "Pending"], key="status_input")

# Tombol untuk menambah data
if st.button("➕ Tambah Data"):
    new_data = pd.DataFrame({
        "Buyer": [buyer],
        "Order No": [order_no],
        "Produk": [produk],
        "Jumlah": [jumlah],
        "Start Date": [start_date],
        "End Date": [end_date],
        "Lead Time (hari)": [lead_time],
        "Progress (%)": [progres],
        "Status": [status]
    })

    # Validasi sederhana
    if buyer and order_no and produk:
        st.session_state["data_produksi"] = pd.concat(
            [st.session_state["data_produksi"], new_data], ignore_index=True
        )
        st.success("✅ Data berhasil ditambahkan!")
        # Reset input field otomatis
        st.session_state["buyer_input"] = ""
        st.session_state["order_input"] = ""
        st.session_state["produk_input"] = ""
        st.session_state["jumlah_input"] = 1
        st.session_state["progress_input"] = 0
    else:
        st.warning("⚠️ Pastikan semua field wajib terisi!")

st.divider()

# ===== Bagian 2: Tabel Data =====
st.subheader("📊 Data Produksi Terkini")
df = st.session_state["data_produksi"]

if not df.empty:
    st.dataframe(df, use_container_width=True)
    # Pilih baris untuk dihapus
    st.markdown("### 🗑️ Hapus Data yang Salah")
    index_to_delete = st.number_input("Masukkan nomor baris yang ingin dihapus (mulai dari 0):", 
                                      min_value=0, 
                                      max_value=len(df)-1 if len(df) > 0 else 0, 
                                      step=1)
    if st.button("Hapus Data"):
        st.session_state["data_produksi"].drop(index_to_delete, inplace=True)
        st.session_state["data_produksi"].reset_index(drop=True, inplace=True)
        st.success(f"✅ Baris ke-{index_to_delete} berhasil dihapus!")
else:
    st.info("Belum ada data yang dimasukkan.")

st.divider()

# ===== Bagian 3: Analisis Ringkas =====
if not df.empty:
    st.subheader("📈 Analisis Produksi Singkat")
    total_order = len(df)
    avg_progress = df["Progress (%)"].mean()
    delayed = len(df[df["Status"] == "Delayed"])
    on_time = len(df[df["Status"] == "On Time"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Order", total_order)
    col2.metric("Rata-rata Progress", f"{avg_progress:.1f}%")
    col3.metric("On Time", on_time)
    col4.metric("Delayed", delayed)

    st.bar_chart(df.set_index("Produk")["Progress (%)"])

# ===== Bagian 4: Simpan ke File =====
if not df.empty:
    st.download_button(
        label="💾 Download Data ke Excel",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="data_produksi_ppic.csv",
        mime="text/csv",
    )

st.caption("© 2025 Sistem PPIC-DSS | Dibangun dengan Streamlit")
