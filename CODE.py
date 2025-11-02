import streamlit as st
import pandas as pd
import datetime
import json
import os

# ===== KONFIGURASI DATABASE =====
DATABASE_PATH = "ppic_data.json"

st.set_page_config(page_title="PPIC-DSS System", layout="wide", page_icon="🏭")

# ===== FUNGSI DATABASE =====
def load_data():
    """Memuat data dari file JSON"""
    if os.path.exists(DATABASE_PATH):
        try:
            with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                df = pd.DataFrame(data)
                if not df.empty:
                    df['Order Date'] = pd.to_datetime(df['Order Date']).dt.date
                    df['Due Date'] = pd.to_datetime(df['Due Date']).dt.date
                return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
    return pd.DataFrame(columns=[
        "Order ID", "Order Date", "Buyer", "Produk", "Qty", "Due Date", 
        "Prioritas", "Status", "Progress", "Proses Saat Ini", "Keterangan"
    ])

def save_data(df):
    """Menyimpan data ke file JSON"""
    try:
        df_copy = df.copy()
        df_copy['Order Date'] = df_copy['Order Date'].astype(str)
        df_copy['Due Date'] = df_copy['Due Date'].astype(str)
        with open(DATABASE_PATH, 'w', encoding='utf-8') as f:
            json.dump(df_copy.to_dict('records'), f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

# ===== INISIALISASI =====
if "data_produksi" not in st.session_state:
    st.session_state["data_produksi"] = load_data()
if "menu" not in st.session_state:
    st.session_state["menu"] = "Dashboard"
if "frozen_start" not in st.session_state:
    st.session_state["frozen_start"] = datetime.date(2025, 10, 27)
    st.session_state["frozen_end"] = datetime.date(2025, 11, 17)

# ===== SIDEBAR MENU =====
st.sidebar.title("🏭 PPIC-DSS MENU")
st.sidebar.markdown("---")

menu_options = {
    "📊 Dashboard": "Dashboard",
    "📋 Input Pesanan Baru": "Input",
    "📦 Daftar Order": "Orders",
    "⚙️ Update Progress": "Progress",
    "❄️ Frozen Zone": "Frozen",
    "📈 Analisis & Laporan": "Analytics"
}

for label, value in menu_options.items():
    if st.sidebar.button(label, use_container_width=True):
        st.session_state["menu"] = value

st.sidebar.markdown("---")
st.sidebar.info(f"📁 Database: `{os.path.basename(DATABASE_PATH)}`")

# ===== HEADER =====
st.title("🏭 Sistem PPIC Decision Support System")
st.caption("Production Planning & Inventory Control Management System v3.5")
st.markdown("---")

# ===== MENU: DASHBOARD =====
if st.session_state["menu"] == "Dashboard":
    st.header("📊 Dashboard Overview")
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        # Metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_orders = len(df)
        accepted = len(df[df["Status"] == "Accepted"])
        pending = len(df[df["Status"] == "Pending"])
        rejected = len(df[df["Status"] == "Rejected"])
        avg_progress = df["Progress"].str.rstrip('%').astype('float').mean()
        
        col1.metric("📦 Total Orders", total_orders)
        col2.metric("✅ Accepted", accepted, delta=f"{(accepted/total_orders*100):.0f}%")
        col3.metric("⏳ Pending", pending, delta=f"{(pending/total_orders*100):.0f}%")
        col4.metric("❌ Rejected", rejected, delta=f"-{(rejected/total_orders*100):.0f}%")
        col5.metric("📈 Avg Progress", f"{avg_progress:.1f}%")
        
        st.markdown("---")
        
        # Charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Status Distribution")
            status_count = df["Status"].value_counts()
            st.bar_chart(status_count)
        
        with col_chart2:
            st.subheader("Top 5 Products")
            product_count = df["Produk"].value_counts().head(5)
            st.bar_chart(product_count)
        
        # Recent Orders
        st.subheader("🕒 Recent Orders (Last 5)")
        recent_df = df.sort_values("Order Date", ascending=False).head(5)
        st.dataframe(recent_df[["Order ID", "Order Date", "Buyer", "Produk", "Qty", "Status", "Progress"]], 
                     use_container_width=True, hide_index=True)
    else:
        st.info("📝 Belum ada data. Silakan input pesanan baru.")

# ===== MENU: INPUT PESANAN BARU =====
elif st.session_state["menu"] == "Input":
    st.header("📋 INPUT PESANAN BARU")
    
    with st.container():
        st.markdown("""
        <div style='background-color: #1E3A8A; padding: 10px; border-radius: 5px; margin-bottom: 20px;'>
            <h3 style='color: white; text-align: center; margin: 0;'>INPUT PESANAN BARU</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("**ORDER DATE**")
            st.markdown("**BUYER NAME**")
            st.markdown("**PRODUK**")
            st.markdown("**JUMLAH**")
            st.markdown("**DUE DATE**")
            st.markdown("**PRIORITAS**")
        
        with col2:
            order_date = st.date_input("", datetime.date.today(), label_visibility="collapsed", key="input_order_date")
            
            # List buyer (bisa disesuaikan)
            buyers_list = ["Belhome", "Indomsk", "SDM", "WMG", "Remar", "ITM", "San Marco", "Olympic", "IKEA"]
            buyer = st.selectbox("", buyers_list, label_visibility="collapsed", key="input_buyer")
            
            produk = st.text_input("", placeholder="Masukkan nama produk", label_visibility="collapsed", key="input_produk")
            qty = st.number_input("", min_value=1, value=1, label_visibility="collapsed", key="input_qty")
            due_date = st.date_input("", datetime.date.today() + datetime.timedelta(days=30), label_visibility="collapsed", key="input_due")
            prioritas = st.selectbox("", ["High", "Medium", "Low"], label_visibility="collapsed", key="input_priority")
        
        st.markdown("")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            if st.button("🔍 CHECK CAPACITY", use_container_width=True, type="secondary"):
                st.info("✅ Kapasitas tersedia untuk produksi")
        
        with col_btn2:
            if st.button("📤 SUBMIT ORDER", use_container_width=True, type="primary"):
                if produk and buyer:
                    # Generate Order ID
                    existing_ids = st.session_state["data_produksi"]["Order ID"].tolist() if not st.session_state["data_produksi"].empty else []
                    new_id_num = max([int(oid.split("-")[1]) for oid in existing_ids if "-" in oid], default=2400) + 1
                    new_order_id = f"ORD-{new_id_num}"
                    
                    new_data = pd.DataFrame({
                        "Order ID": [new_order_id],
                        "Order Date": [order_date],
                        "Buyer": [buyer],
                        "Produk": [produk],
                        "Qty": [qty],
                        "Due Date": [due_date],
                        "Prioritas": [prioritas],
                        "Status": ["Pending"],
                        "Progress": ["0%"],
                        "Proses Saat Ini": ["Drafting"],
                        "Keterangan": [""]
                    })
                    
                    st.session_state["data_produksi"] = pd.concat(
                        [st.session_state["data_produksi"], new_data], ignore_index=True
                    )
                    
                    if save_data(st.session_state["data_produksi"]):
                        st.success(f"✅ Order {new_order_id} berhasil ditambahkan!")
                        st.balloons()
                else:
                    st.warning("⚠️ Harap lengkapi data produk dan buyer!")

# ===== MENU: DAFTAR ORDER =====
elif st.session_state["menu"] == "Orders":
    st.header("📦 DAFTAR ORDER")
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        # Filter
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filter_buyer = st.multiselect("Filter Buyer", df["Buyer"].unique())
        with col_f2:
            filter_status = st.multiselect("Filter Status", ["Accepted", "Pending", "Rejected"], default=["Accepted", "Pending", "Rejected"])
        with col_f3:
            search_order = st.text_input("🔍 Cari Order ID / Produk")
        
        # Apply filters
        df_filtered = df.copy()
        if filter_buyer:
            df_filtered = df_filtered[df_filtered["Buyer"].isin(filter_buyer)]
        if filter_status:
            df_filtered = df_filtered[df_filtered["Status"].isin(filter_status)]
        if search_order:
            df_filtered = df_filtered[
                df_filtered["Order ID"].str.contains(search_order, case=False, na=False) | 
                df_filtered["Produk"].str.contains(search_order, case=False, na=False)
            ]
        
        st.markdown("---")
        
        # Table with actions
        for idx, row in df_filtered.iterrows():
            with st.container():
                cols = st.columns([1, 1.2, 1, 1.5, 0.7, 1, 1, 1.2, 1.2, 0.8])
                
                cols[0].write(f"**{row['Order ID']}**")
                cols[1].write(row['Order Date'])
                cols[2].write(row['Buyer'])
                cols[3].write(row['Produk'])
                cols[4].write(row['Qty'])
                cols[5].write(row['Due Date'])
                
                # Status dengan warna
                status_colors = {
                    "Accepted": "🟢",
                    "Pending": "🟡",
                    "Rejected": "🔴"
                }
                cols[6].write(f"{status_colors.get(row['Status'], '')} {row['Status']}")
                
                cols[7].write(row['Progress'])
                cols[8].write(row['Proses Saat Ini'])
                
                # Action buttons
                with cols[9]:
                    col_edit, col_del = st.columns(2)
                    with col_edit:
                        if st.button("✏️", key=f"edit_order_{idx}"):
                            st.session_state["edit_order_idx"] = idx
                            st.session_state["menu"] = "Progress"
                            st.rerun()
                    with col_del:
                        if st.button("🗑️", key=f"del_order_{idx}"):
                            st.session_state["data_produksi"].drop(idx, inplace=True)
                            st.session_state["data_produksi"].reset_index(drop=True, inplace=True)
                            save_data(st.session_state["data_produksi"])
                            st.rerun()
                
                st.markdown("---")
    else:
        st.info("📝 Belum ada order yang diinput.")

# ===== MENU: UPDATE PROGRESS =====
elif st.session_state["menu"] == "Progress":
    st.header("⚙️ UPDATE PROGRESS PRODUKSI")
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        with st.container():
            st.markdown("""
            <div style='background-color: #1E3A8A; padding: 10px; border-radius: 5px; margin-bottom: 20px;'>
                <h3 style='color: white; text-align: center; margin: 0;'>UPDATE PROGRESS PRODUKSI</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Pilih order
            order_ids = df["Order ID"].tolist()
            selected_order = st.selectbox("Pilih Order ID", order_ids, key="progress_order_select")
            
            if selected_order:
                order_data = df[df["Order ID"] == selected_order].iloc[0]
                order_idx = df[df["Order ID"] == selected_order].index[0]
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown("**ORDER ID**")
                    st.markdown("**PRODUCT**")
                    st.markdown("**PROSES**")
                    st.markdown("**MULAI**")
                    st.markdown("**SELESAI**")
                    st.markdown("**PERSENTASE**")
                    st.markdown("**CATATAN**")
                
                with col2:
                    st.text_input("", value=order_data["Order ID"], disabled=True, label_visibility="collapsed", key="prog_order_id")
                    st.text_input("", value=order_data["Produk"], disabled=True, label_visibility="collapsed", key="prog_product")
                    
                    proses_list = ["Drafting", "Cutting", "Assembly", "Finishing", "Spray", "Packing", "Quality Check"]
                    current_proses = st.selectbox("", proses_list, 
                                                  index=proses_list.index(order_data["Proses Saat Ini"]) if order_data["Proses Saat Ini"] in proses_list else 0,
                                                  label_visibility="collapsed", key="prog_proses")
                    
                    start_date = st.date_input("", value=datetime.date.today(), label_visibility="collapsed", key="prog_start")
                    end_date = st.date_input("", value=datetime.date.today(), label_visibility="collapsed", key="prog_end")
                    
                    progress = st.slider("", 0, 100, int(order_data["Progress"].rstrip('%')), label_visibility="collapsed", key="prog_percentage")
                    st.write(f"**{progress}%**")
                    
                    notes = st.text_area("", value=order_data["Keterangan"], placeholder="Masukkan catatan...", 
                                        label_visibility="collapsed", key="prog_notes", height=80)
                
                st.markdown("")
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
                
                with col_btn1:
                    if st.button("🔄 CLEAR", use_container_width=True):
                        st.rerun()
                
                with col_btn2:
                    if st.button("💾 SAVE", use_container_width=True, type="primary"):
                        st.session_state["data_produksi"].at[order_idx, "Progress"] = f"{progress}%"
                        st.session_state["data_produksi"].at[order_idx, "Proses Saat Ini"] = current_proses
                        st.session_state["data_produksi"].at[order_idx, "Keterangan"] = notes
                        
                        # Auto update status based on progress
                        if progress == 100:
                            st.session_state["data_produksi"].at[order_idx, "Status"] = "Accepted"
                        elif progress > 0:
                            st.session_state["data_produksi"].at[order_idx, "Status"] = "Accepted"
                        
                        if save_data(st.session_state["data_produksi"]):
                            st.success(f"✅ Progress order {selected_order} berhasil diupdate!")
    else:
        st.info("📝 Belum ada order untuk diupdate.")

# ===== MENU: FROZEN ZONE =====
elif st.session_state["menu"] == "Frozen":
    st.header("❄️ FROZEN ZONE")
    
    st.markdown("""
    <div style='background-color: #1E3A8A; padding: 10px; border-radius: 5px; margin-bottom: 20px;'>
        <h3 style='color: white; text-align: center; margin: 0;'>❄️ FROZEN ZONE</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### START")
        frozen_start = st.date_input("", value=st.session_state["frozen_start"], label_visibility="collapsed", key="frozen_start_input")
    with col2:
        st.markdown("### UNTIL")
        frozen_end = st.date_input("", value=st.session_state["frozen_end"], label_visibility="collapsed", key="frozen_end_input")
    
    if st.button("💾 Set Frozen Period", type="primary"):
        st.session_state["frozen_start"] = frozen_start
        st.session_state["frozen_end"] = frozen_end
        st.success("✅ Frozen period berhasil diset!")
    
    st.markdown("---")
    st.subheader("📦 Order in Frozen Zone")
    
    df = st.session_state["data_produksi"]
    if not df.empty:
        # Filter orders dalam frozen zone
        df_frozen = df[
            (df["Due Date"] >= frozen_start) & 
            (df["Due Date"] <= frozen_end)
        ]
        
        if not df_frozen.empty:
            st.dataframe(df_frozen[["Order ID", "Produk", "Qty", "Due Date", "Status"]], 
                        use_container_width=True, hide_index=True)
            st.warning(f"⚠️ {len(df_frozen)} order berada dalam frozen zone!")
        else:
            st.info("✅ Tidak ada order dalam frozen zone.")
    else:
        st.info("📝 Belum ada data order.")

# ===== MENU: ANALYTICS =====
elif st.session_state["menu"] == "Analytics":
    st.header("📈 ANALISIS & LAPORAN")
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "👥 By Buyer", "📦 By Product"])
        
        with tab1:
            st.subheader("Performance Overview")
            col1, col2, col3 = st.columns(3)
            
            total_qty = df["Qty"].sum()
            on_time_orders = len(df[df["Due Date"] >= datetime.date.today()])
            completion_rate = (df["Progress"].str.rstrip('%').astype('float').mean())
            
            col1.metric("Total Quantity", f"{total_qty:,} pcs")
            col2.metric("On-Time Orders", on_time_orders)
            col3.metric("Avg Completion", f"{completion_rate:.1f}%")
        
        with tab2:
            st.subheader("Analysis by Buyer")
            buyer_stats = df.groupby("Buyer").agg({
                "Order ID": "count",
                "Qty": "sum"
            }).rename(columns={"Order ID": "Total Orders", "Qty": "Total Qty"})
            
            st.dataframe(buyer_stats, use_container_width=True)
            st.bar_chart(buyer_stats["Total Orders"])
        
        with tab3:
            st.subheader("Analysis by Product")
            product_stats = df.groupby("Produk").agg({
                "Order ID": "count",
                "Qty": "sum"
            }).rename(columns={"Order ID": "Total Orders", "Qty": "Total Qty"})
            
            st.dataframe(product_stats, use_container_width=True)
            st.bar_chart(product_stats["Total Qty"])
        
        # Export
        st.markdown("---")
        st.subheader("💾 Export Laporan")
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"ppic_report_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_exp2:
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="📋 Download JSON",
                data=json_data,
                file_name=f"ppic_report_{datetime.date.today()}.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.info("📝 Belum ada data untuk dianalisis.")

# Footer
st.markdown("---")
st.caption(f"© 2025 PPIC-DSS System | v3.5 | 💾 Data: {DATABASE_PATH}")
