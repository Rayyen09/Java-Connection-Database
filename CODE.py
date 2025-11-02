import streamlit as st
import pandas as pd
import datetime
import json
import os
from pathlib import Path

# ===== KONFIGURASI DATABASE =====
# GANTI PATH INI SESUAI LOKASI ANDA
DATABASE_PATH = "ppic_data.json"  # Bisa juga: "C:/Users/YourName/Documents/ppic_data.json"

st.set_page_config(page_title="PPIC-DSS Input System", layout="wide", page_icon="🏭")

# ===== FUNGSI DATABASE =====
def load_data():
    """Memuat data dari file JSON"""
    if os.path.exists(DATABASE_PATH):
        try:
            with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                df = pd.DataFrame(data)
                # Konversi tanggal dari string ke date
                if not df.empty:
                    df['Start Date'] = pd.to_datetime(df['Start Date']).dt.date
                    df['End Date'] = pd.to_datetime(df['End Date']).dt.date
                return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame(columns=[
                "Buyer", "Order No", "Produk", "Jumlah", "Start Date", "End Date",
                "Lead Time (hari)", "Progress (%)", "Status"
            ])
    return pd.DataFrame(columns=[
        "Buyer", "Order No", "Produk", "Jumlah", "Start Date", "End Date",
        "Lead Time (hari)", "Progress (%)", "Status"
    ])

def save_data(df):
    """Menyimpan data ke file JSON"""
    try:
        # Konversi date ke string untuk JSON
        df_copy = df.copy()
        df_copy['Start Date'] = df_copy['Start Date'].astype(str)
        df_copy['End Date'] = df_copy['End Date'].astype(str)
        
        with open(DATABASE_PATH, 'w', encoding='utf-8') as f:
            json.dump(df_copy.to_dict('records'), f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

# ===== INISIALISASI DATA =====
if "data_produksi" not in st.session_state:
    st.session_state["data_produksi"] = load_data()

if "edit_mode" not in st.session_state:
    st.session_state["edit_mode"] = False
    st.session_state["edit_index"] = None

# ===== HEADER =====
st.title("🏭 Sistem Perencanaan Produksi Terintegrasi (PPIC-DSS)")
st.caption("Versi 3.0 — Input cepat, edit, hapus data, dan database persisten")

# Info database
col_db1, col_db2 = st.columns([3, 1])
with col_db1:
    st.info(f"📁 **Lokasi Database:** `{os.path.abspath(DATABASE_PATH)}`")
with col_db2:
    if st.button("🔄 Refresh Data"):
        st.session_state["data_produksi"] = load_data()
        st.success("Data direfresh!")

st.divider()

# ===== BAGIAN 1: INPUT/EDIT DATA =====
if st.session_state["edit_mode"]:
    st.subheader("✏️ Edit Data Produksi")
    edit_data = st.session_state["data_produksi"].iloc[st.session_state["edit_index"]]
else:
    st.subheader("📋 Input Data Produksi Baru")
    edit_data = None

col1, col2, col3 = st.columns(3)
with col1:
    buyer = st.text_input("Nama Buyer*", 
                          value=edit_data["Buyer"] if edit_data is not None else "",
                          key="buyer_input")
    order_no = st.text_input("Nomor Order*", 
                             value=edit_data["Order No"] if edit_data is not None else "",
                             key="order_input")
    produk = st.text_input("Jenis Produk*", 
                          value=edit_data["Produk"] if edit_data is not None else "",
                          key="produk_input")
with col2:
    jumlah = st.number_input("Jumlah Pesanan*", min_value=1, step=1, 
                            value=int(edit_data["Jumlah"]) if edit_data is not None else 1,
                            key="jumlah_input")
    start_date = st.date_input("Tanggal Mulai*", 
                              value=edit_data["Start Date"] if edit_data is not None else datetime.date.today(),
                              key="start_input")
    end_date = st.date_input("Tanggal Selesai (Rencana)*", 
                            value=edit_data["End Date"] if edit_data is not None else datetime.date.today(),
                            key="end_input")
with col3:
    lead_time = st.number_input("Lead Time (hari)*", min_value=1, step=1, 
                               value=int(edit_data["Lead Time (hari)"]) if edit_data is not None else 1,
                               key="lead_input")
    progres = st.slider("Progress Produksi (%)", 0, 100, 
                       value=int(edit_data["Progress (%)"]) if edit_data is not None else 0,
                       key="progress_input")
    status = st.selectbox("Status*", ["On Time", "Delayed", "Pending"],
                         index=["On Time", "Delayed", "Pending"].index(edit_data["Status"]) if edit_data is not None else 0,
                         key="status_input")

# Tombol aksi
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
with col_btn1:
    if st.session_state["edit_mode"]:
        if st.button("💾 Simpan Perubahan", type="primary", use_container_width=True):
            if buyer and order_no and produk:
                st.session_state["data_produksi"].loc[st.session_state["edit_index"]] = {
                    "Buyer": buyer,
                    "Order No": order_no,
                    "Produk": produk,
                    "Jumlah": jumlah,
                    "Start Date": start_date,
                    "End Date": end_date,
                    "Lead Time (hari)": lead_time,
                    "Progress (%)": progres,
                    "Status": status
                }
                if save_data(st.session_state["data_produksi"]):
                    st.success("✅ Data berhasil diupdate!")
                    st.session_state["edit_mode"] = False
                    st.session_state["edit_index"] = None
                    st.rerun()
            else:
                st.warning("⚠️ Pastikan semua field wajib (*) terisi!")
    else:
        if st.button("➕ Tambah Data", type="primary", use_container_width=True):
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

            if buyer and order_no and produk:
                st.session_state["data_produksi"] = pd.concat(
                    [st.session_state["data_produksi"], new_data], ignore_index=True
                )
                if save_data(st.session_state["data_produksi"]):
                    st.success("✅ Data berhasil ditambahkan dan disimpan!")
                    st.rerun()
            else:
                st.warning("⚠️ Pastikan semua field wajib (*) terisi!")

with col_btn2:
    if st.session_state["edit_mode"]:
        if st.button("❌ Batal Edit", use_container_width=True):
            st.session_state["edit_mode"] = False
            st.session_state["edit_index"] = None
            st.rerun()

st.divider()

# ===== BAGIAN 2: TABEL DATA DENGAN AKSI =====
st.subheader("📊 Data Produksi Terkini")
df = st.session_state["data_produksi"]

if not df.empty:
    # Filter dan pencarian
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        search_buyer = st.text_input("🔍 Cari Buyer", "")
    with col_filter2:
        filter_status = st.multiselect("Filter Status", 
                                       ["On Time", "Delayed", "Pending"],
                                       default=["On Time", "Delayed", "Pending"])
    with col_filter3:
        sort_by = st.selectbox("Urutkan berdasarkan", 
                              ["Order No", "Start Date", "End Date", "Progress (%)", "Status"])
    
    # Terapkan filter
    df_filtered = df.copy()
    if search_buyer:
        df_filtered = df_filtered[df_filtered["Buyer"].str.contains(search_buyer, case=False, na=False)]
    if filter_status:
        df_filtered = df_filtered[df_filtered["Status"].isin(filter_status)]
    df_filtered = df_filtered.sort_values(by=sort_by)
    
    # Tampilkan tabel dengan aksi di setiap baris
    st.markdown("#### Daftar Order")
    
    # Header tabel
    col_headers = st.columns([0.5, 1.5, 1.5, 1.5, 1, 1.2, 1.2, 1, 1, 1, 1.2])
    headers = ["No", "Buyer", "Order No", "Produk", "Jumlah", "Start Date", "End Date", 
               "Lead Time", "Progress", "Status", "Aksi"]
    for col, header in zip(col_headers, headers):
        col.markdown(f"**{header}**")
    
    st.markdown("---")
    
    # Data rows dengan tombol aksi
    for idx, row in df_filtered.iterrows():
        cols = st.columns([0.5, 1.5, 1.5, 1.5, 1, 1.2, 1.2, 1, 1, 1, 1.2])
        
        cols[0].write(idx)
        cols[1].write(row["Buyer"])
        cols[2].write(row["Order No"])
        cols[3].write(row["Produk"])
        cols[4].write(row["Jumlah"])
        cols[5].write(str(row["Start Date"]))
        cols[6].write(str(row["End Date"]))
        cols[7].write(f"{row['Lead Time (hari)']} hari")
        cols[8].write(f"{row['Progress (%)']}%")
        
        # Status dengan warna
        status_color = {"On Time": "🟢", "Delayed": "🔴", "Pending": "🟡"}
        cols[9].write(f"{status_color.get(row['Status'], '')} {row['Status']}")
        
        # Tombol aksi di kolom paling kanan
        with cols[10]:
            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.button("✏️", key=f"edit_{idx}", help="Edit data ini"):
                    st.session_state["edit_mode"] = True
                    st.session_state["edit_index"] = idx
                    st.rerun()
            with col_delete:
                if st.button("🗑️", key=f"delete_{idx}", help="Hapus data ini", type="secondary"):
                    st.session_state["data_produksi"].drop(idx, inplace=True)
                    st.session_state["data_produksi"].reset_index(drop=True, inplace=True)
                    if save_data(st.session_state["data_produksi"]):
                        st.success(f"✅ Data order {row['Order No']} berhasil dihapus!")
                        st.rerun()
    
    st.markdown("---")
    
    # Hapus semua data (di bawah tabel)
    with st.expander("⚠️ Zona Bahaya - Hapus Semua Data"):
        st.warning("**PERHATIAN:** Tindakan ini akan menghapus SEMUA data produksi!")
        col_danger1, col_danger2 = st.columns([3, 1])
        with col_danger1:
            confirm_delete = st.checkbox("Saya yakin ingin menghapus SEMUA data")
        with col_danger2:
            if st.button("🗑️ Hapus Semua", type="secondary", disabled=not confirm_delete, use_container_width=True):
                st.session_state["data_produksi"] = pd.DataFrame(columns=[
                    "Buyer", "Order No", "Produk", "Jumlah", "Start Date", "End Date",
                    "Lead Time (hari)", "Progress (%)", "Status"
                ])
                if save_data(st.session_state["data_produksi"]):
                    st.success("✅ Semua data berhasil dihapus!")
                    st.rerun()

else:
    st.info("📝 Belum ada data yang dimasukkan. Mulai dengan menambahkan data produksi baru di atas.")

st.divider()

# ===== BAGIAN 3: ANALISIS RINGKAS =====
if not df.empty:
    st.subheader("📈 Dashboard Analisis Produksi")
    
    # Metrics
    total_order = len(df)
    avg_progress = df["Progress (%)"].mean()
    delayed = len(df[df["Status"] == "Delayed"])
    on_time = len(df[df["Status"] == "On Time"])
    pending = len(df[df["Status"] == "Pending"])
    total_qty = df["Jumlah"].sum()

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("📦 Total Order", total_order)
    col2.metric("📊 Rata-rata Progress", f"{avg_progress:.1f}%")
    col3.metric("✅ On Time", on_time)
    col4.metric("⚠️ Delayed", delayed)
    col5.metric("⏳ Pending", pending)
    col6.metric("🔢 Total Qty", f"{total_qty:,}")

    # Charts
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("**Progress per Produk**")
        st.bar_chart(df.set_index("Produk")["Progress (%)"])
    
    with col_chart2:
        st.markdown("**Distribusi Status**")
        status_count = df["Status"].value_counts()
        st.bar_chart(status_count)

st.divider()

# ===== BAGIAN 4: EXPORT DATA =====
if not df.empty:
    st.subheader("💾 Export Data")
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    
    with col_exp1:
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=f"ppic_data_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_exp2:
        excel_buffer = pd.ExcelWriter('temp.xlsx', engine='xlsxwriter')
        df.to_excel(excel_buffer, index=False, sheet_name='PPIC Data')
        excel_buffer.close()
        
        st.download_button(
            label="📊 Download Excel",
            data=open('temp.xlsx', 'rb').read(),
            file_name=f"ppic_data_{datetime.date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col_exp3:
        json_data = df.to_json(orient='records', indent=2)
        st.download_button(
            label="📋 Download JSON",
            data=json_data,
            file_name=f"ppic_data_{datetime.date.today()}.json",
            mime="application/json",
            use_container_width=True
        )

# Footer
st.divider()
st.caption("© 2025 Sistem PPIC-DSS | Dibangun dengan Streamlit | v3.0")
st.caption(f"💾 Data disimpan otomatis ke: {DATABASE_PATH}")
