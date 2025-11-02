import streamlit as st
import pandas as pd
import datetime

# Judul aplikasi
st.set_page_config(page_title="PPIC-DSS Input System", layout="wide")
st.title("🧭 Sistem Perencanaan Produksi Terintegrasi (PPIC-DSS)")
st.markdown("Prototype sederhana untuk input dan analisis manual data produksi secara real-time.")

# ===== Bagian 1: Input Data =====
st.header("📋 Input Data Produksi")

# Form input manual
with st.form("input_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        buyer = st.text_input("Nama Buyer")
        order_no = st.text_input("Nomor Order")
        produk = st.text_input("Jenis Produk")
    with col2:
        jumlah = st.number_input("Jumlah Pesanan", min_value=1, step=1)
        start_date = st.date_input("Tanggal Mulai", datetime.date.today())
        end_date = st.date_input("Tanggal Selesai (Rencana)")
    with col3:
        lead_time = st.number_input("Lead Time (hari)", min_value=1, step=1)
        progres = st.slider("Progress Produksi (%)", 0, 100, 0)
        status = st.selectbox("Status", ["On Time", "Delayed", "Pending"])

    submitted = st.form_submit_button("Simpan Data")

# Inisialisasi data storage
if "data_produksi" not in st.session_state:
    st.session_state["data_produksi"] = pd.DataFrame(columns=[
        "Buyer", "Order No", "Produk", "Jumlah", "Start Date", "End Date",
        "Lead Time (hari)", "Progress (%)", "Status"
    ])

# Simpan data ke tabel jika disubmit
if submitted:
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
    st.session_state["data_produksi"] = pd.concat([st.session_state["data_produksi"], new_data], ignore_index=True)
    st.success("✅ Data berhasil disimpan!")

# ===== Bagian 2: Tabel Data =====
st.header("📊 Data Produksi Terkini")
df = st.session_state["data_produksi"]

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("Belum ada data yang dimasukkan.")

# ===== Bagian 3: Analisis Cepat =====
if not df.empty:
    st.header("📈 Analisis Produksi Singkat")

    total_order = len(df)
    avg_progress = df["Progress (%)"].mean()
    delayed = len(df[df["Status"] == "Delayed"])
    on_time = len(df[df["Status"] == "On Time"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Order", total_order)
    col2.metric("Rata-rata Progress", f"{avg_progress:.1f}%")
    col3.metric("On Time", on_time)
    col4.metric("Delayed", delayed)

    # Grafik progress
    st.bar_chart(df.set_index("Produk")["Progress (%)"])

# ===== Bagian 4: Simpan ke Excel =====
if not df.empty:
    st.download_button(
        label="💾 Download Data ke Excel",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="data_produksi_ppic.csv",
        mime="text/csv",
    )

# Footer
st.markdown("---")
st.caption("© 2025 Sistem PPIC-DSS | Prototype by Streamlit & Python")
