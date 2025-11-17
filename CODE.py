import streamlit as st
import pandas as pd
import datetime
import json
import os
import plotly.express as px
import plotly.figure_factory as ff
from streamlit.components.v1 import html

# ===== KONFIGURASI DATABASE =====
DATABASE_PATH = "ppic_data.json"
BUYER_DB_PATH = "buyers.json"
PRODUCT_DB_PATH = "products.json"
PROCUREMENT_DB_PATH = "procurement.json"
CONTAINER_DB_PATH = "containers.json"

st.set_page_config(
    page_title="PPIC-DSS System", 
    layout="wide",
    page_icon="🏭",
    initial_sidebar_state="collapsed"
)

# ===== CONTAINER SPECIFICATIONS =====
CONTAINER_TYPES = {
    "20 Feet": {
        "capacity_cbm": 33.0,
        "max_weight_kg": 24000,
        "color": "#3B82F6"
    },
    "40 Feet": {
        "capacity_cbm": 67.0,
        "max_weight_kg": 30000,
        "color": "#10B981"
    },
    "40 HC (High Cube)": {
        "capacity_cbm": 76.0,
        "max_weight_kg": 30000,
        "color": "#8B5CF6"
    }
}

# ===== CSS RESPONSIVE & COMPACT =====
def inject_responsive_css():
    st.markdown("""
    <style>
    /* Reduce top padding and margins */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Compact header spacing */
    h1, h2, h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Reduce back button spacing */
    [data-testid="stButton"] {
        margin-top: 0 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Form input alignment */
    .stNumberInput, .stTextInput, .stSelectbox, .stDateInput {
        margin-bottom: 0.3rem !important;
    }
    
    /* Align form elements */
    div[data-testid="column"] {
        padding: 0 0.5rem !important;
    }
    
    /* Enable Tab navigation between inputs */
    input, select, textarea {
        tab-index: auto !important;
    }
    
    /* Mobile responsive */
    @media (max-width: 767px) {
        [data-testid="stSidebar"] {
            position: fixed;
            z-index: 999;
            width: 80vw !important;
        }
        .main .block-container {
            padding: 0.5rem 0.3rem !important;
        }
        h1 { font-size: 1.3rem !important; }
        h2 { font-size: 1.1rem !important; }
        .stButton button { width: 100% !important; }
    }
    
    /* Scrollable table container */
    .recent-orders-container {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #374151;
        border-radius: 5px;
        padding: 10px;
    }
    
    /* WIP Cards styling */
    .wip-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    .finished-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    .shipping-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    /* Container load visualization */
    .container-visual {
        background: #1F2937;
        border: 2px solid #3B82F6;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .container-progress {
        height: 40px;
        background: #374151;
        border-radius: 5px;
        overflow: hidden;
        position: relative;
    }
    
    .container-fill {
        height: 100%;
        background: linear-gradient(90deg, #10B981 0%, #3B82F6 100%);
        transition: width 0.3s ease;
    }
    </style>
    
    <script>
    // Enable Tab navigation between form fields
    document.addEventListener('DOMContentLoaded', function() {
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach((input, index) => {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const nextInput = inputs[index + 1];
                    if (nextInput) {
                        nextInput.focus();
                    }
                }
            });
        });
    });
    </script>
    """, unsafe_allow_html=True)

inject_responsive_css()

# ===== FUNGSI DATABASE =====
def load_data():
    if os.path.exists(DATABASE_PATH):
        try:
            with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                df = pd.DataFrame(data)
                if not df.empty:
                    df['Order Date'] = pd.to_datetime(df['Order Date']).dt.date
                    df['Due Date'] = pd.to_datetime(df['Due Date']).dt.date
                    if 'History' not in df.columns:
                        df['History'] = df.apply(lambda x: json.dumps([]), axis=1)
                    # Add new columns if not exist
                    if 'Product CBM' not in df.columns:
                        df['Product CBM'] = 0.0
                return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
    return pd.DataFrame(columns=[
        "Order ID", "Order Date", "Buyer", "Produk", "Qty", "Due Date", 
        "Prioritas", "Progress", "Proses Saat Ini", "Keterangan",
        "Tracking", "History", "Material", "Finishing", "Description",
        "Product Size P", "Product Size L", "Product Size T", "Product CBM",
        "Packing Size P", "Packing Size L", "Packing Size T",
        "CBM per Pcs", "Total CBM", "Image Path"
    ])

def save_data(df):
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
    if os.path.exists(BUYER_DB_PATH):
        try:
            with open(BUYER_DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data and isinstance(data[0], str):
                    return [{"name": buyer, "address": "", "contact": "", "profile": ""} for buyer in data]
                return data
        except:
            pass
    return []

def save_buyers(buyers):
    try:
        with open(BUYER_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(buyers, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def get_buyer_names():
    buyers = st.session_state["buyers"]
    return [b["name"] for b in buyers]

def load_products():
    if os.path.exists(PRODUCT_DB_PATH):
        try:
            with open(PRODUCT_DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_products(products):
    try:
        with open(PRODUCT_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def load_procurement():
    if os.path.exists(PROCUREMENT_DB_PATH):
        try:
            with open(PROCUREMENT_DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Fix: Ensure it returns a list, not dict
                if isinstance(data, dict):
                    return []
                return data
        except:
            pass
    return []

def save_procurement(procurement_data):
    try:
        with open(PROCUREMENT_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(procurement_data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

# ===== CONTAINER DATABASE =====
def load_containers():
    if os.path.exists(CONTAINER_DB_PATH):
        try:
            with open(CONTAINER_DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_containers(containers_data):
    try:
        with open(CONTAINER_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(containers_data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def get_tracking_stages():
    return [
        "Pre Order", "Order di Supplier", "Warehouse", "Fitting 1",
        "Amplas", "Revisi 1", "Spray", "Fitting 2",
        "Revisi Fitting 2", "Packaging", "Pengiriman"
    ]

def init_tracking_data():
    stages = get_tracking_stages()
    return {stage: {"qty": 0} for stage in stages}

def get_tracking_status_from_progress(progress_str):
    try:
        progress_pct = int(progress_str.rstrip('%')) if progress_str else 0
    except:
        progress_pct = 0
    
    if progress_pct >= 100:
        return "Done"
    elif progress_pct > 0:
        return "On Going"
    else:
        return "On Going"

def add_history_entry(order_id, action, details):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "timestamp": timestamp,
        "action": action,
        "details": details
    }

def save_uploaded_image(uploaded_file, order_id, product_idx):
    if uploaded_file is not None:
        images_dir = "product_images"
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        
        file_extension = uploaded_file.name.split('.')[-1]
        filename = f"{order_id}_product{product_idx}.{file_extension}"
        filepath = os.path.join(images_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return filepath
    return None

def calculate_cbm(p, l, t):
    """Calculate CBM from dimensions in cm with maximum precision"""
    try:
        p_val = float(p) if p else 0
        l_val = float(l) if l else 0
        t_val = float(t) if t else 0
        if p_val > 0 and l_val > 0 and t_val > 0:
            # Return with 6 decimal places precision
            return (p_val * l_val * t_val) / 1000000
        return 0
    except:
        return 0

def get_products_by_buyer(buyer_name):
    """Get unique products for a specific buyer from orders"""
    df = st.session_state["data_produksi"]
    if df.empty or not buyer_name:
        return []
    
    buyer_products = df[df["Buyer"] == buyer_name]["Produk"].unique().tolist()
    return sorted(buyer_products)

def calculate_production_metrics(df):
    """Calculate WIP, Finished Goods, and Shipping metrics"""
    wip_stages = ["Warehouse", "Fitting 1", "Amplas", "Revisi 1", "Spray", "Fitting 2", "Revisi Fitting 2"]
    
    wip_qty = 0
    wip_cbm = 0
    finished_qty = 0  # Packaging stage = Produk Jadi
    finished_cbm = 0
    shipping_qty = 0  # Pengiriman stage
    shipping_cbm = 0
    
    for idx, row in df.iterrows():
        try:
            tracking_data = json.loads(row["Tracking"])
            product_cbm = float(row.get("Product CBM", 0))
            
            for stage, data in tracking_data.items():
                qty = data.get("qty", 0)
                if stage in wip_stages and qty > 0:
                    wip_qty += qty
                    wip_cbm += qty * product_cbm
                elif stage == "Packaging" and qty > 0:
                    finished_qty += qty
                    finished_cbm += qty * product_cbm
                elif stage == "Pengiriman" and qty > 0:
                    shipping_qty += qty
                    shipping_cbm += qty * product_cbm
        except:
            pass
    
    return wip_qty, wip_cbm, finished_qty, finished_cbm, shipping_qty, shipping_cbm

# ===== INISIALISASI =====
if "data_produksi" not in st.session_state:
    st.session_state["data_produksi"] = load_data()
if "buyers" not in st.session_state:
    st.session_state["buyers"] = load_buyers()
if "products" not in st.session_state:
    st.session_state["products"] = load_products()
if "procurement" not in st.session_state:
    st.session_state["procurement"] = load_procurement()
if "containers" not in st.session_state:
    st.session_state["containers"] = load_containers()
if "menu" not in st.session_state:
    st.session_state["menu"] = "Dashboard"

# Initialize container cart
if "container_cart" not in st.session_state:
    st.session_state["container_cart"] = []

# Initialize selected container type
if "selected_container_type" not in st.session_state:
    st.session_state["selected_container_type"] = "40 HC (High Cube)"

# ===== SIDEBAR MENU =====
st.sidebar.title("🏭 PPIC-DSS MENU")
st.sidebar.markdown("---")

menu_options = {
    "📊 Dashboard": "Dashboard",
    "📋 Input Pesanan Baru": "Input",
    "📦 Daftar Order": "Orders",
    "🛒 Procurement": "Procurement",
    "⚙ Update Progress": "Progress",
    "🔍 Tracking Produksi": "Tracking",
    "🚢 Container Loading": "Container",
    "💾 Database": "Database",
    "📈 Analisis & Laporan": "Analytics",
    "📊 Gantt Chart": "Gantt"
}

for label, value in menu_options.items():
    if st.sidebar.button(label, use_container_width=True):
        st.session_state["menu"] = value

st.sidebar.markdown("---")
st.sidebar.info(f"📁 Database: Local Storage")

# ===== BACK BUTTON =====
if st.session_state["menu"] != "Dashboard":
    if st.button("⬅ Back to Dashboard", type="secondary"):
        st.session_state["menu"] = "Dashboard"
        st.rerun()
    st.markdown("---")


# ===== MENU: DASHBOARD =====
if st.session_state["menu"] == "Dashboard":
    st.title("📊 Dashboard PT JAVA CONNECTION")
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        # Calculate tracking status
        df['Tracking Status'] = df.apply(
            lambda row: get_tracking_status_from_progress(row['Progress']), 
            axis=1
        )
        
        # Calculate production metrics
        wip_qty, wip_cbm, finished_qty, finished_cbm, shipping_qty, shipping_cbm = calculate_production_metrics(df)
        
        # ===== SECTION 1: TOP ROW - RECENT ORDERS + KEY METRICS =====
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.markdown("### 🕒 Recent Orders")
            
            # Search/filter for recent orders
            search_recent = st.text_input("🔍 Search orders...", key="search_recent_orders")
            
            recent_df = df.sort_values("Order Date", ascending=False)
            
            if search_recent:
                recent_df = recent_df[
                    recent_df["Order ID"].str.contains(search_recent, case=False, na=False) | 
                    recent_df["Buyer"].str.contains(search_recent, case=False, na=False) |
                    recent_df["Produk"].str.contains(search_recent, case=False, na=False)
                ]
            
            # Scrollable container for recent orders
            with st.container():
                st.markdown('<div class="recent-orders-container">', unsafe_allow_html=True)
                
                for idx, row in recent_df.head(20).iterrows():
                    col1, col2, col3, col4 = st.columns([2.5, 2, 1, 0.5])
                    
                    with col1:
                        st.markdown(f"{row['Order ID']}")
                        st.caption(f"{row['Buyer']} | {row['Produk']}")
                    
                    with col2:
                        st.caption(f"Order: {row['Order Date']}")
                        st.caption(f"Due: {row['Due Date']}")
                    
                    with col3:
                        progress_val = int(row['Progress'].rstrip('%'))
                        st.progress(progress_val / 100)
                        st.caption(f"{row['Progress']}")
                    
                    with col4:
                        if row['Tracking Status'] == 'Done':
                            st.success("✅")
                        else:
                            st.info("🔄")
                    
                    st.divider()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col_right:
            st.markdown("### 📈 Key Metrics")
            
            # Compact metrics
            total_orders = len(df)
            ongoing = len(df[df["Tracking Status"] == "On Going"])
            done = len(df[df["Tracking Status"] == "Done"])
            total_qty = df["Qty"].sum()
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("📦 Total Orders", total_orders)
            col_m2.metric("🔄 On Going", ongoing)
            
            col_m3, col_m4 = st.columns(2)
            col_m3.metric("✅ Done", done)
            col_m4.metric("📊 Total Qty", f"{total_qty:,}")

      
        # Production Status Cards
        st.markdown("#### 🏭 Production Status")
        col_prod1, col_prod2, col_prod3 = st.columns(3)
        
        with col_prod1:
            # WIP Card
            st.markdown(f"""
            <div class="wip-card">
                <h4 style='margin: 0 0 10px 0;'>WIP (Work in Progress)</h4>
                <h2 style='margin: 5px 0; font-size: 2.5rem;'>{wip_qty:,} pcs</h2>
                <p style='margin: 5px 0; font-size: 0.9rem;'>Volume: {wip_cbm:.6f} m³</p>
                <small style='font-size: 0.8rem;'>Warehouse → Revisi Fitting 2</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_prod2:            
            # Finished Goods Card (Packaging)
           st.markdown(f"""
            <div class="finished-card">
                <h4 style='margin: 0 0 10px 0;'>Produk Jadi (Packaging)</h4>
                <h2 style='margin: 5px 0; font-size: 2.5rem;'>{finished_qty:,} pcs</h2>
                <p style='margin: 5px 0; font-size: 0.9rem;'>Volume: {finished_cbm:.6f} m³</p>
                <small style='font-size: 0.8rem;'>Ready for shipment</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_prod3:
            # Shipping Card
             st.markdown(f"""
            <div class="shipping-card">
                <h4 style='margin: 0 0 10px 0;'>Pengiriman</h4>
                <h2 style='margin: 5px 0; font-size: 2.5rem;'>{shipping_qty:,} pcs</h2>
                <p style='margin: 5px 0; font-size: 0.9rem;'>Volume: {shipping_cbm:.6f} m³</p>
                <small style='font-size: 0.8rem;'>In transit / Delivered</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ===== SECTION 2: PRODUCTION CALENDAR =====
        col_cal, col_chart = st.columns([2, 1])
        
        with col_cal:
            st.markdown("### 📅 Production Calendar")
            
            today = datetime.date.today()
            current_month = today.month
            current_year = today.year
            
            col_month, col_year = st.columns(2)
            with col_month:
                months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                         "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                selected_month = st.selectbox("Bulan", months, index=current_month - 1, key="cal_month")
                month_num = months.index(selected_month) + 1
            
            with col_year:
                years = list(range(current_year - 1, current_year + 3))
                selected_year = st.selectbox("Tahun", years, index=1, key="cal_year")
            
            # Filter orders by selected month/year
            df_copy = df.copy()
            df_copy['Due Date'] = pd.to_datetime(df_copy['Due Date'])
            df_month = df_copy[(df_copy['Due Date'].dt.month == month_num) & 
                         (df_copy['Due Date'].dt.year == selected_year)]
            
            if not df_month.empty:
                st.markdown(f"📌 {len(df_month)} orders di bulan ini**")
            
            # Create calendar view
            import calendar
            cal = calendar.monthcalendar(selected_year, month_num)
            
            days = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
            header_cols = st.columns(7)
            for i, day in enumerate(days):
                header_cols[i].markdown(f"<center><b>{day}</b></center>", unsafe_allow_html=True)
            
            for week in cal:
                week_cols = st.columns(7)
                for i, day in enumerate(week):
                    if day == 0:
                        week_cols[i].markdown("")
                    else:
                        date_obj = datetime.date(selected_year, month_num, day)
                        
                        if not df_month.empty:
                            orders_on_date = df_month[df_month['Due Date'].dt.date == date_obj]
                            
                            if len(orders_on_date) > 0:
                                done_count = len(orders_on_date[orders_on_date['Tracking Status'] == 'Done'])
                                if done_count == len(orders_on_date):
                                    bg_color = "#10B981"
                                elif date_obj < today:
                                    bg_color = "#EF4444"
                                elif date_obj == today:
                                    bg_color = "#F59E0B"
                                else:
                                    bg_color = "#3B82F6"
                                
                                week_cols[i].markdown(f"""
                                <div style='background-color: {bg_color}; padding: 5px; border-radius: 5px; text-align: center;'>
                                    <b style='color: white;'>{day}</b><br>
                                    <span style='color: white; font-size: 10px;'>{len(orders_on_date)}</span>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                if date_obj == today:
                                    week_cols[i].markdown(f"<div style='padding: 5px; text-align: center; border: 2px solid #3B82F6; border-radius: 5px;'><b>{day}</b></div>", unsafe_allow_html=True)
                                else:
                                    week_cols[i].markdown(f"<div style='padding: 5px; text-align: center;'>{day}</div>", unsafe_allow_html=True)
                        else:
                            if date_obj == today:
                                week_cols[i].markdown(f"<div style='padding: 5px; text-align: center; border: 2px solid #3B82F6; border-radius: 5px;'><b>{day}</b></div>", unsafe_allow_html=True)
                            else:
                                week_cols[i].markdown(f"<div style='padding: 5px; text-align: center;'>{day}</div>", unsafe_allow_html=True)
        
        with col_chart:
            st.markdown("### 📊 Status Distribution")
            
            status_dist = df["Tracking Status"].value_counts()
            fig_status = px.pie(
                values=status_dist.values, 
                names=status_dist.index,
                color_discrete_map={"On Going": "#3B82F6", "Done": "#10B981"},
                hole=0.4
            )
            fig_status.update_traces(textposition='inside', textinfo='percent+label')
            fig_status.update_layout(showlegend=True, height=250, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_status, use_container_width=True)
        
        st.markdown("---")
        
        # ===== SECTION 3: PRODUCTION PROGRESS BY STAGE =====
        st.markdown("### 🏭 Production Progress by Stage")
        
        stages = get_tracking_stages()
        stage_data = {stage: 0 for stage in stages}
        
        for idx, row in df.iterrows():
            try:
                tracking_data = json.loads(row["Tracking"])
                for stage, data in tracking_data.items():
                    qty = data.get("qty", 0)
                    if stage in stage_data:
                        stage_data[stage] += qty
            except:
                pass
        
        fig_stages = px.bar(
            x=list(stage_data.values()),
            y=list(stage_data.keys()),
            orientation='h',
            color=list(stage_data.values()),
            color_continuous_scale='Blues'
        )
        fig_stages.update_layout(
            xaxis_title="Quantity (pcs)",
            yaxis_title="",
            showlegend=False,
            height=300,
            margin=dict(t=10, b=10)
        )
        st.plotly_chart(fig_stages, use_container_width=True)
    else:
        st.info("📝 Belum ada data. Silakan input pesanan baru.")

# ===== MENU: INPUT PESANAN BARU =====
elif st.session_state["menu"] == "Input":
    st.markdown("<h2 style='margin: 0;'>📋 Form Input Pesanan Baru (Multi-Product)</h2>", unsafe_allow_html=True)
    
    if "input_products" not in st.session_state:
        st.session_state["input_products"] = []
    
    st.markdown("#### 📦 Informasi Order")
    
    col_order1, col_order2, col_order3, col_order4 = st.columns(4)
    
    with col_order1:
        order_date = st.date_input("Order Date", datetime.date.today(), key="input_order_date")
    
    with col_order2:
        buyers_list = get_buyer_names()
        buyer = st.selectbox("Buyer Name", buyers_list, key="input_buyer")
    
    with col_order3:
        due_date = st.date_input("Due Date", datetime.date.today() + datetime.timedelta(days=30), key="input_due")
    
    with col_order4:
        prioritas = st.selectbox("Prioritas", ["High", "Medium", "Low"], key="input_priority")
    
    st.markdown("---")
    st.markdown("#### 📦 Tambah Produk ke Order")
    
    # Create properly aligned columns for form
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.markdown("*Product Information*")
            products_list = st.session_state["products"]
            if products_list:
                produk_option = st.selectbox("Pilih Produk", ["-- Pilih dari Database --"] + products_list, key="form_produk_select")
                if produk_option == "-- Pilih dari Database --":
                    produk_name = st.text_input("Atau ketik nama produk baru", key="form_produk_manual")
                else:
                    produk_name = produk_option
            else:
                produk_name = st.text_input("Nama Produk", key="form_produk")
            
            qty = st.number_input("Quantity (pcs)", min_value=1, value=1, key="form_qty")
            
            uploaded_image = st.file_uploader("Upload Gambar Produk", 
                                             type=['jpg', 'jpeg', 'png'], 
                                             key="form_image")
        
        with col2:
            st.markdown("*Specifications*")
            material = st.text_input("Material", placeholder="Contoh: Kayu Jati, MDF", key="form_material")
            finishing = st.text_input("Finishing", placeholder="Contoh: Natural, Duco Putih", key="form_finishing")
            
            st.markdown("*Product Size (cm)*")
            col_ps1, col_ps2, col_ps3 = st.columns(3)
            with col_ps1:
                prod_p = st.number_input("P", min_value=0.0, value=None, format="%.2f", key="prod_p", step=0.01, placeholder="0.00")
            with col_ps2:
                prod_l = st.number_input("L", min_value=0.0, value=None, format="%.2f", key="prod_l", step=0.01, placeholder="0.00")
            with col_ps3:
                prod_t = st.number_input("T", min_value=0.0, value=None, format="%.2f", key="prod_t", step=0.01, placeholder="0.00")
            
            # Product CBM calculation with 6 decimal places
            product_cbm = calculate_cbm(prod_p, prod_l, prod_t)
            if product_cbm > 0:
                st.success(f"📦 Product CBM: *{product_cbm:.6f} m³*")
            else:
                st.info(f"📦 Product CBM: 0.000000 m³")
        
        with col3:
            st.markdown("*Packing Information*")
            st.markdown("*Packing Size (cm)*")
            col_pack1, col_pack2, col_pack3 = st.columns(3)
            with col_pack1:
                pack_p = st.number_input("P", min_value=0.0, value=None, format="%.2f", key="pack_p", step=0.01, placeholder="0.00")
            with col_pack2:
                pack_l = st.number_input("L", min_value=0.0, value=None, format="%.2f", key="pack_l", step=0.01, placeholder="0.00")
            with col_pack3:
                pack_t = st.number_input("T", min_value=0.0, value=None, format="%.2f", key="pack_t", step=0.01, placeholder="0.00")
            
            # Real-time CBM calculation with 6 decimal places
            cbm_per_pcs = calculate_cbm(pack_p, pack_l, pack_t)
            total_cbm = cbm_per_pcs * qty
            
            if cbm_per_pcs > 0:
                st.success(f"📦 CBM per Pcs: *{cbm_per_pcs:.6f} m³*")
                st.info(f"📦 Total CBM: *{total_cbm:.6f} m³*")
            else:
                st.info(f"📦 CBM per Pcs: 0.000000 m³")
                st.info(f"📦 Total CBM: 0.000000 m³")
            
            description = st.text_area("Description", placeholder="Deskripsi produk...", height=50, key="form_desc")
    
    keterangan = st.text_area("Keterangan Tambahan", placeholder="Catatan khusus...", height=50, key="form_notes")
    
    # Add product button
    if st.button("➕ Tambah Produk ke Order", use_container_width=True, type="primary", key="add_product_btn"):
        if produk_name and qty > 0:
            temp_product = {
                "nama": produk_name,
                "qty": qty,
                "material": material if material else "-",
                "finishing": finishing if finishing else "-",
                "description": description if description else "-",
                "prod_p": prod_p,
                "prod_l": prod_l,
                "prod_t": prod_t,
                "product_cbm": product_cbm,
                "pack_p": pack_p,
                "pack_l": pack_l,
                "pack_t": pack_t,
                "cbm_per_pcs": cbm_per_pcs,
                "total_cbm": total_cbm,
                "keterangan": keterangan if keterangan else "-",
                "image": uploaded_image
            }
            
            st.session_state["input_products"].append(temp_product)
            st.success(f"✅ Produk '{produk_name}' ditambahkan! Total produk: {len(st.session_state['input_products'])}")
            st.rerun()
        else:
            st.warning("⚠ Harap isi nama produk dan quantity!")
    
    if st.session_state["input_products"]:
        st.markdown("---")
        st.markdown("### 📋 Daftar Produk dalam Order Ini")
        
        for idx, product in enumerate(st.session_state["input_products"]):
            with st.expander(f"📦 {idx + 1}. {product['nama']} ({product['qty']} pcs) - CBM: {product['total_cbm']:.6f} m³", expanded=False):
                col_display1, col_display2, col_display3 = st.columns([2, 2, 1])
                
                with col_display1:
                    st.write(f"*Material:* {product['material']}")
                    st.write(f"*Finishing:* {product['finishing']}")
                    st.write(f"*Product Size:* {product['prod_p']:.2f} x {product['prod_l']:.2f} x {product['prod_t']:.2f} cm")
                    st.write(f"*Product CBM:* {product['product_cbm']:.6f} m³")
                
                with col_display2:
                    st.write(f"*Packing Size:* {product['pack_p']:.2f} x {product['pack_l']:.2f} x {product['pack_t']:.2f} cm")
                    st.write(f"*CBM per Pcs:* {product['cbm_per_pcs']:.6f} m³")
                    st.write(f"*Total CBM:* {product['total_cbm']:.6f} m³")
                
                with col_display3:
                    if st.button("🗑 Hapus", key=f"remove_product_{idx}", use_container_width=True):
                        st.session_state["input_products"].pop(idx)
                        st.rerun()
        
        total_cbm_all = sum([p['total_cbm'] for p in st.session_state["input_products"]])
        st.info(f"📦 Total CBM untuk semua produk: *{total_cbm_all:.6f} m³*")
        
        col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 2])
        
        with col_submit1:
            if st.button("🗑 BATAL", use_container_width=True, type="secondary"):
                st.session_state["input_products"] = []
                st.rerun()
        
        with col_submit2:
            if st.button("📤 SUBMIT ORDER", use_container_width=True, type="primary"):
                if buyer and st.session_state["input_products"]:
                    existing_ids = st.session_state["data_produksi"]["Order ID"].tolist() if not st.session_state["data_produksi"].empty else []
                    new_id_num = max([int(oid.split("-")[1]) for oid in existing_ids if "-" in oid], default=2400) + 1
                    new_order_id = f"ORD-{new_id_num}"
                    
                    new_orders = []
                    
                    for prod_idx, product in enumerate(st.session_state["input_products"]):
                        image_path = None
                        if product.get("image"):
                            image_path = save_uploaded_image(product["image"], new_order_id, prod_idx)
                        
                        initial_history = [add_history_entry(f"{new_order_id}-P{prod_idx+1}", "Order Created", 
                        f"Product: {product['nama']}, Priority: {prioritas}")]
                       
                        tracking_data = init_tracking_data()
                        first_stage = get_tracking_stages()[0]
                        tracking_data[first_stage]["qty"] = product["qty"]
                        
                        order_data = {
                            "Order ID": f"{new_order_id}-P{prod_idx+1}",
                            "Order Date": order_date,
                            "Buyer": buyer,
                            "Produk": product["nama"],
                            "Qty": product["qty"],
                            "Material": product["material"],
                            "Finishing": product["finishing"],
                            "Description": product["description"],
                            "Product Size P": product["prod_p"],
                            "Product Size L": product["prod_l"],
                            "Product Size T": product["prod_t"],
                            "Product CBM": product["product_cbm"],
                            "Packing Size P": product["pack_p"],
                            "Packing Size L": product["pack_l"],
                            "Packing Size T": product["pack_t"],
                            "CBM per Pcs": product["cbm_per_pcs"],
                            "Total CBM": product["total_cbm"],
                            "Due Date": due_date,
                            "Prioritas": prioritas,
                            "Progress": "0%",
                            "Proses Saat Ini": first_stage,
                            "Keterangan": product["keterangan"],
                            "Image Path": image_path if image_path else "",
                            "Tracking": json.dumps(tracking_data),
                            "History": json.dumps(initial_history)
                        }
                        
                        new_orders.append(order_data)
                    
                    new_df = pd.DataFrame(new_orders)
                    st.session_state["data_produksi"] = pd.concat(
                        [st.session_state["data_produksi"], new_df], ignore_index=True
                    )
                    
                    if save_data(st.session_state["data_produksi"]):
                        st.success(f"✅ Order {new_order_id} dengan {len(st.session_state['input_products'])} produk berhasil ditambahkan!")
                        st.balloons()
                        st.session_state["input_products"] = []
                        st.rerun()
                else:
                    st.warning("⚠ Harap pilih buyer dan tambahkan minimal 1 produk!")
# ===== MENU: DAFTAR ORDER =====
elif st.session_state["menu"] == "Orders":
    st.header("📦 DAFTAR ORDER")
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_buyer = st.multiselect("Filter Buyer", df["Buyer"].unique().tolist())
        with col_f2:
            search_order = st.text_input("🔍 Cari Order ID / Produk")
        
        df_filtered = df.copy()
        if filter_buyer:
            df_filtered = df_filtered[df_filtered["Buyer"].isin(filter_buyer)]
        if search_order:
            df_filtered = df_filtered[
                df_filtered["Order ID"].str.contains(search_order, case=False, na=False) | 
                df_filtered["Produk"].str.contains(search_order, case=False, na=False)
            ]
        
        st.markdown("---")
        st.info(f"📦 Menampilkan {len(df_filtered)} order dari {df_filtered['Buyer'].nunique()} buyer")
        
        buyers = df_filtered["Buyer"].unique()
        
        for buyer in sorted(buyers):
            buyer_orders = df_filtered[df_filtered["Buyer"] == buyer]
            buyer_count = len(buyer_orders)
            
            with st.expander(f"👤 *{buyer}* ({buyer_count} orders)", expanded=False):
                buyer_orders['Order Date'] = pd.to_datetime(buyer_orders['Order Date'])
                buyer_orders = buyer_orders.sort_values('Order Date', ascending=False)
                
                date_groups = buyer_orders.groupby(buyer_orders['Order Date'].dt.date)
                
                for order_date, date_orders in date_groups:
                    today = datetime.date.today()
                    date_diff = (today - order_date).days
                    
                    if date_diff == 0:
                        date_label = "📅 Hari Ini"
                    elif date_diff == 1:
                        date_label = "📅 Kemarin"
                    elif date_diff <= 7:
                        date_label = f"📅 {date_diff} hari yang lalu"
                    else:
                        date_label = f"📅 {order_date.strftime('%d %b %Y')}"
                    
                    with st.expander(f"{date_label} ({len(date_orders)} orders)", expanded=False):
                        for idx, row in date_orders.iterrows():
                            with st.expander(f"📦 {row['Order ID']} - {row['Produk']}", expanded=False):
                                col1, col2, col3 = st.columns([2, 2, 1])
                                
                                with col1:
                                    st.write(f"*Product:* {row['Produk']}")
                                    st.write(f"*Qty:* {row['Qty']} pcs")
                                    st.write(f"*Material:* {row.get('Material', '-')}")
                                    st.write(f"*Finishing:* {row.get('Finishing', '-')}")
                                    st.write(f"*Product Size:* {row.get('Product Size P', 0)} x {row.get('Product Size L', 0)} x {row.get('Product Size T', 0)} cm")
                                
                                with col2:
                                    st.write(f"*Packing Size:* {row.get('Packing Size P', 0)} x {row.get('Packing Size L', 0)} x {row.get('Packing Size T', 0)} cm")
                                    st.write(f"*CBM per Pcs:* {row.get('CBM per Pcs', 0):.6f} m³")
                                    st.write(f"*Total CBM:* {row.get('Total CBM', 0):.4f} m³")
                                    st.write(f"*Due Date:* {row['Due Date']}")
                                    st.write(f"*Progress:* {row['Progress']}")
                                    st.write(f"*Proses:* {row['Proses Saat Ini']}")
                                
                                with col3:
                                    if row.get('Image Path') and os.path.exists(row['Image Path']):
                                        st.image(row['Image Path'], caption="Product", width=150)
                                    else:
                                        st.info("📷 No image")
                                
                                if row.get('Description') and row['Description'] != '-':
                                    st.markdown("---")
                                    st.markdown(f"📝 Description:** {row['Description']}")
                                
                                if row['Keterangan'] and row['Keterangan'] != '-':
                                    st.markdown(f"💬 Keterangan:** {row['Keterangan']}")
                                
                                st.markdown("---")
                                btn_col1, btn_col2, btn_col3 = st.columns(3)
                                with btn_col1:
                                    if st.button("✏ Edit Order", key=f"edit_order_{idx}", use_container_width=True, type="primary"):
                                        st.session_state["edit_order_mode"] = True
                                        st.session_state["edit_order_index"] = idx
                                        st.rerun()
                                with btn_col2:
                                    if st.button("⚙ Edit Progress", key=f"edit_{idx}", use_container_width=True, type="secondary"):
                                        st.session_state["edit_order_idx"] = idx
                                        st.session_state["menu"] = "Progress"
                                        st.rerun()
                                with btn_col3:
                                    if st.button("🗑 Delete Order", key=f"del_{idx}", use_container_width=True, type="secondary"):
                                        if st.session_state.get(f"confirm_delete_{idx}", False):
                                            st.session_state["data_produksi"].drop(idx, inplace=True)
                                            st.session_state["data_produksi"].reset_index(drop=True, inplace=True)
                                            save_data(st.session_state["data_produksi"])
                                            st.success(f"✅ Order {row['Order ID']} berhasil dihapus!")
                                            del st.session_state[f"confirm_delete_{idx}"]
                                            st.rerun()
                                        else:
                                            st.session_state[f"confirm_delete_{idx}"] = True
                                            st.warning("⚠ Klik sekali lagi untuk konfirmasi hapus!")
                                            st.rerun()
                
                # Check if in edit mode for any order
                if st.session_state.get("edit_order_mode", False) and "edit_order_index" in st.session_state:
                    edit_idx = st.session_state["edit_order_index"]
                    edit_row = st.session_state["data_produksi"].loc[edit_idx]
                    
                    st.markdown("---")
                    st.markdown("## ✏ EDIT ORDER")
                    st.markdown(f"### Editing: {edit_row['Order ID']} - {edit_row['Produk']}")
                    
                    with st.form("edit_order_form"):
                        col_edit1, col_edit2, col_edit3 = st.columns(3)
                        
                        with col_edit1:
                            st.markdown("📦 Order Information**")
                            edit_buyer = st.selectbox("Buyer", get_buyer_names(), 
                                                     index=get_buyer_names().index(edit_row['Buyer']) if edit_row['Buyer'] in get_buyer_names() else 0,
                                                     key="edit_buyer")
                            edit_produk = st.text_input("Nama Produk", value=edit_row['Produk'], key="edit_produk")
                            edit_qty = st.number_input("Quantity (pcs)", min_value=1, value=int(edit_row['Qty']), key="edit_qty")
                            edit_due_date = st.date_input("Due Date", value=edit_row['Due Date'], key="edit_due_date")
                            edit_prioritas = st.selectbox("Prioritas", ["High", "Medium", "Low"],
                                                         index=["High", "Medium", "Low"].index(edit_row['Prioritas']) if edit_row['Prioritas'] in ["High", "Medium", "Low"] else 0,
                                                         key="edit_prioritas")
                        
                        with col_edit2:
                            st.markdown("🔧 Specifications**")
                            edit_material = st.text_input("Material", value=edit_row.get('Material', ''), key="edit_material")
                            edit_finishing = st.text_input("Finishing", value=edit_row.get('Finishing', ''), key="edit_finishing")
                            edit_description = st.text_area("Description", value=edit_row.get('Description', ''), height=100, key="edit_description")
                            
                            st.markdown("*Product Size (cm)*")
                            col_ps1, col_ps2, col_ps3 = st.columns(3)
                            with col_ps1:
                                edit_prod_p = st.number_input("P", min_value=0.0, value=float(edit_row.get('Product Size P', 0)), step=0.1, key="edit_prod_p")
                            with col_ps2:
                                edit_prod_l = st.number_input("L", min_value=0.0, value=float(edit_row.get('Product Size L', 0)), step=0.1, key="edit_prod_l")
                            with col_ps3:
                                edit_prod_t = st.number_input("T", min_value=0.0, value=float(edit_row.get('Product Size T', 0)), step=0.1, key="edit_prod_t")
                        
                        with col_edit3:
                            st.markdown("📦 Packing Information**")
                            st.markdown("*Packing Size (cm)*")
                            col_pack1, col_pack2, col_pack3 = st.columns(3)
                            with col_pack1:
                                edit_pack_p = st.number_input("P", min_value=0.0, value=float(edit_row.get('Packing Size P', 0)), step=0.1, key="edit_pack_p")
                            with col_pack2:
                                edit_pack_l = st.number_input("L", min_value=0.0, value=float(edit_row.get('Packing Size L', 0)), step=0.1, key="edit_pack_l")
                            with col_pack3:
                                edit_pack_t = st.number_input("T", min_value=0.0, value=float(edit_row.get('Packing Size T', 0)), step=0.1, key="edit_pack_t")
                            
                            # Calculate new CBM
                            new_cbm_per_pcs = calculate_cbm(edit_pack_p, edit_pack_l, edit_pack_t)
                            new_total_cbm = new_cbm_per_pcs * edit_qty
                            st.info(f"CBM per Pcs: {new_cbm_per_pcs:.6f} m³")
                            st.info(f"Total CBM: {new_total_cbm:.4f} m³")
                            
                            edit_keterangan = st.text_area("Keterangan", value=edit_row.get('Keterangan', ''), height=80, key="edit_keterangan")
                        
                        col_submit1, col_submit2 = st.columns(2)
                        with col_submit1:
                            submit_edit = st.form_submit_button("💾 Simpan Perubahan", use_container_width=True, type="primary")
                        with col_submit2:
                            cancel_edit = st.form_submit_button("❌ Batal", use_container_width=True, type="secondary")
                        
                        if submit_edit:
                            # Update the order data
                            st.session_state["data_produksi"].at[edit_idx, "Buyer"] = edit_buyer
                            st.session_state["data_produksi"].at[edit_idx, "Produk"] = edit_produk
                            st.session_state["data_produksi"].at[edit_idx, "Qty"] = edit_qty
                            st.session_state["data_produksi"].at[edit_idx, "Due Date"] = edit_due_date
                            st.session_state["data_produksi"].at[edit_idx, "Prioritas"] = edit_prioritas
                            st.session_state["data_produksi"].at[edit_idx, "Material"] = edit_material
                            st.session_state["data_produksi"].at[edit_idx, "Finishing"] = edit_finishing
                            st.session_state["data_produksi"].at[edit_idx, "Description"] = edit_description
                            st.session_state["data_produksi"].at[edit_idx, "Product Size P"] = edit_prod_p
                            st.session_state["data_produksi"].at[edit_idx, "Product Size L"] = edit_prod_l
                            st.session_state["data_produksi"].at[edit_idx, "Product Size T"] = edit_prod_t
                            st.session_state["data_produksi"].at[edit_idx, "Packing Size P"] = edit_pack_p
                            st.session_state["data_produksi"].at[edit_idx, "Packing Size L"] = edit_pack_l
                            st.session_state["data_produksi"].at[edit_idx, "Packing Size T"] = edit_pack_t
                            st.session_state["data_produksi"].at[edit_idx, "CBM per Pcs"] = new_cbm_per_pcs
                            st.session_state["data_produksi"].at[edit_idx, "Total CBM"] = new_total_cbm
                            st.session_state["data_produksi"].at[edit_idx, "Keterangan"] = edit_keterangan
                            
                            # Add history entry
                            try:
                                history = json.loads(edit_row["History"]) if edit_row["History"] else []
                            except:
                                history = []
                            
                            history.append(add_history_entry(edit_row['Order ID'], "Order Edited", 
                                f"Order data updated: Buyer={edit_buyer}, Product={edit_produk}, Qty={edit_qty}"))
                            st.session_state["data_produksi"].at[edit_idx, "History"] = json.dumps(history)
                            
                            if save_data(st.session_state["data_produksi"]):
                                st.success(f"✅ Order {edit_row['Order ID']} berhasil diupdate!")
                                st.session_state["edit_order_mode"] = False
                                del st.session_state["edit_order_index"]
                                st.rerun()
                            else:
                                st.error("Gagal menyimpan perubahan!")
                        
                        if cancel_edit:
                            st.session_state["edit_order_mode"] = False
                            del st.session_state["edit_order_index"]
                            st.rerun()
    else:
        st.info("📝 Belum ada order yang diinput.")
# ===== MENU: CONTAINER LOADING =====
elif st.session_state["menu"] == "Container":
    st.header("🚢 CONTAINER LOADING SIMULATION")
    
    df = st.session_state["data_produksi"]
    
    # Add CSS for order cards
    st.markdown("""
    <style>
    .order-card {
        background: #1F2937;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        transition: all 0.2s ease;
    }
    
    .order-card:hover {
        border-color: #3B82F6;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    if not df.empty:
        tab1, tab2 = st.tabs(["📦 Container Simulator", "📋 Container History"])
        
        with tab1:
            st.info("💡 *Mode Simulasi*: Simulasi loading container berdasarkan packing size yang sudah diinput, tanpa menunggu produksi selesai.")
            
            # Container type selection
            st.markdown("### 🚢 Select Container Type")
            col_type1, col_type2, col_type3, col_type4 = st.columns(4)
            
            with col_type1:
                container_type = st.selectbox(
                    "Container Type",
                    list(CONTAINER_TYPES.keys()),
                    index=list(CONTAINER_TYPES.keys()).index(st.session_state["selected_container_type"]),
                    key="container_type_select"
                )
                st.session_state["selected_container_type"] = container_type
            
            with col_type2:
                selected_specs = CONTAINER_TYPES[container_type]
                st.metric("Capacity", f"{selected_specs['capacity_cbm']} m³")
            
            with col_type3:
                st.metric("Max Weight", f"{selected_specs['max_weight_kg']:,} kg")
            
            with col_type4:
                st.markdown(f"<div style='background: {selected_specs['color']}; height: 40px; border-radius: 5px;'></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 📦 Available Orders for Simulation")
                
                # Filter options
                col_filter1, col_filter2, col_filter3 = st.columns(3)
                
                with col_filter1:
                    filter_buyer = st.multiselect("Filter by Buyer", df["Buyer"].unique().tolist(), key="sim_buyer_filter")
                
                with col_filter2:
                    filter_product = st.multiselect("Filter by Product", df["Produk"].unique().tolist(), key="sim_product_filter")
                
                with col_filter3:
                    search_order = st.text_input("🔍 Search Order ID", key="sim_search")
                
                # Apply filters
                df_filtered = df.copy()
                if filter_buyer:
                    df_filtered = df_filtered[df_filtered["Buyer"].isin(filter_buyer)]
                if filter_product:
                    df_filtered = df_filtered[df_filtered["Produk"].isin(filter_product)]
                if search_order:
                    df_filtered = df_filtered[df_filtered["Order ID"].str.contains(search_order, case=False, na=False)]
                
                # Filter out orders with zero CBM
                df_filtered = df_filtered[df_filtered["Total CBM"] > 0]
                
                st.info(f"📦 {len(df_filtered)} orders available for simulation")
                
                # Display available orders with better styling
                if not df_filtered.empty:
                    # Sort by due date
                    df_filtered_sorted = df_filtered.sort_values("Due Date")
                    
                    for idx, order in df_filtered_sorted.iterrows():
                        # Check if already in cart
                        in_cart = order['Order ID'] in [item['Order ID'] for item in st.session_state["container_cart"]]
                        
                        # Order card - FIXED: Separate variables to avoid f-string issues
                        border_style = "border-color: #10B981; border-width: 2px;" if in_cart else ""
                        status_color = "#10B981" if in_cart else "#9CA3AF"
                        status_text = "✅ In Container" if in_cart else ""
                        
                        st.markdown(f"""
                        <div class="order-card" style="{border_style}">
                            <strong style="color: #3B82F6; font-size: 1.1em;">{order['Order ID']}</strong>
                            <span style="color: {status_color}; margin-left: 10px; font-size: 0.9em;">{status_text}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col_o1, col_o2, col_o3, col_o4 = st.columns([3, 1.5, 1.5, 1])
                        
                        with col_o1:
                            st.caption(f"{order['Buyer']}** | {order['Produk']}")
                            st.caption(f"🏭 Progress: {order['Progress']} | 📅 Due: {order['Due Date']}")
                        
                        with col_o2:
                            st.metric("Qty", f"{order['Qty']} pcs", label_visibility="collapsed")
                            st.caption(f"Qty: {order['Qty']} pcs")
                        
                        with col_o3:
                            cbm_value = order.get('Total CBM', 0)
                            st.metric("CBM", f"{cbm_value:.4f}", label_visibility="collapsed")
                            st.caption(f"CBM: {cbm_value:.6f} m³")
                        
                        with col_o4:
                            if not in_cart:
                                if st.button("➕ Add", key=f"add_sim_{order['Order ID']}", use_container_width=True, type="primary"):
                                    # Check if fits in container
                                    current_cbm = sum([item['Total CBM'] for item in st.session_state["container_cart"]])
                                    new_total = current_cbm + cbm_value
                                    
                                    if new_total <= selected_specs['capacity_cbm']:
                                        st.session_state["container_cart"].append({
                                            "Order ID": order['Order ID'],
                                            "Buyer": order['Buyer'],
                                            "Produk": order['Produk'],
                                            "Qty": order['Qty'],
                                            "CBM per Pcs": order.get('CBM per Pcs', 0),
                                            "Total CBM": cbm_value,
                                            "Progress": order['Progress'],
                                            "Due Date": str(order['Due Date'])
                                        })
                                        st.success("✅ Added!")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Exceeds capacity! ({new_total:.3f} > {selected_specs['capacity_cbm']} m³)")
                            else:
                                st.button("✓ Added", key=f"added_sim_{order['Order ID']}", disabled=True, use_container_width=True)
                        
                        st.markdown("<div style='margin: 5px 0; border-bottom: 1px solid #374151;'></div>", unsafe_allow_html=True)
                else:
                    st.warning("No orders available with packing data. Please add packing size information to orders.")
            
            with col2:
                st.markdown(f"### 🚢 {container_type}")
                
                # Calculate current load
                current_items = st.session_state["container_cart"]
                total_cbm_loaded = sum([item['Total CBM'] for item in current_items])
                total_qty_loaded = sum([item['Qty'] for item in current_items])
                percentage_loaded = (total_cbm_loaded / selected_specs['capacity_cbm']) * 100
                
                # Visual representation
                color = selected_specs['color']
                st.markdown(f"""
                <div class="container-visual" style="border-color: {color};">
                    <h4 style='color: white; margin-bottom: 15px;'>Container Load Status</h4>
                    <p style='color: #D1D5DB; margin: 5px 0;'>Type: <strong>{container_type}</strong></p>
                    <p style='color: #D1D5DB; margin: 5px 0;'>Capacity: {selected_specs['capacity_cbm']} m³</p>
                    <div class="container-progress" style="margin: 15px 0;">
                        <div class="container-fill" style="width: {min(percentage_loaded, 100):.1f}%; background: {color};"></div>
                    </div>
                    <div style='text-align: center; margin: 15px 0;'>
                        <h2 style='color: white; margin: 5px 0;'>{total_cbm_loaded:.6f} m³</h2>
                        <p style='color: #10B981; font-size: 1.2em; margin: 5px 0;'>{percentage_loaded:.1f}% Full</p>
                        <p style='color: #60A5FA; margin: 5px 0;'>Available: {selected_specs['capacity_cbm'] - total_cbm_loaded:.6f} m³</p>
                        <p style='color: #F59E0B; margin: 5px 0;'>Total Qty: {total_qty_loaded:,} pcs</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Items in container
                if current_items:
                    st.markdown("#### 📦 Items in Container:")
                    
                    for idx, item in enumerate(current_items):
                        st.markdown(f"""
                        <div style='background-color: #1F2937; padding: 10px; margin: 8px 0; border-radius: 5px; border-left: 3px solid {color};'>
                            <strong style='color: #60A5FA;'>{item['Order ID']}</strong><br>
                            <span style='color: #D1D5DB; font-size: 0.9em;'>{item['Buyer']}</span><br>
                            <span style='color: #9CA3AF; font-size: 0.85em;'>{item['Produk']}</span><br>
                            <div style='margin-top: 5px;'>
                                <span style='color: #10B981;'>📦 {item['Qty']} pcs</span> | 
                                <span style='color: #F59E0B;'>📏 {item['Total CBM']:.6f} m³</span>
                            </div>
                            <span style='color: #6B7280; font-size: 0.8em;'>Progress: {item['Progress']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("🗑 Remove", key=f"remove_sim_{idx}", use_container_width=True):
                            st.session_state["container_cart"].pop(idx)
                            st.rerun()
                    
                    st.markdown("---")
                    
                    # Container name input
                    container_name = st.text_input("Container Name (Optional)", 
                                                  placeholder=f"CONT-{datetime.datetime.now().strftime('%Y%m%d')}",
                                                  key="container_name_input")
                    
                    container_notes = st.text_area("Notes", 
                                                  placeholder="Add any notes about this container load...",
                                                  height=80,
                                                  key="container_notes")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("💾 Save Simulation", use_container_width=True, type="primary"):
                            # Generate container ID
                            if container_name:
                                cont_id = container_name
                            else:
                                cont_id = f"CONT-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                            
                            # Save container data
                            container_data = {
                                "container_id": cont_id,
                                "date": str(datetime.date.today()),
                                "type": container_type,
                                "capacity": selected_specs['capacity_cbm'],
                                "loaded_cbm": total_cbm_loaded,
                                "percentage": percentage_loaded,
                                "total_qty": total_qty_loaded,
                                "items": current_items.copy(),
                                "notes": container_notes if container_notes else "",
                                "simulation_mode": True
                            }
                            
                            containers = st.session_state["containers"]
                            containers.append(container_data)
                            st.session_state["containers"] = containers
                            
                            if save_containers(containers):
                                st.success(f"✅ Container simulation '{cont_id}' saved successfully!")
                                st.balloons()
                                st.session_state["container_cart"] = []
                                st.rerun()
                    
                    with col_btn2:
                        if st.button("🗑 Clear All", use_container_width=True, type="secondary"):
       port streamlit as st
import pandas as pd
import datetime
import json
import os
import plotly.express as px
import plotly.figure_factory as ff
from streamlit.components.v1 import html

# ===== KONFIGURASI DATABASE =====
DATABASE_PATH = "ppic_data.json"
BUYER_DB_PATH = "buyers.json"
PRODUCT_DB_PATH = "products.json"
PROCUREMENT_DB_PATH = "procurement.json"
CONTAINER_DB_PATH = "containers.json"

st.set_page_config(
    page_title="PPIC-DSS System", 
    layout="wide",
    page_icon="🏭",
    initial_sidebar_state="collapsed"
)

# ===== CONTAINER SPECIFICATIONS =====
CONTAINER_TYPES = {
    "20 Feet": {
        "capacity_cbm": 33.0,
        "max_weight_kg": 24000,
        "color": "#3B82F6"
    },
    "40 Feet": {
        "capacity_cbm": 67.0,
        "max_weight_kg": 30000,
        "color": "#10B981"
    },
    "40 HC (High Cube)": {
        "capacity_cbm": 76.0,
        "max_weight_kg": 30000,
        "color": "#8B5CF6"
    }
}

# ===== CSS RESPONSIVE & COMPACT =====
def inject_responsive_css():
    st.markdown("""
    <style>
    /* Reduce top padding and margins */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Compact header spacing */
    h1, h2, h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Reduce back button spacing */
    [data-testid="stButton"] {
        margin-top: 0 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Form input alignment */
    .stNumberInput, .stTextInput, .stSelectbox, .stDateInput {
        margin-bottom: 0.3rem !important;
    }
    
    /* Align form elements */
    div[data-testid="column"] {
        padding: 0 0.5rem !important;
    }
    
    /* Enable Tab navigation between inputs */
    input, select, textarea {
        tab-index: auto !important;
    }
    
    /* Mobile responsive */
    @media (max-width: 767px) {
        [data-testid="stSidebar"] {
            position: fixed;
            z-index: 999;
            width: 80vw !important;
        }
        .main .block-container {
            padding: 0.5rem 0.3rem !important;
        }
        h1 { font-size: 1.3rem !important; }
        h2 { font-size: 1.1rem !important; }
        .stButton button { width: 100% !important; }
    }
    
    /* Scrollable table container */
    .recent-orders-container {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #374151;
        border-radius: 5px;
        padding: 10px;
    }
    
    /* WIP Cards styling */
    .wip-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    .finished-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    .shipping-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    /* Container load visualization */
    .container-visual {
        background: #1F2937;
        border: 2px solid #3B82F6;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .container-progress {
        height: 40px;
        background: #374151;
        border-radius: 5px;
        overflow: hidden;
        position: relative;
    }
    
    .container-fill {
        height: 100%;
        background: linear-gradient(90deg, #10B981 0%, #3B82F6 100%);
        transition: width 0.3s ease;
    }
    </style>
    
    <script>
    // Enable Tab navigation between form fields
    document.addEventListener('DOMContentLoaded', function() {
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach((input, index) => {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const nextInput = inputs[index + 1];
                    if (nextInput) {
                        nextInput.focus();
                    }
                }
            });
        });
    });
    </script>
    """, unsafe_allow_html=True)

inject_responsive_css()

# ===== FUNGSI DATABASE =====
def load_data():
    if os.path.exists(DATABASE_PATH):
        try:
            with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                df = pd.DataFrame(data)
                if not df.empty:
                    df['Order Date'] = pd.to_datetime(df['Order Date']).dt.date
                    df['Due Date'] = pd.to_datetime(df['Due Date']).dt.date
                    if 'History' not in df.columns:
                        df['History'] = df.apply(lambda x: json.dumps([]), axis=1)
                    # Add new columns if not exist
                    if 'Product CBM' not in df.columns:
                        df['Product CBM'] = 0.0
                return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
    return pd.DataFrame(columns=[
        "Order ID", "Order Date", "Buyer", "Produk", "Qty", "Due Date", 
        "Prioritas", "Progress", "Proses Saat Ini", "Keterangan",
        "Tracking", "History", "Material", "Finishing", "Description",
        "Product Size P", "Product Size L", "Product Size T", "Product CBM",
        "Packing Size P", "Packing Size L", "Packing Size T",
        "CBM per Pcs", "Total CBM", "Image Path"
    ])

def save_data(df):
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
    if os.path.exists(BUYER_DB_PATH):
        try:
            with open(BUYER_DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data and isinstance(data[0], str):
                    return [{"name": buyer, "address": "", "contact": "", "profile": ""} for buyer in data]
                return data
        except:
            pass
    return []

def save_buyers(buyers):
    try:
        with open(BUYER_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(buyers, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def get_buyer_names():
    buyers = st.session_state["buyers"]
    return [b["name"] for b in buyers]

def load_products():
    if os.path.exists(PRODUCT_DB_PATH):
        try:
            with open(PRODUCT_DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_products(products):
    try:
        with open(PRODUCT_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def load_procurement():
    if os.path.exists(PROCUREMENT_DB_PATH):
        try:
            with open(PROCUREMENT_DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Fix: Ensure it returns a list, not dict
                if isinstance(data, dict):
                    return []
                return data
        except:
            pass
    return []

def save_procurement(procurement_data):
    try:
        with open(PROCUREMENT_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(procurement_data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

# ===== CONTAINER DATABASE =====
def load_containers():
    if os.path.exists(CONTAINER_DB_PATH):
        try:
            with open(CONTAINER_DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_containers(containers_data):
    try:
        with open(CONTAINER_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(containers_data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def get_tracking_stages():
    return [
        "Pre Order", "Order di Supplier", "Warehouse", "Fitting 1",
        "Amplas", "Revisi 1", "Spray", "Fitting 2",
        "Revisi Fitting 2", "Packaging", "Pengiriman"
    ]

def init_tracking_data():
    stages = get_tracking_stages()
    return {stage: {"qty": 0} for stage in stages}

def get_tracking_status_from_progress(progress_str):
    try:
        progress_pct = int(progress_str.rstrip('%')) if progress_str else 0
    except:
        progress_pct = 0
    
    if progress_pct >= 100:
        return "Done"
    elif progress_pct > 0:
        return "On Going"
    else:
        return "On Going"

def add_history_entry(order_id, action, details):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "timestamp": timestamp,
        "action": action,
        "details": details
    }

def save_uploaded_image(uploaded_file, order_id, product_idx):
    if uploaded_file is not None:
        images_dir = "product_images"
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        
        file_extension = uploaded_file.name.split('.')[-1]
        filename = f"{order_id}_product{product_idx}.{file_extension}"
        filepath = os.path.join(images_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return filepath
    return None

def calculate_cbm(p, l, t):
    """Calculate CBM from dimensions in cm with maximum precision"""
    try:
        p_val = float(p) if p else 0
        l_val = float(l) if l else 0
        t_val = float(t) if t else 0
        if p_val > 0 and l_val > 0 and t_val > 0:
            # Return with 6 decimal places precision
            return (p_val * l_val * t_val) / 1000000
        return 0
    except:
        return 0

def get_products_by_buyer(buyer_name):
    """Get unique products for a specific buyer from orders"""
    df = st.session_state["data_produksi"]
    if df.empty or not buyer_name:
        return []
    
    buyer_products = df[df["Buyer"] == buyer_name]["Produk"].unique().tolist()
    return sorted(buyer_products)

def calculate_production_metrics(df):
    """Calculate WIP, Finished Goods, and Shipping metrics"""
    wip_stages = ["Warehouse", "Fitting 1", "Amplas", "Revisi 1", "Spray", "Fitting 2", "Revisi Fitting 2"]
    
    wip_qty = 0
    wip_cbm = 0
    finished_qty = 0  # Packaging stage = Produk Jadi
    finished_cbm = 0
    shipping_qty = 0  # Pengiriman stage
    shipping_cbm = 0
    
    for idx, row in df.iterrows():
        try:
            tracking_data = json.loads(row["Tracking"])
            product_cbm = float(row.get("Product CBM", 0))
            
            for stage, data in tracking_data.items():
                qty = data.get("qty", 0)
                if stage in wip_stages and qty > 0:
                    wip_qty += qty
                    wip_cbm += qty * product_cbm
                elif stage == "Packaging" and qty > 0:
                    finished_qty += qty
                    finished_cbm += qty * product_cbm
                elif stage == "Pengiriman" and qty > 0:
                    shipping_qty += qty
                    shipping_cbm += qty * product_cbm
        except:
            pass
    
    return wip_qty, wip_cbm, finished_qty, finished_cbm, shipping_qty, shipping_cbm

# ===== INISIALISASI =====
if "data_produksi" not in st.session_state:
    st.session_state["data_produksi"] = load_data()
if "buyers" not in st.session_state:
    st.session_state["buyers"] = load_buyers()
if "products" not in st.session_state:
    st.session_state["products"] = load_products()
if "procurement" not in st.session_state:
    st.session_state["procurement"] = load_procurement()
if "containers" not in st.session_state:
    st.session_state["containers"] = load_containers()
if "menu" not in st.session_state:
    st.session_state["menu"] = "Dashboard"

# Initialize container cart
if "container_cart" not in st.session_state:
    st.session_state["container_cart"] = []

# Initialize selected container type
if "selected_container_type" not in st.session_state:
    st.session_state["selected_container_type"] = "40 HC (High Cube)"

# ===== SIDEBAR MENU =====
st.sidebar.title("🏭 PPIC-DSS MENU")
st.sidebar.markdown("---")

menu_options = {
    "📊 Dashboard": "Dashboard",
    "📋 Input Pesanan Baru": "Input",
    "📦 Daftar Order": "Orders",
    "🛒 Procurement": "Procurement",
    "⚙ Update Progress": "Progress",
    "🔍 Tracking Produksi": "Tracking",
    "🚢 Container Loading": "Container",
    "💾 Database": "Database",
    "📈 Analisis & Laporan": "Analytics",
    "📊 Gantt Chart": "Gantt"
}

for label, value in menu_options.items():
    if st.sidebar.button(label, use_container_width=True):
        st.session_state["menu"] = value

st.sidebar.markdown("---")
st.sidebar.info(f"📁 Database: Local Storage")

# ===== BACK BUTTON =====
if st.session_state["menu"] != "Dashboard":
    if st.button("⬅ Back to Dashboard", type="secondary"):
        st.session_state["menu"] = "Dashboard"
        st.rerun()
    st.markdown("---")


# ===== MENU: DASHBOARD =====
if st.session_state["menu"] == "Dashboard":
    st.title("📊 Dashboard PT JAVA CONNECTION")
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        # Calculate tracking status
        df['Tracking Status'] = df.apply(
            lambda row: get_tracking_status_from_progress(row['Progress']), 
            axis=1
        )
        
        # Calculate production metrics
        wip_qty, wip_cbm, finished_qty, finished_cbm, shipping_qty, shipping_cbm = calculate_production_metrics(df)
        
        # ===== SECTION 1: TOP ROW - RECENT ORDERS + KEY METRICS =====
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.markdown("### 🕒 Recent Orders")
            
            # Search/filter for recent orders
            search_recent = st.text_input("🔍 Search orders...", key="search_recent_orders")
            
            recent_df = df.sort_values("Order Date", ascending=False)
            
            if search_recent:
                recent_df = recent_df[
                    recent_df["Order ID"].str.contains(search_recent, case=False, na=False) | 
                    recent_df["Buyer"].str.contains(search_recent, case=False, na=False) |
                    recent_df["Produk"].str.contains(search_recent, case=False, na=False)
                ]
            
            # Scrollable container for recent orders
            with st.container():
                st.markdown('<div class="recent-orders-container">', unsafe_allow_html=True)
                
                for idx, row in recent_df.head(20).iterrows():
                    col1, col2, col3, col4 = st.columns([2.5, 2, 1, 0.5])
                    
                    with col1:
                        st.markdown(f"{row['Order ID']}")
                        st.caption(f"{row['Buyer']} | {row['Produk']}")
                    
                    with col2:
                        st.caption(f"Order: {row['Order Date']}")
                        st.caption(f"Due: {row['Due Date']}")
                    
                    with col3:
                        progress_val = int(row['Progress'].rstrip('%'))
                        st.progress(progress_val / 100)
                        st.caption(f"{row['Progress']}")
                    
                    with col4:
                        if row['Tracking Status'] == 'Done':
                            st.success("✅")
                        else:
                            st.info("🔄")
                    
                    st.divider()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col_right:
            st.markdown("### 📈 Key Metrics")
            
            # Compact metrics
            total_orders = len(df)
            ongoing = len(df[df["Tracking Status"] == "On Going"])
            done = len(df[df["Tracking Status"] == "Done"])
            total_qty = df["Qty"].sum()
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("📦 Total Orders", total_orders)
            col_m2.metric("🔄 On Going", ongoing)
            
            col_m3, col_m4 = st.columns(2)
            col_m3.metric("✅ Done", done)
            col_m4.metric("📊 Total Qty", f"{total_qty:,}")

      
        # Production Status Cards
        st.markdown("#### 🏭 Production Status")
        col_prod1, col_prod2, col_prod3 = st.columns(3)
        
        with col_prod1:
            # WIP Card
            st.markdown(f"""
            <div class="wip-card">
                <h4 style='margin: 0 0 10px 0;'>WIP (Work in Progress)</h4>
                <h2 style='margin: 5px 0; font-size: 2.5rem;'>{wip_qty:,} pcs</h2>
                <p style='margin: 5px 0; font-size: 0.9rem;'>Volume: {wip_cbm:.6f} m³</p>
                <small style='font-size: 0.8rem;'>Warehouse → Revisi Fitting 2</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_prod2:            
            # Finished Goods Card (Packaging)
           st.markdown(f"""
            <div class="finished-card">
                <h4 style='margin: 0 0 10px 0;'>Produk Jadi (Packaging)</h4>
                <h2 style='margin: 5px 0; font-size: 2.5rem;'>{finished_qty:,} pcs</h2>
                <p style='margin: 5px 0; font-size: 0.9rem;'>Volume: {finished_cbm:.6f} m³</p>
                <small style='font-size: 0.8rem;'>Ready for shipment</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_prod3:
            # Shipping Card
             st.markdown(f"""
            <div class="shipping-card">
                <h4 style='margin: 0 0 10px 0;'>Pengiriman</h4>
                <h2 style='margin: 5px 0; font-size: 2.5rem;'>{shipping_qty:,} pcs</h2>
                <p style='margin: 5px 0; font-size: 0.9rem;'>Volume: {shipping_cbm:.6f} m³</p>
                <small style='font-size: 0.8rem;'>In transit / Delivered</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ===== SECTION 2: PRODUCTION CALENDAR =====
        col_cal, col_chart = st.columns([2, 1])
        
        with col_cal:
            st.markdown("### 📅 Production Calendar")
            
            today = datetime.date.today()
            current_month = today.month
            current_year = today.year
            
            col_month, col_year = st.columns(2)
            with col_month:
                months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                         "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                selected_month = st.selectbox("Bulan", months, index=current_month - 1, key="cal_month")
                month_num = months.index(selected_month) + 1
            
            with col_year:
                years = list(range(current_year - 1, current_year + 3))
                selected_year = st.selectbox("Tahun", years, index=1, key="cal_year")
            
            # Filter orders by selected month/year
            df_copy = df.copy()
            df_copy['Due Date'] = pd.to_datetime(df_copy['Due Date'])
            df_month = df_copy[(df_copy['Due Date'].dt.month == month_num) & 
                         (df_copy['Due Date'].dt.year == selected_year)]
            
            if not df_month.empty:
                st.markdown(f"📌 {len(df_month)} orders di bulan ini**")
            
            # Create calendar view
            import calendar
            cal = calendar.monthcalendar(selected_year, month_num)
            
            days = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
            header_cols = st.columns(7)
            for i, day in enumerate(days):
                header_cols[i].markdown(f"<center><b>{day}</b></center>", unsafe_allow_html=True)
            
            for week in cal:
                week_cols = st.columns(7)
                for i, day in enumerate(week):
                    if day == 0:
                        week_cols[i].markdown("")
                    else:
                        date_obj = datetime.date(selected_year, month_num, day)
                        
                        if not df_month.empty:
                            orders_on_date = df_month[df_month['Due Date'].dt.date == date_obj]
                            
                            if len(orders_on_date) > 0:
                                done_count = len(orders_on_date[orders_on_date['Tracking Status'] == 'Done'])
                                if done_count == len(orders_on_date):
                                    bg_color = "#10B981"
                                elif date_obj < today:
                                    bg_color = "#EF4444"
                                elif date_obj == today:
                                    bg_color = "#F59E0B"
                                else:
                                    bg_color = "#3B82F6"
                                
                                week_cols[i].markdown(f"""
                                <div style='background-color: {bg_color}; padding: 5px; border-radius: 5px; text-align: center;'>
                                    <b style='color: white;'>{day}</b><br>
                                    <span style='color: white; font-size: 10px;'>{len(orders_on_date)}</span>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                if date_obj == today:
                                    week_cols[i].markdown(f"<div style='padding: 5px; text-align: center; border: 2px solid #3B82F6; border-radius: 5px;'><b>{day}</b></div>", unsafe_allow_html=True)
                                else:
                                    week_cols[i].markdown(f"<div style='padding: 5px; text-align: center;'>{day}</div>", unsafe_allow_html=True)
                        else:
                            if date_obj == today:
                                week_cols[i].markdown(f"<div style='padding: 5px; text-align: center; border: 2px solid #3B82F6; border-radius: 5px;'><b>{day}</b></div>", unsafe_allow_html=True)
                            else:
                                week_cols[i].markdown(f"<div style='padding: 5px; text-align: center;'>{day}</div>", unsafe_allow_html=True)
        
        with col_chart:
            st.markdown("### 📊 Status Distribution")
            
            status_dist = df["Tracking Status"].value_counts()
            fig_status = px.pie(
                values=status_dist.values, 
                names=status_dist.index,
                color_discrete_map={"On Going": "#3B82F6", "Done": "#10B981"},
                hole=0.4
            )
            fig_status.update_traces(textposition='inside', textinfo='percent+label')
            fig_status.update_layout(showlegend=True, height=250, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_status, use_container_width=True)
        
        st.markdown("---")
        
        # ===== SECTION 3: PRODUCTION PROGRESS BY STAGE =====
        st.markdown("### 🏭 Production Progress by Stage")
        
        stages = get_tracking_stages()
        stage_data = {stage: 0 for stage in stages}
        
        for idx, row in df.iterrows():
            try:
                tracking_data = json.loads(row["Tracking"])
                for stage, data in tracking_data.items():
                    qty = data.get("qty", 0)
                    if stage in stage_data:
                        stage_data[stage] += qty
            except:
                pass
        
        fig_stages = px.bar(
            x=list(stage_data.values()),
            y=list(stage_data.keys()),
            orientation='h',
            color=list(stage_data.values()),
            color_continuous_scale='Blues'
        )
        fig_stages.update_layout(
            xaxis_title="Quantity (pcs)",
            yaxis_title="",
            showlegend=False,
            height=300,
            margin=dict(t=10, b=10)
        )
        st.plotly_chart(fig_stages, use_container_width=True)
    else:
        st.info("📝 Belum ada data. Silakan input pesanan baru.")

# ===== MENU: INPUT PESANAN BARU =====
elif st.session_state["menu"] == "Input":
    st.markdown("<h2 style='margin: 0;'>📋 Form Input Pesanan Baru (Multi-Product)</h2>", unsafe_allow_html=True)
    
    if "input_products" not in st.session_state:
        st.session_state["input_products"] = []
    
    st.markdown("#### 📦 Informasi Order")
    
    col_order1, col_order2, col_order3, col_order4 = st.columns(4)
    
    with col_order1:
        order_date = st.date_input("Order Date", datetime.date.today(), key="input_order_date")
    
    with col_order2:
        buyers_list = get_buyer_names()
        buyer = st.selectbox("Buyer Name", buyers_list, key="input_buyer")
    
    with col_order3:
        due_date = st.date_input("Due Date", datetime.date.today() + datetime.timedelta(days=30), key="input_due")
    
    with col_order4:
        prioritas = st.selectbox("Prioritas", ["High", "Medium", "Low"], key="input_priority")
    
    st.markdown("---")
    st.markdown("#### 📦 Tambah Produk ke Order")
    
    # Create properly aligned columns for form
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.markdown("*Product Information*")
            products_list = st.session_state["products"]
            if products_list:
                produk_option = st.selectbox("Pilih Produk", ["-- Pilih dari Database --"] + products_list, key="form_produk_select")
                if produk_option == "-- Pilih dari Database --":
                    produk_name = st.text_input("Atau ketik nama produk baru", key="form_produk_manual")
                else:
                    produk_name = produk_option
            else:
                produk_name = st.text_input("Nama Produk", key="form_produk")
            
            qty = st.number_input("Quantity (pcs)", min_value=1, value=1, key="form_qty")
            
            uploaded_image = st.file_uploader("Upload Gambar Produk", 
                                             type=['jpg', 'jpeg', 'png'], 
                                             key="form_image")
        
        with col2:
            st.markdown("*Specifications*")
            material = st.text_input("Material", placeholder="Contoh: Kayu Jati, MDF", key="form_material")
            finishing = st.text_input("Finishing", placeholder="Contoh: Natural, Duco Putih", key="form_finishing")
            
            st.markdown("*Product Size (cm)*")
            col_ps1, col_ps2, col_ps3 = st.columns(3)
            with col_ps1:
                prod_p = st.number_input("P", min_value=0.0, value=None, format="%.2f", key="prod_p", step=0.01, placeholder="0.00")
            with col_ps2:
                prod_l = st.number_input("L", min_value=0.0, value=None, format="%.2f", key="prod_l", step=0.01, placeholder="0.00")
            with col_ps3:
                prod_t = st.number_input("T", min_value=0.0, value=None, format="%.2f", key="prod_t", step=0.01, placeholder="0.00")
            
            # Product CBM calculation with 6 decimal places
            product_cbm = calculate_cbm(prod_p, prod_l, prod_t)
            if product_cbm > 0:
                st.success(f"📦 Product CBM: *{product_cbm:.6f} m³*")
            else:
                st.info(f"📦 Product CBM: 0.000000 m³")
        
        with col3:
            st.markdown("*Packing Information*")
            st.markdown("*Packing Size (cm)*")
            col_pack1, col_pack2, col_pack3 = st.columns(3)
            with col_pack1:
                pack_p = st.number_input("P", min_value=0.0, value=None, format="%.2f", key="pack_p", step=0.01, placeholder="0.00")
            with col_pack2:
                pack_l = st.number_input("L", min_value=0.0, value=None, format="%.2f", key="pack_l", step=0.01, placeholder="0.00")
            with col_pack3:
                pack_t = st.number_input("T", min_value=0.0, value=None, format="%.2f", key="pack_t", step=0.01, placeholder="0.00")
            
            # Real-time CBM calculation with 6 decimal places
            cbm_per_pcs = calculate_cbm(pack_p, pack_l, pack_t)
            total_cbm = cbm_per_pcs * qty
            
            if cbm_per_pcs > 0:
                st.success(f"📦 CBM per Pcs: *{cbm_per_pcs:.6f} m³*")
                st.info(f"📦 Total CBM: *{total_cbm:.6f} m³*")
            else:
                st.info(f"📦 CBM per Pcs: 0.000000 m³")
                st.info(f"📦 Total CBM: 0.000000 m³")
            
            description = st.text_area("Description", placeholder="Deskripsi produk...", height=50, key="form_desc")
    
    keterangan = st.text_area("Keterangan Tambahan", placeholder="Catatan khusus...", height=50, key="form_notes")
    
    # Add product button
    if st.button("➕ Tambah Produk ke Order", use_container_width=True, type="primary", key="add_product_btn"):
        if produk_name and qty > 0:
            temp_product = {
                "nama": produk_name,
                "qty": qty,
                "material": material if material else "-",
                "finishing": finishing if finishing else "-",
                "description": description if description else "-",
                "prod_p": prod_p,
                "prod_l": prod_l,
                "prod_t": prod_t,
                "product_cbm": product_cbm,
                "pack_p": pack_p,
                "pack_l": pack_l,
                "pack_t": pack_t,
                "cbm_per_pcs": cbm_per_pcs,
                "total_cbm": total_cbm,
                "keterangan": keterangan if keterangan else "-",
                "image": uploaded_image
            }
            
            st.session_state["input_products"].append(temp_product)
            st.success(f"✅ Produk '{produk_name}' ditambahkan! Total produk: {len(st.session_state['input_products'])}")
            st.rerun()
        else:
            st.warning("⚠ Harap isi nama produk dan quantity!")
    
    if st.session_state["input_products"]:
        st.markdown("---")
        st.markdown("### 📋 Daftar Produk dalam Order Ini")
        
        for idx, product in enumerate(st.session_state["input_products"]):
            with st.expander(f"📦 {idx + 1}. {product['nama']} ({product['qty']} pcs) - CBM: {product['total_cbm']:.6f} m³", expanded=False):
                col_display1, col_display2, col_display3 = st.columns([2, 2, 1])
                
                with col_display1:
                    st.write(f"*Material:* {product['material']}")
                    st.write(f"*Finishing:* {product['finishing']}")
                    st.write(f"*Product Size:* {product['prod_p']:.2f} x {product['prod_l']:.2f} x {product['prod_t']:.2f} cm")
                    st.write(f"*Product CBM:* {product['product_cbm']:.6f} m³")
                
                with col_display2:
                    st.write(f"*Packing Size:* {product['pack_p']:.2f} x {product['pack_l']:.2f} x {product['pack_t']:.2f} cm")
                    st.write(f"*CBM per Pcs:* {product['cbm_per_pcs']:.6f} m³")
                    st.write(f"*Total CBM:* {product['total_cbm']:.6f} m³")
                
                with col_display3:
                    if st.button("🗑 Hapus", key=f"remove_product_{idx}", use_container_width=True):
                        st.session_state["input_products"].pop(idx)
                        st.rerun()
        
        total_cbm_all = sum([p['total_cbm'] for p in st.session_state["input_products"]])
        st.info(f"📦 Total CBM untuk semua produk: *{total_cbm_all:.6f} m³*")
        
        col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 2])
        
        with col_submit1:
            if st.button("🗑 BATAL", use_container_width=True, type="secondary"):
                st.session_state["input_products"] = []
                st.rerun()
        
        with col_submit2:
            if st.button("📤 SUBMIT ORDER", use_container_width=True, type="primary"):
                if buyer and st.session_state["input_products"]:
                    existing_ids = st.session_state["data_produksi"]["Order ID"].tolist() if not st.session_state["data_produksi"].empty else []
                    new_id_num = max([int(oid.split("-")[1]) for oid in existing_ids if "-" in oid], default=2400) + 1
                    new_order_id = f"ORD-{new_id_num}"
                    
                    new_orders = []
                    
                    for prod_idx, product in enumerate(st.session_state["input_products"]):
                        image_path = None
                        if product.get("image"):
                            image_path = save_uploaded_image(product["image"], new_order_id, prod_idx)
                        
                        initial_history = [add_history_entry(f"{new_order_id}-P{prod_idx+1}", "Order Created", 
                        f"Product: {product['nama']}, Priority: {prioritas}")]
                       
                        tracking_data = init_tracking_data()
                        first_stage = get_tracking_stages()[0]
                        tracking_data[first_stage]["qty"] = product["qty"]
                        
                        order_data = {
                            "Order ID": f"{new_order_id}-P{prod_idx+1}",
                            "Order Date": order_date,
                            "Buyer": buyer,
                            "Produk": product["nama"],
                            "Qty": product["qty"],
                            "Material": product["material"],
                            "Finishing": product["finishing"],
                            "Description": product["description"],
                            "Product Size P": product["prod_p"],
                            "Product Size L": product["prod_l"],
                            "Product Size T": product["prod_t"],
                            "Product CBM": product["product_cbm"],
                            "Packing Size P": product["pack_p"],
                            "Packing Size L": product["pack_l"],
                            "Packing Size T": product["pack_t"],
                            "CBM per Pcs": product["cbm_per_pcs"],
                            "Total CBM": product["total_cbm"],
                            "Due Date": due_date,
                            "Prioritas": prioritas,
                            "Progress": "0%",
                            "Proses Saat Ini": first_stage,
                            "Keterangan": product["keterangan"],
                            "Image Path": image_path if image_path else "",
                            "Tracking": json.dumps(tracking_data),
                            "History": json.dumps(initial_history)
                        }
                        
                        new_orders.append(order_data)
                    
                    new_df = pd.DataFrame(new_orders)
                    st.session_state["data_produksi"] = pd.concat(
                        [st.session_state["data_produksi"], new_df], ignore_index=True
                    )
                    
                    if save_data(st.session_state["data_produksi"]):
                        st.success(f"✅ Order {new_order_id} dengan {len(st.session_state['input_products'])} produk berhasil ditambahkan!")
                        st.balloons()
                        st.session_state["input_products"] = []
                        st.rerun()
                else:
                    st.warning("⚠ Harap pilih buyer dan tambahkan minimal 1 produk!")
# ===== MENU: DAFTAR ORDER =====
elif st.session_state["menu"] == "Orders":
    st.header("📦 DAFTAR ORDER")
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_buyer = st.multiselect("Filter Buyer", df["Buyer"].unique().tolist())
        with col_f2:
            search_order = st.text_input("🔍 Cari Order ID / Produk")
        
        df_filtered = df.copy()
        if filter_buyer:
            df_filtered = df_filtered[df_filtered["Buyer"].isin(filter_buyer)]
        if search_order:
            df_filtered = df_filtered[
                df_filtered["Order ID"].str.contains(search_order, case=False, na=False) | 
                df_filtered["Produk"].str.contains(search_order, case=False, na=False)
            ]
        
        st.markdown("---")
        st.info(f"📦 Menampilkan {len(df_filtered)} order dari {df_filtered['Buyer'].nunique()} buyer")
        
        buyers = df_filtered["Buyer"].unique()
        
        for buyer in sorted(buyers):
            buyer_orders = df_filtered[df_filtered["Buyer"] == buyer]
            buyer_count = len(buyer_orders)
            
            with st.expander(f"👤 *{buyer}* ({buyer_count} orders)", expanded=False):
                buyer_orders['Order Date'] = pd.to_datetime(buyer_orders['Order Date'])
                buyer_orders = buyer_orders.sort_values('Order Date', ascending=False)
                
                date_groups = buyer_orders.groupby(buyer_orders['Order Date'].dt.date)
                
                for order_date, date_orders in date_groups:
                    today = datetime.date.today()
                    date_diff = (today - order_date).days
                    
                    if date_diff == 0:
                        date_label = "📅 Hari Ini"
                    elif date_diff == 1:
                        date_label = "📅 Kemarin"
                    elif date_diff <= 7:
                        date_label = f"📅 {date_diff} hari yang lalu"
                    else:
                        date_label = f"📅 {order_date.strftime('%d %b %Y')}"
                    
                    with st.expander(f"{date_label} ({len(date_orders)} orders)", expanded=False):
                        for idx, row in date_orders.iterrows():
                            with st.expander(f"📦 {row['Order ID']} - {row['Produk']}", expanded=False):
                                col1, col2, col3 = st.columns([2, 2, 1])
                                
                                with col1:
                                    st.write(f"*Product:* {row['Produk']}")
                                    st.write(f"*Qty:* {row['Qty']} pcs")
                                    st.write(f"*Material:* {row.get('Material', '-')}")
                                    st.write(f"*Finishing:* {row.get('Finishing', '-')}")
                                    st.write(f"*Product Size:* {row.get('Product Size P', 0)} x {row.get('Product Size L', 0)} x {row.get('Product Size T', 0)} cm")
                                
                                with col2:
                                    st.write(f"*Packing Size:* {row.get('Packing Size P', 0)} x {row.get('Packing Size L', 0)} x {row.get('Packing Size T', 0)} cm")
                                    st.write(f"*CBM per Pcs:* {row.get('CBM per Pcs', 0):.6f} m³")
                                    st.write(f"*Total CBM:* {row.get('Total CBM', 0):.4f} m³")
                                    st.write(f"*Due Date:* {row['Due Date']}")
                                    st.write(f"*Progress:* {row['Progress']}")
                                    st.write(f"*Proses:* {row['Proses Saat Ini']}")
                                
                                with col3:
                                    if row.get('Image Path') and os.path.exists(row['Image Path']):
                                        st.image(row['Image Path'], caption="Product", width=150)
                                    else:
                                        st.info("📷 No image")
                                
                                if row.get('Description') and row['Description'] != '-':
                                    st.markdown("---")
                                    st.markdown(f"📝 Description:** {row['Description']}")
                                
                                if row['Keterangan'] and row['Keterangan'] != '-':
                                    st.markdown(f"💬 Keterangan:** {row['Keterangan']}")
                                
                                st.markdown("---")
                                btn_col1, btn_col2, btn_col3 = st.columns(3)
                                with btn_col1:
                                    if st.button("✏ Edit Order", key=f"edit_order_{idx}", use_container_width=True, type="primary"):
                                        st.session_state["edit_order_mode"] = True
                                        st.session_state["edit_order_index"] = idx
                                        st.rerun()
                                with btn_col2:
                                    if st.button("⚙ Edit Progress", key=f"edit_{idx}", use_container_width=True, type="secondary"):
                                        st.session_state["edit_order_idx"] = idx
                                        st.session_state["menu"] = "Progress"
                                        st.rerun()
                                with btn_col3:
                                    if st.button("🗑 Delete Order", key=f"del_{idx}", use_container_width=True, type="secondary"):
                                        if st.session_state.get(f"confirm_delete_{idx}", False):
                                            st.session_state["data_produksi"].drop(idx, inplace=True)
                                            st.session_state["data_produksi"].reset_index(drop=True, inplace=True)
                                            save_data(st.session_state["data_produksi"])
                                            st.success(f"✅ Order {row['Order ID']} berhasil dihapus!")
                                            del st.session_state[f"confirm_delete_{idx}"]
                                            st.rerun()
                                        else:
                                            st.session_state[f"confirm_delete_{idx}"] = True
                                            st.warning("⚠ Klik sekali lagi untuk konfirmasi hapus!")
                                            st.rerun()
                
                # Check if in edit mode for any order
                if st.session_state.get("edit_order_mode", False) and "edit_order_index" in st.session_state:
                    edit_idx = st.session_state["edit_order_index"]
                    edit_row = st.session_state["data_produksi"].loc[edit_idx]
                    
                    st.markdown("---")
                    st.markdown("## ✏ EDIT ORDER")
                    st.markdown(f"### Editing: {edit_row['Order ID']} - {edit_row['Produk']}")
                    
                    with st.form("edit_order_form"):
                        col_edit1, col_edit2, col_edit3 = st.columns(3)
                        
                        with col_edit1:
                            st.markdown("📦 Order Information**")
                            edit_buyer = st.selectbox("Buyer", get_buyer_names(), 
                                                     index=get_buyer_names().index(edit_row['Buyer']) if edit_row['Buyer'] in get_buyer_names() else 0,
                                                     key="edit_buyer")
                            edit_produk = st.text_input("Nama Produk", value=edit_row['Produk'], key="edit_produk")
                            edit_qty = st.number_input("Quantity (pcs)", min_value=1, value=int(edit_row['Qty']), key="edit_qty")
                            edit_due_date = st.date_input("Due Date", value=edit_row['Due Date'], key="edit_due_date")
                            edit_prioritas = st.selectbox("Prioritas", ["High", "Medium", "Low"],
                                                         index=["High", "Medium", "Low"].index(edit_row['Prioritas']) if edit_row['Prioritas'] in ["High", "Medium", "Low"] else 0,
                                                         key="edit_prioritas")
                        
                        with col_edit2:
                            st.markdown("🔧 Specifications**")
                            edit_material = st.text_input("Material", value=edit_row.get('Material', ''), key="edit_material")
                            edit_finishing = st.text_input("Finishing", value=edit_row.get('Finishing', ''), key="edit_finishing")
                            edit_description = st.text_area("Description", value=edit_row.get('Description', ''), height=100, key="edit_description")
                            
                            st.markdown("*Product Size (cm)*")
                            col_ps1, col_ps2, col_ps3 = st.columns(3)
                            with col_ps1:
                                edit_prod_p = st.number_input("P", min_value=0.0, value=float(edit_row.get('Product Size P', 0)), step=0.1, key="edit_prod_p")
                            with col_ps2:
                                edit_prod_l = st.number_input("L", min_value=0.0, value=float(edit_row.get('Product Size L', 0)), step=0.1, key="edit_prod_l")
                            with col_ps3:
                                edit_prod_t = st.number_input("T", min_value=0.0, value=float(edit_row.get('Product Size T', 0)), step=0.1, key="edit_prod_t")
                        
                        with col_edit3:
                            st.markdown("📦 Packing Information**")
                            st.markdown("*Packing Size (cm)*")
                            col_pack1, col_pack2, col_pack3 = st.columns(3)
                            with col_pack1:
                                edit_pack_p = st.number_input("P", min_value=0.0, value=float(edit_row.get('Packing Size P', 0)), step=0.1, key="edit_pack_p")
                            with col_pack2:
                                edit_pack_l = st.number_input("L", min_value=0.0, value=float(edit_row.get('Packing Size L', 0)), step=0.1, key="edit_pack_l")
                            with col_pack3:
                                edit_pack_t = st.number_input("T", min_value=0.0, value=float(edit_row.get('Packing Size T', 0)), step=0.1, key="edit_pack_t")
                            
                            # Calculate new CBM
                            new_cbm_per_pcs = calculate_cbm(edit_pack_p, edit_pack_l, edit_pack_t)
                            new_total_cbm = new_cbm_per_pcs * edit_qty
                            st.info(f"CBM per Pcs: {new_cbm_per_pcs:.6f} m³")
                            st.info(f"Total CBM: {new_total_cbm:.4f} m³")
                            
                            edit_keterangan = st.text_area("Keterangan", value=edit_row.get('Keterangan', ''), height=80, key="edit_keterangan")
                        
                        col_submit1, col_submit2 = st.columns(2)
                        with col_submit1:
                            submit_edit = st.form_submit_button("💾 Simpan Perubahan", use_container_width=True, type="primary")
                        with col_submit2:
                            cancel_edit = st.form_submit_button("❌ Batal", use_container_width=True, type="secondary")
                        
                        if submit_edit:
                            # Update the order data
                            st.session_state["data_produksi"].at[edit_idx, "Buyer"] = edit_buyer
                            st.session_state["data_produksi"].at[edit_idx, "Produk"] = edit_produk
                            st.session_state["data_produksi"].at[edit_idx, "Qty"] = edit_qty
                            st.session_state["data_produksi"].at[edit_idx, "Due Date"] = edit_due_date
                            st.session_state["data_produksi"].at[edit_idx, "Prioritas"] = edit_prioritas
                            st.session_state["data_produksi"].at[edit_idx, "Material"] = edit_material
                            st.session_state["data_produksi"].at[edit_idx, "Finishing"] = edit_finishing
                            st.session_state["data_produksi"].at[edit_idx, "Description"] = edit_description
                            st.session_state["data_produksi"].at[edit_idx, "Product Size P"] = edit_prod_p
                            st.session_state["data_produksi"].at[edit_idx, "Product Size L"] = edit_prod_l
                            st.session_state["data_produksi"].at[edit_idx, "Product Size T"] = edit_prod_t
                            st.session_state["data_produksi"].at[edit_idx, "Packing Size P"] = edit_pack_p
                            st.session_state["data_produksi"].at[edit_idx, "Packing Size L"] = edit_pack_l
                            st.session_state["data_produksi"].at[edit_idx, "Packing Size T"] = edit_pack_t
                            st.session_state["data_produksi"].at[edit_idx, "CBM per Pcs"] = new_cbm_per_pcs
                            st.session_state["data_produksi"].at[edit_idx, "Total CBM"] = new_total_cbm
                            st.session_state["data_produksi"].at[edit_idx, "Keterangan"] = edit_keterangan
                            
                            # Add history entry
                            try:
                                history = json.loads(edit_row["History"]) if edit_row["History"] else []
                            except:
                                history = []
                            
                            history.append(add_history_entry(edit_row['Order ID'], "Order Edited", 
                                f"Order data updated: Buyer={edit_buyer}, Product={edit_produk}, Qty={edit_qty}"))
                            st.session_state["data_produksi"].at[edit_idx, "History"] = json.dumps(history)
                            
                            if save_data(st.session_state["data_produksi"]):
                                st.success(f"✅ Order {edit_row['Order ID']} berhasil diupdate!")
                                st.session_state["edit_order_mode"] = False
                                del st.session_state["edit_order_index"]
                                st.rerun()
                            else:
                                st.error("Gagal menyimpan perubahan!")
                        
                        if cancel_edit:
                            st.session_state["edit_order_mode"] = False
                            del st.session_state["edit_order_index"]
                            st.rerun()
    else:
        st.info("📝 Belum ada order yang diinput.")
# ===== MENU: CONTAINER LOADING =====
elif st.session_state["menu"] == "Container":
    st.header("🚢 CONTAINER LOADING SIMULATION")
    
    df = st.session_state["data_produksi"]
    
    # Add CSS for order cards
    st.markdown("""
    <style>
    .order-card {
        background: #1F2937;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        transition: all 0.2s ease;
    }
    
    .order-card:hover {
        border-color: #3B82F6;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    if not df.empty:
        tab1, tab2 = st.tabs(["📦 Container Simulator", "📋 Container History"])
        
        with tab1:
            st.info("💡 *Mode Simulasi*: Simulasi loading container berdasarkan packing size yang sudah diinput, tanpa menunggu produksi selesai.")
            
            # Container type selection
            st.markdown("### 🚢 Select Container Type")
            col_type1, col_type2, col_type3, col_type4 = st.columns(4)
            
            with col_type1:
                container_type = st.selectbox(
                    "Container Type",
                    list(CONTAINER_TYPES.keys()),
                    index=list(CONTAINER_TYPES.keys()).index(st.session_state["selected_container_type"]),
                    key="container_type_select"
                )
                st.session_state["selected_container_type"] = container_type
            
            with col_type2:
                selected_specs = CONTAINER_TYPES[container_type]
                st.metric("Capacity", f"{selected_specs['capacity_cbm']} m³")
            
            with col_type3:
                st.metric("Max Weight", f"{selected_specs['max_weight_kg']:,} kg")
            
            with col_type4:
                st.markdown(f"<div style='background: {selected_specs['color']}; height: 40px; border-radius: 5px;'></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 📦 Available Orders for Simulation")
                
                # Filter options
                col_filter1, col_filter2, col_filter3 = st.columns(3)
                
                with col_filter1:
                    filter_buyer = st.multiselect("Filter by Buyer", df["Buyer"].unique().tolist(), key="sim_buyer_filter")
                
                with col_filter2:
                    filter_product = st.multiselect("Filter by Product", df["Produk"].unique().tolist(), key="sim_product_filter")
                
                with col_filter3:
                    search_order = st.text_input("🔍 Search Order ID", key="sim_search")
                
                # Apply filters
                df_filtered = df.copy()
                if filter_buyer:
                    df_filtered = df_filtered[df_filtered["Buyer"].isin(filter_buyer)]
                if filter_product:
                    df_filtered = df_filtered[df_filtered["Produk"].isin(filter_product)]
                if search_order:
                    df_filtered = df_filtered[df_filtered["Order ID"].str.contains(search_order, case=False, na=False)]
                
                # Filter out orders with zero CBM
                df_filtered = df_filtered[df_filtered["Total CBM"] > 0]
                
                st.info(f"📦 {len(df_filtered)} orders available for simulation")
                
                # Display available orders with better styling
                if not df_filtered.empty:
                    # Sort by due date
                    df_filtered_sorted = df_filtered.sort_values("Due Date")
                    
                    for idx, order in df_filtered_sorted.iterrows():
                        # Check if already in cart
                        in_cart = order['Order ID'] in [item['Order ID'] for item in st.session_state["container_cart"]]
                        
                        # Order card - FIXED: Separate variables to avoid f-string issues
                        border_style = "border-color: #10B981; border-width: 2px;" if in_cart else ""
                        status_color = "#10B981" if in_cart else "#9CA3AF"
                        status_text = "✅ In Container" if in_cart else ""
                        
                        st.markdown(f"""
                        <div class="order-card" style="{border_style}">
                            <strong style="color: #3B82F6; font-size: 1.1em;">{order['Order ID']}</strong>
                            <span style="color: {status_color}; margin-left: 10px; font-size: 0.9em;">{status_text}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col_o1, col_o2, col_o3, col_o4 = st.columns([3, 1.5, 1.5, 1])
                        
                        with col_o1:
                            st.caption(f"{order['Buyer']}** | {order['Produk']}")
                            st.caption(f"🏭 Progress: {order['Progress']} | 📅 Due: {order['Due Date']}")
                        
                        with col_o2:
                            st.metric("Qty", f"{order['Qty']} pcs", label_visibility="collapsed")
                            st.caption(f"Qty: {order['Qty']} pcs")
                        
                        with col_o3:
                            cbm_value = order.get('Total CBM', 0)
                            st.metric("CBM", f"{cbm_value:.4f}", label_visibility="collapsed")
                            st.caption(f"CBM: {cbm_value:.6f} m³")
                        
                        with col_o4:
                            if not in_cart:
                                if st.button("➕ Add", key=f"add_sim_{order['Order ID']}", use_container_width=True, type="primary"):
                                    # Check if fits in container
                                    current_cbm = sum([item['Total CBM'] for item in st.session_state["container_cart"]])
                                    new_total = current_cbm + cbm_value
                                    
                                    if new_total <= selected_specs['capacity_cbm']:
                                        st.session_state["container_cart"].append({
                                            "Order ID": order['Order ID'],
                                            "Buyer": order['Buyer'],
                                            "Produk": order['Produk'],
                                            "Qty": order['Qty'],
                                            "CBM per Pcs": order.get('CBM per Pcs', 0),
                                            "Total CBM": cbm_value,
                                            "Progress": order['Progress'],
                                            "Due Date": str(order['Due Date'])
                                        })
                                        st.success("✅ Added!")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Exceeds capacity! ({new_total:.3f} > {selected_specs['capacity_cbm']} m³)")
                            else:
                                st.button("✓ Added", key=f"added_sim_{order['Order ID']}", disabled=True, use_container_width=True)
                        
                        st.markdown("<div style='margin: 5px 0; border-bottom: 1px solid #374151;'></div>", unsafe_allow_html=True)
                else:
                    st.warning("No orders available with packing data. Please add packing size information to orders.")
            
            with col2:
                st.markdown(f"### 🚢 {container_type}")
                
                # Calculate current load
                current_items = st.session_state["container_cart"]
                total_cbm_loaded = sum([item['Total CBM'] for item in current_items])
                total_qty_loaded = sum([item['Qty'] for item in current_items])
                percentage_loaded = (total_cbm_loaded / selected_specs['capacity_cbm']) * 100
                
                # Visual representation
                color = selected_specs['color']
                st.markdown(f"""
                <div class="container-visual" style="border-color: {color};">
                    <h4 style='color: white; margin-bottom: 15px;'>Container Load Status</h4>
                    <p style='color: #D1D5DB; margin: 5px 0;'>Type: <strong>{container_type}</strong></p>
                    <p style='color: #D1D5DB; margin: 5px 0;'>Capacity: {selected_specs['capacity_cbm']} m³</p>
                    <div class="container-progress" style="margin: 15px 0;">
                        <div class="container-fill" style="width: {min(percentage_loaded, 100):.1f}%; background: {color};"></div>
                    </div>
                    <div style='text-align: center; margin: 15px 0;'>
                        <h2 style='color: white; margin: 5px 0;'>{total_cbm_loaded:.6f} m³</h2>
                        <p style='color: #10B981; font-size: 1.2em; margin: 5px 0;'>{percentage_loaded:.1f}% Full</p>
                        <p style='color: #60A5FA; margin: 5px 0;'>Available: {selected_specs['capacity_cbm'] - total_cbm_loaded:.6f} m³</p>
                        <p style='color: #F59E0B; margin: 5px 0;'>Total Qty: {total_qty_loaded:,} pcs</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Items in container
                if current_items:
                    st.markdown("#### 📦 Items in Container:")
                    
                    for idx, item in enumerate(current_items):
                        st.markdown(f"""
                        <div style='background-color: #1F2937; padding: 10px; margin: 8px 0; border-radius: 5px; border-left: 3px solid {color};'>
                            <strong style='color: #60A5FA;'>{item['Order ID']}</strong><br>
                            <span style='color: #D1D5DB; font-size: 0.9em;'>{item['Buyer']}</span><br>
                            <span style='color: #9CA3AF; font-size: 0.85em;'>{item['Produk']}</span><br>
                            <div style='margin-top: 5px;'>
                                <span style='color: #10B981;'>📦 {item['Qty']} pcs</span> | 
                                <span style='color: #F59E0B;'>📏 {item['Total CBM']:.6f} m³</span>
                            </div>
                            <span style='color: #6B7280; font-size: 0.8em;'>Progress: {item['Progress']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("🗑 Remove", key=f"remove_sim_{idx}", use_container_width=True):
                            st.session_state["container_cart"].pop(idx)
                            st.rerun()
                    
                    st.markdown("---")
                    
                    # Container name input
                    container_name = st.text_input("Container Name (Optional)", 
                                                  placeholder=f"CONT-{datetime.datetime.now().strftime('%Y%m%d')}",
                                                  key="container_name_input")
                    
                    container_notes = st.text_area("Notes", 
                                                  placeholder="Add any notes about this container load...",
                                                  height=80,
                                                  key="container_notes")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("💾 Save Simulation", use_container_width=True, type="primary"):
                            # Generate container ID
                            if container_name:
                                cont_id = container_name
                            else:
                                cont_id = f"CONT-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                            
                            # Save container data
                            container_data = {
                                "container_id": cont_id,
                                "date": str(datetime.date.today()),
                                "type": container_type,
                                "capacity": selected_specs['capacity_cbm'],
                                "loaded_cbm": total_cbm_loaded,
                                "percentage": percentage_loaded,
                                "total_qty": total_qty_loaded,
                                "items": current_items.copy(),
                                "notes": container_notes if container_notes else "",
                                "simulation_mode": True
                            }
                            
                            containers = st.session_state["containers"]
                            containers.append(container_data)
                            st.session_state["containers"] = containers
                            
                            if save_containers(containers):
                                st.success(f"✅ Container simulation '{cont_id}' saved successfully!")
                                st.balloons()
                                st.session_state["container_cart"] = []
                                st.rerun()
                    
                    with col_btn2:
                        if st.button("🗑 Clear All", use_container_width=True, type="secondary"):
