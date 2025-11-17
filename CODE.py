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

# ===== CSS RESPONSIVE & COMPACT WITH IMPROVED CALENDAR =====
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
    
    /* === RESPONSIVE CALENDAR STYLING === */
    .calendar-wrapper {
        width: 100%;
        overflow-x: auto;
        margin: 10px 0;
    }
    
    .calendar-cell {
        min-width: 50px;
        min-height: 60px;
        padding: 10px 5px;
        text-align: center;
        border-radius: 8px;
        margin: 3px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transition: transform 0.2s ease;
    }
    
    .calendar-cell:hover {
        transform: scale(1.05);
    }
    
    .calendar-day-number {
        font-weight: bold;
        font-size: 1.2em;
        margin-bottom: 3px;
    }
    
    .calendar-order-count {
        font-size: 0.75em;
        opacity: 0.9;
    }
    
    .calendar-header {
        font-weight: bold;
        text-align: center;
        padding: 8px;
        background: #1F2937;
        border-radius: 5px;
        margin-bottom: 5px;
    }
    
    /* Mobile responsive - Tablet */
    @media (max-width: 1024px) {
        .calendar-cell {
            min-width: 45px;
            min-height: 55px;
            padding: 8px 4px;
        }
        .calendar-day-number {
            font-size: 1.1em;
        }
        .calendar-order-count {
            font-size: 0.7em;
        }
    }
    
    /* Mobile responsive - Phone Landscape */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 0.5rem !important;
        }
        .calendar-cell {
            min-width: 40px;
            min-height: 50px;
            padding: 6px 3px;
        }
        .calendar-day-number {
            font-size: 1em;
        }
        .calendar-order-count {
            font-size: 0.65em;
        }
        .calendar-header {
            font-size: 0.9em;
            padding: 6px;
        }
        /* Stack calendar and chart vertically on mobile */
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
    }
    
    /* Mobile responsive - Phone Portrait */
    @media (max-width: 480px) {
        .calendar-cell {
            min-width: 32px;
            min-height: 42px;
            padding: 4px 2px;
            margin: 2px 1px;
        }
        .calendar-day-number {
            font-size: 0.9em;
        }
        .calendar-order-count {
            font-size: 0.6em;
        }
        .calendar-header {
            font-size: 0.8em;
            padding: 5px 2px;
        }
        h1 { font-size: 1.3rem !important; }
        h2 { font-size: 1.1rem !important; }
        h3 { font-size: 1rem !important; }
        .stButton button { width: 100% !important; }
    }
    
    /* Calendar Legend */
    .calendar-legend {
        margin-top: 15px;
        padding: 15px;
        background: #1F2937;
        border-radius: 8px;
    }
    
    .legend-items {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        justify-content: center;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .legend-color {
        width: 24px;
        height: 24px;
        border-radius: 4px;
    }
    
    @media (max-width: 480px) {
        .legend-items {
            gap: 10px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
        }
        .legend-item {
            font-size: 0.85em;
        }
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
    "⚙️ Update Progress": "Progress",
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
    if st.button("⬅️ Back to Dashboard", type="secondary"):
        st.session_state["menu"] = "Dashboard"
        st.rerun()
    st.markdown("---")


# ===== MENU: DASHBOARD WITH RESPONSIVE CALENDAR =====
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
                        st.markdown(f"**{row['Order ID']}**")
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
        
        # ===== SECTION 2: RESPONSIVE PRODUCTION CALENDAR =====
        st.markdown("### 📅 Production Calendar")
        
        today = datetime.date.today()
        current_month = today.month
        current_year = today.year
        
        # Responsive filter row
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
            st.markdown(f"**📌 {len(df_month)} orders di bulan ini**")
        
        st.markdown("---")
        
        # Calendar and chart in responsive columns
        # On mobile, these will stack automatically
        col_cal, col_chart = st.columns([7, 3])
        
        with col_cal:
            st.markdown("#### 📆 Kalender Produksi")
            
            import calendar
            cal = calendar.monthcalendar(selected_year, month_num)
            
            # Calendar header with responsive styling
            days = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
            header_cols = st.columns(7)
            for i, day in enumerate(days):
                header_cols[i].markdown(
                    f"<div class='calendar-header'>{day}</div>", 
                    unsafe_allow_html=True
                )
            
            # Calendar body with responsive cells
            for week in cal:
                week_cols = st.columns(7)
                for i, day in enumerate(week):
                    if day == 0:
                        week_cols[i].markdown(
                            "<div style='min-height: 60px;'></div>", 
                            unsafe_allow_html=True
                        )
                    else:
                        date_obj = datetime.date(selected_year, month_num, day)
                        
                        # Determine cell color and content
                        cell_html = ""
                        if not df_month.empty:
                            orders_on_date = df_month[df_month['Due Date'].dt.date == date_obj]
                            
                            if len(orders_on_date) > 0:
                                done_count = len(orders_on_date[orders_on_date['Tracking Status'] == 'Done'])
                                if done_count == len(orders_on_date):
                                    bg_color = "#10B981"
                                    status_text = "✅"
                                elif date_obj < today:
                                    bg_color = "#EF4444"
                                    status_text = "⚠️"
                                elif date_obj == today:
                                    bg_color = "#F59E0B"
                                    status_text = "📅"
                                else:
                                    bg_color = "#3B82F6"
                                    status_text = "📦"
                                
                                cell_html = f"""
                                <div class='calendar-cell' style='background-color: {bg_color}; color: white;'>
                                    <div class='calendar-day-number'>{day}</div>
                                    <div class='calendar-order-count'>{status_text} {len(orders_on_date)}</div>
                                </div>
                                """
                            else:
                                if date_obj == today:
                                    cell_html = f"""
                                    <div class='calendar-cell' style='border: 2px solid #3B82F6; color: #3B82F6;'>
                                        <div class='calendar-day-number'>{day}</div>
                                    </div>
                                    """
                                else:
                                    cell_html = f"""
                                    <div class='calendar-cell' style='background: #1F2937; color: #6B7280;'>
                                        <div class='calendar-day-number'>{day}</div>
                                    </div>
                                    """
                        else:
                            if date_obj == today:
                                cell_html = f"""
                                <div class='calendar-cell' style='border: 2px solid #3B82F6; color: #3B82F6;'>
                                    <div class='calendar-day-number'>{day}</div>
                                </div>
                                """
                            else:
                                cell_html = f"""
                                <div class='calendar-cell' style='background: #1F2937; color: #6B7280;'>
                                    <div class='calendar-day-number'>{day}</div>
                                </div>
                                """
                        
                        week_cols[i].markdown(cell_html, unsafe_allow_html=True)
            
            # Calendar legend with responsive design
            st.markdown("""
            <div class='calendar-legend'>
                <div class='legend-items'>
                    <div class='legend-item'>
                        <div class='legend-color' style='background: #10B981;'></div>
                        <span>Selesai</span>
                    </div>
                    <div class='legend-item'>
                        <div class='legend-color' style='background: #3B82F6;'></div>
                        <span>Dijadwalkan</span>
                    </div>
                    <div class='legend-item'>
                        <div class='legend-color' style='background: #F59E0B;'></div>
                        <span>Hari Ini</span>
                    </div>
                    <div class='legend-item'>
                        <div class='legend-color' style='background: #EF4444;'></div>
                        <span>Terlambat</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_chart:
            st.markdown("#### 📊 Status Distribution")
            
            status_dist = df["Tracking Status"].value_counts()
            fig_status = px.pie(
                values=status_dist.values, 
                names=status_dist.index,
                color_discrete_map={"On Going": "#3B82F6", "Done": "#10B981"},
                hole=0.4
            )
            fig_status.update_traces(textposition='inside', textinfo='percent+label')
            fig_status.update_layout(
                showlegend=True, 
                height=350,  # Increased height for better visibility
                margin=dict(t=20, b=20, l=10, r=10)
            )
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

# Note: Bagian menu lainnya (Input, Orders, Progress, dll.) tetap sama seperti kode asli
# Hanya bagian Dashboard Calendar yang diupdate untuk responsiveness

st.markdown("---")
st.caption(f"© 2025 PPIC-DSS System | Responsive Calendar v12.0 | Optimized for Mobile & Desktop")
