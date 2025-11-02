import streamlit as st
import pandas as pd
import datetime
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ===== KONFIGURASI DATABASE =====
DATABASE_PATH = "ppic_data.json"

st.set_page_config(page_title="PPIC-DSS System", layout="wide", page_icon="🏭")

# ===== DEFINISI PROSES PRODUKSI =====
PRODUCTION_STAGES = [
    "Pre-Order", "Order di Supplier", "Warehouse", "Fitting 1", 
    "Amplas", "Revisi 1", "Spray", "Fitting 2", "Revisi Fitting 2", 
    "Packaging", "Pengiriman"
]

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
                    # Konversi progress tracking
                    for stage in PRODUCTION_STAGES:
                        if stage in df.columns:
                            df[stage] = pd.to_datetime(df[stage], errors='coerce')
                return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
    
    # Return empty dataframe dengan struktur lengkap
    columns = [
        "Order ID", "Order Date", "Buyer", "Produk", "Qty", "Due Date", 
        "Prioritas", "Status", "Progress", "Proses Saat Ini", "Keterangan"
    ] + PRODUCTION_STAGES
    
    return pd.DataFrame(columns=columns)

def save_data(df):
    """Menyimpan data ke file JSON"""
    try:
        df_copy = df.copy()
        df_copy['Order Date'] = df_copy['Order Date'].astype(str)
        df_copy['Due Date'] = df_copy['Due Date'].astype(str)
        # Konversi datetime ke string untuk progress tracking
        for stage in PRODUCTION_STAGES:
            if stage in df_copy.columns:
                df_copy[stage] = df_copy[stage].astype(str)
        
        with open(DATABASE_PATH, 'w', encoding='utf-8') as f:
            json.dump(df_copy.to_dict('records'), f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

# ===== FUNGSI GANTT CHART =====
def create_gantt_chart(df):
    """Membuat Gantt Chart dari data produksi"""
    if df.empty:
        return None
    
    gantt_data = []
    for _, order in df.iterrows():
        for i, stage in enumerate(PRODUCTION_STAGES):
            if pd.notna(order.get(stage)) and order[stage] != 'NaT':
                gantt_data.append({
                    'Task': order['Order ID'],
                    'Start': order[stage],
                    'Finish': order[stage] + timedelta(days=1),
                    'Stage': stage,
                    'Product': order['Produk'],
                    'Buyer': order['Buyer']
                })
    
    if not gantt_data:
        return None
    
    gantt_df = pd.DataFrame(gantt_data)
    fig = px.timeline(gantt_df, x_start="Start", x_end="Finish", y="Task", 
                     color="Stage", title="Gantt Chart Progress Produksi",
                     hover_data=["Product", "Buyer"])
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(height=400)
    return fig

def create_progress_chart(df):
    """Membuat chart progress produksi"""
    if df.empty:
        return None
    
    progress_data = []
    for _, order in df.iterrows():
        completed_stages = sum(1 for stage in PRODUCTION_STAGES 
                             if pd.notna(order.get(stage)) and order[stage] != 'NaT')
        total_stages = len(PRODUCTION_STAGES)
        progress_percent = (completed_stages / total_stages) * 100
        
        progress_data.append({
            'Order ID': order['Order ID'],
            'Progress': progress_percent,
            'Buyer': order['Buyer'],
            'Product': order['Produk']
        })
    
    progress_df = pd.DataFrame(progress_data)
    fig = px.bar(progress_df, x='Order ID', y='Progress', 
                title='Progress Produksi per Order',
                hover_data=['Buyer', 'Product'],
                color='Progress',
                color_continuous_scale='Viridis')
    fig.update_layout(height=400)
    return fig

# ===== INISIALISASI =====
if "data_produksi" not in st.session_state:
    st.session_state["data_produksi"] = load_data()
if "menu" not in st.session_state:
    st.session_state["menu"] = "Dashboard"
if "frozen_start" not in st.session_state:
    st.session_state["frozen_start"] = datetime.date(2025, 10, 27)
    st.session_state["frozen_end"] = datetime.date(2025, 11, 17)
if "previous_menu" not in st.session_state:
    st.session_state["previous_menu"] = "Dashboard"

# ===== SIDEBAR MENU =====
st.sidebar.title("🏭 PPIC-DSS MENU")
st.sidebar.markdown("---")

menu_options = {
    "📊 Dashboard": "Dashboard",
    "📋 Input Pesanan Baru": "Input",
    "📦 Daftar Order": "Orders",
    "⚙️ Update Progress": "Progress",
    "📍 Production Tracking": "Tracking",
    "📈 Gantt Chart": "GanttChart",
    "❄️ Frozen Zone": "Frozen",
    "📊 Analisis & Laporan": "Analytics"
}

for label, value in menu_options.items():
    if st.sidebar.button(label, use_container_width=True):
        st.session_state["previous_menu"] = st.session_state["menu"]
        st.session_state["menu"] = value

st.sidebar.markdown("---")
st.sidebar.info(f"📁 Database: `{os.path.basename(DATABASE_PATH)}`")

# ===== HEADER =====
st.title("🏭 Sistem PPIC Decision Support System")
st.caption("Production Planning & Inventory Control Management System v4.0")
st.markdown("---")

# ===== FUNGSI TOMBOL BACK =====
def back_button():
    """Tombol untuk kembali ke menu sebelumnya"""
    if st.button("← Kembali", use_container_width=False):
        st.session_state["menu"] = st.session_state["previous_menu"]
        st.session_state["previous_menu"] = st.session_state["menu"]
        st.rerun()

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
        
        # Hitung progress rata-rata
        progress_values = []
        for _, order in df.iterrows():
            completed_stages = sum(1 for stage in PRODUCTION_STAGES 
                                 if pd.notna(order.get(stage)) and order[stage] != 'NaT')
            progress_percent = (completed_stages / len(PRODUCTION_STAGES)) * 100
            progress_values.append(progress_percent)
        
        avg_progress = sum(progress_values) / len(progress_values) if progress_values else 0
        
        col1.metric("📦 Total Orders", total_orders)
        col2.metric("✅ Accepted", accepted, delta=f"{(accepted/total_orders*100):.0f}%" if total_orders > 0 else "0%")
        col3.metric("⏳ Pending", pending, delta=f"{(pending/total_orders*100):.0f}%" if total_orders > 0 else "0%")
        col4.metric("❌ Rejected", rejected, delta=f"-{(rejected/total_orders*100):.0f}%" if total_orders > 0 else "0%")
        col5.metric("📈 Avg Progress", f"{avg_progress:.1f}%")
        
        st.markdown("---")
        
        # Charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Status Distribution")
            status_count = df["Status"].value_counts()
            fig_status = px.pie(values=status_count.values, names=status_count.index, 
                               title="Distribusi Status Order")
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col_chart2:
            st.subheader("Top 5 Products")
            product_count = df["Produk"].value_counts().head(5)
            fig_product = px.bar(x=product_count.values, y=product_count.index, 
                               orientation='h', title="Top 5 Produk",
                               labels={'x': 'Jumlah Order', 'y': 'Produk'})
            st.plotly_chart(fig_product, use_container_width=True)
        
        # Recent Orders
        st.subheader("🕒 Recent Orders (Last 5)")
        recent_df = df.sort_values("Order Date", ascending=False).head(5)
        st.dataframe(recent_df[["Order ID", "Order Date", "Buyer", "Produk", "Qty", "Status"]], 
                     use_container_width=True, hide_index=True)
    else:
        st.info("📝 Belum ada data. Silakan input pesanan baru.")

# ===== MENU: INPUT PESANAN BARU =====
elif st.session_state["menu"] == "Input":
    st.header("📋 INPUT PESANAN BARU")
    back_button()
    
    with st.container():
        st.markdown("""
        <div style='background-color: #1E3A8A; padding: 10px; border-radius: 5px; margin-bottom: 20px;'>
            <h3 style='color: white; text-align: center; margin: 0;'>INPUT PESANAN BARU</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Layout dengan form yang lebih rapi
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("**ORDER DATE**")
            st.markdown("**BUYER NAME**")
            st.markdown("**PRODUK**")
            st.markdown("**JUMLAH (Qty)**")
            st.markdown("**DUE DATE**")
            st.markdown("**PRIORITAS**")
        
        with col2:
            order_date = st.date_input("Order Date", datetime.date.today(), label_visibility="collapsed", key="input_order_date")
            
            buyers_list = ["Belhome", "Indomsk", "SDM", "WMG", "Remar", "ITM", "San Marco", "Olympic", "IKEA"]
            buyer = st.selectbox("Buyer", buyers_list, label_visibility="collapsed", key="input_buyer")
            
            produk = st.text_input("Produk", placeholder="Masukkan nama produk", label_visibility="collapsed", key="input_produk")
            qty = st.number_input("Quantity", min_value=1, value=1, label_visibility="collapsed", key="input_qty")
            due_date = st.date_input("Due Date", datetime.date.today() + datetime.timedelta(days=30), label_visibility="collapsed", key="input_due")
            prioritas = st.selectbox("Prioritas", ["High", "Medium", "Low"], label_visibility="collapsed", key="input_priority")
        
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
                    new_id_num = 2400
                    if existing_ids:
                        numeric_ids = []
                        for oid in existing_ids:
                            try:
                                if "-" in oid:
                                    numeric_ids.append(int(oid.split("-")[1]))
                            except ValueError:
                                continue
                        if numeric_ids:
                            new_id_num = max(numeric_ids) + 1
                    
                    new_order_id = f"ORD-{new_id_num}"
                    
                    # Buat data baru dengan semua stage production
                    new_data = {
                        "Order ID": new_order_id,
                        "Order Date": order_date,
                        "Buyer": buyer,
                        "Produk": produk,
                        "Qty": qty,
                        "Due Date": due_date,
                        "Prioritas": prioritas,
                        "Status": "Pending",
                        "Progress": "0%",
                        "Proses Saat Ini": "Pre-Order",
                        "Keterangan": ""
                    }
                    
                    # Tambahkan kolom untuk setiap stage production
                    for stage in PRODUCTION_STAGES:
                        new_data[stage] = None
                    
                    new_df = pd.DataFrame([new_data])
                    
                    st.session_state["data_produksi"] = pd.concat(
                        [st.session_state["data_produksi"], new_df], ignore_index=True
                    )
                    
                    if save_data(st.session_state["data_produksi"]):
                        st.success(f"✅ Order {new_order_id} berhasil ditambahkan!")
                        st.balloons()
                else:
                    st.warning("⚠️ Harap lengkapi data produk dan buyer!")

# ===== MENU: DAFTAR ORDER =====
elif st.session_state["menu"] == "Orders":
    st.header("📦 DAFTAR ORDER")
    back_button()
    
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
        
        # Tampilkan data dalam tabel dengan styling yang lebih baik
        display_columns = ["Order ID", "Order Date", "Buyer", "Produk", "Qty", "Due Date", "Status", "Progress", "Proses Saat Ini"]
        st.dataframe(
            df_filtered[display_columns],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Order ID": st.column_config.TextColumn("Order ID", width="small"),
                "Order Date": st.column_config.DateColumn("Order Date"),
                "Buyer": st.column_config.TextColumn("Buyer"),
                "Produk": st.column_config.TextColumn("Produk"),
                "Qty": st.column_config.NumberColumn("Qty"),
                "Due Date": st.column_config.DateColumn("Due Date"),
                "Status": st.column_config.TextColumn("Status"),
                "Progress": st.column_config.TextColumn("Progress"),
                "Proses Saat Ini": st.column_config.TextColumn("Proses Saat Ini")
            }
        )
        
        # Actions untuk setiap order
        st.subheader("🛠️ Order Actions")
        selected_order_id = st.selectbox("Pilih Order untuk Action:", df_filtered["Order ID"].tolist())
        
        if selected_order_id:
            order_idx = df[df["Order ID"] == selected_order_id].index[0]
            col_act1, col_act2, col_act3 = st.columns(3)
            
            with col_act1:
                if st.button("✏️ Edit Order", use_container_width=True):
                    st.session_state["edit_order_idx"] = order_idx
                    st.session_state["previous_menu"] = "Orders"
                    st.session_state["menu"] = "Progress"
                    st.rerun()
            
            with col_act2:
                if st.button("📍 Tracking", use_container_width=True):
                    st.session_state["track_order_id"] = selected_order_id
                    st.session_state["previous_menu"] = "Orders"
                    st.session_state["menu"] = "Tracking"
                    st.rerun()
            
            with col_act3:
                if st.button("🗑️ Hapus Order", use_container_width=True, type="secondary"):
                    st.session_state["data_produksi"].drop(order_idx, inplace=True)
                    st.session_state["data_produksi"].reset_index(drop=True, inplace=True)
                    save_data(st.session_state["data_produksi"])
                    st.success(f"✅ Order {selected_order_id} berhasil dihapus!")
                    st.rerun()
    else:
        st.info("📝 Belum ada order yang diinput.")

# ===== MENU: UPDATE PROGRESS =====
elif st.session_state["menu"] == "Progress":
    st.header("⚙️ UPDATE PROGRESS PRODUKSI")
    back_button()
    
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
                
                # Layout yang lebih rapi
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown("**ORDER ID**")
                    st.markdown("**PRODUK**")
                    st.markdown("**PROSES SAAT INI**")
                    st.markdown("**TANGGAL MULAI**")
                    st.markdown("**TANGGAL SELESAI**")
                    st.markdown("**PERSENTASE PROGRESS**")
                    st.markdown("**CATATAN**")
                
                with col2:
                    # Order ID dan Produk tidak bisa diubah
                    st.text_input("Order ID", value=order_data["Order ID"], disabled=True, label_visibility="collapsed", key="prog_order_id")
                    st.text_input("Produk", value=order_data["Produk"], disabled=True, label_visibility="collapsed", key="prog_product")
                    
                    current_proses = st.selectbox("Proses Saat Ini", PRODUCTION_STAGES, 
                                                  index=PRODUCTION_STAGES.index(order_data["Proses Saat Ini"]) if order_data["Proses Saat Ini"] in PRODUCTION_STAGES else 0,
                                                  label_visibility="collapsed", key="prog_proses")
                    
                    start_date = st.date_input("Tanggal Mulai", value=datetime.date.today(), label_visibility="collapsed", key="prog_start")
                    end_date = st.date_input("Tanggal Selesai", value=datetime.date.today(), label_visibility="collapsed", key="prog_end")
                    
                    progress = st.slider("Progress", 0, 100, 
                                        int(order_data["Progress"].rstrip('%')) if '%' in str(order_data["Progress"]) else 0, 
                                        label_visibility="collapsed", key="prog_percentage")
                    st.write(f"**Progress: {progress}%**")
                    
                    notes = st.text_area("Catatan", value=order_data["Keterangan"], placeholder="Masukkan catatan produksi...", 
                                        label_visibility="collapsed", key="prog_notes", height=100)
                
                st.markdown("")
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
                
                with col_btn1:
                    if st.button("🔄 Reset Form", use_container_width=True):
                        st.rerun()
                
                with col_btn2:
                    if st.button("💾 Simpan Perubahan", use_container_width=True, type="primary"):
                        st.session_state["data_produksi"].at[order_idx, "Progress"] = f"{progress}%"
                        st.session_state["data_produksi"].at[order_idx, "Proses Saat Ini"] = current_proses
                        st.session_state["data_produksi"].at[order_idx, "Keterangan"] = notes
                        
                        # Update tanggal untuk stage yang aktif
                        if current_proses in PRODUCTION_STAGES:
                            st.session_state["data_produksi"].at[order_idx, current_proses] = datetime.datetime.now()
                        
                        # Auto update status based on progress
                        if progress == 100:
                            st.session_state["data_produksi"].at[order_idx, "Status"] = "Completed"
                        elif progress > 0:
                            st.session_state["data_produksi"].at[order_idx, "Status"] = "In Progress"
                        
                        if save_data(st.session_state["data_produksi"]):
                            st.success(f"✅ Progress order {selected_order} berhasil diupdate!")
    else:
        st.info("📝 Belum ada order untuk diupdate.")

# ===== MENU: PRODUCTION TRACKING =====
elif st.session_state["menu"] == "Tracking":
    st.header("📍 PRODUCTION TRACKING")
    back_button()
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        # Pilih order untuk tracking
        order_ids = df["Order ID"].tolist()
        selected_order_id = st.selectbox("Pilih Order untuk Tracking:", order_ids, 
                                       key="tracking_order_select")
        
        if selected_order_id:
            order_data = df[df["Order ID"] == selected_order_id].iloc[0]
            
            st.subheader(f"Tracking Order: {selected_order_id}")
            st.write(f"**Produk:** {order_data['Produk']} | **Buyer:** {order_data['Buyer']} | **Qty:** {order_data['Qty']}")
            
            # Progress tracking timeline
            st.markdown("### 📋 Timeline Produksi")
            
            completed_stages = 0
            for i, stage in enumerate(PRODUCTION_STAGES):
                col1, col2, col3 = st.columns([1, 3, 2])
                
                with col1:
                    # Status indicator
                    if pd.notna(order_data.get(stage)) and order_data[stage] != 'NaT':
                        st.success("✅")
                        completed_stages += 1
                    else:
                        st.info("⏳")
                
                with col2:
                    st.write(f"**{stage}**")
                
                with col3:
                    if pd.notna(order_data.get(stage)) and order_data[stage] != 'NaT':
                        st.write(f"Completed: {order_data[stage]}")
                    else:
                        st.write("Pending")
            
            # Progress bar
            total_stages = len(PRODUCTION_STAGES)
            progress_percent = (completed_stages / total_stages) * 100
            
            st.markdown("### 📊 Overall Progress")
            st.progress(progress_percent / 100)
            st.write(f"**{completed_stages}/{total_stages} stages completed ({progress_percent:.1f}%)**")
            
            # Update stage progress
            st.markdown("### 🛠️ Update Stage Progress")
            current_stage = st.selectbox("Pilih Stage untuk Update:", PRODUCTION_STAGES)
            update_date = st.date_input("Tanggal Penyelesaian:", datetime.date.today())
            
            if st.button("✅ Tandai Stage Selesai", type="primary"):
                order_idx = df[df["Order ID"] == selected_order_id].index[0]
                st.session_state["data_produksi"].at[order_idx, current_stage] = datetime.datetime.combine(update_date, datetime.time())
                st.session_state["data_produksi"].at[order_idx, "Proses Saat Ini"] = current_stage
                
                # Update progress percentage
                new_completed = sum(1 for stage in PRODUCTION_STAGES 
                                  if pd.notna(st.session_state["data_produksi"].at[order_idx, stage]) and 
                                  st.session_state["data_produksi"].at[order_idx, stage] != 'NaT')
                new_progress = (new_completed / total_stages) * 100
                st.session_state["data_produksi"].at[order_idx, "Progress"] = f"{new_progress:.0f}%"
                
                if save_data(st.session_state["data_produksi"]):
                    st.success(f"✅ Stage {current_stage} berhasil ditandai selesai!")
                    st.rerun()
    else:
        st.info("📝 Belum ada order untuk ditracking.")

# ===== MENU: GANTT CHART =====
elif st.session_state["menu"] == "GanttChart":
    st.header("📈 GANTT CHART PRODUKSI")
    back_button()
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        # Filter untuk order yang memiliki progress
        has_progress = []
        for _, order in df.iterrows():
            if any(pd.notna(order.get(stage)) and order[stage] != 'NaT' for stage in PRODUCTION_STAGES):
                has_progress.append(True)
            else:
                has_progress.append(False)
        
        df_with_progress = df[has_progress]
        
        if not df_with_progress.empty:
            tab1, tab2 = st.tabs(["Gantt Chart", "Progress Chart"])
            
            with tab1:
                st.subheader("Gantt Chart Timeline Produksi")
                gantt_fig = create_gantt_chart(df_with_progress)
                if gantt_fig:
                    st.plotly_chart(gantt_fig, use_container_width=True)
                else:
                    st.info("📊 Tidak ada data timeline yang dapat ditampilkan dalam Gantt Chart.")
            
            with tab2:
                st.subheader("Progress Chart")
                progress_fig = create_progress_chart(df_with_progress)
                if progress_fig:
                    st.plotly_chart(progress_fig, use_container_width=True)
                else:
                    st.info("📈 Tidak ada data progress yang dapat ditampilkan.")
        else:
            st.info("📝 Belum ada data progress produksi untuk ditampilkan dalam chart.")
    else:
        st.info("📝 Belum ada data order.")

# ===== MENU: FROZEN ZONE =====
elif st.session_state["menu"] == "Frozen":
    st.header("❄️ FROZEN ZONE")
    back_button()
    
    st.markdown("""
    <div style='background-color: #1E3A8A; padding: 10px; border-radius: 5px; margin-bottom: 20px;'>
        <h3 style='color: white; text-align: center; margin: 0;'>❄️ FROZEN ZONE</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### START")
        frozen_start = st.date_input("Tanggal Mulai", value=st.session_state["frozen_start"], label_visibility="collapsed", key="frozen_start_input")
    with col2:
        st.markdown("### UNTIL")
        frozen_end = st.date_input("Tanggal Akhir", value=st.session_state["frozen_end"], label_visibility="collapsed", key="frozen_end_input")
    
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
            st.dataframe(df_frozen[["Order ID", "Produk", "Qty", "Due Date", "Status", "Proses Saat Ini"]], 
                        use_container_width=True, hide_index=True)
            
            # Summary
            col_sum1, col_sum2, col_sum3 = st.columns(3)
            with col_sum1:
                st.metric("Total Order Frozen", len(df_frozen))
            with col_sum2:
                total_qty_frozen = df_frozen["Qty"].sum()
                st.metric("Total Quantity", f"{total_qty_frozen:,} pcs")
            with col_sum3:
                high_priority = len(df_frozen[df_frozen["Prioritas"] == "High"])
                st.metric("High Priority", high_priority)
            
            st.warning(f"⚠️ {len(df_frozen)} order berada dalam frozen zone ({frozen_start} hingga {frozen_end})!")
        else:
            st.info("✅ Tidak ada order dalam frozen zone.")
    else:
        st.info("📝 Belum ada data order.")

# ===== MENU: ANALYTICS =====
elif st.session_state["menu"] == "Analytics":
    st.header("📊 ANALISIS & LAPORAN")
    back_button()
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 By Buyer", "📦 By Product", "🚀 Performance"])
        
        with tab1:
            st.subheader("Performance Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            total_qty = df["Qty"].sum()
            on_time_orders = len(df[df["Due Date"] >= datetime.date.today()])
            
            # Hitung completion rate berdasarkan stage production
            completion_rates = []
            for _, order in df.iterrows():
                completed_stages = sum(1 for stage in PRODUCTION_STAGES 
                                     if pd.notna(order.get(stage)) and order[stage] != 'NaT')
                completion_rate = (completed_stages / len(PRODUCTION_STAGES)) * 100
                completion_rates.append(completion_rate)
            
            avg_completion = sum(completion_rates) / len(completion_rates) if completion_rates else 0
            delayed_orders = len(df[df["Due Date"] < datetime.date.today()])
            
            col1.metric("Total Quantity", f"{total_qty:,} pcs")
            col2.metric("On-Time Orders", on_time_orders)
            col3.metric("Avg Completion", f"{avg_completion:.1f}%")
            col4.metric("Delayed Orders", delayed_orders, delta=f"-{delayed_orders}" if delayed_orders > 0 else "0")
        
        with tab2:
            st.subheader("Analysis by Buyer")
            buyer_stats = df.groupby("Buyer").agg({
                "Order ID": "count",
                "Qty": "sum",
                "Prioritas": lambda x: (x == "High").sum()
            }).rename(columns={
                "Order ID": "Total Orders", 
                "Qty": "Total Qty",
                "Prioritas": "High Priority Orders"
            })
            
            st.dataframe(buyer_stats, use_container_width=True)
            
            fig_buyer = px.bar(buyer_stats, x=buyer_stats.index, y="Total Orders",
                              title="Total Orders per Buyer",
                              color="Total Orders")
            st.plotly_chart(fig_buyer, use_container_width=True)
        
        with tab3:
            st.subheader("Analysis by Product")
            product_stats = df.groupby("Produk").agg({
                "Order ID": "count",
                "Qty": "sum"
            }).rename(columns={"Order ID": "Total Orders", "Qty": "Total Qty"})
            
            st.dataframe(product_stats, use_container_width=True)
            
            fig_product = px.pie(product_stats, values="Total Qty", names=product_stats.index,
                                title="Distribusi Quantity per Produk")
            st.plotly_chart(fig_product, use_container_width=True)
        
        with tab4:
            st.subheader("Production Performance")
            
            # Stage completion analysis
            stage_completion = {}
            for stage in PRODUCTION_STAGES:
                completed = sum(1 for _, order in df.iterrows() 
                              if pd.notna(order.get(stage)) and order[stage] != 'NaT')
                stage_completion[stage] = completed
            
            stage_df = pd.DataFrame({
                'Stage': list(stage_completion.keys()),
                'Completed': list(stage_completion.values()),
                'Completion Rate': [f"{(count/len(df)*100):.1f}%" for count in stage_completion.values()]
            })
            
            st.dataframe(stage_df, use_container_width=True, hide_index=True)
            
            fig_stage = px.bar(stage_df, x='Stage', y='Completed', 
                              title='Stage Completion Analysis',
                              color='Completed')
            fig_stage.update_xaxes(tickangle=45)
            st.plotly_chart(fig_stage, use_container_width=True)
        
        # Export
        st.markdown("---")
        st.subheader("💾 Export Laporan")
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        
        with col_exp1:
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📄 Download CSV Report",
                data=csv_data,
                file_name=f"ppic_report_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_exp2:
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="📋 Download JSON Report",
                data=json_data,
                file_name=f"ppic_report_{datetime.date.today()}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col_exp3:
            # Buat summary report
            summary_report = f"""
            PPIC PRODUCTION REPORT
            Generated: {datetime.date.today()}
            
            SUMMARY:
            - Total Orders: {len(df)}
            - Total Quantity: {total_qty:,} pcs
            - Average Completion: {avg_completion:.1f}%
            - On-Time Orders: {on_time_orders}
            - Delayed Orders: {delayed_orders}
            
            STAGE COMPLETION:
            {chr(10).join([f'- {stage}: {stage_df[stage_df["Stage"] == stage]["Completion Rate"].iloc[0]}' for stage in PRODUCTION_STAGES])}
            """
            
            st.download_button(
                label="📝 Download Summary Report",
                data=summary_report,
                file_name=f"ppic_summary_{datetime.date.today()}.txt",
                mime="text/plain",
                use_container_width=True
            )
    else:
        st.info("📝 Belum ada data untuk dianalisis.")

# Footer
st.markdown("---")
st.caption(f"© 2025 PPIC-DSS System | v4.0 | 💾 Data: {DATABASE_PATH} | 🏭 Production Stages: {len(PRODUCTION_STAGES)}")
