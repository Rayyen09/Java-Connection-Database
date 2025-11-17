import streamlit as st
import pandas as pd
import datetime
import json
import os
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from streamlit.components.v1 import html

# ===== KONFIGURASI DATABASE =====
DATABASE_PATH = "ppic_data.json"
BUYER_DB_PATH = "buyers.json"
PRODUCT_DB_PATH = "products.json"
PROCUREMENT_DB_PATH = "procurement.json"
CONTAINER_DB_PATH = "containers.json"
TEMPLATE_ORDER_DB_PATH = "template_orders.json"

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
    """
    /* Buyer Stats Card */
    .buyer-stats-card {
        background: #667eea;
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin: 5px 0;
    }
    
    /* Workstation Card */
    .workstation-card {
        background: #1F2937;
        border-left: 4px solid #3B82F6;
        padding: 15px;
        border-radius: 5px;
        margin: 5px 0;
    }
    """

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
                df_filtered = pd.DataFrame(data)
                if not df_filtered.empty:
                    df_filtered['Order Date'] = pd.to_datetime(df_filtered['Order Date']).dt.date
                    df_filtered['Due Date'] = pd.to_datetime(df_filtered['Due Date']).dt.date
                    if 'History' not in df_filtered.columns:
                        df_filtered['History'] = df_filtered.apply(lambda x: json.dumps([]), axis=1)
                    # Add new columns if not exist
                    if 'Product CBM' not in df_filtered.columns:
                        df_filtered['Product CBM'] = 0.0
                return df_filtered
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

def save_data(df_filtered):
    try:
        df_filtered_copy = df_filtered.copy()
        df_filtered_copy['Order Date'] = df_filtered_copy['Order Date'].astype(str)
        df_filtered_copy['Due Date'] = df_filtered_copy['Due Date'].astype(str)
        with open(DATABASE_PATH, 'w', encoding='utf-8') as f:
            json.dump(df_filtered_copy.to_dict('records'), f, ensure_ascii=False, indent=2)
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
    df_filtered = st.session_state["data_produksi"]
    if df_filtered.empty or not buyer_name:
        return []
    
    buyer_products = df_filtered[df_filtered["Buyer"] == buyer_name]["Produk"].unique().tolist()
    return sorted(buyer_products)

def calculate_production_metrics(df_filtered):
    """Calculate WIP, Finished Goods, and Shipping metrics"""
    wip_stages = ["Warehouse", "Fitting 1", "Amplas", "Revisi 1", "Spray", "Fitting 2", "Revisi Fitting 2"]
    
    wip_qty = 0
    wip_cbm = 0
    finished_qty = 0  # Packaging stage = Produk Jadi
    finished_cbm = 0
    shipping_qty = 0  # Pengiriman stage
    shipping_cbm = 0
    
    for idx, row in df_filtered.iterrows():
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

def calculate_buyer_stats(df_filtered, buyer_name=None):
    """Calculate detailed statistics for a buyer"""
    if buyer_name:
        buyer_df_filtered = df_filtered[df_filtered["Buyer"] == buyer_name]
    else:
        buyer_df_filtered = df_filtered
    
    if buyer_df_filtered.empty:
        return None
    
    stats = {
        "total_orders": len(buyer_df_filtered),
        "total_qty": buyer_df_filtered["Qty"].sum(),
        "total_cbm": buyer_df_filtered["Total CBM"].sum(),
        "avg_progress": buyer_df_filtered["Progress"].str.rstrip('%').astype('float').mean(),
        "completed_orders": len(buyer_df_filtered[buyer_df_filtered["Progress"] == "100%"]),
        "in_progress_orders": len(buyer_df_filtered[buyer_df_filtered["Progress"] != "100%"])
    }
    
    # Calculate workstation CBM
    workstation_cbm = {}
    stages = get_tracking_stages()
    
    for stage in stages:
        stage_cbm = 0
        stage_qty = 0
        
        for idx, row in buyer_df_filtered.iterrows():
            try:
                tracking_data = json.loads(row["Tracking"])
                qty_in_stage = tracking_data.get(stage, {}).get("qty", 0)
                if qty_in_stage > 0:
                    cbm_per_pcs = float(row.get("CBM per Pcs", 0))
                    stage_cbm += qty_in_stage * cbm_per_pcs
                    stage_qty += qty_in_stage
            except:
                pass
        
        if stage_cbm > 0:
            workstation_cbm[stage] = {
                "cbm": stage_cbm,
                "qty": stage_qty,
                "percentage": (stage_cbm / stats["total_cbm"] * 100) if stats["total_cbm"] > 0 else 0
            }
    
    stats["workstation_cbm"] = workstation_cbm
    return stats

def get_order_date_category(order_date):
    """Categorize order by date"""
    today = datetime.date.today()
    
    if isinstance(order_date, str):
        order_date = pd.to_datetime(order_date).date()
    elif isinstance(order_date, pd.Timestamp):
        order_date = order_date.date()
    
    days_diff = (today - order_date).days
    
    if days_diff == 0:
        return "Today"
    elif days_diff <= 7:
        return "This Week"
    elif days_diff <= 30:
        return "This Month"
    else:
        return "Older"

def load_template_orders():
    """Load template orders from database"""
    if os.path.exists(TEMPLATE_ORDER_DB_PATH):
        try:
            with open(TEMPLATE_ORDER_DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_template_orders(templates):
    """Save template orders to database"""
    try:
        with open(TEMPLATE_ORDER_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def add_template_order(buyer, produk, template_data):
    """Add a new template order"""
    templates = st.session_state["template_orders"]
    template_id = f"TMPL-{buyer[:3].upper()}-{produk[:5].upper()}-{len(templates)+1}"
    
    new_template = {
        "template_id": template_id,
        "buyer": buyer,
        "produk": produk,
        "data": template_data,
        "created_at": str(datetime.datetime.now()),
        "last_used": None,
        "usage_count": 0
    }
    
    templates.append(new_template)
    st.session_state["template_orders"] = templates
    return save_template_orders(templates)

def get_templates_by_buyer_product(buyer, produk):
    """Get templates for specific buyer and product"""
    templates = st.session_state["template_orders"]
    return [t for t in templates if t["buyer"] == buyer and t["produk"] == produk]

def update_template_usage(template_id):
    """Update template usage statistics"""
    templates = st.session_state["template_orders"]
    for template in templates:
        if template["template_id"] == template_id:
            template["usage_count"] += 1
            template["last_used"] = str(datetime.datetime.now())
            break
    st.session_state["template_orders"] = templates
    save_template_orders(templates)

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
if "template_orders" not in st.session_state:
    st.session_state["template_orders"] = load_template_orders()


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


# ===== MENU: DASHBOARD =====
if st.session_state["menu"] == "Dashboard":
    st.title("📊 Dashboard PT JAVA CONNECTION")
    
    df_filtered = st.session_state["data_produksi"]
    
    if not df_filtered.empty:
        # Calculate tracking status
        df_filtered['Tracking Status'] = df_filtered.apply(
            lambda row: get_tracking_status_from_progress(row['Progress']), 
            axis=1
        )
        
        # Calculate production metrics
        wip_qty, wip_cbm, finished_qty, finished_cbm, shipping_qty, shipping_cbm = calculate_production_metrics(df_filtered)

         # ===== BUYER FILTER (BARU) =====
        st.markdown("### 🎯 Filter Dashboard")
        col_filter1, col_filter2 = st.columns([2, 1])
        
        with col_filter1:
            all_buyers = sorted(df_filtered["Buyer"].unique().tolist())
            selected_buyer = st.selectbox(
                "Pilih Buyer (Kosongkan untuk semua)",
                ["-- Semua Buyer --"] + all_buyers,
                key="dashboard_buyer_filter"
            )
        
        # Apply buyer filter
        if selected_buyer and selected_buyer != "-- Semua Buyer --":
            df_filtered_filtered = df_filtered[df_filtered["Buyer"] == selected_buyer].copy()
            st.info(f"📊 Menampilkan data untuk: **{selected_buyer}**")
        else:
            df_filtered_filtered = df_filtered.copy()
            st.info(f"📊 Menampilkan data untuk: **Semua Buyer**")
        
        st.markdown("---")
        
        # Calculate production metrics with filtered data
        wip_qty, wip_cbm, finished_qty, finished_cbm, shipping_qty, shipping_cbm = calculate_production_metrics(df_filtered_filtered)
        
        # ===== BUYER STATISTICS (BARU) =====
        if selected_buyer and selected_buyer != "-- Semua Buyer --":
            st.markdown("### 📊 Statistik Buyer")
            
            buyer_stats = calculate_buyer_stats(df_filtered_filtered, selected_buyer)
            
            if buyer_stats:
                col_stat1, col_stat2, col_stat3, col_stat4, col_stat5 = st.columns(5)
                
                col_stat1.metric("Total Orders", f"{buyer_stats['total_orders']}")
                col_stat2.metric("Total Qty", f"{buyer_stats['total_qty']:,} pcs")
                col_stat3.metric("Total CBM", f"{buyer_stats['total_cbm']:.4f} m³")
                col_stat4.metric("Avg Progress", f"{buyer_stats['avg_progress']:.1f}%")
                col_stat5.metric("Completed", f"{buyer_stats['completed_orders']}/{buyer_stats['total_orders']}")
                
                st.markdown("---")
                
                # Workstation CBM Distribution
                st.markdown("#### 🏭 Distribusi CBM per Workstation")
                
                if buyer_stats["workstation_cbm"]:
                    ws_data = []
                    for stage, data in buyer_stats["workstation_cbm"].items():
                        ws_data.append({
                            "Workstation": stage,
                            "CBM": data["cbm"],
                            "Qty": data["qty"],
                            "Percentage": data["percentage"]
                        })
                    
                    ws_df_filtered = pd.DataFrame(ws_data)
                    ws_df_filtered = ws_df_filtered.sort_values("CBM", ascending=False)
                    
                    col_ws1, col_ws2 = st.columns([2, 1])
                    
                    with col_ws1:
                        fig_ws = px.bar(
                            ws_df_filtered,
                            x="Workstation",
                            y="CBM",
                            color="CBM",
                            color_continuous_scale="Blues",
                            title=f"CBM Distribution - {selected_buyer}"
                        )
                        fig_ws.update_layout(showlegend=False, height=300)
                        st.plotly_chart(fig_ws, use_container_width=True)
                    
                    with col_ws2:
                        for idx, row in ws_df_filtered.iterrows():
                            st.markdown(f"""
                            <div class="workstation-card">
                                <strong style='color: #60A5FA;'>{row['Workstation']}</strong><br>
                                <span style='color: #10B981;'>📦 {row['Qty']} pcs</span><br>
                                <span style='color: #F59E0B;'>📏 {row['CBM']:.6f} m³</span><br>
                                <span style='color: #9CA3AF;'>📊 {row['Percentage']:.1f}%</span>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Tidak ada data di workstation untuk buyer ini")
                
                st.markdown("---")
        
        # ===== PROGRESS BY TIME PERIOD (BARU) =====
        st.markdown("### 📅 Progress Orders by Time Period")
        
        df_filtered_filtered['Date Category'] = df_filtered_filtered['Order Date'].apply(get_order_date_category)
        df_filtered_filtered['Progress_Num'] = df_filtered_filtered['Progress'].str.rstrip('%').astype('float')
        
        date_categories = ["Today", "This Week", "This Month", "Older"]
        
        col_date1, col_date2 = st.columns([2, 1])
        
        with col_date1:
            progress_by_date = []
            
            for category in date_categories:
                cat_df_filtered = df_filtered_filtered[df_filtered_filtered['Date Category'] == category]
                if not cat_df_filtered.empty:
                    completed = len(cat_df_filtered[cat_df_filtered['Progress_Num'] == 100])
                    in_progress = len(cat_df_filtered[cat_df_filtered['Progress_Num'] < 100])
                    avg_progress = cat_df_filtered['Progress_Num'].mean()
                    
                    progress_by_date.append({
                        "Period": category,
                        "Completed": completed,
                        "In Progress": in_progress,
                        "Avg Progress": avg_progress,
                        "Total": len(cat_df_filtered)
                    })
            
            if progress_by_date:
                prog_df_filtered = pd.DataFrame(progress_by_date)
                
                fig_prog = go.Figure()
                
                fig_prog.add_trace(go.Bar(
                    name='Completed',
                    x=prog_df_filtered['Period'],
                    y=prog_df_filtered['Completed'],
                    marker_color='#10B981'
                ))
                
                fig_prog.add_trace(go.Bar(
                    name='In Progress',
                    x=prog_df_filtered['Period'],
                    y=prog_df_filtered['In Progress'],
                    marker_color='#F59E0B'
                ))
                
                fig_prog.update_layout(
                    barmode='group',
                    title='Orders Status by Time Period',
                    xaxis_title='Period',
                    yaxis_title='Number of Orders',
                    height=300
                )
                
                st.plotly_chart(fig_prog, use_container_width=True)
        
        with col_date2:
            for item in progress_by_date:
                completion_rate = (item['Completed'] / item['Total'] * 100) if item['Total'] > 0 else 0
                
                st.markdown(f"""
                <div class="buyer-stats-card">
                    <h4 style='margin: 0 0 10px 0;'>{item['Period']}</h4>
                    <p style='margin: 5px 0;'>Total: <strong>{item['Total']}</strong></p>
                    <p style='margin: 5px 0;'>✅ Completed: <strong>{item['Completed']}</strong></p>
                    <p style='margin: 5px 0;'>🔄 In Progress: <strong>{item['In Progress']}</strong></p>
                    <p style='margin: 5px 0;'>📊 Avg: <strong>{item['Avg Progress']:.1f}%</strong></p>
                    <p style='margin: 5px 0;'>📈 Rate: <strong>{completion_rate:.1f}%</strong></p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ===== BUYER COMPARISON (BARU - hanya muncul jika semua buyer) =====
        if selected_buyer == "-- Semua Buyer --":
            st.markdown("### 👥 Comparison by Buyer")
            
            buyers_list = df_filtered["Buyer"].unique().tolist()
            buyer_comparison = []
            
            for buyer in buyers_list:
                buyer_data = df_filtered[df_filtered["Buyer"] == buyer]
                total_cbm = buyer_data["Total CBM"].sum()
                total_qty = buyer_data["Qty"].sum()
                avg_progress = buyer_data["Progress"].str.rstrip('%').astype('float').mean()
                completed = len(buyer_data[buyer_data["Progress"] == "100%"])
                
                buyer_comparison.append({
                    "Buyer": buyer,
                    "Orders": len(buyer_data),
                    "Total Qty": total_qty,
                    "Total CBM": total_cbm,
                    "Avg Progress": avg_progress,
                    "Completed": completed
                })
            
            comp_df_filtered = pd.DataFrame(buyer_comparison)
            comp_df_filtered = comp_df_filtered.sort_values("Total CBM", ascending=False)
            
            col_comp1, col_comp2 = st.columns(2)
            
            with col_comp1:
                fig_buyer_cbm = px.bar(
                    comp_df_filtered,
                    x="Buyer",
                    y="Total CBM",
                    color="Total CBM",
                    color_continuous_scale="Viridis",
                    title="Total CBM by Buyer"
                )
                fig_buyer_cbm.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig_buyer_cbm, use_container_width=True)
            
            with col_comp2:
                fig_buyer_prog = px.scatter(
                    comp_df_filtered,
                    x="Total Qty",
                    y="Avg Progress",
                    size="Total CBM",
                    color="Buyer",
                    title="Progress vs Quantity by Buyer",
                    hover_data=["Orders", "Completed"]
                )
                fig_buyer_prog.update_layout(height=300)
                st.plotly_chart(fig_buyer_prog, use_container_width=True)
            
            st.markdown("---")

        
        # ===== SECTION 1: TOP ROW - RECENT ORDERS + KEY METRICS =====
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.markdown("### 🕒 Recent Orders")
            
            # Search/filter for recent orders
            search_recent = st.text_input("🔍 Search orders...", key="search_recent_orders")
            
            recent_df_filtered = df_filtered.sort_values("Order Date", ascending=False)
            
            if search_recent:
                recent_df_filtered_filtered = recent_df_filtered[
                    recent_df_filtered["Order ID"].str.contains(search_recent, case=False, na=False) | 
                    recent_df_filtered["Buyer"].str.contains(search_recent, case=False, na=False) |
                    recent_df_filtered["Produk"].str.contains(search_recent, case=False, na=False)
                ]
            
            # Scrollable container for recent orders
            with st.container():
                st.markdown('<div class="recent-orders-container">', unsafe_allow_html=True)
                
                for idx, row in recent_df_filtered.head(20).iterrows():
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
            total_orders = len(df_filtered)
            ongoing = len(df_filtered[df_filtered["Tracking Status"] == "On Going"])
            done = len(df_filtered[df_filtered["Tracking Status"] == "Done"])
            total_qty = df_filtered["Qty"].sum()
            
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
            df_filtered_copy = df_filtered.copy()
            df_filtered_copy['Due Date'] = pd.to_datetime(df_filtered_copy['Due Date'])
            df_filtered_month = df_filtered_copy[(df_filtered_copy['Due Date'].dt.month == month_num) & 
                         (df_filtered_copy['Due Date'].dt.year == selected_year)]
            
            if not df_filtered_month.empty:
                st.markdown(f"**📌 {len(df_filtered_month)} orders di bulan ini**")
            
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
                        
                        if not df_filtered_month.empty:
                            orders_on_date = df_filtered_month[df_filtered_month['Due Date'].dt.date == date_obj]
                            
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
            
            status_dist = df_filtered["Tracking Status"].value_counts()
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
        
        for idx, row in df_filtered.iterrows():
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
    st.markdown("### 📚 Quick Order from Template")
    
    col_tmpl1, col_tmpl2, col_tmpl3 = st.columns([2, 2, 1])
    
    with col_tmpl1:
        buyers_list = get_buyer_names()
        template_buyer = st.selectbox("Pilih Buyer", [""] + buyers_list, key="template_buyer_select")
    
    with col_tmpl2:
        if template_buyer:
            buyer_products = get_products_by_buyer(template_buyer)
            if buyer_products:
                template_product = st.selectbox("Pilih Produk", [""] + buyer_products, key="template_product_select")
            else:
                st.info("Buyer ini belum punya order")
                template_product = None
        else:
            template_product = st.selectbox("Pilih Produk", ["Pilih buyer terlebih dahulu"], disabled=True, key="template_product_disabled")
    
    with col_tmpl3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Cari Template", use_container_width=True, disabled=not (template_buyer and template_product)):
            templates = get_templates_by_buyer_product(template_buyer, template_product)
            st.session_state["found_templates"] = templates
    
    # Display found templates
    if st.session_state.get("found_templates"):
        templates = st.session_state["found_templates"]
        
        st.markdown(f"**📋 Ditemukan {len(templates)} template**")
        
        for tmpl_idx, template in enumerate(templates):
            with st.expander(f"Template #{tmpl_idx + 1} | Used {template.get('usage_count', 0)}x", expanded=False):
                template_data = template["data"]
                
                st.write(f"**Material:** {template_data.get('material', '-')}")
                st.write(f"**Finishing:** {template_data.get('finishing', '-')}")
                st.write(f"**Packing Size:** {template_data.get('pack_p', 0)} x {template_data.get('pack_l', 0)} x {template_data.get('pack_t', 0)} cm")
                st.write(f"**CBM per Pcs:** {template_data.get('cbm_per_pcs', 0):.6f} m³")
                
                col_use1, col_use2 = st.columns([3, 1])
                
                with col_use1:
                    new_qty = st.number_input(
                        "Quantity untuk order baru",
                        min_value=1,
                        value=template_data.get('qty', 1),
                        key=f"template_qty_{tmpl_idx}"
                    )
                
                with col_use2:
                    if st.button("✅ Gunakan", key=f"use_template_{tmpl_idx}", use_container_width=True, type="primary"):
                        st.session_state["prefill_buyer"] = template_buyer
                        st.session_state["prefill_product"] = template_product
                        st.session_state["prefill_data"] = template_data
                        st.session_state["prefill_qty"] = new_qty
                        update_template_usage(template["template_id"])
                        st.success("✅ Template loaded!")
                        st.rerun()
    
    st.markdown("---")
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
            st.markdown("**Product Information**")
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
            st.markdown("**Specifications**")
            material = st.text_input("Material", placeholder="Contoh: Kayu Jati, Mdf_filtered", key="form_material")
            finishing = st.text_input("Finishing", placeholder="Contoh: Natural, Duco Putih", key="form_finishing")
            
            st.markdown("**Product Size (cm)**")
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
                st.success(f"📦 Product CBM: **{product_cbm:.6f} m³**")
            else:
                st.info(f"📦 Product CBM: 0.000000 m³")
        
        with col3:
            st.markdown("**Packing Information**")
            st.markdown("**Packing Size (cm)**")
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
                st.success(f"📦 CBM per Pcs: **{cbm_per_pcs:.6f} m³**")
                st.info(f"📦 Total CBM: **{total_cbm:.6f} m³**")
            else:
                st.info(f"📦 CBM per Pcs: 0.000000 m³")
                st.info(f"📦 Total CBM: 0.000000 m³")
            
            description = st.text_area("Description", placeholder="Deskripsi produk...", height=50, key="form_desc")
    
    keterangan = st.text_area("Keterangan Tambahan", placeholder="Catatan khusus...", height=50, key="form_notes")

    save_as_template = st.checkbox("💾 Simpan sebagai template", key="save_template_check")
    # Add product button
    if add_product_btn:
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
            if save_as_template and buyer and produk_name:
                template_data = {
                    "qty": qty,
                    "material": material,
                    "finishing": finishing,
                    "prod_p": prod_p,
                    "prod_l": prod_l,
                    "prod_t": prod_t,
                    "pack_p": pack_p,
                    "pack_l": pack_l,
                    "pack_t": pack_t,
                    "cbm_per_pcs": cbm_per_pcs,
                }
                
                if add_template_order(buyer, produk_name, template_data):
                    st.success(f"✅ Produk ditambahkan dan disimpan sebagai template!")
                else:
                    st.success(f"✅ Produk ditambahkan!")
            else:
                st.success(f"✅ Produk ditambahkan!")
            
            st.rerun()

            st.success(f"✅ Produk '{produk_name}' ditambahkan! Total produk: {len(st.session_state['input_products'])}")
            st.rerun()
        else:
            st.warning("⚠️ Harap isi nama produk dan quantity!")
    
    if st.session_state["input_products"]:
        st.markdown("---")
        st.markdown("### 📋 Daftar Produk dalam Order Ini")
        
        for idx, product in enumerate(st.session_state["input_products"]):
            with st.expander(f"📦 {idx + 1}. {product['nama']} ({product['qty']} pcs) - CBM: {product['total_cbm']:.6f} m³", expanded=False):
                col_display1, col_display2, col_display3 = st.columns([2, 2, 1])
                
                with col_display1:
                    st.write(f"**Material:** {product['material']}")
                    st.write(f"**Finishing:** {product['finishing']}")
                    st.write(f"**Product Size:** {product['prod_p']:.2f} x {product['prod_l']:.2f} x {product['prod_t']:.2f} cm")
                    st.write(f"**Product CBM:** {product['product_cbm']:.6f} m³")
                
                with col_display2:
                    st.write(f"**Packing Size:** {product['pack_p']:.2f} x {product['pack_l']:.2f} x {product['pack_t']:.2f} cm")
                    st.write(f"**CBM per Pcs:** {product['cbm_per_pcs']:.6f} m³")
                    st.write(f"**Total CBM:** {product['total_cbm']:.6f} m³")
                
                with col_display3:
                    if st.button("🗑️ Hapus", key=f"remove_product_{idx}", use_container_width=True):
                        st.session_state["input_products"].pop(idx)
                        st.rerun()
        
        total_cbm_all = sum([p['total_cbm'] for p in st.session_state["input_products"]])
        st.info(f"📦 Total CBM untuk semua produk: **{total_cbm_all:.6f} m³**")
        
        col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 2])
        
        with col_submit1:
            if st.button("🗑️ BATAL", use_container_width=True, type="secondary"):
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
                    
                    new_df_filtered = pd.DataFrame(new_orders)
                    st.session_state["data_produksi"] = pd.concat(
                        [st.session_state["data_produksi"], new_df_filtered], ignore_index=True
                    )
                    
                    if save_data(st.session_state["data_produksi"]):
                        st.success(f"✅ Order {new_order_id} dengan {len(st.session_state['input_products'])} produk berhasil ditambahkan!")
                        st.balloons()
                        st.session_state["input_products"] = []
                        st.rerun()
                else:
                    st.warning("⚠️ Harap pilih buyer dan tambahkan minimal 1 produk!")
# ===== MENU: DAFTAR ORDER =====
elif st.session_state["menu"] == "Orders":
    st.header("📦 DAFTAR ORDER")
    
    df_filtered = st.session_state["data_produksi"]
    
    if not df_filtered.empty:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_buyer = st.multiselect("Filter Buyer", df_filtered["Buyer"].unique().tolist())
        with col_f2:
            search_order = st.text_input("🔍 Cari Order ID / Produk")
        
        df_filtered_filtered = df_filtered.copy()
        if filter_buyer:
            df_filtered_filtered = df_filtered_filtered[df_filtered_filtered["Buyer"].isin(filter_buyer)]
        if search_order:
            df_filtered_filtered = df_filtered_filtered[
                df_filtered_filtered["Order ID"].str.contains(search_order, case=False, na=False) | 
                df_filtered_filtered["Produk"].str.contains(search_order, case=False, na=False)
            ]
        
        st.markdown("---")
        st.info(f"📦 Menampilkan {len(df_filtered_filtered)} order dari {df_filtered_filtered['Buyer'].nunique()} buyer")
        
        buyers = df_filtered_filtered["Buyer"].unique()
        
        for buyer in sorted(buyers):
            buyer_orders = df_filtered_filtered[df_filtered_filtered["Buyer"] == buyer]
            buyer_count = len(buyer_orders)
            
            with st.expander(f"👤 **{buyer}** ({buyer_count} orders)", expanded=False):
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
                                    st.write(f"**Product:** {row['Produk']}")
                                    st.write(f"**Qty:** {row['Qty']} pcs")
                                    st.write(f"**Material:** {row.get('Material', '-')}")
                                    st.write(f"**Finishing:** {row.get('Finishing', '-')}")
                                    st.write(f"**Product Size:** {row.get('Product Size P', 0)} x {row.get('Product Size L', 0)} x {row.get('Product Size T', 0)} cm")
                                
                                with col2:
                                    st.write(f"**Packing Size:** {row.get('Packing Size P', 0)} x {row.get('Packing Size L', 0)} x {row.get('Packing Size T', 0)} cm")
                                    st.write(f"**CBM per Pcs:** {row.get('CBM per Pcs', 0):.6f} m³")
                                    st.write(f"**Total CBM:** {row.get('Total CBM', 0):.4f} m³")
                                    st.write(f"**Due Date:** {row['Due Date']}")
                                    st.write(f"**Progress:** {row['Progress']}")
                                    st.write(f"**Proses:** {row['Proses Saat Ini']}")
                                
                                with col3:
                                    if row.get('Image Path') and os.path.exists(row['Image Path']):
                                        st.image(row['Image Path'], caption="Product", width=150)
                                    else:
                                        st.info("📷 No image")
                                
                                if row.get('Description') and row['Description'] != '-':
                                    st.markdown("---")
                                    st.markdown(f"**📝 Description:** {row['Description']}")
                                
                                if row['Keterangan'] and row['Keterangan'] != '-':
                                    st.markdown(f"**💬 Keterangan:** {row['Keterangan']}")
                                
                                st.markdown("---")
                                btn_col1, btn_col2, btn_col3 = st.columns(3)
                                with btn_col1:
                                    if st.button("✏️ Edit Order", key=f"edit_order_{idx}", use_container_width=True, type="primary"):
                                        st.session_state["edit_order_mode"] = True
                                        st.session_state["edit_order_index"] = idx
                                        st.rerun()
                                with btn_col2:
                                    if st.button("⚙️ Edit Progress", key=f"edit_{idx}", use_container_width=True, type="secondary"):
                                        st.session_state["edit_order_idx"] = idx
                                        st.session_state["menu"] = "Progress"
                                        st.rerun()
                                with btn_col3:
                                    if st.button("🗑️ Delete Order", key=f"del_{idx}", use_container_width=True, type="secondary"):
                                        if st.session_state.get(f"confirm_delete_{idx}", False):
                                            st.session_state["data_produksi"].drop(idx, inplace=True)
                                            st.session_state["data_produksi"].reset_index(drop=True, inplace=True)
                                            save_data(st.session_state["data_produksi"])
                                            st.success(f"✅ Order {row['Order ID']} berhasil dihapus!")
                                            del st.session_state[f"confirm_delete_{idx}"]
                                            st.rerun()
                                        else:
                                            st.session_state[f"confirm_delete_{idx}"] = True
                                            st.warning("⚠️ Klik sekali lagi untuk konfirmasi hapus!")
                                            st.rerun()
                
                # Check if in edit mode for any order
                if st.session_state.get("edit_order_mode", False) and "edit_order_index" in st.session_state:
                    edit_idx = st.session_state["edit_order_index"]
                    edit_row = st.session_state["data_produksi"].loc[edit_idx]
                    
                    st.markdown("---")
                    st.markdown("## ✏️ EDIT ORDER")
                    st.markdown(f"### Editing: {edit_row['Order ID']} - {edit_row['Produk']}")
                    
                    with st.form("edit_order_form"):
                        col_edit1, col_edit2, col_edit3 = st.columns(3)
                        
                        with col_edit1:
                            st.markdown("**📦 Order Information**")
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
                            st.markdown("**🔧 Specifications**")
                            edit_material = st.text_input("Material", value=edit_row.get('Material', ''), key="edit_material")
                            edit_finishing = st.text_input("Finishing", value=edit_row.get('Finishing', ''), key="edit_finishing")
                            edit_description = st.text_area("Description", value=edit_row.get('Description', ''), height=100, key="edit_description")
                            
                            st.markdown("**Product Size (cm)**")
                            col_ps1, col_ps2, col_ps3 = st.columns(3)
                            with col_ps1:
                                edit_prod_p = st.number_input("P", min_value=0.0, value=float(edit_row.get('Product Size P', 0)), step=0.1, key="edit_prod_p")
                            with col_ps2:
                                edit_prod_l = st.number_input("L", min_value=0.0, value=float(edit_row.get('Product Size L', 0)), step=0.1, key="edit_prod_l")
                            with col_ps3:
                                edit_prod_t = st.number_input("T", min_value=0.0, value=float(edit_row.get('Product Size T', 0)), step=0.1, key="edit_prod_t")
                        
                        with col_edit3:
                            st.markdown("**📦 Packing Information**")
                            st.markdown("**Packing Size (cm)**")
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
    
    df_filtered = st.session_state["data_produksi"]
    
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
    
    if not df_filtered.empty:
        tab1, tab2 = st.tabs(["📦 Container Simulator", "📋 Container History"])
        
        with tab1:
            st.info("💡 **Mode Simulasi**: Simulasi loading container berdasarkan packing size yang sudah diinput, tanpa menunggu produksi selesai.")
            
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
                    filter_buyer = st.multiselect("Filter by Buyer", df_filtered["Buyer"].unique().tolist(), key="sim_buyer_filter")
                
                with col_filter2:
                    filter_product = st.multiselect("Filter by Product", df_filtered["Produk"].unique().tolist(), key="sim_product_filter")
                
                with col_filter3:
                    search_order = st.text_input("🔍 Search Order ID", key="sim_search")
                
                # Apply filters
                df_filtered_filtered = df_filtered.copy()
                if filter_buyer:
                    df_filtered_filtered = df_filtered_filtered[df_filtered_filtered["Buyer"].isin(filter_buyer)]
                if filter_product:
                    df_filtered_filtered = df_filtered_filtered[df_filtered_filtered["Produk"].isin(filter_product)]
                if search_order:
                    df_filtered_filtered = df_filtered_filtered[df_filtered_filtered["Order ID"].str.contains(search_order, case=False, na=False)]
                
                # Filter out orders with zero CBM
                df_filtered_filtered = df_filtered_filtered[df_filtered_filtered["Total CBM"] > 0]
                
                st.info(f"📦 {len(df_filtered_filtered)} orders available for simulation")
                
                # Display available orders with better styling
                if not df_filtered_filtered.empty:
                    # Sort by due date
                    df_filtered_filtered_sorted = df_filtered_filtered.sort_values("Due Date")
                    
                    for idx, order in df_filtered_filtered_sorted.iterrows():
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
                            st.caption(f"**{order['Buyer']}** | {order['Produk']}")
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
                        
                        if st.button("🗑️ Remove", key=f"remove_sim_{idx}", use_container_width=True):
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
                        if st.button("🗑️ Clear All", use_container_width=True, type="secondary"):
                            st.session_state["container_cart"] = []
                            st.rerun()
                else:
                    st.info("📦 Container is empty\n\nAdd orders from the left panel to start simulation.")
        
        with tab2:
            st.markdown("### 📋 Container Loading History")
            
            containers = st.session_state["containers"]
            
            if containers:
                # Add filter
                col_hist1, col_hist2 = st.columns(2)
                with col_hist1:
                    filter_type = st.multiselect("Filter by Container Type", 
                                                list(CONTAINER_TYPES.keys()),
                                                key="hist_type_filter")
                with col_hist2:
                    search_hist = st.text_input("🔍 Search Container ID", key="hist_search")
                
                # Apply filters
                filtered_containers = containers
                if filter_type:
                    filtered_containers = [c for c in filtered_containers if c['type'] in filter_type]
                if search_hist:
                    filtered_containers = [c for c in filtered_containers if search_hist.lower() in c['container_id'].lower()]
                
                st.info(f"📦 Showing {len(filtered_containers)} of {len(containers)} container simulations")
                
                for idx, container in enumerate(reversed(filtered_containers)):
                    is_simulation = container.get('simulation_mode', False)
                    
                    with st.expander(
                        f"🚢 {container['container_id']} - {container['date']} {'📝 (Simulation)' if is_simulation else ''}",
                        expanded=False
                    ):
                        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
                        
                        with col_c1:
                            st.metric("Type", container['type'])
                        with col_c2:
                            st.metric("Loaded", f"{container['loaded_cbm']:.6f} m³")
                        with col_c3:
                            st.metric("Utilization", f"{container['percentage']:.1f}%")
                        with col_c4:
                            st.metric("Total Qty", f"{container.get('total_qty', 0):,} pcs")
                        
                        if container.get('notes'):
                            st.markdown(f"**📝 Notes:** {container['notes']}")
                        
                        st.markdown("#### Items in Container:")
                        
                        # Create summary table
                        items_df_filtered = pd.DataFrame(container['items'])
                        if not items_df_filtered.empty:
                            display_df_filtered = items_df_filtered[['Order ID', 'Buyer', 'Produk', 'Qty', 'Total CBM']]
                            display_df_filtered['Total CBM'] = display_df_filtered['Total CBM'].apply(lambda x: f"{x:.6f} m³")
                            display_df_filtered['Qty'] = display_df_filtered['Qty'].apply(lambda x: f"{x:,} pcs")
                            
                            st.dataframe(display_df_filtered, use_container_width=True, hide_index=True)
                            
                            # Summary statistics
                            st.markdown("---")
                            col_sum1, col_sum2, col_sum3 = st.columns(3)
                            with col_sum1:
                                st.metric("Total Orders", len(container['items']))
                            with col_sum2:
                                unique_buyers = items_df_filtered['Buyer'].nunique()
                                st.metric("Unique Buyers", unique_buyers)
                            with col_sum3:
                                unique_products = items_df_filtered['Produk'].nunique()
                                st.metric("Unique Products", unique_products)
                        
                        # Delete button
                        if st.button("🗑️ Delete Container", key=f"del_cont_{idx}_{container['container_id']}", type="secondary"):
                            if st.session_state.get(f"confirm_del_cont_{idx}", False):
                                # Find original index in full list
                                original_idx = len(containers) - 1 - idx
                                containers.pop(original_idx)
                                st.session_state["containers"] = containers
                                if save_containers(containers):
                                    st.success("✅ Container deleted!")
                                    del st.session_state[f"confirm_del_cont_{idx}"]
                                    st.rerun()
                            else:
                                st.session_state[f"confirm_del_cont_{idx}"] = True
                                st.warning("⚠️ Click again to confirm deletion!")
                                st.rerun()
            else:
                st.info("📝 No container simulations saved yet. Create your first simulation in the 'Container Simulator' tab!")
    else:
        st.info("📝 No orders available. Please create orders first in 'Input Pesanan Baru'.")

# Continue with other menus (Orders, Progress, Tracking, etc.) - these remain the same as the original code
# but with the aligned form fixes for Procurement section...

# ===== MENU: UPDATE PROGRESS =====
elif st.session_state["menu"] == "Progress":
    st.header("⚙️ UPDATE PROGRESS PRODUKSI")
    
    df_filtered = st.session_state["data_produksi"]
    
    if df_filtered.empty:
        st.warning("📝 Belum ada order untuk diupdate.")
    else:
        st.markdown("### 📦 Pilih Order untuk Update")
        
        col_select1, col_select2 = st.columns(2)
        
        with col_select1:
            buyers_list = ["-- Pilih Buyer --"] + sorted(df_filtered["Buyer"].unique().tolist())
            selected_buyer = st.selectbox("1️⃣ Pilih Buyer", buyers_list, key="progress_select_buyer")
        
        with col_select2:
            if selected_buyer and selected_buyer != "-- Pilih Buyer --":
                buyer_df_filtered = df_filtered[df_filtered["Buyer"] == selected_buyer]
                products_list = ["-- Pilih Produk --"] + sorted(buyer_df_filtered["Produk"].unique().tolist())
                selected_product = st.selectbox("2️⃣ Pilih Produk", products_list, key="progress_select_product")
            else:
                st.selectbox("2️⃣ Pilih Produk", ["-- Pilih Buyer Terlebih Dahulu --"], disabled=True, key="progress_select_product_disabled")
                selected_product = None
        
        st.markdown("---")
        
        if selected_buyer and selected_buyer != "-- Pilih Buyer --" and selected_product and selected_product != "-- Pilih Produk --":
            df_filtered_filtered = df_filtered[(df_filtered["Buyer"] == selected_buyer) & (df_filtered["Produk"] == selected_product)]
            
            if df_filtered_filtered.empty:
                st.warning("⚠️ Tidak ada order yang sesuai dengan pilihan Anda.")
            else:
                stage_to_progress = {
                    "Pre Order": 0, "Order di Supplier": 10, "Warehouse": 20,
                    "Fitting 1": 30, "Amplas": 40, "Revisi 1": 50,
                    "Spray": 60, "Fitting 2": 70, "Revisi Fitting 2": 80,
                    "Packaging": 90, "Pengiriman": 100
                }
                stages_list = get_tracking_stages()

                for order_idx_in_filtered, (idx, order_data) in enumerate(df_filtered_filtered.iterrows()):
                    order_id = order_data["Order ID"]
                    
                    st.markdown(f"### 📦 Order: {order_id}")
                    st.info(f"**Buyer:** {order_data['Buyer']} | **Produk:** {order_data['Produk']} | **Qty Total:** {order_data['Qty']} pcs | **Progress:** {order_data['Progress']}")
                    
                    total_order_qty = order_data["Qty"]
                    
                    try:
                        tracking_data = json.loads(order_data["Tracking"])
                        for stage in stages_list:
                            if stage not in tracking_data:
                                tracking_data[stage] = {"qty": 0}
                    except:
                        tracking_data = init_tracking_data()
                        tracking_data[order_data["Proses Saat Ini"]] = {"qty": total_order_qty}
                    
                    st.subheader("📍 Posisi Qty Saat Ini")
                    
                    cols = st.columns(3)
                    col_idx = 0
                    qty_in_progress = 0
                    for stage in stages_list:
                        qty = tracking_data.get(stage, {}).get("qty", 0)
                        if qty > 0:
                            with cols[col_idx % 3]:
                                st.metric(f"**{stage}**", f"{qty} pcs")
                            col_idx += 1
                            qty_in_progress += qty
                    
                    if qty_in_progress != total_order_qty:
                        st.warning(f"Data Qty tidak sinkron! Qty terlacak: {qty_in_progress}, Total Qty Order: {total_order_qty}")
                    
                    st.markdown("---")
                    st.subheader("🚚 Pindahkan Qty ke Workstation Berikutnya")
                    
                    stages_with_qty = [stage for stage, data in tracking_data.items() if data.get("qty", 0) > 0]
                    
                    if not stages_with_qty:
                        st.warning("Semua Qty sudah 'Selesai' atau belum ada Qty di workstation manapun.")
                    else:
                        # Aligned form columns with proper spacing
                        with st.container():
                            col1, col2, col3 = st.columns([1, 1, 1])
                            
                            with col1:
                                from_stage = st.selectbox("Pindahkan DARI", stages_with_qty, key=f"from_stage_{order_id}")
                            
                            try:
                                from_stage_index = stages_list.index(from_stage)
                                if from_stage_index < len(stages_list) - 1:
                                    to_stage = stages_list[from_stage_index + 1]
                                else:
                                    to_stage = from_stage
                            except:
                                to_stage = stages_list[0]
                            
                            with col2:
                                max_qty_available = tracking_data.get(from_stage, {}).get("qty", 0)
                                qty_to_move = st.number_input(
                                    f"Jumlah Qty (Max: {max_qty_available})", 
                                    min_value=1, 
                                    max_value=max_qty_available, 
                                    value=max_qty_available,
                                    key=f"qty_move_{order_id}"
                                )
                            
                            with col3:
                                st.markdown("**Pindahkan KE:**")
                                if to_stage != from_stage:
                                    st.info(f"**{to_stage}**")
                                else:
                                    st.info("Sudah di workstation terakhir")

                        notes = st.text_area("Catatan Update (Opsional)", placeholder="Misal: 5 pcs selesai...", key=f"notes_{order_id}")
                        
                        confirm_key = f"confirm_move_{order_id}"
                        
                        if st.session_state.get(confirm_key, False):
                            st.warning(f"⚠️ KONFIRMASI: Anda akan memindahkan **{qty_to_move} pcs** dari **{from_stage}** ke **{to_stage}**. Pastikan sudah benar!")
                            
                            col_confirm1, col_confirm2 = st.columns(2)
                            
                            with col_confirm1:
                                if st.button("✅ YA, PINDAHKAN", type="primary", use_container_width=True, key=f"yes_move_{order_id}"):
                                    if not to_stage or not from_stage or to_stage == from_stage:
                                        st.error("Tidak dapat memindahkan Qty!")
                                        st.session_state[confirm_key] = False
                                    else:
                                        tracking_data[from_stage]["qty"] -= qty_to_move
                                        tracking_data[to_stage]["qty"] += qty_to_move
                                        
                                        new_proses_saat_ini = "Selesai"
                                        for stage in stages_list:
                                            if tracking_data.get(stage, {}).get("qty", 0) > 0:
                                                new_proses_saat_ini = stage
                                                break
                                        
                                        total_progress_score = 0
                                        for stage, data in tracking_data.items():
                                            qty_in_stage = data.get("qty", 0)
                                            progress_per_stage = stage_to_progress.get(stage, 0)
                                            total_progress_score += (qty_in_stage * progress_per_stage)
                                        
                                        if total_order_qty > 0:
                                            new_progress_percent = total_progress_score / total_order_qty
                                        else:
                                            new_progress_percent = 0

                                        if tracking_data["Pengiriman"]["qty"] == total_order_qty:
                                            new_progress_percent = 100
                                            new_proses_saat_ini = "Pengiriman"

                                        try:
                                            history = json.loads(order_data["History"]) if order_data["History"] else []
                                        except:
                                            history = []
                                        
                                        update_details = f"Memindahkan {qty_to_move} pcs dari {from_stage} ke {to_stage}. "
                                        update_details += f"Progress baru: {new_progress_percent:.0f}%, "
                                        update_details += f"Proses utama: {new_proses_saat_ini}"
                                        if notes:
                                            update_details += f", Note: {notes}"
                                        
                                        history.append(add_history_entry(order_id, "Partial Qty Moved", update_details))
                                        
                                        st.session_state["data_produksi"].at[idx, "Tracking"] = json.dumps(tracking_data)
                                        st.session_state["data_produksi"].at[idx, "Proses Saat Ini"] = new_proses_saat_ini
                                        st.session_state["data_produksi"].at[idx, "Progress"] = f"{new_progress_percent:.0f}%"
                                        st.session_state["data_produksi"].at[idx, "History"] = json.dumps(history)

                                        if notes:
                                            current_keterangan = str(order_data["Keterangan"]) if order_data["Keterangan"] else ""
                                            new_keterangan = f"{current_keterangan}\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] {notes}".strip()
                                            st.session_state["data_produksi"].at[idx, "Keterangan"] = new_keterangan
                                        
                                        if save_data(st.session_state["data_produksi"]):
                                            st.success(f"✅ Berhasil memindahkan {qty_to_move} pcs dari {from_stage} ke {to_stage}!")
                                            st.balloons()
                                            st.session_state[confirm_key] = False
                                            st.rerun()
                                        else:
                                            st.error("Gagal menyimpan data!")
                                            st.session_state[confirm_key] = False
                            
                            with col_confirm2:
                                if st.button("❌ BATAL", type="secondary", use_container_width=True, key=f"cancel_move_{order_id}"):
                                    st.session_state[confirm_key] = False
                                    st.rerun()
                        else:
                            if st.button("💾 Pindahkan Qty", type="primary", use_container_width=True, key=f"submit_move_{order_id}"):
                                st.session_state[confirm_key] = True
                                st.rerun()

# ===== MENU: TRACKING PRODUKSI =====
elif st.session_state["menu"] == "Tracking":
    st.header("🔍 TRACKING PRODUKSI PER WORKSTATION")
    
    df_filtered = st.session_state["data_produksi"]
    
    if not df_filtered.empty:
        st.markdown("""
        <div style='background-color: #1E3A8A; padding: 15px; border-radius: 8px; margin-bottom: 25px;'>
            <h3 style='color: white; text-align: center; margin: 0;'>📋 STATUS TRACKING PER TAHAPAN</h3>
        </div>
        """, unsafe_allow_html=True)
        
        track_col1, track_col2 = st.columns(2)
        with track_col1:
            filter_track_buyer = st.multiselect("Filter Buyer", df_filtered["Buyer"].unique().tolist(), key="track_buyer_filter")
        with track_col2:
            search_track_order = st.text_input("🔍 Cari Order ID", key="track_search")
        
        df_filtered_track_filtered = df_filtered.copy()
        if filter_track_buyer:
            df_filtered_track_filtered = df_filtered_track_filtered[df_filtered_track_filtered["Buyer"].isin(filter_track_buyer)]
        if search_track_order:
            df_filtered_track_filtered = df_filtered_track_filtered[df_filtered_track_filtered["Order ID"].str.contains(search_track_order, case=False, na=False)]
        
        st.markdown("---")
        
        sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
        
        total_orders_filtered = len(df_filtered_track_filtered)
        pending_count = 0
        ongoing_count = 0
        done_count = 0
        
        for idx, row in df_filtered_track_filtered.iterrows():
            tracking_status = get_tracking_status_from_progress(row['Progress'])
            if tracking_status == "Pending":
                pending_count += 1
            elif tracking_status == "On Going":
                ongoing_count += 1
            elif tracking_status == "Done":
                done_count += 1
        
        sum_col1.metric("📦 Total Orders", total_orders_filtered)
        sum_col2.metric("⏳ Pending", pending_count)
        sum_col3.metric("🔄 On Going", ongoing_count)
        sum_col4.metric("✅ Done", done_count)
        
        st.markdown("---")
        
        st.subheader("📋 Workstation WIP (Work in Progress)")
        today = datetime.date.today()

        stages = get_tracking_stages()
        
        stage_wip_data = {stage: {"total_qty": 0, "orders": []} for stage in stages}
        
        for idx, row in df_filtered_track_filtered.iterrows():
            try:
                tracking_data = json.loads(row["Tracking"])
                if not tracking_data:
                    raise ValueError("Tracking data is empty")
                    
                for stage in stages:
                    qty_in_stage = tracking_data.get(stage, {}).get("qty", 0)
                    if qty_in_stage > 0:
                        stage_wip_data[stage]["total_qty"] += qty_in_stage
                        stage_wip_data[stage]["orders"].append((row, qty_in_stage))
            except:
                current_stage = row["Proses Saat Ini"]
                if current_stage in stage_wip_data:
                    if get_tracking_status_from_progress(row['Progress']) != "Done":
                        stage_wip_data[current_stage]["total_qty"] += row["Qty"]
                        stage_wip_data[current_stage]["orders"].append((row, row["Qty"]))

        cumulative_qty = 0
        for stage_index, stage in enumerate(stages):
            data = stage_wip_data[stage]
            qty_at_this_stage = data["total_qty"]
            order_count_at_stage = len(data["orders"])

            cumulative_qty += qty_at_this_stage
            
            st.markdown(f"### {stage_index + 1}. {stage}")
            
            metric_col1, metric_col2 = st.columns(2)
            metric_col1.metric(f"Qty di Tahap Ini", f"{qty_at_this_stage:,} pcs")
            metric_col2.metric("Total WIP (Kumulatif)", f"{cumulative_qty:,} pcs")
            
            with st.expander(f"Lihat {order_count_at_stage} order di tahap '{stage}'", expanded=False):
                if order_count_at_stage > 0:
                    sorted_orders = sorted(data["orders"], key=lambda x: x[0]["Due Date"])
                    
                    for order_row, qty_in_stage in sorted_orders:
                        row = order_row
                        st.markdown(f"**{row['Order ID']}** - {row['Produk']}")
                        
                        det_col1, det_col2, det_col3 = st.columns(3)
                        det_col1.write(f"**Buyer:** {row['Buyer']}")
                        det_col2.write(f"**Qty di Tahap Ini:** {qty_in_stage} / {row['Qty']} pcs")
                        
                       # FIX: Ensure due_date is datetime.date for comparison
                        due_date_raw = row['Due Date']
                        if isinstance(due_date_raw, pd.Timestamp):
                            due_date = due_date_raw.date()
                        elif isinstance(due_date_raw, str):
                            due_date = pd.to_datetime(due_date_raw).date()
                        else:
                            due_date = due_date_raw
                        
                        days_until_due = (due_date - today).days
                        if days_until_due < 0:
                            date_color = "#EF4444"; date_icon = "🔴"
                        elif days_until_due <= 7:
                            date_color = "#F59E0B"; date_icon = "🟡"
                        else:
                            date_color = "#10B981"; date_icon = "🟢"
                        det_col3.markdown(f"**Due:** <span style='color: {date_color};'>{date_icon} {str(due_date)}</span>", unsafe_allow_html=True)
                        
                        st.progress(int(row['Progress'].rstrip('%')) / 100)
                        
                        # Get original index from dataframe
                        original_idx = df_filtered_track_filtered[df_filtered_track_filtered['Order ID'] == row['Order ID']].index[0]
                        
                        if st.button("⚙️ Update Progress", key=f"track_edit_{row['Order ID']}_{stage}", use_container_width=True, type="secondary"):
                            st.session_state["edit_order_idx"] = original_idx
                            st.session_state["menu"] = "Progress"
                            st.rerun()
                            
                        st.divider()
                else:
                    st.write(f"Tidak ada Qty di tahap {stage}.")
            
    
    else:
        st.info("📝 Belum ada order untuk di-tracking.")

# ===== MENU: PROCUREMENT =====
elif st.session_state["menu"] == "Procurement":
    st.header("🛒 PROCUREMENT MANAGEMENT")
    st.markdown("### Pembelian Bahan Baku & Aksesoris")
    
    procurement_list = st.session_state["procurement"]
    
    tab1, tab2 = st.tabs(["📋 Daftar Procurement", "➕ Tambah Procurement Baru"])
    with tab1:
        if not procurement_list:
            st.info("📝 Belum ada data procurement. Silakan tambah procurement baru di tab sebelah.")
        else:
            st.markdown("### 📊 Daftar Procurement")
            
            for proc_idx, procurement in enumerate(procurement_list):
                proc_status = procurement.get("status", "Open")
                status_color = {"Open": "#F59E0B", "Ordered": "#3B82F6", "Received": "#10B981", "Closed": "#6B7280"}
                
                with st.expander(
                    f"🛒 Procurement #{proc_idx + 1} - {procurement.get('nama_produk', 'N/A')} | Status: {proc_status}",
                    expanded=False
                ):
                    st.markdown(f"**Nama Produk:** {procurement.get('nama_produk', '-')}")
                    st.markdown(f"**Buyer:** {procurement.get('buyer', '-')}")
                    st.markdown(f"**Tanggal:** {procurement.get('tanggal', '-')}")
                    st.markdown(f"**Notes:** {procurement.get('notes', '-')}")
                    
                    st.markdown("---")
                    st.markdown("### 📦 Item Barang Setengah Jadi & Aksesoris")
                    
                    items = procurement.get("items", [])
                    
                    if items:
                        # Create DataFrame for display
                        df_filtered_items = pd.DataFrame(items)
                        df_filtered_items["Harga Total"] = df_filtered_items["Harga Total"].apply(lambda x: f"Rp {x:,.0f}")
                        df_filtered_items["Harga per Unit"] = df_filtered_items["Harga per Unit"].apply(lambda x: f"Rp {x:,.0f}")
                        
                        st.dataframe(
                            df_filtered_items[["Nama Barang", "Jumlah per Pcs", "Jumlah Total", "Harga per Unit", "Harga Total"]],
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Total calculation
                        total_cost = sum([item["Harga Total"] for item in items])
                        st.markdown(f"### 💰 **Total Biaya Procurement: Rp {total_cost:,.0f}**")
                    else:
                        st.info("Belum ada item dalam procurement ini.")
                    
                    st.markdown("---")
                    
                    # Update Status
                    col_status1, col_status2, col_status3 = st.columns(3)
                    
                    with col_status1:
                        new_status = st.selectbox(
                            "Update Status",
                            ["Open", "Ordered", "Received", "Closed"],
                            index=["Open", "Ordered", "Received", "Closed"].index(proc_status),
                            key=f"status_proc_{proc_idx}"
                        )
                    
                    with col_status2:
                        if st.button("💾 Update Status", key=f"update_status_{proc_idx}", use_container_width=True):
                            procurement_list[proc_idx]["status"] = new_status
                            st.session_state["procurement"] = procurement_list
                            if save_procurement(procurement_list):
                                st.success("✅ Status berhasil diupdate!")
                                st.rerun()
                    
                    with col_status3:
                        if st.button("🗑️ Hapus Procurement", key=f"delete_proc_{proc_idx}", use_container_width=True, type="secondary"):
                            if st.session_state.get(f"confirm_del_proc_{proc_idx}", False):
                                procurement_list.pop(proc_idx)
                                st.session_state["procurement"] = procurement_list
                                if save_procurement(procurement_list):
                                    st.success("✅ Procurement berhasil dihapus!")
                                    del st.session_state[f"confirm_del_proc_{proc_idx}"]
                                    st.rerun()
                            else:
                                st.session_state[f"confirm_del_proc_{proc_idx}"] = True
                                st.warning("⚠️ Klik sekali lagi untuk konfirmasi hapus!")
                                st.rerun()
    with tab2:
        st.markdown("### ➕ Buat Procurement Baru")
        
        if "procurement_items" not in st.session_state:
            st.session_state["procurement_items"] = []
        
        st.markdown("#### 📋 Informasi Procurement")
        col_proc1, col_proc2, col_proc3 = st.columns(3)
        
        with col_proc1:
            df_filtered = st.session_state["data_produksi"]
            buyers = df_filtered["Buyer"].unique().tolist() if not df_filtered.empty else []
            proc_buyer = st.selectbox("Buyer", [""] + buyers if buyers else [""], key="proc_buyer_select")
        
        with col_proc2:
            if proc_buyer:
                buyer_products = get_products_by_buyer(proc_buyer)
                if buyer_products:
                    proc_nama_produk = st.selectbox("Nama Produk", [""] + buyer_products, key="proc_product_select")
                else:
                    st.info("Buyer ini belum punya order")
                    proc_nama_produk = st.text_input("Nama Produk (Manual)", placeholder="Ketik nama produk", key="proc_product_manual")
            else:
                proc_nama_produk = st.text_input("Nama Produk", placeholder="Pilih buyer terlebih dahulu", disabled=True, key="proc_product_disabled")
        
        with col_proc3:
            proc_tanggal = st.date_input("Tanggal Procurement", datetime.date.today())
        
        proc_notes = st.text_area("Catatan Procurement", placeholder="Catatan tambahan...", height=50)
        
        st.markdown("---")
        st.markdown("#### 📦 Tambah Item Barang")
        
        # Properly aligned columns for item input
        with st.container():
            col_item1, col_item2, col_item3, col_item4 = st.columns([1, 1, 1, 1])
            
            with col_item1:
                item_name = st.text_input("Nama Barang", placeholder="Contoh: Kayu Jati", key="proc_item_name")
            
            with col_item2:
                item_qty_per_pcs = st.number_input("Jumlah per Pcs", min_value=0.0, value=None, format="%.2f", step=1.0, key="proc_item_qty_per", placeholder="0.00")
            
            with col_item3:
                item_qty_total = st.number_input("Jumlah Total", min_value=0.0, value=None, format="%.2f", step=1.0, key="proc_item_qty_total", placeholder="0.00")
            
            with col_item4:
                item_price = st.number_input("Harga per Unit (Rp)", min_value=0, value=None, step=1000, key="proc_item_price", placeholder="0")
        
        if st.button("➕ Tambah Item", use_container_width=True, type="primary", key="add_proc_item_btn"):
            if item_name:
                item_total_price = item_price * item_qty_total
                
                new_item = {
                    "Nama Barang": item_name,
                    "Jumlah per Pcs": item_qty_per_pcs,
                    "Jumlah Total": item_qty_total,
                    "Harga per Unit": item_price,
                    "Harga Total": item_total_price
                }
                
                st.session_state["procurement_items"].append(new_item)
                st.success(f"✅ Item '{item_name}' ditambahkan!")
                st.rerun()
            else:
                st.warning("⚠️ Nama barang tidak boleh kosong!")
        
        if st.session_state["procurement_items"]:
            st.markdown("---")
            st.markdown("#### 📋 Daftar Item dalam Procurement Ini")
            
            for idx, item in enumerate(st.session_state["procurement_items"]):
                col_display1, col_display2 = st.columns([4, 1])
                
                with col_display1:
                    st.markdown(f"**{idx + 1}. {item['Nama Barang']}**")
                    st.write(f"Jumlah per Pcs: {item['Jumlah per Pcs']:.2f} | Total: {item['Jumlah Total']:.2f} | Harga: Rp {item['Harga per Unit']:,.0f} | **Total: Rp {item['Harga Total']:,.0f}**")
                
                with col_display2:
                    if st.button("🗑️", key=f"remove_item_{idx}", use_container_width=True):
                        st.session_state["procurement_items"].pop(idx)
                        st.rerun()
            
            # Grand Total
            grand_total = sum([item["Harga Total"] for item in st.session_state["procurement_items"]])
            st.markdown(f"### 💰 **Total Biaya: Rp {grand_total:,.0f}**")
            
            st.markdown("---")
            
            col_submit1, col_submit2 = st.columns(2)
            
            with col_submit1:
                if st.button("🗑️ BATAL & HAPUS SEMUA", use_container_width=True, type="secondary"):
                    st.session_state["procurement_items"] = []
                    st.rerun()
            
            with col_submit2:
                if st.button("📤 SUBMIT PROCUREMENT", use_container_width=True, type="primary"):
                    if proc_nama_produk and proc_buyer and st.session_state["procurement_items"]:
                        new_procurement = {
                            "nama_produk": proc_nama_produk,
                            "buyer": proc_buyer,
                            "tanggal": str(proc_tanggal),
                            "notes": proc_notes,
                            "status": "Open",
                            "items": st.session_state["procurement_items"].copy(),
                            "created_at": str(datetime.datetime.now())
                        }
                        
                        procurement_list.append(new_procurement)
                        st.session_state["procurement"] = procurement_list
                        
                        if save_procurement(procurement_list):
                            st.success(f"✅ Procurement untuk '{proc_nama_produk}' berhasil ditambahkan!")
                            st.balloons()
                            st.session_state["procurement_items"] = []
                            st.rerun()
                    else:
                        st.warning("⚠️ Harap pilih buyer, nama produk, dan tambahkan minimal 1 item!")
        else:
            st.info("📝 Belum ada item yang ditambahkan. Silakan tambah item menggunakan form di atas.")
# ===== MENU: DATABASE =====
elif st.session_state["menu"] == "Database":
    st.header("💾 DATABASE MANAGEMENT")
    
    tab1, tab2 = st.tabs(["👥 Buyers Database", "📦 Products Database"])
    
    with tab1:
        st.subheader("👥 Manage Buyers")
        
        buyers = st.session_state["buyers"]
        
        if "edit_buyer_mode" not in st.session_state:
            st.session_state["edit_buyer_mode"] = False
            st.session_state["edit_buyer_idx"] = None
        
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
                    update_buyer = st.form_submit_button("💾 Update", use_container_width=True, type="primary")
                with col_btn2:
                    delete_buyer = st.form_submit_button("🗑️ Delete", use_container_width=True, type="secondary")
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
                            st.success(f"✅ Buyer '{edit_name}' berhasil diupdate!")
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
        
        st.markdown("### Current Buyers Database")
        if buyers:
            header_cols = st.columns([2, 2.5, 2, 2.5, 0.8])
            header_cols[0].markdown("**Nama Buyer**")
            header_cols[1].markdown("**Alamat**")
            header_cols[2].markdown("**Contact**")
            header_cols[3].markdown("**Profile**")
            header_cols[4].markdown("**Action**")
            
            for idx, buyer in enumerate(buyers):
                row_cols = st.columns([2, 2.5, 2, 2.5, 0.8])
                row_cols[0].write(buyer["name"])
                row_cols[1].write(buyer["address"] if buyer["address"] else "-")
                row_cols[2].write(buyer["contact"] if buyer["contact"] else "-")
                row_cols[3].write(buyer["profile"][:50] + "..." if len(buyer["profile"]) > 50 else (buyer["profile"] if buyer["profile"] else "-"))
                
                with row_cols[4]:
                    if st.button("✏️", key=f"edit_buyer_{idx}", use_container_width=True):
                        st.session_state["edit_buyer_mode"] = True
                        st.session_state["edit_buyer_idx"] = idx
                        st.rerun()
                
                st.markdown("<div style='margin: 5px 0; border-bottom: 1px solid #374151;'></div>", unsafe_allow_html=True)
        else:
            st.info("Belum ada buyer yang terdaftar")
        
        st.markdown("---")
        
        st.markdown("### ➕ Add New Buyer")
        with st.form("add_buyer_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                new_buyer_name = st.text_input("Nama Buyer *", placeholder="PT. ABC Indonesia")
                new_buyer_address = st.text_area("Alamat", placeholder="Jl. Example No. 123", height=100)
            with col2:
                new_buyer_contact = st.text_input("Contact", placeholder="John Doe / +62812345678")
                new_buyer_profile = st.text_area("Profile", placeholder="Informasi tambahan...", height=100)
            
            submit_buyer = st.form_submit_button("➕ Add Buyer", use_container_width=True, type="primary")
            
            if submit_buyer:
                if new_buyer_name:
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
                        st.warning("⚠️ Buyer sudah ada")
                else:
                    st.warning("⚠️ Nama buyer tidak boleh kosong")
    
    with tab2:
        st.subheader("📦 Manage Products")
        
        products = st.session_state["products"]
        
        st.markdown("### Current Products")
        if products:
            product_df_filtered = pd.DataFrame({"Product Name": products})
            st.dataframe(product_df_filtered, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada produk yang terdaftar")
        
        st.markdown("---")
        
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
                    st.warning("⚠️ Produk sudah ada")
                else:
                    st.warning("⚠️ Nama produk tidak boleh kosong")
        
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

# ===== MENU: ANALYTICS =====
elif st.session_state["menu"] == "Analytics":
    st.header("📈 ANALISIS & LAPORAN")
    
    df_filtered = st.session_state["data_produksi"]
    
    if not df_filtered.empty:
        # Ensure Due Date is datetime for comparisons
        df_filtered_analysis = df_filtered.copy()
        df_filtered_analysis['Due Date'] = pd.to_datetime(df_filtered_analysis['Due Date'])
        
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "👥 By Buyer", "📦 By Product"])
        
        with tab1:
            st.subheader("Performance Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            total_qty = df_filtered_analysis["Qty"].sum()
            # Convert today to Timestamp for comparison
            today_ts = pd.Timestamp(datetime.date.today())
            on_time_orders = len(df_filtered_analysis[df_filtered_analysis["Due Date"] >= today_ts])
            completion_rate = (df_filtered_analysis["Progress"].str.rstrip('%').astype('float').mean())
            total_buyers = df_filtered_analysis["Buyer"].nunique()
            
            col1.metric("Total Quantity", f"{total_qty:,} pcs")
            col2.metric("On-Time Orders", on_time_orders)
            col3.metric("Avg Completion", f"{completion_rate:.1f}%")
            col4.metric("Total Buyers", total_buyers)
            
            st.markdown("---")
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                priority_count = df_filtered_analysis["Prioritas"].value_counts()
                fig_priority = px.bar(x=priority_count.index, y=priority_count.values,
                                   title="Orders by Priority")
                st.plotly_chart(fig_priority, use_container_width=True)
            
            with col_chart2:
                stage_count = df_filtered_analysis["Proses Saat Ini"].value_counts()
                fig_stage = px.pie(values=stage_count.values, names=stage_count.index,
                                     title="Orders by Stage")
                st.plotly_chart(fig_stage, use_container_width=True)
        
        with tab2:
            st.subheader("Analysis by Buyer")
            buyer_stats = df_filtered_analysis.groupby("Buyer").agg({
                "Order ID": "count",
                "Qty": "sum",
                "Progress": lambda x: x.str.rstrip('%').astype('float').mean()
            }).rename(columns={"Order ID": "Total Orders", "Qty": "Total Qty", "Progress": "Avg Progress"})
            buyer_stats["Avg Progress"] = buyer_stats["Avg Progress"].round(1).astype(str) + "%"
            
            st.dataframe(buyer_stats, use_container_width=True)
            
            fig_buyer = px.bar(buyer_stats, y="Total Orders", 
                              title="Total Orders per Buyer")
            st.plotly_chart(fig_buyer, use_container_width=True)
        
        with tab3:
            st.subheader("Analysis by Product")
            product_stats = df_filtered_analysis.groupby("Produk").agg({
                "Order ID": "count",
                "Qty": "sum"
            }).rename(columns={"Order ID": "Total Orders", "Qty": "Total Qty"})
            product_stats = product_stats.sort_values("Total Orders", ascending=False).head(10)
            
            st.dataframe(product_stats, use_container_width=True)
            
            fig_product = px.bar(product_stats, y="Total Qty",
                               title="Top 10 Products by Quantity")
            st.plotly_chart(fig_product, use_container_width=True)
        
        st.markdown("---")
        st.subheader("💾 Export Laporan")
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            csv_data = df_filtered_analysis.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"ppic_report_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_exp2:
            json_data = df_filtered_analysis.to_json(orient='records', indent=2, date_format='iso')
            st.download_button(
                label="📋 Download JSON",
                data=json_data,
                file_name=f"ppic_report_{datetime.date.today()}.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.info("📝 Belum ada data untuk dianalisis.")

# ===== MENU: GANTT CHART =====
elif st.session_state["menu"] == "Gantt":
    st.header("📊 GANTT CHART PRODUKSI")
    
    df_filtered = st.session_state["data_produksi"]
    
    if not df_filtered.empty:
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            filter_buyers = st.multiselect("Filter Buyer", df_filtered["Buyer"].unique(), default=df_filtered["Buyer"].unique())
        with col_filter2:
            filter_priority = st.multiselect("Filter Priority", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
        
        df_filtered_filtered = df_filtered[df_filtered["Buyer"].isin(filter_buyers) & df_filtered["Prioritas"].isin(filter_priority)].copy()
        
        if not df_filtered_filtered.empty:
            df_filtered_filtered['Progress_Num'] = df_filtered_filtered['Progress'].str.rstrip('%').astype('float')
            df_filtered_filtered['Order Date'] = pd.to_datetime(df_filtered_filtered['Order Date'])
            df_filtered_filtered['Due Date'] = pd.to_datetime(df_filtered_filtered['Due Date'])
            df_filtered_filtered['Duration'] = (df_filtered_filtered['Due Date'] - df_filtered_filtered['Order Date']).dt.days
            
            gantt_data = []
            
            for idx, row in df_filtered_filtered.iterrows():
                task_name = f"{row['Order ID']} - {row['Produk'][:30]}"
                progress_pct = row['Progress_Num']
                
                gantt_data.append(dict(
                    Task=task_name,
                    Start=row['Order Date'].strftime('%Y-%m-%d'),
                    Finish=row['Due Date'].strftime('%Y-%m-%d'),
                    Resource="Order",
                    Description=f"{row['Buyer']} | Progress: {progress_pct:.0f}%"
                ))
            
            if gantt_data:
                fig = ff.create_gantt(
                    gantt_data,
                    colors=['#3B82F6'],
                    index_col='Resource',
                    show_colorbar=False,
                    showgrid_x=True,
                    showgrid_y=True,
                    title='Production Schedule',
                    bar_width=0.4,
                    group_tasks=True
                )
                
                today_date = datetime.date.today()
                
                fig.add_shape(
                    type="line",
                    x0=today_date,
                    y0=-0.5,
                    x1=today_date,
                    y1=len(df_filtered_filtered) - 0.5,
                    line=dict(color="#EF4444", width=2, dash="dash")
                )
                
                fig.update_layout(
                    height=max(450, len(df_filtered_filtered) * 70),
                    xaxis_title="Timeline",
                    yaxis_title="Orders",
                    hovermode='closest'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                st.subheader("📋 Order Timeline Summary")
                
                summary_df_filtered = df_filtered_filtered[["Order ID", "Buyer", "Produk", "Order Date", "Due Date", 
                                         "Progress", "Prioritas"]].copy()
                summary_df_filtered["Order Date"] = summary_df_filtered["Order Date"].dt.strftime('%Y-%m-%d')
                summary_df_filtered["Due Date"] = summary_df_filtered["Due Date"].dt.strftime('%Y-%m-%d')
                
                st.dataframe(summary_df_filtered, use_container_width=True, hide_index=True)
        else:
            st.warning("Tidak ada data sesuai filter")
    else:
        st.info("📝 Belum ada data untuk membuat Gantt Chart.")
# Add remaining menus (Orders, Tracking, Database, Analytics, Gantt) with same code as original


st.markdown("---")
st.caption(f"© 2025 PPIC-DSS System | Enhanced with Multiple Container Types & Production Categories | v11.0")
