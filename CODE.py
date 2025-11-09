import streamlit as st
import pandas as pd
import datetime
import json
import os
import plotly.express as px
import plotly.figure_factory as ff

# ===== KONFIGURASI DATABASE =====
DATABASE_PATH = "ppic_data.json"
BUYER_DB_PATH = "buyers.json"
PRODUCT_DB_PATH = "products.json"

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
                    # Ensure History column exists
                    if 'History' not in df.columns:
                        df['History'] = df.apply(lambda x: json.dumps([]), axis=1)
                return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
    return pd.DataFrame(columns=[
        "Order ID", "Order Date", "Buyer", "Produk", "Qty", "Due Date", 
        "Prioritas", "Status", "Progress", "Proses Saat Ini", "Keterangan",
        "Tracking", "History"
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

def load_buyers():
    """Memuat database buyer"""
    if os.path.exists(BUYER_DB_PATH):
        try:
            with open(BUYER_DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle old format (list) vs new format (list of dicts)
                if data and isinstance(data[0], str):
                    # Convert old format to new format
                    return [{"name": buyer, "address": "", "contact": "", "profile": ""} for buyer in data]
                return data
        except:
            pass
    return [
        {"name": "Belhome", "address": "", "contact": "", "profile": ""},
        {"name": "Indoteak", "address": "", "contact": "", "profile": ""},
        {"name": "SDM", "address": "", "contact": "", "profile": ""},
        {"name": "WMG", "address": "", "contact": "", "profile": ""},
        {"name": "Remar", "address": "", "contact": "", "profile": ""},
        {"name": "ITM", "address": "", "contact": "", "profile": ""},
        {"name": "San Marco", "address": "", "contact": "", "profile": ""}
    ]

def save_buyers(buyers):
    """Menyimpan database buyer"""
    try:
        with open(BUYER_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(buyers, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def get_buyer_names():
    """Get list of buyer names only"""
    buyers = st.session_state["buyers"]
    return [b["name"] for b in buyers]

def load_products():
    """Memuat database produk"""
    if os.path.exists(PRODUCT_DB_PATH):
        try:
            with open(PRODUCT_DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_products(products):
    """Menyimpan database produk"""
    try:
        with open(PRODUCT_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        return True
    except:
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
    
    if order_status == "Rejected":
        return "Pending"
    elif progress_pct == 100:
        return "Done"
    elif progress_pct == 0:
        return "Pending"
    else:
        return "On Going"

def add_history_entry(order_id, action, details):
    """Menambahkan entry ke history order"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "timestamp": timestamp,
        "action": action,
        "details": details
    }

# ===== INISIALISASI =====
if "data_produksi" not in st.session_state:
    st.session_state["data_produksi"] = load_data()
if "buyers" not in st.session_state:
    st.session_state["buyers"] = load_buyers()
if "products" not in st.session_state:
    st.session_state["products"] = load_products()
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
    "💾 Database": "Database",
    "❄️ Frozen Zone": "Frozen",
    "📈 Analisis & Laporan": "Analytics",
    "📊 Gantt Chart": "Gantt"
}

for label, value in menu_options.items():
    if st.sidebar.button(label, use_container_width=True):
        st.session_state["menu"] = value

st.sidebar.markdown("---")
st.sidebar.info(f"📁 Database: `{os.path.basename(DATABASE_PATH)}`")

# ===== BACK BUTTON =====
if st.session_state["menu"] != "Dashboard":
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
        df['Tracking Status'] = df.apply(lambda row: get_tracking_status_from_progress(row['Progress'], row['Status']), axis=1)
        
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
        
        st.subheader("🔍 Tracking Status Overview")
        track_col1, track_col2, track_col3 = st.columns(3)
        
        track_pending = len(df[df['Tracking Status'] == 'Pending'])
        track_ongoing = len(df[df['Tracking Status'] == 'On Going'])
        track_done = len(df[df['Tracking Status'] == 'Done'])
        
        track_col1.metric("⏳ Pending", track_pending, delta=f"{(track_pending/total_orders*100):.0f}%")
        track_col2.metric("🔄 On Going", track_ongoing, delta=f"{(track_ongoing/total_orders*100):.0f}%")
        track_col3.metric("✅ Done", track_done, delta=f"{(track_done/total_orders*100):.0f}%")
        
        st.markdown("---")
        
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
        
        st.subheader("🕒 Recent Orders (Last 10)")
        recent_df = df.sort_values("Order Date", ascending=False).head(10)
        st.dataframe(recent_df[["Order ID", "Order Date", "Buyer", "Produk", "Qty", "Status", "Progress", "Proses Saat Ini", "Tracking Status"]], 
                     use_container_width=True, hide_index=True)
    else:
        st.info("📝 Belum ada data. Silakan input pesanan baru.")

# ===== MENU: INPUT PESANAN BARU =====
elif st.session_state["menu"] == "Input":
    st.header("📋 Form Input Pesanan Baru")
    
    with st.container():
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
            st.markdown("<div class='label-row'>Status</div>", unsafe_allow_html=True)
        
        with col2:
            order_date = st.date_input("", datetime.date.today(), label_visibility="collapsed", key="input_order_date")
            
            buyers_list = get_buyer_names()
            buyer = st.selectbox("", buyers_list, label_visibility="collapsed", key="input_buyer")
            
            products_list = st.session_state["products"]
            if products_list:
                produk_option = st.selectbox("", ["-- Pilih Produk --"] + products_list, label_visibility="collapsed", key="input_produk_select")
                if produk_option == "-- Pilih Produk --":
                    produk = st.text_input("", placeholder="Atau ketik nama produk baru", label_visibility="collapsed", key="input_produk_manual")
                else:
                    produk = produk_option
            else:
                produk = st.text_input("", placeholder="Masukkan nama produk", label_visibility="collapsed", key="input_produk")
            
            qty = st.number_input("", min_value=1, value=1, label_visibility="collapsed", key="input_qty")
            due_date = st.date_input("", datetime.date.today() + datetime.timedelta(days=30), label_visibility="collapsed", key="input_due")
            prioritas = st.selectbox("", ["High", "Medium", "Low"], label_visibility="collapsed", key="input_priority")
            status = st.selectbox("", ["Pending", "Accepted", "Rejected"], label_visibility="collapsed", key="input_status")
        
        st.markdown("")
        col_btn = st.columns([1, 3])
        
        with col_btn[0]:
            if st.button("📤 SUBMIT ORDER", use_container_width=True, type="primary"):
                if produk and buyer:
                    existing_ids = st.session_state["data_produksi"]["Order ID"].tolist() if not st.session_state["data_produksi"].empty else []
                    new_id_num = max([int(oid.split("-")[1]) for oid in existing_ids if "-" in oid], default=2400) + 1
                    new_order_id = f"ORD-{new_id_num}"
                    
                    # Initialize history with first entry
                    initial_history = [add_history_entry(new_order_id, "Order Created", 
                        f"Status: {status}, Priority: {prioritas}")]
                    
                    new_data = pd.DataFrame({
                        "Order ID": [new_order_id],
                        "Order Date": [order_date],
                        "Buyer": [buyer],
                        "Produk": [produk],
                        "Qty": [qty],
                        "Due Date": [due_date],
                        "Prioritas": [prioritas],
                        "Status": [status],
                        "Progress": ["0%"],
                        "Proses Saat Ini": ["Pre Order"],
                        "Keterangan": [""],
                        "Tracking": [json.dumps(init_tracking_data(new_order_id))],
                        "History": [json.dumps(initial_history)]
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
        df['Tracking Status'] = df.apply(lambda row: get_tracking_status_from_progress(row['Progress'], row['Status']), axis=1)
        
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
        
        if "delete_confirm" not in st.session_state:
            st.session_state["delete_confirm"] = {}
        
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
                    if st.session_state["delete_confirm"].get(idx, False):
                        if st.button("✅", key=f"confirm_del_{idx}", help="Confirm Delete", use_container_width=True):
                            st.session_state["data_produksi"].drop(idx, inplace=True)
                            st.session_state["data_produksi"].reset_index(drop=True, inplace=True)
                            save_data(st.session_state["data_produksi"])
                            st.session_state["delete_confirm"][idx] = False
                            st.success(f"✅ Order {row['Order ID']} berhasil dihapus!")
                            st.rerun()
                    else:
                        if st.button("🗑️", key=f"del_{idx}", help="Delete Order", use_container_width=True):
                            st.session_state["delete_confirm"][idx] = True
                            st.rerun()
            
            if st.session_state["delete_confirm"].get(idx, False):
                st.markdown(f"""
                <div style='background-color: #991B1B; padding: 10px; border-radius: 5px; margin: 5px 0;'>
                    <span style='color: white; font-weight: bold;'>⚠️ Konfirmasi Hapus Order {row['Order ID']}?</span>
                    <br>
                    <span style='color: #FEE2E2; font-size: 0.9em;'>Klik tombol ✅ untuk konfirmasi atau refresh halaman untuk batal</span>
                </div>
                """, unsafe_allow_html=True)
                
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
    
    with st.container():
        st.markdown("""
        <style>
        .label-row {
            display: flex;
            align-items: center;
            height: 38px;
            margin-bottom: 18px;
            font-weight: bold;
        }
        .progress-slider-label {
            display: flex;
            align-items: center;
            height: 38px;
            margin-bottom: 10px;
            margin-top: 10px;
            font-weight: bold;
        }
        .progress-textarea-label {
            display: flex;
            align-items: flex-start;
            padding-top: 8px;
            margin-bottom: 10px;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Format: ORDER ID | BUYER
        order_options = [f"{row['Order ID']} | {row['Buyer']} | {row['Produk']} | {row['Progress']}" for idx, row in df.iterrows()]
        
        default_idx = 0
        if "edit_order_idx" in st.session_state:
            edit_order_id = df.iloc[st.session_state["edit_order_idx"]]["Order ID"]
            for i, opt in enumerate(order_options):
                if opt.startswith(edit_order_id):
                    default_idx = i
                    break
            del st.session_state["edit_order_idx"]
        
        # Get selected order data first to show progress overview
        selected_option = order_options[default_idx]
        selected_order = selected_option.split(" | ")[0]
        
        if selected_order:
            order_data = df[df["Order ID"] == selected_order].iloc[0]
            order_idx = df[df["Order ID"] == selected_order].index[0]
            
            # Get current progress value first
            current_saved_progress = int(order_data["Progress"].rstrip('%')) if order_data["Progress"] else 0
            
            # 3. Pilih Order - tepat di atas form
            st.markdown("### 📦 Pilih Order untuk Update")
            selected_option = st.selectbox("", order_options, index=default_idx, label_visibility="collapsed", key="select_order_update")
            selected_order = selected_option.split(" | ")[0]
            
            # Reload order data if selection changed
            order_data = df[df["Order ID"] == selected_order].iloc[0]
            order_idx = df[df["Order ID"] == selected_order].index[0]
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Update Form - Rapikan dengan spacing yang lebih baik
            progress_col1, progress_col2 = st.columns([1, 3])
            
            with progress_col1:
                st.markdown("<div class='label-row'>Product</div>", unsafe_allow_html=True)
                st.markdown("<div class='label-row'>Proses Saat Ini</div>", unsafe_allow_html=True)
                st.markdown("<div class='progress-slider-label'>Persentase Progress</div>", unsafe_allow_html=True)
                st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)  # Spacer untuk slider
                st.markdown("<div class='progress-textarea-label'></div>", unsafe_allow_html=True)
            
            with progress_col2:
                st.text_input("", value=order_data["Produk"], disabled=True, label_visibility="collapsed", key=f"produk_{selected_order}")
                
                proses_list = get_tracking_stages()
                current_proses_idx = proses_list.index(order_data["Proses Saat Ini"]) if order_data["Proses Saat Ini"] in proses_list else 0
                
                current_proses = st.selectbox("", proses_list, 
                                              index=current_proses_idx,
                                              label_visibility="collapsed",
                                              key=f"proses_{selected_order}")
                
                # Mapping progress berdasarkan stage
                stage_to_progress = {
                    "Pre Order": 0,
                    "Order di Supplier": 10,
                    "Warehouse": 20,
                    "Fitting 1": 30,
                    "Amplas": 40,
                    "Revisi 1": 50,
                    "Spray": 60,
                    "Fitting 2": 70,
                    "Revisi Fitting 2": 80,
                    "Packaging": 90,
                    "Pengiriman": 100
                }
                
                auto_progress = stage_to_progress.get(current_proses, 0)
                current_saved_progress = int(order_data["Progress"].rstrip('%')) if order_data["Progress"] else 0
                
                if auto_progress != current_saved_progress:
                    st.info(f"💡 Progress otomatis: {auto_progress}% untuk tahap '{current_proses}'")
                
                use_manual_progress = st.checkbox("Override progress manual", value=False, 
                                                 key=f"manual_{selected_order}",
                                                 help="Centang jika ingin mengatur progress secara manual")
                
                if use_manual_progress:
                    progress_value = st.slider("", 0, 100, current_saved_progress, 
                                       label_visibility="collapsed",
                                       key=f"slider_{selected_order}",
                                       help="Slide untuk mengatur progress manual")
                else:
                    progress_value = auto_progress
                    st.slider("", 0, 100, progress_value, label_visibility="collapsed", 
                            disabled=True, 
                            key=f"slider_auto_{selected_order}",
                            help="Progress otomatis berdasarkan tahapan proses")
                
                if progress_value == 100:
                    progress_color = "#10B981"
                elif progress_value >= 50:
                    progress_color = "#3B82F6"
                elif progress_value >= 25:
                    progress_color = "#F59E0B"
                else:
                    progress_color = "#EF4444"
                    
                st.markdown(f"<h2 style='color: {progress_color}; margin-top: -15px; margin-bottom: 20px;'>{progress_value}%</h2>", unsafe_allow_html=True)
                
                notes = st.text_area("", value="", 
                                    placeholder="Masukkan catatan update (opsional)...", 
                                    label_visibility="collapsed", 
                                    key=f"notes_{selected_order}",
                                    height=100)
            
            st.markdown("")
            
            with st.expander("ℹ️ Lihat Mapping Progress per Tahapan"):
                st.markdown("""
                | Tahapan | Progress |
                |---------|----------|
                | Pre Order | 0% |
                | Order di Supplier | 10% |
                | Warehouse | 20% |
                | Fitting 1 | 30% |
                | Amplas | 40% |
                | Revisi 1 | 50% |
                | Spray | 60% |
                | Fitting 2 | 70% |
                | Revisi Fitting 2 | 80% |
                | Packaging | 90% |
                | Pengiriman | 100% |
                """)
            
            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
            
            with btn_col1:
                if st.button("🔄 RESET", use_container_width=True):
                    st.rerun()
            
            with btn_col2:
                if st.button("💾 SAVE PROGRESS", use_container_width=True, type="primary"):
                    # Get current history
                    try:
                        history = json.loads(order_data["History"]) if order_data["History"] else []
                    except:
                        history = []
                    
                    # Add new history entry
                    update_details = f"Progress: {order_data['Progress']} → {progress_value}%, Proses: {order_data['Proses Saat Ini']} → {current_proses}"
                    if notes:
                        update_details += f", Note: {notes}"
                    
                    history.append(add_history_entry(selected_order, "Progress Updated", update_details))
                    
                    # Update data
                    st.session_state["data_produksi"].at[order_idx, "Progress"] = f"{progress_value}%"
                    st.session_state["data_produksi"].at[order_idx, "Proses Saat Ini"] = current_proses
                    st.session_state["data_produksi"].at[order_idx, "History"] = json.dumps(history)
                    
                    # Update keterangan if notes provided
                    if notes:
                        current_keterangan = str(order_data["Keterangan"]) if order_data["Keterangan"] else ""
                        new_keterangan = f"{current_keterangan}\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] {notes}".strip()
                        st.session_state["data_produksi"].at[order_idx, "Keterangan"] = new_keterangan
                    
                    if save_data(st.session_state["data_produksi"]):
                        new_tracking = get_tracking_status_from_progress(f"{progress_value}%", order_data["Status"])
                        st.success(f"✅ Progress order {selected_order} berhasil diupdate! Tracking Status: {new_tracking}")
                        st.balloons()
                        st.rerun()
            
            # History Section
            st.markdown("---")
            st.subheader("📜 Riwayat Update")
            
            try:
                history = json.loads(order_data["History"]) if order_data["History"] else []
            except:
                history = []
            
            if history:
                for entry in reversed(history[-10:]):  # Show last 10 entries
                    timestamp = entry.get("timestamp", "")
                    action = entry.get("action", "")
                    details = entry.get("details", "")
                    
                    st.markdown(f"""
                    <div style='background-color: #1F2937; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 3px solid #3B82F6;'>
                        <strong style='color: #60A5FA;'>⏱️ {timestamp}</strong><br>
                        <strong style='color: #10B981;'>{action}</strong><br>
                        <span style='color: #D1D5DB;'>{details}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Belum ada riwayat update untuk order ini")
        else:
            st.info("📝 Belum ada order untuk diupdate.")
            
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
        
        # Simplified filters
        track_col1, track_col2 = st.columns(2)
        with track_col1:
            filter_track_buyer = st.multiselect("Filter Buyer", df["Buyer"].unique().tolist(), key="track_buyer_filter")
        with track_col2:
            search_track_order = st.text_input("🔍 Cari Order ID", key="track_search")
        
        df_track_filtered = df.copy()
        if filter_track_buyer:
            df_track_filtered = df_track_filtered[df_track_filtered["Buyer"].isin(filter_track_buyer)]
        if search_track_order:
            df_track_filtered = df_track_filtered[df_track_filtered["Order ID"].str.contains(search_track_order, case=False, na=False)]
        
        st.markdown("---")
        
        # Summary cards at the top
        sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
        
        total_orders = len(df_track_filtered)
        pending_count = 0
        ongoing_count = 0
        done_count = 0
        
        for idx, row in df_track_filtered.iterrows():
            tracking = get_tracking_status_from_progress(row['Progress'], row['Status'])
            if tracking == "Pending":
                pending_count += 1
            elif tracking == "On Going":
                ongoing_count += 1
            elif tracking == "Done":
                done_count += 1
        
        sum_col1.metric("📦 Total Orders", total_orders)
        sum_col2.metric("⏳ Pending", pending_count)
        sum_col3.metric("🔄 On Going", ongoing_count)
        sum_col4.metric("✅ Done", done_count)
        
        st.markdown("---")
        
        # Table view - Flat list of all orders
        st.subheader("📋 All Orders with Stage Details")
        
        # Header
        header_cols = st.columns([1, 1, 1, 1.5, 0.6, 1.2, 0.9, 1])
        header_cols[0].markdown("**Order ID**")
        header_cols[1].markdown("**Buyer**")
        header_cols[2].markdown("**Produk**")
        header_cols[3].markdown("**Current Stage**")
        header_cols[4].markdown("**Qty**")
        header_cols[5].markdown("**Due Date**")
        header_cols[6].markdown("**Progress**")
        header_cols[7].markdown("**Tracking**")
        
        # Sort by current stage order
        stages = get_tracking_stages()
        df_track_filtered['Stage_Order'] = df_track_filtered['Proses Saat Ini'].apply(
            lambda x: stages.index(x) if x in stages else 999
        )
        df_track_filtered = df_track_filtered.sort_values(['Stage_Order', 'Order Date'])
        
        for idx, row in df_track_filtered.iterrows():
            order_cols = st.columns([1, 1, 1, 1.5, 0.6, 1.2, 0.9, 1])
            
            order_cols[0].write(row['Order ID'])
            order_cols[1].write(row['Buyer'])
            order_cols[2].write(row['Produk'][:20] + "..." if len(row['Produk']) > 20 else row['Produk'])
            
            # Current stage with icon
            stage_idx = stages.index(row['Proses Saat Ini']) if row['Proses Saat Ini'] in stages else -1
            stage_display = f"**{stage_idx + 1}. {row['Proses Saat Ini']}**" if stage_idx >= 0 else row['Proses Saat Ini']
            order_cols[3].markdown(stage_display)
            
            order_cols[4].write(f"{row['Qty']} pcs")
            
            # Due date with color
            due_date = row['Due Date']
            days_until_due = (due_date - datetime.date.today()).days
            if days_until_due < 0:
                date_color = "#EF4444"
                date_icon = "🔴"
            elif days_until_due <= 7:
                date_color = "#F59E0B"
                date_icon = "🟡"
            else:
                date_color = "#10B981"
                date_icon = "🟢"
            order_cols[5].markdown(f"<span style='color: {date_color};'>{date_icon} {str(due_date)}</span>", unsafe_allow_html=True)
            
            # Progress bar
            try:
                progress_pct = int(row['Progress'].rstrip('%')) if row['Progress'] else 0
            except:
                progress_pct = 0
            
            order_cols[6].progress(progress_pct / 100)
            
            # Tracking status
            tracking_status = get_tracking_status_from_progress(row['Progress'], row['Status'])
            tracking_colors = {
                "Pending": ("⏳", "#6B7280"),
                "On Going": ("🔄", "#3B82F6"),
                "Done": ("✅", "#10B981")
            }
            track_icon, track_color = tracking_colors.get(tracking_status, ("⚪", "#6B7280"))
            order_cols[7].markdown(f"<span style='color: {track_color}; font-weight: bold;'>{track_icon} {tracking_status}</span>", unsafe_allow_html=True)
            
            # Expandable details
            with st.expander(f"📝 Details: {row['Order ID']}", expanded=False):
                detail_col1, detail_col2 = st.columns(2)
                with detail_col1:
                    st.markdown(f"**Order Date:** {row['Order Date']}")
                    st.markdown(f"**Status:** {row['Status']}")
                    st.markdown(f"**Priority:** {row['Prioritas']}")
                with detail_col2:
                    st.markdown(f"**Full Product:** {row['Produk']}")
                    if row['Keterangan']:
                        st.markdown(f"**Notes:** {row['Keterangan']}")
        
        # Progress Distribution Chart
        st.markdown("---")
        st.subheader("📈 Distribution by Process Stage")
        
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
        
        # Timeline alerts
        st.markdown("---")
        st.subheader("⚠️ Timeline Alerts")
        
        timeline_col1, timeline_col2 = st.columns(2)
        
        with timeline_col1:
            st.markdown("**🔴 Overdue Orders**")
            overdue_orders = df_track_filtered[
                (df_track_filtered["Due Date"] < datetime.date.today()) & 
                (df_track_filtered["Progress"] != "100%") &
                (df_track_filtered["Status"] != "Rejected")
            ]
            if not overdue_orders.empty:
                for idx, row in overdue_orders.iterrows():
                    days_overdue = (datetime.date.today() - row["Due Date"]).days
                    st.error(f"**{row['Order ID']}** - {row['Produk'][:30]} | ⏰ {days_overdue} hari terlambat")
            else:
                st.success("✅ Tidak ada order yang terlambat")
        
        with timeline_col2:
            st.markdown("**🟡 Upcoming Deadlines (7 Days)**")
            upcoming_orders = df_track_filtered[
                (df_track_filtered["Due Date"] >= datetime.date.today()) & 
                (df_track_filtered["Due Date"] <= datetime.date.today() + datetime.timedelta(days=7)) &
                (df_track_filtered["Progress"] != "100%") &
                (df_track_filtered["Status"] != "Rejected")
            ]
            if not upcoming_orders.empty:
                for idx, row in upcoming_orders.iterrows():
                    days_left = (row["Due Date"] - datetime.date.today()).days
                    st.warning(f"**{row['Order ID']}** - {row['Produk'][:30]} | ⏰ {days_left} hari lagi")
            else:
                st.success("✅ Tidak ada deadline mendesak")
        
    else:
        st.info("📝 Belum ada order untuk di-tracking.")

# ===== MENU: DATABASE =====
elif st.session_state["menu"] == "Database":
    st.header("💾 DATABASE MANAGEMENT")
    
    tab1, tab2 = st.tabs(["👥 Buyers Database", "📦 Products Database"])
    
    with tab1:
        st.subheader("👥 Manage Buyers")
        
        buyers = st.session_state["buyers"]
        
        # Initialize edit mode in session state
        if "edit_buyer_mode" not in st.session_state:
            st.session_state["edit_buyer_mode"] = False
            st.session_state["edit_buyer_idx"] = None
        
        # Edit Form - Show at top when in edit mode
        if st.session_state["edit_buyer_mode"] and st.session_state["edit_buyer_idx"] is not None:
            idx = st.session_state["edit_buyer_idx"]
            selected_buyer = buyers[idx]
            
            st.markdown("### ✏️ Edit Buyer")
            with st.form("edit_buyer_form_top"):
                st.markdown(f"**Editing: {selected_buyer['name']}**")
                col1, col2 = st.columns(2)
                with col1:
                    edit_name = st.text_input("Nama Buyer *", value=selected_buyer["name"])
                    edit_address = st.text_area("Alamat", value=selected_buyer["address"], height=100)
                with col2:
                    edit_contact = st.text_input("Contact", value=selected_buyer["contact"])
                    edit_profile = st.text_area("Profile", value=selected_buyer["profile"], height=100)
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    update_buyer = st.form_submit_button("💾 Update Buyer", use_container_width=True, type="primary")
                with col_btn2:
                    delete_buyer = st.form_submit_button("🗑️ Delete Buyer", use_container_width=True, type="secondary")
                with col_btn3:
                    cancel_edit = st.form_submit_button("❌ Cancel", use_container_width=True)
                
                if update_buyer:
                    if edit_name:
                        buyers[idx] = {
                            "name": edit_name,
                            "address": edit_address,
                            "contact": edit_contact,
                            "profile": edit_profile
                        }
                        st.session_state["buyers"] = buyers
                        if save_buyers(buyers):
                            st.success(f"✅ Data buyer '{edit_name}' berhasil diupdate!")
                            st.session_state["edit_buyer_mode"] = False
                            st.session_state["edit_buyer_idx"] = None
                            st.rerun()
                    else:
                        st.warning("⚠️ Nama buyer tidak boleh kosong")
                
                if delete_buyer:
                    buyer_name = buyers[idx]["name"]
                    buyers.pop(idx)
                    st.session_state["buyers"] = buyers
                    if save_buyers(buyers):
                        st.success(f"✅ Buyer '{buyer_name}' berhasil dihapus!")
                        st.session_state["edit_buyer_mode"] = False
                        st.session_state["edit_buyer_idx"] = None
                        st.rerun()
                
                if cancel_edit:
                    st.session_state["edit_buyer_mode"] = False
                    st.session_state["edit_buyer_idx"] = None
                    st.rerun()
            
            st.markdown("---")
        
        # Display current buyers in table format with Edit buttons
        st.markdown("### Current Buyers Database")
        if buyers:
            # Create header
            header_cols = st.columns([2, 2.5, 2, 2.5, 0.8])
            header_cols[0].markdown("**Nama Buyer**")
            header_cols[1].markdown("**Alamat**")
            header_cols[2].markdown("**Contact**")
            header_cols[3].markdown("**Profile**")
            header_cols[4].markdown("**Action**")
            
            # Display each buyer row
            for idx, buyer in enumerate(buyers):
                row_cols = st.columns([2, 2.5, 2, 2.5, 0.8])
                row_cols[0].write(buyer["name"])
                row_cols[1].write(buyer["address"] if buyer["address"] else "-")
                row_cols[2].write(buyer["contact"] if buyer["contact"] else "-")
                row_cols[3].write(buyer["profile"][:50] + "..." if len(buyer["profile"]) > 50 else (buyer["profile"] if buyer["profile"] else "-"))
                
                with row_cols[4]:
                    if st.button("✏️", key=f"edit_buyer_{idx}", help="Edit Buyer", use_container_width=True):
                        st.session_state["edit_buyer_mode"] = True
                        st.session_state["edit_buyer_idx"] = idx
                        st.rerun()
                
                st.markdown("<div style='margin: 5px 0; border-bottom: 1px solid #374151;'></div>", unsafe_allow_html=True)
        else:
            st.info("Belum ada buyer yang terdaftar")
        
        st.markdown("---")
        
        # Add new buyer with multiple fields
        st.markdown("### ➕ Add New Buyer")
        with st.form("add_buyer_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                new_buyer_name = st.text_input("Nama Buyer *", placeholder="Contoh: PT. ABC Indonesia")
                new_buyer_address = st.text_area("Alamat", placeholder="Jl. Example No. 123, Jakarta", height=100)
            with col2:
                new_buyer_contact = st.text_input("Contact Person / Phone", placeholder="John Doe / +62812345678")
                new_buyer_profile = st.text_area("Profile (Optional)", placeholder="Informasi tambahan tentang buyer...", height=100)
            
            submit_buyer = st.form_submit_button("➕ Add Buyer", use_container_width=True, type="primary")
            
            if submit_buyer:
                if new_buyer_name:
                    # Check if buyer already exists
                    existing_names = [b["name"] for b in buyers]
                    if new_buyer_name not in existing_names:
                        new_buyer_data = {
                            "name": new_buyer_name,
                            "address": new_buyer_address,
                            "contact": new_buyer_contact,
                            "profile": new_buyer_profile
                        }
                        buyers.append(new_buyer_data)
                        st.session_state["buyers"] = buyers
                        if save_buyers(buyers):
                            st.success(f"✅ Buyer '{new_buyer_name}' berhasil ditambahkan!")
                            st.rerun()
                    else:
                        st.warning("⚠️ Buyer dengan nama tersebut sudah ada dalam database")
                else:
                    st.warning("⚠️ Nama buyer tidak boleh kosong")
    
    with tab2:
        st.subheader("📦 Manage Products")
        
        products = st.session_state["products"]
        
        # Display current products
        st.markdown("### Current Products")
        if products:
            product_df = pd.DataFrame({"Product Name": products})
            st.dataframe(product_df, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada produk yang terdaftar")
        
        st.markdown("---")
        
        # Add new product
        st.markdown("### ➕ Add New Product")
        col1, col2 = st.columns([3, 1])
        with col1:
            new_product = st.text_input("", placeholder="Masukkan nama produk baru", label_visibility="collapsed", key="new_product_input")
        with col2:
            if st.button("➕ Add", use_container_width=True, type="primary", key="add_product_btn"):
                if new_product and new_product not in products:
                    products.append(new_product)
                    st.session_state["products"] = products
                    if save_products(products):
                        st.success(f"✅ Produk '{new_product}' berhasil ditambahkan!")
                        st.rerun()
                elif new_product in products:
                    st.warning("⚠️ Produk sudah ada dalam database")
                else:
                    st.warning("⚠️ Nama produk tidak boleh kosong")
        
        # Delete product
        st.markdown("---")
        st.markdown("### 🗑️ Delete Product")
        if products:
            col1, col2 = st.columns([3, 1])
            with col1:
                product_to_delete = st.selectbox("", products, label_visibility="collapsed", key="delete_product_select")
            with col2:
                if st.button("🗑️ Delete", use_container_width=True, type="secondary", key="delete_product_btn"):
                    products.remove(product_to_delete)
                    st.session_state["products"] = products
                    if save_products(products):
                        st.success(f"✅ Produk '{product_to_delete}' berhasil dihapus!")
                        st.rerun()

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
        # Filter options
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        with col_filter1:
            filter_buyers = st.multiselect("Filter Buyer", df["Buyer"].unique(), default=df["Buyer"].unique())
        with col_filter2:
            filter_statuses = st.multiselect("Filter Status", ["Accepted", "Pending", "Rejected"], default=["Accepted", "Pending"])
        with col_filter3:
            show_progress = st.checkbox("Tampilkan Progress Detail", value=True)
        
        # Apply filters
        df_filtered = df[df["Buyer"].isin(filter_buyers) & df["Status"].isin(filter_statuses)].copy()
        
        if not df_filtered.empty:
            # Calculate progress
            df_filtered['Progress_Num'] = df_filtered['Progress'].str.rstrip('%').astype('float')
            df_filtered['Order Date'] = pd.to_datetime(df_filtered['Order Date'])
            df_filtered['Due Date'] = pd.to_datetime(df_filtered['Due Date'])
            df_filtered['Duration'] = (df_filtered['Due Date'] - df_filtered['Order Date']).dt.days
            
            # Prepare data for Gantt chart
            gantt_data = []
            
            for idx, row in df_filtered.iterrows():
                task_name = f"{row['Order ID']} - {row['Produk'][:25]}"
                progress_pct = row['Progress_Num']
                
                # Bar utama (total duration)
                gantt_data.append(dict(
                    Task=task_name,
                    Start=row['Order Date'].strftime('%Y-%m-%d'),
                    Finish=row['Due Date'].strftime('%Y-%m-%d'),
                    Resource=row['Buyer'],
                    Description=f"Status: {row['Status']} | Progress: {progress_pct:.0f}% | {row['Proses Saat Ini']}"
                ))
            
            # Create Gantt chart
            if gantt_data:
                # Define colors by buyer
                buyer_colors = {
                    'Belhome': '#3B82F6',
                    'Indoteak': '#8B5CF6',
                    'WMG': '#F59E0B',
                    'SDM': '#EF4444',
                    'Remar': '#EC4899',
                    'ITM': '#14B8A6',
                    'San Marco': '#6366F1'
                }
                
                colors = []
                for buyer in df_filtered['Buyer'].unique():
                    colors.append(buyer_colors.get(buyer, '#10B981'))
                
                fig = ff.create_gantt(
                    gantt_data,
                    colors=colors,
                    index_col='Resource',
                    show_colorbar=False,
                    showgrid_x=True,
                    showgrid_y=True,
                    title='Production Schedule with Progress Tracking',
                    bar_width=0.5,
                    group_tasks=True
                )
                
                # Get today's date
                today = datetime.date.today()
                
                # Add shapes for today's line (using add_shape instead of add_vline)
                fig.add_shape(
                    type="line",
                    x0=today,
                    y0=0,
                    x1=today,
                    y1=len(df_filtered),
                    line=dict(color="red", width=2, dash="dash")
                )
                
                # Add annotation for today
                fig.add_annotation(
                    x=today,
                    y=len(df_filtered),
                    text="Hari Ini",
                    showarrow=False,
                    yshift=10,
                    font=dict(color="red", size=12)
                )
                
                # Add progress markers for each order
                for idx, row in df_filtered.iterrows():
                    progress_pct = row['Progress_Num']
                    
                    if progress_pct > 0 and progress_pct < 100:
                        # Find task position in reversed list
                        task_idx = len(df_filtered) - 1 - list(df_filtered.index).index(idx)
                        
                        # Add progress line at today's position
                        fig.add_shape(
                            type="line",
                            x0=today,
                            y0=task_idx - 0.4,
                            x1=today,
                            y1=task_idx + 0.4,
                            line=dict(color='#10B981', width=4)
                        )
                        
                        # Add progress percentage text
                        fig.add_annotation(
                            x=today,
                            y=task_idx + 0.5,
                            text=f"{progress_pct:.0f}%",
                            showarrow=False,
                            font=dict(color='#10B981', size=11, family='Arial Black'),
                            yshift=5
                        )
                    elif progress_pct == 100:
                        # Mark completed orders at due date
                        task_idx = len(df_filtered) - 1 - list(df_filtered.index).index(idx)
                        
                        fig.add_annotation(
                            x=row['Due Date'],
                            y=task_idx,
                            text="✓ 100%",
                            showarrow=False,
                            font=dict(color='#10B981', size=11, family='Arial Black'),
                            xshift=35
                        )
                
                # Update layout
                fig.update_layout(
                    height=max(400, len(df_filtered) * 60),
                    xaxis_title="Timeline",
                    yaxis_title="Orders",
                    hovermode='closest',
                    font=dict(size=10),
                    plot_bgcolor='#1F2937',
                    paper_bgcolor='#111827',
                    xaxis=dict(gridcolor='#374151'),
                    yaxis=dict(gridcolor='#374151')
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Legend explanation
                st.markdown("---")
                col_legend1, col_legend2, col_legend3 = st.columns(3)
                with col_legend1:
                    st.markdown("**📊 Legend:**")
                    st.markdown("📊 **Bar Horizontal** = Total durasi order")
                    st.markdown("🟢 **Garis Vertikal** = Progress saat ini")
                    st.markdown("🔴 **Garis Putus-putus** = Hari ini")
                with col_legend2:
                    st.markdown("**🎨 Color Code:**")
                    st.markdown("🟦 Belhome | 🟪 Indoteak | 🟧 WMG")
                    st.markdown("🔴 SDM | 🟣 Remar | 🟢 ITM | 🔵 San Marco")
                with col_legend3:
                    st.markdown("**ℹ️ Info:**")
                    st.markdown(f"📦 Total Orders: {len(df_filtered)}")
                    st.markdown(f"📅 Today: {today.strftime('%Y-%m-%d')}")
                
                # Summary table with progress
                st.markdown("---")
                st.subheader("📋 Order Timeline Summary")
                
                if show_progress:
                    summary_df = df_filtered[["Order ID", "Produk", "Buyer", "Order Date", "Due Date", 
                                             "Progress", "Proses Saat Ini", "Status"]].copy()
                    summary_df["Order Date"] = summary_df["Order Date"].dt.strftime('%Y-%m-%d')
                    summary_df["Due Date"] = summary_df["Due Date"].dt.strftime('%Y-%m-%d')
                    summary_df["Duration (days)"] = df_filtered["Duration"].values
                    
                    # Calculate days from start and days to deadline
                    summary_df["Days from Start"] = (today - df_filtered["Order Date"].dt.date).apply(lambda x: x.days)
                    summary_df["Days to Deadline"] = (df_filtered["Due Date"].dt.date - today).apply(lambda x: x.days)
                else:
                    summary_df = df_filtered[["Order ID", "Produk", "Buyer", "Order Date", "Due Date", "Status", "Progress"]].copy()
                    summary_df["Order Date"] = summary_df["Order Date"].dt.strftime('%Y-%m-%d')
                    summary_df["Due Date"] = summary_df["Due Date"].dt.strftime('%Y-%m-%d')
                    summary_df["Duration (days)"] = df_filtered["Duration"].values
                
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
                
                # Progress Analysis
                st.markdown("---")
                st.subheader("📈 Progress Analysis")
                
                analysis_col1, analysis_col2 = st.columns(2)
                
                with analysis_col1:
                    st.markdown("**⚠️ Orders Needing Attention**")
                    for idx, row in df_filtered.iterrows():
                        days_from_start = (today - row['Order Date'].date()).days
                        days_to_deadline = (row['Due Date'].date() - today).days
                        expected_progress = min(100, (days_from_start / row['Duration'] * 100)) if row['Duration'] > 0 else 0
                        actual_progress = row['Progress_Num']
                        
                        if actual_progress < expected_progress - 10 and days_to_deadline > 0:  # 10% tolerance
                            st.warning(f"🔔 **{row['Order ID']}** - Progress: {actual_progress:.0f}% (Expected: {expected_progress:.0f}%)")
                
                with analysis_col2:
                    st.markdown("**✅ On-Track Orders**")
                    on_track_count = 0
                    for idx, row in df_filtered.iterrows():
                        days_from_start = (today - row['Order Date'].date()).days
                        expected_progress = min(100, (days_from_start / row['Duration'] * 100)) if row['Duration'] > 0 else 0
                        actual_progress = row['Progress_Num']
                        
                        if actual_progress >= expected_progress - 10:
                            on_track_count += 1
                    
                    st.success(f"✅ {on_track_count} dari {len(df_filtered)} orders on-track atau ahead")
                    
            else:
                st.warning("Tidak ada data untuk ditampilkan dalam Gantt Chart")
        else:
            st.warning("Tidak ada data sesuai filter yang dipilih")
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
            
            fig_product = px.bar(product_stats, y="Total Qty",
                               labels={'index': 'Produk', 'Total Qty': 'Total Quantity'},
                               title="Top 10 Products by Quantity",
                               color="Total Qty",
                               color_continuous_scale='Greens')
            st.plotly_chart(fig_product, use_container_width=True)
        
        with tab4:
            st.subheader("Analysis by Timeline")
            
            df_copy = df.copy()
            df_copy['Order Month'] = pd.to_datetime(df_copy['Order Date']).dt.to_period('M').astype(str)
            monthly_orders = df_copy.groupby('Order Month').agg({
                'Order ID': 'count',
                'Qty': 'sum'
            }).rename(columns={'Order ID': 'Total Orders', 'Qty': 'Total Qty'})
            
            st.dataframe(monthly_orders, use_container_width=True)
            
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
st.caption(f"© 2025 PPIC-DSS System | v5.0 Enhanced | 💾 Database: {DATABASE_PATH}")
st.caption("Features: Dashboard • Input Order • Order List • Progress Update • Production Tracking • Database Management • Frozen Zone • Analytics • Gantt Chart")
