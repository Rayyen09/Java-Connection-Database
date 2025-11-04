import streamlit as st
import pandas as pd
import datetime
import json
import os
import plotly.express as px
import plotly.figure_factory as ff

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
        "Prioritas", "Status", "Progress", "Proses Saat Ini", "Keterangan",
        "Tracking"
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

def get_tracking_stages():
    """Daftar tahapan tracking produksi"""
    return [
        "Pre Order",
        "Order di Supplier",
        "Warehouse",
        "Fitting 1",
        "Amplas",
        "Revisi 1",
        "Spray",
        "Fitting 2",
        "Revisi Fitting 2",
        "Packaging",
        "Pengiriman"
    ]

def init_tracking_data(order_id):
    """Inisialisasi data tracking untuk order baru"""
    stages = get_tracking_stages()
    return {stage: {"status": "Pending", "date": None} for stage in stages}

def get_tracking_status_from_progress(progress_str, order_status):
    """Menentukan tracking status berdasarkan progress dan order status"""
    try:
        progress_pct = int(progress_str.rstrip('%')) if progress_str else 0
    except:
        progress_pct = 0
    
    # Jika order Rejected, tracking tetap Pending
    if order_status == "Rejected":
        return "Pending"
    # Jika progress 100%, Done
    elif progress_pct == 100:
        return "Done"
    # Jika progress 0%, Pending
    elif progress_pct == 0:
        return "Pending"
    # Jika progress 1-99%, On Going
    else:
        return "On Going"

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
    "🔍 Tracking Produksi": "Tracking",
    "❄️ Frozen Zone": "Frozen",
    "📈 Analisis & Laporan": "Analytics",
    "📊 Gantt Chart": "Gantt"
}

for label, value in menu_options.items():
    if st.sidebar.button(label, use_container_width=True):
        st.session_state["menu"] = value

st.sidebar.markdown("---")
st.sidebar.info(f"📁 Database: `{os.path.basename(DATABASE_PATH)}`")

# ===== HEADER =====
st.title("🏭 Sistem PPIC Decision Support System")
st.caption("Production Planning & Inventory Control Management System v4.0")
st.markdown("---")

# ===== BACK BUTTON (untuk semua menu kecuali Dashboard) =====
if st.session_state["menu"] != "Dashboard":
    # Back button khusus untuk Update Progress
    if st.session_state["menu"] == "Progress":
        col_back1, col_back2, col_back3 = st.columns([1.2, 1.2, 3.6])
        with col_back1:
            if st.button("⬅️ Back to Dashboard", type="secondary", use_container_width=True):
                st.session_state["menu"] = "Dashboard"
                st.rerun()
        with col_back2:
            if st.button("📦 Back to Orders", type="secondary", use_container_width=True):
                st.session_state["menu"] = "Orders"
                st.rerun()
    else:
        if st.button("⬅️ Back to Dashboard", type="secondary"):
            st.session_state["menu"] = "Dashboard"
            st.rerun()
    st.markdown("---")

# ===== MENU: DASHBOARD =====
if st.session_state["menu"] == "Dashboard":
    st.header("📊 Dashboard Overview")
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        # Add tracking status column
        df['Tracking Status'] = df.apply(lambda row: get_tracking_status_from_progress(row['Progress'], row['Status']), axis=1)
        
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
        
        # Tracking Status Metrics
        st.subheader("🔍 Tracking Status Overview")
        track_col1, track_col2, track_col3 = st.columns(3)
        
        track_pending = len(df[df['Tracking Status'] == 'Pending'])
        track_ongoing = len(df[df['Tracking Status'] == 'On Going'])
        track_done = len(df[df['Tracking Status'] == 'Done'])
        
        track_col1.metric("⏳ Pending", track_pending, delta=f"{(track_pending/total_orders*100):.0f}%")
        track_col2.metric("🔄 On Going", track_ongoing, delta=f"{(track_ongoing/total_orders*100):.0f}%")
        track_col3.metric("✅ Done", track_done, delta=f"{(track_done/total_orders*100):.0f}%")
        
        st.markdown("---")
        
        # Charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Status Distribution")
            status_count = df["Status"].value_counts()
            fig1 = px.pie(values=status_count.values, names=status_count.index, 
                         title="Status Orders", color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col_chart2:
            st.subheader("Tracking Status Distribution")
            tracking_count = df["Tracking Status"].value_counts()
            fig2 = px.pie(values=tracking_count.values, names=tracking_count.index, 
                         title="Tracking Status", color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Recent Orders
        st.subheader("🕒 Recent Orders (Last 10)")
        recent_df = df.sort_values("Order Date", ascending=False).head(10)
        st.dataframe(recent_df[["Order ID", "Order Date", "Buyer", "Produk", "Qty", "Status", "Progress", "Proses Saat Ini", "Tracking Status"]], 
                     use_container_width=True, hide_index=True)
    else:
        st.info("📝 Belum ada data. Silakan input pesanan baru.")

# ===== MENU: INPUT PESANAN BARU =====
elif st.session_state["menu"] == "Input":
    st.header("📋 INPUT PESANAN BARU")
    
    with st.container():
        st.markdown("""
        <div style='background-color: #1E3A8A; padding: 15px; border-radius: 8px; margin-bottom: 25px;'>
            <h3 style='color: white; text-align: center; margin: 0;'>FORM INPUT PESANAN BARU</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Custom CSS untuk alignment yang sempurna
        st.markdown("""
        <style>
        .label-row {
            display: flex;
            align-items: center;
            height: 38px;
            margin-bottom: 18px;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown("<div class='label-row'>Order Date</div>", unsafe_allow_html=True)
            st.markdown("<div class='label-row'>Buyer Name</div>", unsafe_allow_html=True)            
            st.markdown("<div class='label-row'>Produk</div>", unsafe_allow_html=True)            
            st.markdown("<div class='label-row'>Jumlah (pcs)</div>", unsafe_allow_html=True)            
            st.markdown("<div class='label-row'>Due Date</div>", unsafe_allow_html=True)            
            st.markdown("<div class='label-row'>Prioritas</div>", unsafe_allow_html=True)
        
        with col2:
            order_date = st.date_input("", datetime.date.today(), label_visibility="collapsed", key="input_order_date")
            
            buyers_list = ["Belhome", "Indoteak", "SDM", "WMG", "Remar", "ITM", "San Marco"]
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
                        "Proses Saat Ini": ["Pre Order"],
                        "Keterangan": [""],
                        "Tracking": [json.dumps(init_tracking_data(new_order_id))]
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
        # Add tracking status column
        df['Tracking Status'] = df.apply(lambda row: get_tracking_status_from_progress(row['Progress'], row['Status']), axis=1)
        
        # Filter
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            filter_buyer = st.multiselect("Filter Buyer", df["Buyer"].unique())
        with col_f2:
            filter_status = st.multiselect("Filter Status", ["Accepted", "Pending", "Rejected"], default=["Accepted", "Pending", "Rejected"])
        with col_f3:
            filter_tracking = st.multiselect("Filter Tracking Status", ["Pending", "On Going", "Done"])
        with col_f4:
            search_order = st.text_input("🔍 Cari Order ID / Produk")
        
        df_filtered = df.copy()
        if filter_buyer:
            df_filtered = df_filtered[df_filtered["Buyer"].isin(filter_buyer)]
        if filter_status:
            df_filtered = df_filtered[df_filtered["Status"].isin(filter_status)]
        if filter_tracking:
            df_filtered = df_filtered[df_filtered["Tracking Status"].isin(filter_tracking)]
        if search_order:
            df_filtered = df_filtered[
                df_filtered["Order ID"].str.contains(search_order, case=False, na=False) | 
                df_filtered["Produk"].str.contains(search_order, case=False, na=False)
            ]
        
        st.markdown("---")
              
        # Header
        st.markdown("<div class='order-table-header'>", unsafe_allow_html=True)
        header_cols = st.columns([1, 1, 0.8, 1.3, 0.5, 1, 0.8, 0.9, 1, 1, 0.8])
        header_cols[0].markdown("**Order ID**")
        header_cols[1].markdown("**Order Date**")
        header_cols[2].markdown("**Buyer**")
        header_cols[3].markdown("**Produk**")
        header_cols[4].markdown("**Qty**")
        header_cols[5].markdown("**Due Date**")
        header_cols[6].markdown("**Status**")
        header_cols[7].markdown("**Progress**")
        header_cols[8].markdown("**Proses**")
        header_cols[9].markdown("**Tracking**")
        header_cols[10].markdown("**Action**")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Inisialisasi session state untuk konfirmasi delete
        if "delete_confirm" not in st.session_state:
            st.session_state["delete_confirm"] = {}
        
        # Table with actions
        for idx, row in df_filtered.iterrows():
            cols = st.columns([1, 1, 0.8, 1.3, 0.5, 1, 0.8, 0.9, 1, 1, 0.8])
            
            cols[0].write(row['Order ID'])
            cols[1].write(str(row['Order Date']))
            cols[2].write(row['Buyer'])
            cols[3].write(row['Produk'])
            cols[4].write(row['Qty'])
            cols[5].write(str(row['Due Date']))
            
            status_colors = {
                "Accepted": "🟢",
                "Pending": "🟡",
                "Rejected": "🔴"
            }
            cols[6].write(f"{status_colors.get(row['Status'], '')} {row['Status']}")
            
            cols[7].write(row['Progress'])
            cols[8].write(row['Proses Saat Ini'])
            
            # Tracking Status dengan warna
            tracking_colors = {
                "Pending": ("⏳", "#6B7280"),
                "On Going": ("🔄", "#3B82F6"),
                "Done": ("✅", "#10B981")
            }
            track_icon, track_color = tracking_colors.get(row['Tracking Status'], ("⚪", "#6B7280"))
            cols[9].markdown(f"<span style='color: {track_color};'>{track_icon} {row['Tracking Status']}</span>", unsafe_allow_html=True)
            
            with cols[10]:
                action_col1, action_col2 = st.columns(2)
                with action_col1:
                    if st.button("✏️", key=f"edit_{idx}", help="Edit Order", use_container_width=True):
                        st.session_state["edit_order_idx"] = idx
                        st.session_state["menu"] = "Progress"
                        st.rerun()
                
                with action_col2:
                    # Cek apakah order ini sedang dalam mode konfirmasi delete
                    if st.session_state["delete_confirm"].get(idx, False):
                        # Mode konfirmasi aktif - tampilkan tombol konfirmasi
                        if st.button("✅", key=f"confirm_del_{idx}", help="Confirm Delete", use_container_width=True):
                            # Hapus order
                            st.session_state["data_produksi"].drop(idx, inplace=True)
                            st.session_state["data_produksi"].reset_index(drop=True, inplace=True)
                            save_data(st.session_state["data_produksi"])
                            # Reset konfirmasi
                            st.session_state["delete_confirm"][idx] = False
                            st.success(f"✅ Order {row['Order ID']} berhasil dihapus!")
                            st.rerun()
                    else:
                        # Mode normal - tampilkan tombol delete
                        if st.button("🗑️", key=f"del_{idx}", help="Delete Order", use_container_width=True):
                            # Aktifkan mode konfirmasi
                            st.session_state["delete_confirm"][idx] = True
                            st.rerun()
            
            # Tampilkan warning jika dalam mode konfirmasi
            if st.session_state["delete_confirm"].get(idx, False):
                st.markdown(f"""
                <div style='background-color: #991B1B; padding: 10px; border-radius: 5px; margin: 5px 0;'>
                    <span style='color: white; font-weight: bold;'>⚠️ Konfirmasi Hapus Order {row['Order ID']}?</span>
                    <br>
                    <span style='color: #FEE2E2; font-size: 0.9em;'>Klik tombol ✅ untuk konfirmasi atau refresh halaman untuk batal</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Tombol batal
                if st.button(f"❌ Batal Hapus", key=f"cancel_del_{idx}", type="secondary"):
                    st.session_state["delete_confirm"][idx] = False
                    st.rerun()
            
            st.markdown("<div style='margin: 8px 0; border-bottom: 1px solid #374151;'></div>", unsafe_allow_html=True)
    else:
        st.info("📝 Belum ada order yang diinput.")

# ===== MENU: UPDATE PROGRESS =====
elif st.session_state["menu"] == "Progress":
    st.header("⚙️ UPDATE PROGRESS PRODUKSI")
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        with st.container():
            st.markdown("""
            <div style='background-color: #1E3A8A; padding: 15px; border-radius: 8px; margin-bottom: 25px;'>
                <h3 style='color: white; text-align: center; margin: 0;'>FORM UPDATE PROGRESS</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Pilih order
            order_ids = df["Order ID"].tolist()
            
            # Cek jika ada order yang di-edit dari menu Orders
            default_idx = 0
            if "edit_order_idx" in st.session_state:
                edit_order_id = df.iloc[st.session_state["edit_order_idx"]]["Order ID"]
                if edit_order_id in order_ids:
                    default_idx = order_ids.index(edit_order_id)
                del st.session_state["edit_order_idx"]
            
            selected_order = st.selectbox("Pilih Order ID", order_ids, index=default_idx)
            
            # Filter di bawah Pilih Order ID
            st.markdown("---")
            st.markdown("### 🔍 Filter Order")
            filter_cols = st.columns(2)
            with filter_cols[0]:
                filter_track_status = st.multiselect("Filter Tracking Status", ["Pending", "On Going", "Done"], key="filter_tracking_progress")
            with filter_cols[1]:
                filter_buyer_progress = st.multiselect("Filter Buyer", df["Buyer"].unique().tolist(), key="filter_buyer_progress")
            
            # Apply filters untuk menampilkan order yang sesuai
            df_filtered_display = df.copy()
            
            # Add tracking status untuk filtering
            df_filtered_display['Tracking Status'] = df_filtered_display.apply(
                lambda row: get_tracking_status_from_progress(row['Progress'], row['Status']), 
                axis=1
            )
            
            if filter_track_status:
                df_filtered_display = df_filtered_display[df_filtered_display["Tracking Status"].isin(filter_track_status)]
            if filter_buyer_progress:
                df_filtered_display = df_filtered_display[df_filtered_display["Buyer"].isin(filter_buyer_progress)]
            
            # Tampilkan hasil filter
            if not df_filtered_display.empty and (filter_track_st)
                        
# ===== MENU: TRACKING PRODUKSI =====
elif st.session_state["menu"] == "Tracking":
    st.header("🔍 TRACKING PRODUKSI")
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        st.markdown("""
        <div style='background-color: #1E3A8A; padding: 15px; border-radius: 8px; margin-bottom: 25px;'>
            <h3 style='color: white; text-align: center; margin: 0;'>📋 STATUS TRACKING PER TAHAPAN</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Filter options
        track_col1, track_col2, track_col3 = st.columns(3)
        with track_col1:
            filter_track_buyer = st.multiselect("Filter Buyer", df["Buyer"].unique().tolist(), key="track_buyer_filter")
        with track_col2:
            filter_track_status = st.multiselect("Filter Status Order", ["Pending", "Accepted", "Rejected"], key="track_status_filter")
        with track_col3:
            search_track_order = st.text_input("🔍 Cari Order ID", key="track_search")
        
        # Apply filters
        df_track_filtered = df.copy()
        if filter_track_buyer:
            df_track_filtered = df_track_filtered[df_track_filtered["Buyer"].isin(filter_track_buyer)]
        if filter_track_status:
            df_track_filtered = df_track_filtered[df_track_filtered["Status"].isin(filter_track_status)]
        if search_track_order:
            df_track_filtered = df_track_filtered[df_track_filtered["Order ID"].str.contains(search_track_order, case=False, na=False)]
        
        st.markdown("---")
        
        # Get all tracking stages
        stages = get_tracking_stages()
        
        # Loop through each stage and display orders in that stage
        for stage_idx, stage in enumerate(stages):
            # Filter orders yang berada di tahap ini
            orders_in_stage = df_track_filtered[df_track_filtered["Proses Saat Ini"] == stage].copy()
            
            # Hitung jumlah order dan tentukan status tracking
            total_in_stage = len(orders_in_stage)
            
            # Hitung tracking status secara manual
            pending_track = 0
            ongoing_track = 0
            done_track = 0
            
            for idx, row in orders_in_stage.iterrows():
                try:
                    progress_pct = int(row['Progress'].rstrip('%')) if row['Progress'] else 0
                except:
                    progress_pct = 0
                
                order_status = row['Status']
                
                # Tentukan tracking status
                if order_status == "Rejected":
                    pending_track += 1
                elif progress_pct == 100:
                    done_track += 1
                elif progress_pct == 0:
                    pending_track += 1
                else:
                    ongoing_track += 1
            
            # Status icon untuk tahapan
            if total_in_stage > 0:
                stage_icon = "🔄"  # Ada order di tahap ini
            else:
                stage_icon = "⏸️"  # Tidak ada order
            
            # Expander untuk setiap tahapan
            with st.expander(f"{stage_icon} **{stage_idx + 1}. {stage}** - ({total_in_stage} orders)", expanded=(total_in_stage > 0)):
                if total_in_stage > 0:
                    # Summary cards
                    sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
                    sum_col1.metric("📦 Total Orders", total_in_stage)
                    sum_col2.metric("⏳ Pending", pending_track)
                    sum_col3.metric("🔄 On Going", ongoing_track)
                    sum_col4.metric("✅ Done", done_track)
                    
                    st.markdown("---")
                    
                    # Table header
                    header_cols = st.columns([1.2, 1, 1.2, 1.2, 0.7, 1, 1])
                    header_cols[0].markdown("**Order ID**")
                    header_cols[1].markdown("**Order Date**")
                    header_cols[2].markdown("**Buyer**")
                    header_cols[3].markdown("**Produk**")
                    header_cols[4].markdown("**Qty**")
                    header_cols[5].markdown("**Order Status**")
                    header_cols[6].markdown("**Tracking Status**")
                    
                    # Display orders
                    for idx, row in orders_in_stage.iterrows():
                        order_cols = st.columns([1.2, 1, 1.2, 1.2, 0.7, 1, 1])
                        
                        order_cols[0].write(row['Order ID'])
                        order_cols[1].write(str(row['Order Date']))
                        order_cols[2].write(row['Buyer'])
                        order_cols[3].write(row['Produk'][:20] + "..." if len(row['Produk']) > 20 else row['Produk'])
                        order_cols[4].write(f"{row['Qty']} pcs")
                        
                        # Order Status dengan warna
                        order_status_colors = {
                            "Accepted": ("🟢", "#10B981"),
                            "Pending": ("🟡", "#F59E0B"),
                            "Rejected": ("🔴", "#EF4444")
                        }
                        status_icon, status_color = order_status_colors.get(row['Status'], ("⚪", "#6B7280"))
                        order_cols[5].markdown(f"<span style='color: {status_color}; font-weight: bold;'>{status_icon} {row['Status']}</span>", unsafe_allow_html=True)
                        
                        # Tentukan tracking status berdasarkan progress dan order status
                        try:
                            progress_pct = int(row['Progress'].rstrip('%')) if row['Progress'] else 0
                        except:
                            progress_pct = 0
                        
                        if row['Status'] == "Rejected":
                            tracking_status = "⏳ Pending"
                            track_color = "#6B7280"  # Gray
                        elif progress_pct == 100:
                            tracking_status = "✅ Done"
                            track_color = "#10B981"  # Green
                        elif progress_pct == 0:
                            tracking_status = "⏳ Pending"
                            track_color = "#6B7280"  # Gray
                        else:
                            tracking_status = "🔄 On Going"
                            track_color = "#3B82F6"  # Blue
                        
                        order_cols[6].markdown(f"<span style='color: {track_color}; font-weight: bold;'>{tracking_status}</span>", unsafe_allow_html=True)
                        
                        st.markdown("<div style='margin: 5px 0; border-bottom: 1px solid #374151;'></div>", unsafe_allow_html=True)
                    
                    # Keterangan jika ada
                    orders_with_notes = orders_in_stage[orders_in_stage["Keterangan"].notna() & (orders_in_stage["Keterangan"] != "")]
                    if not orders_with_notes.empty:
                        st.markdown("---")
                        st.markdown("**📝 Catatan:**")
                        for idx, row in orders_with_notes.iterrows():
                            st.info(f"**{row['Order ID']}:** {row['Keterangan']}")
                else:
                    st.info(f"✨ Tidak ada order di tahap {stage}")
        
        # Summary Statistics
        st.markdown("---")
        st.subheader("📊 Summary Statistics")
        
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        total_orders = len(df_track_filtered)
        
        if total_orders > 0:
            avg_progress = df_track_filtered["Progress"].str.rstrip('%').astype('float').mean()
            completed_orders = len(df_track_filtered[df_track_filtered["Progress"] == "100%"])
            in_progress_orders = len(df_track_filtered[(df_track_filtered["Progress"] != "100%") & (df_track_filtered["Progress"] != "0%") & (df_track_filtered["Status"] != "Rejected")])
            
            stat_col1.metric("📦 Total Orders", total_orders)
            stat_col2.metric("✅ Done", completed_orders, delta=f"{(completed_orders/total_orders*100):.0f}%")
            stat_col3.metric("🔄 On Going", in_progress_orders)
            stat_col4.metric("📈 Avg Progress", f"{avg_progress:.1f}%")
        else:
            stat_col1.metric("📦 Total Orders", 0)
            stat_col2.metric("✅ Done", 0)
            stat_col3.metric("🔄 On Going", 0)
            stat_col4.metric("📈 Avg Progress", "0%")
        
        # Progress Distribution Chart
        st.markdown("---")
        st.subheader("📈 Distribution by Process Stage")
        
        if not df_track_filtered.empty:
            stage_distribution = df_track_filtered["Proses Saat Ini"].value_counts()
            fig_stage = px.bar(
                x=stage_distribution.index, 
                y=stage_distribution.values,
                labels={'x': 'Tahapan Proses', 'y': 'Jumlah Order'},
                title="Jumlah Order per Tahapan",
                color=stage_distribution.values,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_stage, use_container_width=True)
        else:
            st.info("Tidak ada data untuk ditampilkan")
        
        # Timeline view
        st.markdown("---")
        st.subheader("📅 Timeline View")
        
        timeline_col1, timeline_col2 = st.columns(2)
        
        with timeline_col1:
            st.markdown("**🔴 Overdue Orders (Past Due Date)**")
            overdue_orders = df_track_filtered[
                (df_track_filtered["Due Date"] < datetime.date.today()) & 
                (df_track_filtered["Progress"] != "100%") &
                (df_track_filtered["Status"] != "Rejected")
            ]
            if not overdue_orders.empty:
                for idx, row in overdue_orders.iterrows():
                    days_overdue = (datetime.date.today() - row["Due Date"]).days
                    st.warning(f"**{row['Order ID']}** - {row['Produk'][:30]} | ⏰ {days_overdue} hari terlambat")
            else:
                st.success("✅ Tidak ada order yang terlambat")
        
        with timeline_col2:
            st.markdown("**🟡 Upcoming Deadlines (Next 7 Days)**")
            upcoming_orders = df_track_filtered[
                (df_track_filtered["Due Date"] >= datetime.date.today()) & 
                (df_track_filtered["Due Date"] <= datetime.date.today() + datetime.timedelta(days=7)) &
                (df_track_filtered["Progress"] != "100%") &
                (df_track_filtered["Status"] != "Rejected")
            ]
            if not upcoming_orders.empty:
                for idx, row in upcoming_orders.iterrows():
                    days_left = (row["Due Date"] - datetime.date.today()).days
                    st.info(f"**{row['Order ID']}** - {row['Produk'][:30]} | ⏰ {days_left} hari lagi")
            else:
                st.success("✅ Tidak ada deadline mendesak")
        
    else:
        st.info("📝 Belum ada order untuk di-tracking.")
        
# ===== MENU: FROZEN ZONE =====
elif st.session_state["menu"] == "Frozen":
    st.header("❄️ FROZEN ZONE")
    
    st.markdown("""
    <div style='background-color: #1E3A8A; padding: 15px; border-radius: 8px; margin-bottom: 25px;'>
        <h3 style='color: white; text-align: center; margin: 0;'>❄️ PENGATURAN FROZEN ZONE</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### START DATE")
        frozen_start = st.date_input("", value=st.session_state["frozen_start"], label_visibility="collapsed", key="frozen_start_input")
    with col2:
        st.markdown("### END DATE")
        frozen_end = st.date_input("", value=st.session_state["frozen_end"], label_visibility="collapsed", key="frozen_end_input")
    
    if st.button("💾 Set Frozen Period", type="primary"):
        st.session_state["frozen_start"] = frozen_start
        st.session_state["frozen_end"] = frozen_end
        st.success("✅ Frozen period berhasil diset!")
    
    st.markdown("---")
    st.subheader("📦 Order in Frozen Zone")
    
    df = st.session_state["data_produksi"]
    if not df.empty:
        df_frozen = df[
            (df["Due Date"] >= frozen_start) & 
            (df["Due Date"] <= frozen_end)
        ]
        
        if not df_frozen.empty:
            st.dataframe(df_frozen[["Order ID", "Buyer", "Produk", "Qty", "Due Date", "Status", "Progress"]], 
                        use_container_width=True, hide_index=True)
            st.warning(f"⚠️ {len(df_frozen)} order berada dalam frozen zone!")
        else:
            st.info("✅ Tidak ada order dalam frozen zone.")
    else:
        st.info("📝 Belum ada data order.")

# ===== MENU: GANTT CHART =====
elif st.session_state["menu"] == "Gantt":
    st.header("📊 GANTT CHART PRODUKSI")
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        # Prepare data for Gantt chart
        gantt_data = []
        for idx, row in df.iterrows():
            gantt_data.append(dict(
                Task=f"{row['Order ID']} - {row['Produk'][:20]}",
                Start=row['Order Date'],
                Finish=row['Due Date'],
                Resource=row['Buyer']
            ))
        
        # Create Gantt chart
        if gantt_data:
            fig = ff.create_gantt(
                gantt_data,
                colors=['#1E3A8A', '#3B82F6', '#60A5FA', '#93C5FD'],
                index_col='Resource',
                show_colorbar=True,
                group_tasks=True,
                showgrid_x=True,
                showgrid_y=True,
                title='Production Schedule Gantt Chart'
            )
            fig.update_layout(height=600, xaxis_title="Timeline", yaxis_title="Orders")
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary table
            st.markdown("---")
            st.subheader("📋 Order Timeline Summary")
            summary_df = df[["Order ID", "Produk", "Buyer", "Order Date", "Due Date", "Status", "Progress"]].copy()
            summary_df["Duration (days)"] = (pd.to_datetime(summary_df["Due Date"]) - pd.to_datetime(summary_df["Order Date"])).dt.days
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
        else:
            st.warning("Tidak ada data untuk ditampilkan dalam Gantt Chart")
    else:
        st.info("📝 Belum ada data untuk membuat Gantt Chart.")

# ===== MENU: ANALYTICS =====
elif st.session_state["menu"] == "Analytics":
    st.header("📈 ANALISIS & LAPORAN")
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 By Buyer", "📦 By Product", "📅 By Timeline"])
        
        with tab1:
            st.subheader("Performance Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            total_qty = df["Qty"].sum()
            on_time_orders = len(df[df["Due Date"] >= datetime.date.today()])
            completion_rate = (df["Progress"].str.rstrip('%').astype('float').mean())
            total_buyers = df["Buyer"].nunique()
            
            col1.metric("Total Quantity", f"{total_qty:,} pcs")
            col2.metric("On-Time Orders", on_time_orders)
            col3.metric("Avg Completion", f"{completion_rate:.1f}%")
            col4.metric("Total Buyers", total_buyers)
            
            st.markdown("---")
            
            # Status distribution chart
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                status_count = df["Status"].value_counts()
                fig_status = px.bar(x=status_count.index, y=status_count.values,
                                   labels={'x': 'Status', 'y': 'Count'},
                                   title="Orders by Status",
                                   color=status_count.values,
                                   color_continuous_scale='Viridis')
                st.plotly_chart(fig_status, use_container_width=True)
            
            with col_chart2:
                priority_count = df["Prioritas"].value_counts()
                fig_priority = px.pie(values=priority_count.values, names=priority_count.index,
                                     title="Orders by Priority",
                                     color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(fig_priority, use_container_width=True)
        
        with tab2:
            st.subheader("Analysis by Buyer")
            buyer_stats = df.groupby("Buyer").agg({
                "Order ID": "count",
                "Qty": "sum",
                "Progress": lambda x: x.str.rstrip('%').astype('float').mean()
            }).rename(columns={"Order ID": "Total Orders", "Qty": "Total Qty", "Progress": "Avg Progress"})
            buyer_stats["Avg Progress"] = buyer_stats["Avg Progress"].round(1).astype(str) + "%"
            
            st.dataframe(buyer_stats, use_container_width=True)
            
            # Bar chart
            fig_buyer = px.bar(buyer_stats, y="Total Orders", 
                              labels={'index': 'Buyer', 'Total Orders': 'Jumlah Order'},
                              title="Total Orders per Buyer",
                              color="Total Orders",
                              color_continuous_scale='Blues')
            st.plotly_chart(fig_buyer, use_container_width=True)
        
        with tab3:
            st.subheader("Analysis by Product")
            product_stats = df.groupby("Produk").agg({
                "Order ID": "count",
                "Qty": "sum"
            }).rename(columns={"Order ID": "Total Orders", "Qty": "Total Qty"})
            product_stats = product_stats.sort_values("Total Orders", ascending=False).head(10)
            
            st.dataframe(product_stats, use_container_width=True)
            
            # Bar chart
            fig_product = px.bar(product_stats, y="Total Qty",
                               labels={'index': 'Produk', 'Total Qty': 'Total Quantity'},
                               title="Top 10 Products by Quantity",
                               color="Total Qty",
                               color_continuous_scale='Greens')
            st.plotly_chart(fig_product, use_container_width=True)
        
        with tab4:
            st.subheader("Analysis by Timeline")
            
            # Orders by month
            df_copy = df.copy()
            df_copy['Order Month'] = pd.to_datetime(df_copy['Order Date']).dt.to_period('M').astype(str)
            monthly_orders = df_copy.groupby('Order Month').agg({
                'Order ID': 'count',
                'Qty': 'sum'
            }).rename(columns={'Order ID': 'Total Orders', 'Qty': 'Total Qty'})
            
            st.dataframe(monthly_orders, use_container_width=True)
            
            # Line chart
            fig_timeline = px.line(monthly_orders, y=['Total Orders', 'Total Qty'],
                                  labels={'value': 'Count', 'Order Month': 'Month'},
                                  title="Orders & Quantity Trend by Month",
                                  markers=True)
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Export section
        st.markdown("---")
        st.subheader("💾 Export Laporan")
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        
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
            json_data = df.to_json(orient='records', indent=2, date_format='iso')
            st.download_button(
                label="📋 Download JSON",
                data=json_data,
                file_name=f"ppic_report_{datetime.date.today()}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col_exp3:
            # Excel export (sebagai CSV karena tidak perlu library tambahan)
            excel_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📊 Download Excel (CSV)",
                data=excel_data,
                file_name=f"ppic_report_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("📝 Belum ada data untuk dianalisis.")

# Footer
st.markdown("---")
st.caption(f"© 2025 PPIC-DSS System | v4.0 Enhanced | 💾 Database: {DATABASE_PATH}")
st.caption("Features: Dashboard, Input Order, Order List, Progress Update, Production Tracking, Frozen Zone, Analytics, Gantt Chart")
