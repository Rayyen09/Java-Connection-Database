import streamlit as st
import pandas as pd
import datetime
import json
import os
import plotly.express as px
import plotly.figure_factory as ff
from streamlit.components.v1 import html
import hashlib

# ===== KONFIGURASI DATABASE =====
DATABASE_PATH = "ppic_data.json"
BUYER_DB_PATH = "buyers.json"
PRODUCT_DB_PATH = "products.json"
SUPPLIER_DB_PATH = "suppliers.json"  # NEW
PROCUREMENT_DB_PATH = "procurement.json"
CONTAINER_DB_PATH = "containers.json"
USERS_DB_PATH = "users.json"
WORKERS_DB_PATH = "workers.json"  # NEW
ATTENDANCE_DB_PATH = "attendance.json"  # NEW
FROZEN_DATES_DB_PATH = "frozen_dates.json"

TOTAL_STORAGE_AREA_M2 = 318.0  # Total storage area in square meters


st.set_page_config(
    page_title="PPIC-DSS System", 
    layout="wide",
    page_icon="🏭",
    initial_sidebar_state="collapsed"
)

# ===== USER AUTHENTICATION SYSTEM =====
def hash_password(password):
    """Hash password menggunakan SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users dari database"""
    if os.path.exists(USERS_DB_PATH):
        try:
            with open(USERS_DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # Default users
    default_users = {
        "owner": {
            "password": hash_password("owner123"),
            "role": "owner",
            "name": "Owner"
        },
        "mandor": {
            "password": hash_password("mandor123"),
            "role": "mandor",
            "name": "Mandor Operasional"
        },
        "procurement": {
            "password": hash_password("procurement123"),
            "role": "procurement",
            "name": "Admin Procurement"
        },
        "admin": {
            "password": hash_password("admin123"),
            "role": "admin",
            "name": "Admin"
        }
    }
    save_users(default_users)
    return default_users

def save_users(users_data):
    """Save users ke database"""
    try:
        with open(USERS_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def authenticate(username, password):
    """Authenticate user"""
    users = load_users()
    if username in users:
        if users[username]["password"] == hash_password(password):
            return True, users[username]["role"], users[username]["name"]
    return False, None, None

def check_permission(required_role):
    """Check if current user has permission"""
    if "user_role" not in st.session_state:
        return False
    
    user_role = st.session_state["user_role"]
    
    # Owner: Hanya Dashboard
    if user_role == "owner":
        return required_role in ["Dashboard","Orders","Tracking","Frozen","Container","Database","Analytics","Gantt"]
    
    # Mandor: Hanya Progress
    elif user_role == "mandor":
        return required_role in ["Dashboard","Progress","Tracking","Absensi"]
    
    # Procurement: Database, Input, Procurement
    elif user_role == "admin":
        return required_role in ["Dashboard","Database","Input","Procurement","Absensi"]
    
    # Admin: Semua menu
    elif user_role == "procurement":
        return True
    
    return False

def get_role_display_name(role):
    """Get display name for role"""
    role_names = {
        "owner": "👔 Owner",
        "mandor": "⚙️ Mandor Operasional",
        "procurement": "🛒 Admin Procurement",
        "admin": "👨‍💼 Administrator"
    }
    return role_names.get(role, role)

# ===== LOGIN PAGE =====
def show_login_page():
    st.markdown("""
    <style>
    /* Clean background */
    .main {
        background-color: #F8F9FA;
    }
    
    /* Simple centered card */
    .login-card {
        max-width: 420px;
        margin: 80px auto;
        padding: 40px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Simple title */
    .login-title {
        color: #1F2937;
        text-align: center;
        font-size: 1.8rem;
        margin-bottom: 8px;
        font-weight: 600;
    }
    
    .login-subtitle {
        color: #6B7280;
        text-align: center;
        font-size: 0.95rem;
        margin-bottom: 35px;
    }
    
    /* Input fields - simple and clean */
    .stTextInput > div > div > input {
        background-color: #F9FAFB !important;
        border: 1.5px solid #E5E7EB !important;
        border-radius: 8px !important;
        padding: 11px 14px !important;
        font-size: 0.95rem !important;
        color: #1F2937 !important;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        background-color: white !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #9CA3AF !important;
    }
    
    /* Labels */
    .stTextInput > label {
        color: #374151 !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        margin-bottom: 6px !important;
    }
    
    /* Login button */
    .stButton button {
        background: #3B82F6 !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 11px !important;
        border-radius: 8px !important;
        border: none !important;
        width: 100% !important;
        margin-top: 8px !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton button:hover {
        background: #2563EB !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        transform: translateY(-1px);
    }
    
    /* Credentials info box */
    .credentials-box {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 16px;
        margin-top: 24px;
        font-size: 0.85rem;
    }
    
    .credentials-box h4 {
        color: #374151;
        font-size: 0.9rem;
        margin: 0 0 10px 0;
        font-weight: 600;
    }
    
    .credentials-box div {
        color: #6B7280;
        line-height: 1.6;
        margin: 4px 0;
    }
    
    .credentials-box strong {
        color: #1F2937;
        font-weight: 600;
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 8px;
        border: none;
        font-size: 0.9rem;
    }
    
    /* Remove extra padding */
    .block-container {
        padding-top: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Simple centered layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Header
        st.markdown('<h1 class="login-title">🏭 PT JAVA CONNECTION</h1>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Sistem Pencatatan dan Perencanaan Terintegrasi</p>', unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form"):
            username = st.text_input(
                "Username", 
                placeholder="Masukkan username",
                key="login_username"
            )
            password = st.text_input(
                "Password", 
                type="password",
                placeholder="Masukkan password",
                key="login_password"
            )
            
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if username and password:
                    success, role, name = authenticate(username, password)
                    
                    if success:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username
                        st.session_state["user_role"] = role
                        st.session_state["user_name"] = name
                        st.session_state["menu"] = "Dashboard"
                        st.success(f"✅ Login berhasil! Selamat datang, {name}")
                        st.rerun()
                    else:
                        st.error("❌ Username atau password salah")
                else:
                    st.warning("⚠️ Harap isi username dan password")
        
        st.markdown('</div>', unsafe_allow_html=True)

def logout():
    """Logout user"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

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
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 1rem !important;
    }
    
    h1, h2, h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    [data-testid="stButton"] {
        margin-top: 0 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stNumberInput, .stTextInput, .stSelectbox, .stDateInput {
        margin-bottom: 0.3rem !important;
    }
    
    div[data-testid="column"] {
        padding: 0 0.5rem !important;
    }
    
    input, select, textarea {
        tab-index: auto !important;
    }
    
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
    
    .recent-orders-container {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #374151;
        border-radius: 5px;
        padding: 10px;
    }
    
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
    
    .knockdown-piece {
        background: #1F2937;
        border: 1px solid #3B82F6;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
    }
    
    .piece-badge {
        background: #3B82F6;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: bold;
    }
    
    .user-info-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
        margin: 5px 0;
    }
    
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
    
    <script>
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
# ===== FUNGSI DATABASE - ENHANCED PRODUCTS =====
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
                    if 'Product CBM' not in df.columns:
                        df['Product CBM'] = 0.0
                    if 'Is Knockdown' not in df.columns:
                        df['Is Knockdown'] = False
                    if 'Knockdown Pieces' not in df.columns:
                        df['Knockdown Pieces'] = df.apply(lambda x: json.dumps([]), axis=1)
                return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
    return pd.DataFrame(columns=[
        "Order ID", "Order Date", "Buyer", "Produk", "Qty", "Due Date", 
        "Prioritas", "Progress", "Proses Saat Ini", "Keterangan",
        "Tracking", "History", "Material", "Finishing", "Description",
        "Product Size P", "Product Size L", "Product Size T", "Product CBM",
        "Packing Size P", "Packing Size L", "Packing Size T",
        "CBM per Pcs", "Total CBM", "Image Path", 
        "Is Knockdown", "Knockdown Pieces"
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
    """Load enhanced product database with full specifications"""
    if os.path.exists(PRODUCT_DB_PATH):
        try:
            with open(PRODUCT_DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert old format to new format if needed
                if data and isinstance(data[0], str):
                    return []  # Return empty for fresh start
                
                # Migration: convert old string format to new numeric format
                migrated_data = []
                for product in data:
                    # Check if already in new format
                    if "product_size_p" in product:
                        migrated_data.append(product)
                    else:
                        # Convert old format
                        migrated_product = {
                            "name": product.get("name", ""),
                            "material": product.get("material", ""),
                            "finishing": product.get("finishing", ""),
                            "description": product.get("description", ""),
                            "is_knockdown": product.get("is_knockdown", False),
                            "knockdown_pieces": product.get("knockdown_pieces", []),
                            "image_path": product.get("image_path", "")
                        }
                        
                        # Parse product size
                        prod_size = product.get("product_size", "")
                        if prod_size:
                            try:
                                sizes = [float(x.strip()) for x in prod_size.replace("cm", "").split("x")]
                                migrated_product["product_size_p"] = sizes[0] if len(sizes) > 0 else 0.0
                                migrated_product["product_size_l"] = sizes[1] if len(sizes) > 1 else 0.0
                                migrated_product["product_size_t"] = sizes[2] if len(sizes) > 2 else 0.0
                            except:
                                migrated_product["product_size_p"] = 0.0
                                migrated_product["product_size_l"] = 0.0
                                migrated_product["product_size_t"] = 0.0
                        else:
                            migrated_product["product_size_p"] = 0.0
                            migrated_product["product_size_l"] = 0.0
                            migrated_product["product_size_t"] = 0.0
                        
                        # Parse packing size
                        pack_size = product.get("packing_size", "")
                        if pack_size:
                            try:
                                sizes = [float(x.strip()) for x in pack_size.replace("cm", "").split("x")]
                                migrated_product["packing_size_p"] = sizes[0] if len(sizes) > 0 else 0.0
                                migrated_product["packing_size_l"] = sizes[1] if len(sizes) > 1 else 0.0
                                migrated_product["packing_size_t"] = sizes[2] if len(sizes) > 2 else 0.0
                            except:
                                migrated_product["packing_size_p"] = 0.0
                                migrated_product["packing_size_l"] = 0.0
                                migrated_product["packing_size_t"] = 0.0
                        else:
                            migrated_product["packing_size_p"] = 0.0
                            migrated_product["packing_size_l"] = 0.0
                            migrated_product["packing_size_t"] = 0.0
                        
                        migrated_data.append(migrated_product)
                
                # Save migrated data
                if migrated_data != data:
                    save_products(migrated_data)
                
                return migrated_data
        except:
            pass
    return []

def save_products(products):
    """Save enhanced product database"""
    try:
        with open(PRODUCT_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def save_product_image(uploaded_file, product_name):
    """Save uploaded product image to database"""
    if uploaded_file is not None:
        images_dir = "product_images"
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        
        # Clean product name for filename
        clean_name = "".join(c if c.isalnum() else "_" for c in product_name.lower())
        file_extension = uploaded_file.name.split('.')[-1]
        filename = f"product_{clean_name}.{file_extension}"
        filepath = os.path.join(images_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return filepath
    return None

def get_product_by_name(product_name):
    """Get product details by name"""
    products = st.session_state["products"]
    for product in products:
        if product.get("name") == product_name:
            return product
    return None

def load_procurement():
    if os.path.exists(PROCUREMENT_DB_PATH):
        try:
            with open(PROCUREMENT_DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
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

# ===== WORKERS DATABASE FUNCTIONS - NEW =====
def load_workers():
    if os.path.exists(WORKERS_DB_PATH):
        try:
            with open(WORKERS_DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_workers(workers):
    try:
        with open(WORKERS_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(workers, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

# ===== ATTENDANCE DATABASE FUNCTIONS - NEW =====
def load_attendance():
    if os.path.exists(ATTENDANCE_DB_PATH):
        try:
            with open(ATTENDANCE_DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_attendance(attendance_data):
    try:
        with open(ATTENDANCE_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(attendance_data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def get_attendance_by_date(date_str):
    attendance = st.session_state.get("attendance", [])
    for record in attendance:
        if record.get("date") == date_str:
            return record
    return None

def get_tracking_stages():
    return [
        "Pre Order", "Order di Supplier", "Warehouse", "Fitting 1",
        "Amplas", "Revisi 1", "Spray", "Fitting 2",
        "Revisi Fitting 2", "Packaging", "Pengiriman"
    ]

def get_storage_stages():
    """Stages where items are physically in storage"""
    return ["Warehouse", "Fitting 1", "Amplas", "Revisi 1", "Spray", "Fitting 2", "Revisi Fitting 2", "Packaging"]

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
            return (p_val * l_val * t_val) / 1000000
        return 0
    except:
        return 0

def calculate_floor_area_m2(p_cm, l_cm):
    """Calculate floor area in m² from P and L in cm"""
    try:
        p_val = float(p_cm) if p_cm else 0
        l_val = float(l_cm) if l_cm else 0
        if p_val > 0 and l_val > 0:
            return (p_val * l_val) / 10000  # cm² to m²
        return 0
    except:
        return 0

def calculate_storage_usage(df):
    """Calculate total storage floor area used (only items in storage stages)"""
    storage_stages = get_storage_stages()
    total_area_used = 0
    
    for idx, row in df.iterrows():
        try:
            tracking_data = json.loads(row["Tracking"])
            prod_p = float(row.get("Product Size P", 0))
            prod_l = float(row.get("Product Size L", 0))
            area_per_unit = calculate_floor_area_m2(prod_p, prod_l)
            
            for stage in storage_stages:
                qty_in_stage = tracking_data.get(stage, {}).get("qty", 0)
                if qty_in_stage > 0:
                    total_area_used += qty_in_stage * area_per_unit
        except:
            pass
    
    return total_area_used

def get_products_by_buyer(buyer_name):
    """Get unique products for a specific buyer from orders"""
    df = st.session_state["data_produksi"]
    if df.empty or not buyer_name:
        return []
    
    buyer_products = df[df["Buyer"] == buyer_name]["Produk"].unique().tolist()
    return sorted(buyer_products)

def calculate_production_metrics(df):
    wip_stages = ["Warehouse", "Fitting 1", "Amplas", "Revisi 1", "Spray", "Fitting 2", "Revisi Fitting 2"]
    
    wip_qty = 0
    wip_cbm = 0
    finished_qty = 0
    finished_cbm = 0
    shipping_qty = 0
    shipping_cbm = 0
    
    for idx, row in df.iterrows():
        try:
            tracking_data = json.loads(row["Tracking"])
            
            if row.get("Is Knockdown", False):
                try:
                    knockdown_pieces = json.loads(row.get("Knockdown Pieces", "[]"))
                    total_cbm_per_unit = sum([piece.get("cbm", 0) for piece in knockdown_pieces])
                except:
                    total_cbm_per_unit = float(row.get("Total CBM", 0)) / max(row.get("Qty", 1), 1)
            else:
                total_cbm_per_unit = float(row.get("CBM per Pcs", 0))
            
            for stage, data in tracking_data.items():
                qty = data.get("qty", 0)
                if stage in wip_stages and qty > 0:
                    wip_qty += qty
                    wip_cbm += qty * total_cbm_per_unit
                elif stage == "Packaging" and qty > 0:
                    finished_qty += qty
                    finished_cbm += qty * total_cbm_per_unit
                elif stage == "Pengiriman" and qty > 0:
                    shipping_qty += qty
                    shipping_cbm += qty * total_cbm_per_unit
        except:
            pass
    
    return wip_qty, wip_cbm, finished_qty, finished_cbm, shipping_qty, shipping_cbm

# ===== OVERTIME CALCULATION FUNCTIONS - NEW =====
def calculate_overtime_hours(check_in_time, check_out_time):
    """Calculate overtime hours from check-out time"""
    try:
        if isinstance(check_out_time, str):
            checkout = datetime.datetime.strptime(check_out_time, "%H:%M").time()
        else:
            checkout = check_out_time
        
        # Regular end time is 16:00
        regular_end = datetime.time(16, 0)
        
        # Convert to datetime for calculation
        checkout_dt = datetime.datetime.combine(datetime.date.today(), checkout)
        regular_end_dt = datetime.datetime.combine(datetime.date.today(), regular_end)
        
        # Calculate overtime
        if checkout_dt > regular_end_dt:
            overtime_delta = checkout_dt - regular_end_dt
            overtime_hours = overtime_delta.total_seconds() / 3600
            return overtime_hours
        return 0.0
    except:
        return 0.0

def calculate_overtime_cost(overtime_hours, hourly_rate=10840):
    """Calculate overtime cost based on labor law"""
    if overtime_hours <= 0:
        return 0
    
    # First hour: 1.5x
    # Next hours: 2.0x
    if overtime_hours <= 1:
        cost = overtime_hours * hourly_rate * 1.5
    else:
        first_hour_cost = 1 * hourly_rate * 1.5
        remaining_hours = overtime_hours - 1
        remaining_cost = remaining_hours * hourly_rate * 2.0
        cost = first_hour_cost + remaining_cost
    
    return cost

def get_working_days_in_month(year, month):
    """Calculate working days (Monday-Saturday) in a month"""
    import calendar
    
    num_days = calendar.monthrange(year, month)[1]
    working_days = 0
    
    for day in range(1, num_days + 1):
        date = datetime.date(year, month, day)
        # 0=Monday, 6=Sunday
        if date.weekday() != 6:  # Exclude Sunday
            working_days += 1
    
    return working_days

def calculate_monthly_overtime_metrics(attendance_list, year, month):
    """Calculate overtime metrics for a specific month"""
    monthly_attendance = [
        att for att in attendance_list
        if att.get("date", "").startswith(f"{year}-{month:02d}")
    ]
    
    if not monthly_attendance:
        return {
            "total_overtime_hours": 0,
            "total_workers": 0,
            "workers_with_overtime": 0,
            "avg_overtime_rate": 0,
            "total_overtime_cost": 0,
            "regular_cost": 0,
            "cost_increase_pct": 0,
            "top_overtime_workers": []
        }
    
    working_days = get_working_days_in_month(year, month)
    regular_hours_per_worker = working_days * 7  # 7 hours per day
    
    worker_overtime = {}  # {worker_id: {hours, cost, rate}}
    total_regular_cost = 0
    total_overtime_cost = 0
    
    for att in monthly_attendance:
        records = att.get("records", {})
        for worker_id, record in records.items():
            if record.get("status") == "Hadir":
                check_in = record.get("check_in", "08:00")
                check_out = record.get("check_out", "16:00")
                
                ot_hours = calculate_overtime_hours(check_in, check_out)
                
                if worker_id not in worker_overtime:
                    worker_overtime[worker_id] = {
                        "name": record.get("name", "Unknown"),
                        "hours": 0,
                        "cost": 0,
                        "rate": 0
                    }
                
                worker_overtime[worker_id]["hours"] += ot_hours
                
                if ot_hours > 0:
                    ot_cost = calculate_overtime_cost(ot_hours)
                    worker_overtime[worker_id]["cost"] += ot_cost
                    total_overtime_cost += ot_cost
                
                # Assume regular daily wage of Rp 79,000 (from Excel)
                total_regular_cost += 79000
    
    # Calculate rates per worker
    workers_with_ot = 0
    for worker_id, data in worker_overtime.items():
        if data["hours"] > 0:
            data["rate"] = (data["hours"] / regular_hours_per_worker) * 100
            workers_with_ot += 1
        else:
            data["rate"] = 0
    
    # Average overtime rate
    if worker_overtime:
        avg_rate = sum([w["rate"] for w in worker_overtime.values()]) / len(worker_overtime)
    else:
        avg_rate = 0
    
    # Cost increase percentage
    if total_regular_cost > 0:
        cost_increase_pct = (total_overtime_cost / total_regular_cost) * 100
    else:
        cost_increase_pct = 0
    
    # Top 3 overtime workers
    top_workers = sorted(
        worker_overtime.items(),
        key=lambda x: x[1]["hours"],
        reverse=True
    )[:3]
    
    return {
        "total_overtime_hours": sum([w["hours"] for w in worker_overtime.values()]),
        "total_workers": len(worker_overtime),
        "workers_with_overtime": workers_with_ot,
        "avg_overtime_rate": avg_rate,
        "total_overtime_cost": total_overtime_cost,
        "regular_cost": total_regular_cost,
        "cost_increase_pct": cost_increase_pct,
        "top_overtime_workers": [
            {
                "name": worker_overtime[wid]["name"],
                "hours": worker_overtime[wid]["hours"],
                "rate": worker_overtime[wid]["rate"],
                "cost": worker_overtime[wid]["cost"]
            }
            for wid, _ in top_workers
        ]
    }

# ===== FUNGSI DATABASE - SUPPLIERS =====
def load_suppliers():
    """Load supplier database"""
    if os.path.exists(SUPPLIER_DB_PATH):
        try:
            with open(SUPPLIER_DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_suppliers(suppliers):
    """Save supplier database"""
    try:
        with open(SUPPLIER_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(suppliers, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def load_frozen_dates():
    """Load frozen dates from database"""
    if os.path.exists(FROZEN_DATES_DB_PATH):
        try:
            with open(FROZEN_DATES_DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_frozen_dates(frozen_dates_data):
    """Save frozen dates to database"""
    try:
        with open(FROZEN_DATES_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(frozen_dates_data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def is_date_frozen(check_date):
    """Check if a date is frozen - returns True/False and reason"""
    frozen_dates = st.session_state.get("frozen_dates", [])
    date_str = str(check_date)
    
    for frozen in frozen_dates:
        if frozen.get("date") == date_str:
            return True, frozen.get("reason", "No reason provided")
    
    return False, ""

def get_frozen_date_range():
    """Get list of all frozen dates"""
    frozen_dates = st.session_state.get("frozen_dates", [])
    return [frozen.get("date") for frozen in frozen_dates]

# ===== INITIALIZATION =====
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    show_login_page()
    st.stop()

if "data_produksi" not in st.session_state:
    st.session_state["data_produksi"] = load_data()
if "buyers" not in st.session_state:
    st.session_state["buyers"] = load_buyers()
if "products" not in st.session_state:
    st.session_state["products"] = load_products()
if "suppliers" not in st.session_state:
    st.session_state["suppliers"] = load_suppliers()
if "procurement" not in st.session_state:
    st.session_state["procurement"] = load_procurement()
if "containers" not in st.session_state:
    st.session_state["containers"] = load_containers()
if "workers" not in st.session_state:
    st.session_state["workers"] = load_workers()
if "attendance" not in st.session_state:
    st.session_state["attendance"] = load_attendance()
if "frozen_dates" not in st.session_state:
    st.session_state["frozen_dates"] = load_frozen_dates()
if "menu" not in st.session_state:
    st.session_state["menu"] = "Dashboard"
if "container_cart" not in st.session_state:
    st.session_state["container_cart"] = []
if "selected_container_type" not in st.session_state:
    st.session_state["selected_container_type"] = "40 HC (High Cube)"
if "knockdown_pieces" not in st.session_state:
    st.session_state["knockdown_pieces"] = []

# ===== SIDEBAR MENU =====
st.sidebar.title("🏭 PT JAVA CONNECTION")

user_name = st.session_state.get("user_name", "User")
user_role = st.session_state.get("user_role", "")
role_display = get_role_display_name(user_role)

st.sidebar.markdown(f"""
<div class="user-info-badge">
    {role_display}<br>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

menu_options = {
    "📊 Dashboard": "Dashboard",
    "📋 Input Pesanan Baru": "Input",
    "📦 Daftar Order": "Orders",
    "🛒 Procurement": "Procurement",
    "⚙️ Update Progress": "Progress",
    "🔍 Tracking Produksi": "Tracking",
    "❄️ Frozen Zone": "Frozen",
    "🚢 Container Loading": "Container",
    "📝 Absensi": "Absensi",  # NEW
    "📈 Analisis & Laporan": "Analytics",
    "📊 Gantt Chart": "Gantt",
    "💾 Database": "Database"
}

for label, value in menu_options.items():
    if check_permission(value):
        if st.sidebar.button(label, use_container_width=True):
            st.session_state["menu"] = value

st.sidebar.markdown("---")

if st.sidebar.button("🚪 Logout", use_container_width=True, type="secondary"):
    logout()

st.sidebar.info(f"📁 Database: Local Storage")

# Back button
if st.session_state["menu"] != "Dashboard":
    if st.button("⬅️ Back to Dashboard", type="secondary"):
        st.session_state["menu"] = "Dashboard"
        st.rerun()
    st.markdown("---")

# Permission check
current_menu = st.session_state.get("menu", "Dashboard")
if not check_permission(current_menu):
    st.error("🚫 Anda tidak memiliki akses ke menu ini!")
    st.info("Silakan pilih menu yang tersedia di sidebar.")
    st.stop()

# ===== MENU: DASHBOARD =====
# ===== MENU: DASHBOARD =====
if st.session_state["menu"] == "Dashboard":
    st.title("📊 Dashboard PT JAVA CONNECTION")
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        df['Tracking Status'] = df.apply(lambda row: get_tracking_status_from_progress(row['Progress']), axis=1)
        
        # ===== TOP METRICS ROW =====
        st.markdown("### 📈 Key Metrics")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

        total_orders = len(df)
        ongoing = len(df[df["Tracking Status"] == "On Going"])
        done = len(df[df["Tracking Status"] == "Done"])
        total_qty = df["Qty"].sum()

        col_m1.metric("📦 Total Orders", total_orders)
        col_m2.metric("🔄 On Going", ongoing)
        col_m3.metric("✅ Done", done)
        col_m4.metric("📊 Total Qty", f"{total_qty:,}")

        st.markdown("---")

        # ===== PRODUCTION OVERVIEW - SIMPLE CARDS =====
        st.markdown("### 📦 Production Overview")

        # Calculate all metrics
        wip_qty, wip_cbm, finished_qty, finished_cbm, shipping_qty, shipping_cbm = calculate_production_metrics(df)
        storage_used_m2 = calculate_storage_usage(df)
        storage_percentage = (storage_used_m2 / TOTAL_STORAGE_AREA_M2) * 100
        storage_available = TOTAL_STORAGE_AREA_M2 - storage_used_m2

        # Calculate floor areas
        wip_floor = 0
        finished_floor = 0
        wip_stages = ["Warehouse", "Fitting 1", "Amplas", "Revisi 1", "Spray", "Fitting 2", "Revisi Fitting 2"]

        for idx, row in df.iterrows():
            try:
                tracking_data = json.loads(row["Tracking"])
                prod_p = float(row.get("Product Size P", 0))
                prod_l = float(row.get("Product Size L", 0))
                area_per_unit = calculate_floor_area_m2(prod_p, prod_l)
                
                for stage in wip_stages:
                    qty_in_stage = tracking_data.get(stage, {}).get("qty", 0)
                    if qty_in_stage > 0:
                        wip_floor += qty_in_stage * area_per_unit
                
                qty_packaging = tracking_data.get("Packaging", {}).get("qty", 0)
                if qty_packaging > 0:
                    finished_floor += qty_packaging * area_per_unit
            except:
                pass

        # Storage status color
        if storage_percentage > 90:
            bar_color = "#EF4444"
            status_text = "CRITICAL"
            status_icon = "⚠️"
        elif storage_percentage > 70:
            bar_color = "#F59E0B"
            status_text = "HIGH"
            status_icon = "⚡"
        else:
            bar_color = "#3B82F6"
            status_text = "NORMAL"
            status_icon = "✅"

        # Simple 3-column layout
        col1, col2, col3 = st.columns(3)

        # Storage Card
        with col1:
            with st.container():
                st.markdown(f"#### 📦 Storage Capacity")
                st.markdown(f"**Status:** {status_icon} {status_text}")
                st.progress(storage_percentage / 100)
                st.metric("Usage", f"{storage_percentage:.1f}%")
                
                subcol1, subcol2, subcol3 = st.columns(3)
                subcol1.metric("Used", f"{storage_used_m2:.1f} m²")
                subcol2.metric("Available", f"{storage_available:.1f} m²")
                subcol3.metric("Total", f"{TOTAL_STORAGE_AREA_M2:.0f} m²")

        # WIP Card
        with col2:
            with st.container():
                st.markdown("#### 🏭 Work in Progress")
                st.metric("Quantity", f"{wip_qty:,} pcs", label_visibility="collapsed")
                st.markdown(f"**Quantity:** {wip_qty:,} pcs")
                st.caption(f"📦 Volume: {wip_cbm:.4f} m³")
                st.caption(f"📐 Floor: {wip_floor:.2f} m²")

        # Finished Card
        with col3:
            with st.container():
                st.markdown("#### ✅ Finished Goods")
                st.metric("Quantity", f"{finished_qty:,} pcs", label_visibility="collapsed")
                st.markdown(f"**Quantity:** {finished_qty:,} pcs")
                st.caption(f"📦 Volume: {finished_cbm:.4f} m³")
                st.caption(f"📐 Floor: {finished_floor:.2f} m²")

        st.markdown("---")

        # ===== OVERTIME ANALYTICS - SIMPLE LAYOUT =====
        st.markdown("### ⏰ Overtime Analytics")

        attendance_list = st.session_state.get("attendance", [])
        today = datetime.date.today()

        col_month, col_info = st.columns([1, 3])
        with col_month:
            months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                     "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            selected_month_idx = st.selectbox(
                "📅 Bulan",
                range(1, 13),
                index=today.month - 1,
                format_func=lambda x: f"{months[x-1]} {today.year}",
                key="dashboard_overtime_month"
            )

        ot_metrics = calculate_monthly_overtime_metrics(attendance_list, today.year, selected_month_idx)

        with col_info:
            workers_count = ot_metrics['total_workers']
            ot_workers = ot_metrics['workers_with_overtime']

        # Simple 5-column metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        HOURLY_RATE = 10840

        with col1:
            st.metric(
                "Total Overtime",
                f"{ot_metrics['total_overtime_hours']:.1f} jam",
                delta=None if ot_metrics['total_overtime_hours'] == 0 else f"⚠️ Active"
            )
            st.caption(f"{months[selected_month_idx-1]}")

        with col2:
            avg_ot = ot_metrics['total_overtime_hours'] / max(ot_metrics['total_workers'], 1)
            st.metric("Avg OT/Worker", f"{avg_ot:.1f} jam")
            st.caption("per pekerja")

        with col3:
            st.metric("Avg OT Rate", f"{ot_metrics['avg_overtime_rate']:.1f}%")
            st.caption("dari jam kerja")

        with col4:
            st.metric("Total Cost", f"Rp {ot_metrics['total_overtime_cost']:,.0f}")
            st.caption(f"@ Rp {HOURLY_RATE:,}/jam")

        with col5:
            st.metric("Cost Increase", f"+{ot_metrics['cost_increase_pct']:.1f}%")
            st.caption("vs regular cost")

        st.markdown("---")

        # ===== RECENT ORDERS =====
        st.markdown("### 🕒 Recent Orders")
        
        col_filter1, col_filter2 = st.columns([2, 1])
        with col_filter1:
            buyers_list = ["-- All Buyers --"] + sorted(df["Buyer"].unique().tolist())
            selected_buyer_filter = st.selectbox("Filter by Buyer", buyers_list, key="recent_buyer_filter")
        with col_filter2:
            search_recent = st.text_input("🔍 Search", key="search_recent_orders", placeholder="Order ID/Product")
        
        if selected_buyer_filter and selected_buyer_filter != "-- All Buyers --":
            recent_df = df[df["Buyer"] == selected_buyer_filter].sort_values("Order Date", ascending=False)
        else:
            recent_df = df.sort_values("Order Date", ascending=False)
        
        if search_recent:
            recent_df = recent_df[
                recent_df["Order ID"].str.contains(search_recent, case=False, na=False) | 
                recent_df["Produk"].str.contains(search_recent, case=False, na=False)
            ]
        
        st.caption(f"📊 Showing {len(recent_df)} orders")
        
        for idx, row in recent_df.head(10).iterrows():
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
        
        st.markdown("---")
        
        # ===== PRODUCTION CALENDAR =====
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
                st.markdown(f"**📌 {len(df_month)} orders di bulan ini**")
            
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
                                ongoing_count = len(orders_on_date[orders_on_date['Tracking Status'] == 'On Going'])
                                
                                # Build tooltip content
                                tooltip_items = []
                                for idx, order in orders_on_date.iterrows():
                                    status_icon = "✅" if order['Tracking Status'] == 'Done' else "🔄"
                                    tooltip_items.append(f"{status_icon} {order['Order ID']} - {order['Buyer']}")
                                
                                tooltip_text = "\\n".join(tooltip_items)
                                
                                if done_count == len(orders_on_date):
                                    bg_color = "#10B981"
                                    status_label = "All Done"
                                elif date_obj < today:
                                    bg_color = "#EF4444"
                                    status_label = "Overdue"
                                elif date_obj == today:
                                    bg_color = "#F59E0B"
                                    status_label = "Due Today"
                                else:
                                    bg_color = "#3B82F6"
                                    status_label = "Upcoming"
                                
                                week_cols[i].markdown(f"""
                                <div style='background-color: {bg_color}; padding: 5px; border-radius: 5px; text-align: center; cursor: pointer;' 
                                     title="{status_label}&#10;{len(orders_on_date)} orders&#10;Done: {done_count} | Ongoing: {ongoing_count}&#10;&#10;{tooltip_text}">
                                    <b style='color: white;'>{day}</b><br>
                                    <span style='color: white; font-size: 10px;'>{len(orders_on_date)}</span>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                if date_obj == today:
                                    week_cols[i].markdown(f"<div style='padding: 5px; text-align: center; border: 2px solid #3B82F6; border-radius: 5px;' title='Today'><b>{day}</b></div>", unsafe_allow_html=True)
                                else:
                                    week_cols[i].markdown(f"<div style='padding: 5px; text-align: center;'>{day}</div>", unsafe_allow_html=True)
                        else:
                            if date_obj == today:
                                week_cols[i].markdown(f"<div style='padding: 5px; text-align: center; border: 2px solid #3B82F6; border-radius: 5px;' title='Today'><b>{day}</b></div>", unsafe_allow_html=True)
                            else:
                                week_cols[i].markdown(f"<div style='padding: 5px; text-align: center;'>{day}</div>", unsafe_allow_html=True)
        
            # Calendar Legend
            st.markdown("---")
            st.markdown("**📖 Calendar Legend:**")
            col_leg1, col_leg2, col_leg3, col_leg4 = st.columns(4)
            col_leg1.markdown("🟢 **All Done** - All orders completed")
            col_leg2.markdown("🔴 **Overdue** - Past due date")
            col_leg3.markdown("🟠 **Due Today** - Due today")
            col_leg4.markdown("🔵 **Upcoming** - Future orders")
            
            # Expandable details for each date with orders
            if not df_month.empty:
                st.markdown("---")
                st.markdown("**📋 Orders Details by Date:**")
                
                dates_with_orders = df_month['Due Date'].dt.date.unique()
                dates_with_orders = sorted(dates_with_orders)
                
                for date_obj in dates_with_orders:
                    orders_on_date = df_month[df_month['Due Date'].dt.date == date_obj]
                    done_count = len(orders_on_date[orders_on_date['Tracking Status'] == 'Done'])
                    ongoing_count = len(orders_on_date) - done_count
                    
                    # Date status icon
                    if done_count == len(orders_on_date):
                        date_icon = "🟢"
                    elif date_obj < today:
                        date_icon = "🔴"
                    elif date_obj == today:
                        date_icon = "🟠"
                    else:
                        date_icon = "🔵"
                    
                    with st.expander(f"{date_icon} **{date_obj.strftime('%d %B %Y')}** - {len(orders_on_date)} orders (✅ {done_count} | 🔄 {ongoing_count})"):
                        for idx, order in orders_on_date.iterrows():
                            status_icon = "✅" if order['Tracking Status'] == 'Done' else "🔄"
                            progress_val = int(order['Progress'].rstrip('%'))
                            
                            col_ord1, col_ord2 = st.columns([3, 1])
                            with col_ord1:
                                st.markdown(f"{status_icon} **{order['Order ID']}** - {order['Buyer']}")
                                st.caption(f"📦 {order['Produk']} | Qty: {order['Qty']} pcs")
                            with col_ord2:
                                st.progress(progress_val / 100)
                                st.caption(f"{order['Progress']}")
                            st.divider()
        
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
        
        # ===== PRODUCTION PROGRESS BY STAGE =====
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
#input
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
    
    col_type1, col_type2 = st.columns([1, 3])
    with col_type1:
        is_knockdown = st.checkbox("🔧 Produk Knockdown", key="is_knockdown_check")
    
    with col_type2:
        if is_knockdown:
            st.info("💡 **Mode Knockdown**: Produk terdiri dari beberapa pieces")
        else:
            st.info("📦 **Mode Normal**: Satu produk = satu packing size")

    # Product selection with auto-fill
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.markdown("**Product Information**")
            products_list = st.session_state["products"]
            
            if "selected_product_cache" not in st.session_state:
                st.session_state["selected_product_cache"] = ""
            if "knockdown_pieces" not in st.session_state:
                st.session_state["knockdown_pieces"] = []
            if "autofill_image_path" not in st.session_state:
                st.session_state["autofill_image_path"] = ""
            
            if products_list:
                product_names = [p.get("name", "") for p in products_list]
                produk_option = st.selectbox(
                    "Pilih Produk", 
                    ["-- Input Manual --", "-- Pilih dari Database --"] + product_names, 
                    key="form_produk_select"
                )
                
                # Auto-fill logic
                if produk_option != st.session_state["selected_product_cache"]:
                    st.session_state["selected_product_cache"] = produk_option
                    
                    if produk_option in ["-- Input Manual --", "-- Pilih dari Database --"]:
                        st.session_state["form_material"] = ""
                        st.session_state["form_finishing"] = ""
                        st.session_state["form_desc"] = ""
                        st.session_state["prod_p"] = 0.0
                        st.session_state["prod_l"] = 0.0
                        st.session_state["prod_t"] = 0.0
                        st.session_state["pack_p"] = 0.0
                        st.session_state["pack_l"] = 0.0
                        st.session_state["pack_t"] = 0.0
                        st.session_state["knockdown_pieces"] = []
                        st.session_state["autofill_image_path"] = ""
                        st.rerun()
                    else:
                        selected_product = get_product_by_name(produk_option)
                        if selected_product:
                            st.session_state["form_material"] = selected_product.get("material", "")
                            st.session_state["form_finishing"] = selected_product.get("finishing", "")
                            st.session_state["form_desc"] = selected_product.get("description", "")
                            st.session_state["prod_p"] = float(selected_product.get("product_size_p", 0))
                            st.session_state["prod_l"] = float(selected_product.get("product_size_l", 0))
                            st.session_state["prod_t"] = float(selected_product.get("product_size_t", 0))
                            st.session_state["pack_p"] = float(selected_product.get("packing_size_p", 0))
                            st.session_state["pack_l"] = float(selected_product.get("packing_size_l", 0))
                            st.session_state["pack_t"] = float(selected_product.get("packing_size_t", 0))
                            st.session_state["autofill_image_path"] = selected_product.get("image_path", "")
                            
                            if selected_product.get("is_knockdown", False):
                                pieces = selected_product.get("knockdown_pieces", [])
                                st.session_state["knockdown_pieces"] = [piece.copy() for piece in pieces]
                            else:
                                st.session_state["knockdown_pieces"] = []
                            
                            st.rerun()
                
                if produk_option == "-- Input Manual --":
                    produk_name = st.text_input("Nama Produk Manual", key="form_produk_manual")
                elif produk_option not in ["-- Input Manual --", "-- Pilih dari Database --"]:
                    produk_name = produk_option
                    st.success(f"✅ Product '{produk_name}' loaded")
                else:
                    produk_name = ""
                    st.info("📝 Pilih produk dari dropdown")
            else:
                st.warning("⚠️ Product database kosong")
                produk_name = st.text_input("Nama Produk", key="form_produk")
            
            qty = st.number_input("Quantity (unit)" if not is_knockdown else "Quantity (set)", 
                                 min_value=1, value=1, key="form_qty")
            
            uploaded_image = st.file_uploader("Upload Gambar Produk", type=['jpg', 'jpeg', 'png'], key="form_image")
            
            # Show database image if available
            db_image_path = st.session_state.get("autofill_image_path", "")
            if db_image_path and os.path.exists(db_image_path) and not uploaded_image:
                st.image(db_image_path, caption="📷 From Database", width=150)
            
        with col2:
            st.markdown("**Specifications**")
            
            material = st.text_input("Material", placeholder="Contoh: Kayu Jati", key="form_material")
            finishing = st.text_input("Finishing", placeholder="Contoh: Natural", key="form_finishing")
            
            st.markdown("**Product Size (cm)**")
            col_ps1, col_ps2, col_ps3 = st.columns(3)
            with col_ps1:
                prod_p = st.number_input("P", min_value=0.0, value=None, format="%.2f", key="prod_p", step=0.01, placeholder="0.00")
            with col_ps2:
                prod_l = st.number_input("L", min_value=0.0, value=None, format="%.2f", key="prod_l", step=0.01, placeholder="0.00")
            with col_ps3:
                prod_t = st.number_input("T", min_value=0.0, value=None, format="%.2f", key="prod_t", step=0.01, placeholder="0.00")
            
            product_cbm = calculate_cbm(prod_p, prod_l, prod_t)
            floor_area = calculate_floor_area_m2(prod_p, prod_l)
            if product_cbm > 0:
                st.success(f"📦 Product CBM: **{product_cbm:.6f} m³**")
                st.caption(f"📐 Floor area: {floor_area:.4f} m² per unit")
            else:
                st.info("📦 Product CBM: 0.000000 m³")
        
        with col3:
            if not is_knockdown:
                st.markdown("**Packing Information**")
                st.markdown("**Packing Size (cm)**")
                col_pack1, col_pack2, col_pack3 = st.columns(3)
                with col_pack1:
                    pack_p = st.number_input("P", min_value=0.0, value=None, format="%.2f", key="pack_p", step=0.01, placeholder="0.00")
                with col_pack2:
                    pack_l = st.number_input("L", min_value=0.0, value=None, format="%.2f", key="pack_l", step=0.01, placeholder="0.00")
                with col_pack3:
                    pack_t = st.number_input("T", min_value=0.0, value=None, format="%.2f", key="pack_t", step=0.01, placeholder="0.00")
                
                cbm_per_pcs = calculate_cbm(pack_p, pack_l, pack_t)
                total_cbm = cbm_per_pcs * qty
                
                if cbm_per_pcs > 0:
                    st.success(f"📦 CBM per Unit: **{cbm_per_pcs:.6f} m³**")
                    st.info(f"📦 Total CBM: **{total_cbm:.6f} m³**")
                else:
                    st.info("📦 CBM per Unit: 0.000000 m³")
            else:
                st.markdown("**🔧 Knockdown Pieces**")
                if st.session_state["knockdown_pieces"]:
                    total_cbm_per_set = sum([p["cbm"] for p in st.session_state["knockdown_pieces"]])
                    total_cbm = total_cbm_per_set * qty
                    st.success(f"📦 CBM per Set: **{total_cbm_per_set:.6f} m³**")
                    st.info(f"📦 Total CBM: **{total_cbm:.6f} m³**")
                    st.caption(f"✓ {len(st.session_state['knockdown_pieces'])} pieces")
                else:
                    st.warning("⚠️ Belum ada piece")
                    total_cbm = 0
                    cbm_per_pcs = 0
                
                pack_p, pack_l, pack_t = 0, 0, 0
                cbm_per_pcs = total_cbm / qty if qty > 0 else 0

    description = st.text_area("Description", placeholder="Deskripsi produk...", height=50, key="form_desc")
    keterangan = st.text_area("Keterangan Tambahan", placeholder="Catatan khusus...", height=50, key="form_notes")
    
    # Knockdown pieces management
    if is_knockdown:
        st.markdown("---")
        st.markdown("### 🔧 Kelola Knockdown Pieces")
        
        with st.expander("➕ Tambah Piece Baru", expanded=True):
            col_kd1, col_kd2, col_kd3, col_kd4 = st.columns([2, 1, 2, 1])
            
            with col_kd1:
                piece_name = st.text_input("Nama Piece", placeholder="Body, Door, Shelf", key="piece_name")
            with col_kd2:
                piece_qty = st.number_input("Qty per Set", min_value=1, value=1, key="piece_qty")
            with col_kd3:
                st.caption("**Packing Size (cm)**")
                col_kd_p1, col_kd_p2, col_kd_p3 = st.columns(3)
                with col_kd_p1:
                    piece_p = st.number_input("P", min_value=0.0, value=0.0, format="%.2f", key="piece_p", step=0.01)
                with col_kd_p2:
                    piece_l = st.number_input("L", min_value=0.0, value=0.0, format="%.2f", key="piece_l", step=0.01)
                with col_kd_p3:
                    piece_t = st.number_input("T", min_value=0.0, value=0.0, format="%.2f", key="piece_t", step=0.01)
            with col_kd4:
                piece_cbm = calculate_cbm(piece_p, piece_l, piece_t) * piece_qty
                st.metric("CBM Piece", f"{piece_cbm:.6f}")
                
                if st.button("➕ Add Piece", use_container_width=True, type="primary", key="add_piece_btn"):
                    if piece_name and piece_cbm > 0:
                        new_piece = {"name": piece_name, "qty_per_set": piece_qty, "p": piece_p, "l": piece_l, "t": piece_t, "cbm": piece_cbm}
                        st.session_state["knockdown_pieces"].append(new_piece)
                        st.success(f"✅ Piece '{piece_name}' ditambahkan!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Nama dan dimensi harus diisi!")
        
        if st.session_state["knockdown_pieces"]:
            st.markdown("#### 📋 Pieces dalam Set")
            for idx, piece in enumerate(st.session_state["knockdown_pieces"]):
                col_p1, col_p2 = st.columns([4, 1])
                with col_p1:
                    st.markdown(f"**{idx+1}. {piece['name']}** (x{piece['qty_per_set']}) - {piece['p']:.2f} × {piece['l']:.2f} × {piece['t']:.2f} cm = {piece['cbm']:.6f} m³")
                with col_p2:
                    if st.button("🗑️", key=f"remove_piece_{idx}"):
                        st.session_state["knockdown_pieces"].pop(idx)
                        st.rerun()
    
    # Add product button
    if st.button("➕ Tambah Produk ke Order", use_container_width=True, type="primary", key="add_product_btn"):
        if produk_name and qty > 0:
            if is_knockdown and not st.session_state["knockdown_pieces"]:
                st.warning("⚠️ Produk knockdown harus memiliki minimal 1 piece!")
            else:
                if is_knockdown:
                    total_cbm_per_set = sum([p["cbm"] for p in st.session_state["knockdown_pieces"]])
                    total_cbm = total_cbm_per_set * qty
                    cbm_per_pcs = total_cbm_per_set
                    knockdown_pieces_data = st.session_state["knockdown_pieces"].copy()
                else:
                    cbm_per_pcs = calculate_cbm(pack_p, pack_l, pack_t)
                    total_cbm = cbm_per_pcs * qty
                    knockdown_pieces_data = []
                
                # Use database image if no new upload
                final_image = uploaded_image
                final_image_path = st.session_state.get("autofill_image_path", "")
                
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
                    "pack_p": pack_p if not is_knockdown else 0,
                    "pack_l": pack_l if not is_knockdown else 0,
                    "pack_t": pack_t if not is_knockdown else 0,
                    "cbm_per_pcs": cbm_per_pcs,
                    "total_cbm": total_cbm,
                    "keterangan": keterangan if keterangan else "-",
                    "image": final_image,
                    "image_path_from_db": final_image_path,
                    "is_knockdown": is_knockdown,
                    "knockdown_pieces": knockdown_pieces_data
                }
                
                st.session_state["input_products"].append(temp_product)
                
                # Reset form
                # st.session_state["form_material"] = ""
                # st.session_state["form_finishing"] = ""
                # st.session_state["form_desc"] = ""
                # st.session_state["prod_p"] = 0.0
                # st.session_state["prod_l"] = 0.0
                # st.session_state["prod_t"] = 0.0
                # st.session_state["pack_p"] = 0.0
                # st.session_state["pack_l"] = 0.0
                # st.session_state["pack_t"] = 0.0
                # st.session_state["selected_product_cache"] = ""
                # st.session_state["knockdown_pieces"] = []
                # st.session_state["autofill_image_path"] = ""
                # st.success(f"✅ Produk '{produk_name}' ditambahkan!")
                # st.rerun()
        else:
            st.warning("⚠️ Harap isi nama produk dan quantity!")
    
    # Display added products
    if st.session_state["input_products"]:
        st.markdown("---")
        st.markdown("### 📋 Daftar Produk dalam Order Ini")
        
        for idx, product in enumerate(st.session_state["input_products"]):
            knockdown_badge = " 🔧" if product.get("is_knockdown", False) else ""
            with st.expander(f"📦 {idx + 1}. {product['nama']}{knockdown_badge} ({product['qty']} unit) - CBM: {product['total_cbm']:.6f} m³"):
                col_d1, col_d2, col_d3 = st.columns([2, 2, 1])
                with col_d1:
                    st.write(f"**Material:** {product['material']}")
                    st.write(f"**Finishing:** {product['finishing']}")
                with col_d2:
                    st.write(f"**CBM per Unit:** {product['cbm_per_pcs']:.6f} m³")
                    st.write(f"**Total CBM:** {product['total_cbm']:.6f} m³")
                with col_d3:
                    if st.button("🗑️ Hapus", key=f"remove_product_{idx}"):
                        st.session_state["input_products"].pop(idx)
                        st.rerun()
        
        total_cbm_all = sum([p['total_cbm'] for p in st.session_state["input_products"]])
        st.info(f"📦 Total CBM semua produk: **{total_cbm_all:.6f} m³**")
        
        col_submit1, col_submit2 = st.columns(2)
        
        with col_submit1:
            if st.button("🗑️ BATAL", use_container_width=True, type="secondary"):
                st.session_state["input_products"] = []
                st.session_state["knockdown_pieces"] = []
                st.rerun()
        
        with col_submit2:
            if st.button("📤 SUBMIT ORDER", use_container_width=True, type="primary"):
                # ===== CHECK FROZEN DATES (ONLY FOR NEW ORDER CREATION) =====
                is_order_date_frozen, order_reason = is_date_frozen(order_date)
                is_due_date_frozen, due_reason = is_date_frozen(due_date)
                
                if is_order_date_frozen:
                    st.markdown("""
                    <div style='background: #FEE2E2; border: 2px solid #EF4444; border-radius: 8px; padding: 20px; margin: 15px 0;'>
                        <h3 style='color: #DC2626; margin: 0 0 10px 0;'>❌ CANNOT CREATE ORDER</h3>
                        <p style='color: #991B1B; margin: 5px 0;'>
                            <strong>Order Date {}</strong> is currently <strong>FROZEN</strong>
                        </p>
                        <p style='color: #991B1B; margin: 5px 0;'>
                            <strong>🔒 Reason:</strong> {}
                        </p>
                        <p style='color: #991B1B; margin: 15px 0 0 0; font-size: 0.9rem;'>
                            💡 Please choose a different Order Date or contact Owner to unfreeze this date
                        </p>
                    </div>
                    """.format(order_date, order_reason), unsafe_allow_html=True)
                elif is_due_date_frozen:
                    st.markdown("""
                    <div style='background: #FEE2E2; border: 2px solid #EF4444; border-radius: 8px; padding: 20px; margin: 15px 0;'>
                        <h3 style='color: #DC2626; margin: 0 0 10px 0;'>❌ CANNOT CREATE ORDER</h3>
                        <p style='color: #991B1B; margin: 5px 0;'>
                            <strong>Due Date {}</strong> is currently <strong>FROZEN</strong>
                        </p>
                        <p style='color: #991B1B; margin: 5px 0;'>
                            <strong>🔒 Reason:</strong> {}
                        </p>
                        <p style='color: #991B1B; margin: 15px 0 0 0; font-size: 0.9rem;'>
                            💡 Please choose a different Due Date or contact Owner to unfreeze this date
                        </p>
                    </div>
                    """.format(due_date, due_reason), unsafe_allow_html=True)
                else:
                    # ===== PROCEED WITH NORMAL ORDER CREATION =====
                    if buyer and st.session_state["input_products"]:
                        existing_ids = st.session_state["data_produksi"]["Order ID"].tolist() if not st.session_state["data_produksi"].empty else []
                        new_id_num = max([int(oid.split("-")[1]) for oid in existing_ids if "-" in oid], default=2400) + 1
                        new_order_id = f"ORD-{new_id_num}"
                        
                        new_orders = []
                        
                        for prod_idx, product in enumerate(st.session_state["input_products"]):
                            # image_path = None
                            # if product.get("image"):
                            #     image_path = save_uploaded_image(product["image"], new_order_id, prod_idx)
                            image_path = ""  # ✅ Default empty string
                            if product.get("image"):
                                saved_path = save_uploaded_image(...)
                                if saved_path:  # ✅ Cek kalau berhasil disimpan
                                    image_path = saved_path
                            elif product.get("image_path_from_db"):
                                image_path = product["image_path_from_db"]  # ✅ Gunakan gambar dari DB                            
                            initial_history = [add_history_entry(f"{new_order_id}-P{prod_idx+1}", "Order Created", 
                            f"Product: {product['nama']}, Priority: {prioritas}, Type: {'Knockdown' if product.get('is_knockdown', False) else 'Normal'}")]
                        
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
                                "History": json.dumps(initial_history),
                                "Is Knockdown": product.get("is_knockdown", False),
                                "Knockdown Pieces": json.dumps(product.get("knockdown_pieces", []))
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
                            st.session_state["knockdown_pieces"] = []
                            st.rerun()
                    else:
                        st.warning("⚠️ Harap pilih buyer dan tambahkan minimal 1 produk!")                    

# ===== MENU: ABSENSI - TAB BASED WITH SEARCH =====
elif st.session_state["menu"] == "Absensi":
    st.header("📝 ABSENSI PEKERJA HARIAN")
    st.caption("Input kehadiran pekerja oleh Mandor")
    
    workers = st.session_state["workers"]
    attendance_list = st.session_state["attendance"]
    
    if not workers:
        st.warning("⚠️ Belum ada data pekerja. Silakan tambah pekerja di menu Database → Pekerja Harian")
        st.stop()
    
    tab1, tab2, tab3 = st.tabs(["📝 Input Absensi", "📋 Riwayat Absensi", "📊 Laporan"])
    
    with tab1:
        st.markdown("### 📅 Input Absensi")
        
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            attendance_date = st.date_input("Tanggal Absensi", datetime.date.today(), key="attendance_date")
        with col_date2:
            st.info(f"📆 {attendance_date.strftime('%A, %d %B %Y')}")
        
        date_str = str(attendance_date)
        existing_attendance = get_attendance_by_date(date_str)
        
        if existing_attendance:
            st.warning(f"⚠️ Absensi tanggal {date_str} sudah ada. Anda bisa mengeditnya.")
            existing_records = existing_attendance.get("records", {})
        else:
            existing_records = {}
        
        st.markdown("---")
        
        # Tab untuk Absen Masuk / Pulang
        tab_masuk, tab_pulang = st.tabs(["🌅 ABSEN MASUK", "🌆 ABSEN PULANG"])
        
        # ===== TAB ABSEN MASUK WITH CONFIRMATION =====
        with tab_masuk:
            st.markdown("### 🌅 Absen Masuk (Check-In)")
            st.info("💡 Default: Semua hadir jam 08:00. Uncheck yang tidak masuk atau ubah jam yang telat.")
            
            # Search bar
            search_masuk = st.text_input("🔍 Cari nama pekerja", key="search_masuk", placeholder="Ketik nama...")
            
            st.markdown("---")
            
            # Filter workers
            filtered_workers = workers
            if search_masuk:
                filtered_workers = [w for w in workers if search_masuk.lower() in w.get("name", "").lower()]
            
            if not filtered_workers:
                st.warning("Tidak ada pekerja yang cocok dengan pencarian")
            else:
                # Attendance data untuk absen masuk
                masuk_data = {}
                
                # Header
                col_h1, col_h2, col_h3, col_h4 = st.columns([0.5, 2, 1.5, 1.5])
                col_h1.markdown("**✓**")
                col_h2.markdown("**Nama**")
                col_h3.markdown("**Jam Masuk**")
                col_h4.markdown("**Status**")
                st.markdown("---")
                
                for idx, worker in enumerate(filtered_workers):
                    worker_id = worker.get("id", str(idx))
                    worker_name = worker.get("name", "Unknown")
                    worker_position = worker.get("position", "-")
                    
                    # Get existing data
                    existing = existing_records.get(worker_id, {})
                    default_hadir = existing.get("status", "Hadir") == "Hadir"
                    
                    col1, col2, col3, col4 = st.columns([0.5, 2, 1.5, 1.5])
                    
                    with col1:
                        is_hadir = st.checkbox("", value=default_hadir, key=f"masuk_check_{worker_id}", label_visibility="collapsed")
                    
                    with col2:
                        st.markdown(f"**{worker_name}**")
                        st.caption(worker_position)
                    
                    with col3:
                        if is_hadir:
                            try:
                                default_time_str = existing.get("check_in", "08:00")
                                default_time = datetime.datetime.strptime(default_time_str, "%H:%M").time()
                            except:
                                default_time = datetime.time(8, 0)
                            
                            check_in_time = st.time_input(
                                "Jam",
                                value=default_time,
                                key=f"masuk_time_{worker_id}",
                                label_visibility="collapsed"
                            )
                            check_in = check_in_time.strftime("%H:%M")
                        else:
                            st.text_input("Jam", value="-", disabled=True, key=f"masuk_time_disabled_{worker_id}", label_visibility="collapsed")
                            check_in = "-"
                    
                    with col4:
                        if is_hadir:
                            status = st.selectbox(
                                "Status",
                                ["Hadir", "Izin", "Sakit"],
                                index=0,
                                key=f"masuk_status_{worker_id}",
                                label_visibility="collapsed"
                            )
                        else:
                            status = "Tidak Hadir"
                            st.text_input("Status", value="Tidak Hadir", disabled=True, key=f"masuk_status_disabled_{worker_id}", label_visibility="collapsed")
                    
                    masuk_data[worker_id] = {
                        "name": worker_name,
                        "position": worker_position,
                        "status": status,
                        "check_in": check_in,
                        "check_out": existing.get("check_out", "-")
                    }
                
                st.markdown("---")
                
                # Summary with styling
                hadir_count = sum(1 for d in masuk_data.values() if d["status"] == "Hadir")
                tidak_hadir = sum(1 for d in masuk_data.values() if d["status"] == "Tidak Hadir")
                izin = sum(1 for d in masuk_data.values() if d["status"] == "Izin")
                sakit = sum(1 for d in masuk_data.values() if d["status"] == "Sakit")
                
                st.markdown("""
                <div style='background: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 20px; margin: 15px 0;'>
                    <h4 style='color: #1F2937; margin: 0 0 15px 0;'>📊 Ringkasan Absensi</h4>
                    <table style='width: 100%; font-size: 0.9rem;'>
                        <tr>
                            <td style='color: #6B7280; padding: 8px 0;'>✅ Hadir:</td>
                            <td style='color: #10B981; font-weight: 600; text-align: right;'>{} pekerja</td>
                        </tr>
                        <tr>
                            <td style='color: #6B7280; padding: 8px 0;'>❌ Tidak Hadir:</td>
                            <td style='color: #EF4444; font-weight: 600; text-align: right;'>{} pekerja</td>
                        </tr>
                        <tr>
                            <td style='color: #6B7280; padding: 8px 0;'>📝 Izin:</td>
                            <td style='color: #3B82F6; font-weight: 600; text-align: right;'>{} pekerja</td>
                        </tr>
                        <tr>
                            <td style='color: #6B7280; padding: 8px 0;'>🏥 Sakit:</td>
                            <td style='color: #F59E0B; font-weight: 600; text-align: right;'>{} pekerja</td>
                        </tr>
                        <tr style='border-top: 2px solid #E5E7EB;'>
                            <td style='color: #1F2937; padding: 12px 0 0 0; font-weight: 600;'>Total:</td>
                            <td style='color: #1F2937; font-weight: 600; text-align: right; padding: 12px 0 0 0;'>{} pekerja</td>
                        </tr>
                    </table>
                </div>
                """.format(hadir_count, tidak_hadir, izin, sakit, len(filtered_workers)), unsafe_allow_html=True)
                
                # CONFIRMATION SYSTEM
                if "confirm_save_masuk" not in st.session_state:
                    st.session_state["confirm_save_masuk"] = False
                
                if st.session_state["confirm_save_masuk"]:
                    # CONFIRMATION DIALOG
                    st.markdown("""
                    <div style='background: #FEF3C7; border: 2px solid #F59E0B; border-radius: 8px; padding: 20px; margin: 20px 0;'>
                        <h3 style='color: #D97706; margin: 0 0 15px 0;'>⚠️ KONFIRMASI SIMPAN DATA</h3>
                        <p style='color: #92400E; margin: 0 0 10px 0; font-size: 0.95rem;'>
                            Anda akan menyimpan data absensi masuk dengan rincian:
                        </p>
                        <table style='width: 100%; font-size: 0.9rem; color: #92400E;'>
                            <tr><td style='padding: 5px 0;'><strong>📅 Tanggal:</strong></td><td style='text-align: right;'>{}</td></tr>
                            <tr><td style='padding: 5px 0;'><strong>👥 Total Pekerja:</strong></td><td style='text-align: right;'>{}</td></tr>
                            <tr><td style='padding: 5px 0;'><strong>✅ Hadir:</strong></td><td style='text-align: right;'>{}</td></tr>
                            <tr><td style='padding: 5px 0;'><strong>❌ Tidak Hadir:</strong></td><td style='text-align: right;'>{}</td></tr>
                        </table>
                        <p style='color: #92400E; margin: 15px 0 0 0; font-weight: 600;'>
                            ⚠️ Pastikan semua data sudah benar sebelum menyimpan!
                        </p>
                    </div>
                    """.format(date_str, len(filtered_workers), hadir_count, tidak_hadir), unsafe_allow_html=True)
                    
                    col_conf1, col_conf2 = st.columns(2)
                    
                    with col_conf1:
                        if st.button("✅ YA, SIMPAN SEKARANG", use_container_width=True, type="primary", key="confirm_yes_masuk"):
                            with st.spinner("💾 Menyimpan data absensi..."):
                                import time
                                time.sleep(0.5)  # Brief pause for UX
                                
                                # Save logic
                                if existing_attendance:
                                    for worker_id, data in masuk_data.items():
                                        if worker_id in existing_records:
                                            existing_records[worker_id].update({
                                                "status": data["status"],
                                                "check_in": data["check_in"]
                                            })
                                        else:
                                            existing_records[worker_id] = data
                                    
                                    for i, att in enumerate(attendance_list):
                                        if att.get("date") == date_str:
                                            attendance_list[i]["records"] = existing_records
                                            attendance_list[i]["hadir"] = hadir_count
                                            attendance_list[i]["tidak_hadir"] = tidak_hadir
                                            attendance_list[i]["izin"] = izin
                                            attendance_list[i]["sakit"] = sakit
                                            break
                                else:
                                    new_attendance = {
                                        "date": date_str,
                                        "created_at": str(datetime.datetime.now()),
                                        "created_by": st.session_state.get("user_name", "Unknown"),
                                        "total_workers": len(workers),
                                        "hadir": hadir_count,
                                        "tidak_hadir": tidak_hadir,
                                        "izin": izin,
                                        "sakit": sakit,
                                        "overtime_hours": 0,
                                        "records": masuk_data
                                    }
                                    attendance_list.append(new_attendance)
                                
                                st.session_state["attendance"] = attendance_list
                                
                                if save_attendance(attendance_list):
                                    # SUCCESS NOTIFICATION
                                    st.markdown("""
                                    <div style='background: #DCFCE7; border: 2px solid #22C55E; border-radius: 8px; padding: 25px; margin: 20px 0;'>
                                        <h2 style='color: #16A34A; margin: 0 0 15px 0;'>✅ BERHASIL DISIMPAN!</h2>
                                        <p style='color: #15803D; margin: 0 0 15px 0; font-size: 1rem;'>
                                            Data absensi masuk telah tersimpan dengan sukses.
                                        </p>
                                        <table style='width: 100%; font-size: 0.95rem; color: #15803D;'>
                                            <tr style='border-bottom: 1px solid #86EFAC;'>
                                                <td style='padding: 10px 0;'><strong>📅 Tanggal:</strong></td>
                                                <td style='text-align: right; padding: 10px 0;'>{}</td>
                                            </tr>
                                            <tr style='border-bottom: 1px solid #86EFAC;'>
                                                <td style='padding: 10px 0;'><strong>👥 Total Pekerja:</strong></td>
                                                <td style='text-align: right; padding: 10px 0;'>{} pekerja</td>
                                            </tr>
                                            <tr style='border-bottom: 1px solid #86EFAC;'>
                                                <td style='padding: 10px 0;'><strong>✅ Hadir:</strong></td>
                                                <td style='text-align: right; padding: 10px 0;'>{} pekerja</td>
                                            </tr>
                                            <tr style='border-bottom: 1px solid #86EFAC;'>
                                                <td style='padding: 10px 0;'><strong>❌ Tidak Hadir:</strong></td>
                                                <td style='text-align: right; padding: 10px 0;'>{} pekerja</td>
                                            </tr>
                                            <tr>
                                                <td style='padding: 10px 0 0 0;'><strong>🕐 Disimpan pada:</strong></td>
                                                <td style='text-align: right; padding: 10px 0 0 0;'>{}</td>
                                            </tr>
                                        </table>
                                    </div>
                                    """.format(
                                        date_str,
                                        len(filtered_workers),
                                        hadir_count,
                                        tidak_hadir,
                                        datetime.datetime.now().strftime("%H:%M:%S")
                                    ), unsafe_allow_html=True)
                                    
                                    st.balloons()
                                    st.session_state["confirm_save_masuk"] = False
                                    
                                    # Auto refresh after 2 seconds
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error("❌ Gagal menyimpan data! Silakan coba lagi.")
                                    st.session_state["confirm_save_masuk"] = False
                    
                    with col_conf2:
                        if st.button("❌ BATAL", use_container_width=True, type="secondary", key="confirm_no_masuk"):
                            st.session_state["confirm_save_masuk"] = False
                            st.info("Dibatalkan. Data tidak disimpan.")
                            st.rerun()
                else:
                    # INITIAL SAVE BUTTON
                    if st.button("💾 SIMPAN ABSEN MASUK", use_container_width=True, type="primary", key="save_masuk"):
                        st.session_state["confirm_save_masuk"] = True
                        st.rerun()
        
        # ===== TAB ABSEN PULANG WITH CONFIRMATION =====
        with tab_pulang:
            st.markdown("### 🌆 Absen Pulang (Check-Out)")
            
            if not existing_attendance:
                st.error("❌ Belum ada data absen masuk untuk tanggal ini!")
                st.info("💡 Silakan input absen masuk terlebih dahulu di tab 🌅 ABSEN MASUK")
                st.stop()
            
            st.info("💡 Default: Semua pulang jam 16:00. Ubah jam untuk yang overtime.")
            
            # Search bar
            search_pulang = st.text_input("🔍 Cari nama pekerja", key="search_pulang", placeholder="Ketik nama...")
            
            st.markdown("---")
            
            # Filter workers yang hadir
            workers_hadir = [w for w in workers if existing_records.get(w.get("id", ""), {}).get("status") == "Hadir"]
            
            if search_pulang:
                workers_hadir = [w for w in workers_hadir if search_pulang.lower() in w.get("name", "").lower()]
            
            if not workers_hadir:
                st.warning("Tidak ada pekerja yang hadir atau cocok dengan pencarian")
            else:
                # Attendance data untuk absen pulang
                pulang_data = {}
                
                # Header
                col_h1, col_h2, col_h3, col_h4 = st.columns([2, 1.5, 1.5, 2])
                col_h1.markdown("**Nama**")
                col_h2.markdown("**Jam Masuk**")
                col_h3.markdown("**Jam Pulang**")
                col_h4.markdown("**Overtime**")
                st.markdown("---")
                
                for idx, worker in enumerate(workers_hadir):
                    worker_id = worker.get("id", str(idx))
                    worker_name = worker.get("name", "Unknown")
                    worker_position = worker.get("position", "-")
                    
                    existing = existing_records.get(worker_id, {})
                    check_in = existing.get("check_in", "08:00")
                    
                    col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 2])
                    
                    with col1:
                        st.markdown(f"**{worker_name}**")
                        st.caption(worker_position)
                    
                    with col2:
                        st.caption(f"🌅 {check_in}")
                    
                    with col3:
                        try:
                            default_out_str = existing.get("check_out", "16:00")
                            if default_out_str == "-":
                                default_out = datetime.time(16, 0)
                            else:
                                default_out = datetime.datetime.strptime(default_out_str, "%H:%M").time()
                        except:
                            default_out = datetime.time(16, 0)
                        
                        check_out_time = st.time_input(
                            "Pulang",
                            value=default_out,
                            key=f"pulang_time_{worker_id}",
                            label_visibility="collapsed"
                        )
                        check_out = check_out_time.strftime("%H:%M")
                    
                    with col4:
                        # Calculate overtime
                        ot_hours = calculate_overtime_hours(check_in, check_out)
                        if ot_hours > 0:
                            ot_cost = calculate_overtime_cost(ot_hours)
                            st.warning(f"⏰ {ot_hours:.1f}h | 💰 Rp {ot_cost:,.0f}")
                        else:
                            st.success("✅ Normal")
                    
                    pulang_data[worker_id] = {
                        "check_out": check_out
                    }
                
                st.markdown("---")
                
                # Calculate summary
                total_ot = sum(calculate_overtime_hours(existing_records.get(wid, {}).get("check_in", "08:00"), pulang_data[wid]["check_out"]) for wid in pulang_data.keys())
                ot_workers = sum(1 for wid in pulang_data.keys() if calculate_overtime_hours(existing_records.get(wid, {}).get("check_in", "08:00"), pulang_data[wid]["check_out"]) > 0)
                total_ot_cost = sum(calculate_overtime_cost(calculate_overtime_hours(existing_records.get(wid, {}).get("check_in", "08:00"), pulang_data[wid]["check_out"])) for wid in pulang_data.keys())
                
                # Summary box
                st.markdown("""
                <div style='background: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 20px; margin: 15px 0;'>
                    <h4 style='color: #1F2937; margin: 0 0 15px 0;'>⏰ Ringkasan Overtime</h4>
                    <table style='width: 100%; font-size: 0.9rem;'>
                        <tr>
                            <td style='color: #6B7280; padding: 8px 0;'>👷 Pekerja Hadir:</td>
                            <td style='color: #1F2937; font-weight: 600; text-align: right;'>{} pekerja</td>
                        </tr>
                        <tr>
                            <td style='color: #6B7280; padding: 8px 0;'>👷 Pekerja Overtime:</td>
                            <td style='color: #F59E0B; font-weight: 600; text-align: right;'>{} pekerja</td>
                        </tr>
                        <tr>
                            <td style='color: #6B7280; padding: 8px 0;'>⏰ Total Jam Overtime:</td>
                            <td style='color: #F59E0B; font-weight: 600; text-align: right;'>{:.1f} jam</td>
                        </tr>
                        <tr style='border-top: 2px solid #E5E7EB;'>
                            <td style='color: #1F2937; padding: 12px 0 0 0; font-weight: 600;'>💰 Total Biaya Overtime:</td>
                            <td style='color: #EF4444; font-weight: 600; text-align: right; padding: 12px 0 0 0;'>Rp {:,.0f}</td>
                        </tr>
                    </table>
                </div>
                """.format(len(workers_hadir), ot_workers, total_ot, total_ot_cost), unsafe_allow_html=True)
                
                # CONFIRMATION SYSTEM
                if "confirm_save_pulang" not in st.session_state:
                    st.session_state["confirm_save_pulang"] = False
                
                if st.session_state["confirm_save_pulang"]:
                    # CONFIRMATION DIALOG
                    st.markdown("""
                    <div style='background: #FEF3C7; border: 2px solid #F59E0B; border-radius: 8px; padding: 20px; margin: 20px 0;'>
                        <h3 style='color: #D97706; margin: 0 0 15px 0;'>⚠️ KONFIRMASI SIMPAN DATA</h3>
                        <p style='color: #92400E; margin: 0 0 10px 0; font-size: 0.95rem;'>
                            Anda akan menyimpan data absensi pulang dengan rincian:
                        </p>
                        <table style='width: 100%; font-size: 0.9rem; color: #92400E;'>
                            <tr><td style='padding: 5px 0;'><strong>📅 Tanggal:</strong></td><td style='text-align: right;'>{}</td></tr>
                            <tr><td style='padding: 5px 0;'><strong>👷 Pekerja Hadir:</strong></td><td style='text-align: right;'>{}</td></tr>
                            <tr><td style='padding: 5px 0;'><strong>⏰ Total Overtime:</strong></td><td style='text-align: right;'>{:.1f} jam</td></tr>
                            <tr><td style='padding: 5px 0;'><strong>👷 Pekerja Overtime:</strong></td><td style='text-align: right;'>{}</td></tr>
                            <tr><td style='padding: 5px 0;'><strong>💰 Biaya Overtime:</strong></td><td style='text-align: right;'>Rp {:,.0f}</td></tr>
                        </table>
                        <p style='color: #92400E; margin: 15px 0 0 0; font-weight: 600;'>
                            ⚠️ Pastikan semua jam pulang sudah benar!
                        </p>
                    </div>
                    """.format(date_str, len(workers_hadir), total_ot, ot_workers, total_ot_cost), unsafe_allow_html=True)
                    
                    col_conf1, col_conf2 = st.columns(2)
                    
                    with col_conf1:
                        if st.button("✅ YA, SIMPAN SEKARANG", use_container_width=True, type="primary", key="confirm_yes_pulang"):
                            with st.spinner("💾 Menyimpan data absensi pulang..."):
                                import time
                                time.sleep(0.5)
                                
                                # Update existing records
                                for worker_id, data in pulang_data.items():
                                    if worker_id in existing_records:
                                        existing_records[worker_id]["check_out"] = data["check_out"]
                                
                                # Recalculate overtime
                                total_overtime_hours = 0
                                for worker_id, record in existing_records.items():
                                    if record.get("status") == "Hadir":
                                        ot = calculate_overtime_hours(record.get("check_in", "08:00"), record.get("check_out", "16:00"))
                                        total_overtime_hours += ot
                                
                                # Update attendance record
                                for i, att in enumerate(attendance_list):
                                    if att.get("date") == date_str:
                                        attendance_list[i]["records"] = existing_records
                                        attendance_list[i]["overtime_hours"] = total_overtime_hours
                                        break
                                
                                st.session_state["attendance"] = attendance_list
                                
                                if save_attendance(attendance_list):
                                    # SUCCESS NOTIFICATION
                                    st.markdown("""
                                    <div style='background: #DCFCE7; border: 2px solid #22C55E; border-radius: 8px; padding: 25px; margin: 20px 0;'>
                                        <h2 style='color: #16A34A; margin: 0 0 15px 0;'>✅ BERHASIL DISIMPAN!</h2>
                                        <p style='color: #15803D; margin: 0 0 15px 0; font-size: 1rem;'>
                                            Data absensi pulang telah tersimpan dengan sukses.
                                        </p>
                                        <table style='width: 100%; font-size: 0.95rem; color: #15803D;'>
                                            <tr style='border-bottom: 1px solid #86EFAC;'>
                                                <td style='padding: 10px 0;'><strong>📅 Tanggal:</strong></td>
                                                <td style='text-align: right; padding: 10px 0;'>{}</td>
                                            </tr>
                                            <tr style='border-bottom: 1px solid #86EFAC;'>
                                                <td style='padding: 10px 0;'><strong>👷 Pekerja Hadir:</strong></td>
                                                <td style='text-align: right; padding: 10px 0;'>{} pekerja</td>
                                            </tr>
                                            <tr style='border-bottom: 1px solid #86EFAC;'>
                                                <td style='padding: 10px 0;'><strong>⏰ Total Overtime:</strong></td>
                                                <td style='text-align: right; padding: 10px 0;'>{:.1f} jam</td>
                                            </tr>
                                            <tr style='border-bottom: 1px solid #86EFAC;'>
                                                <td style='padding: 10px 0;'><strong>👷 Pekerja Overtime:</strong></td>
                                                <td style='text-align: right; padding: 10px 0;'>{} dari {} pekerja</td>
                                            </tr>
                                            <tr style='border-bottom: 1px solid #86EFAC;'>
                                                <td style='padding: 10px 0;'><strong>💰 Total Biaya:</strong></td>
                                                <td style='text-align: right; padding: 10px 0;'>Rp {:,.0f}</td>
                                            </tr>
                                            <tr>
                                                <td style='padding: 10px 0 0 0;'><strong>🕐 Disimpan pada:</strong></td>
                                                <td style='text-align: right; padding: 10px 0 0 0;'>{}</td>
                                            </tr>
                                        </table>
                                    </div>
                                    """.format(
                                        date_str,
                                        len(workers_hadir),
                                        total_overtime_hours,
                                        ot_workers,
                                        len(workers_hadir),
                                        total_ot_cost,
                                        datetime.datetime.now().strftime("%H:%M:%S")
                                    ), unsafe_allow_html=True)
                                    
                                    st.balloons()
                                    st.session_state["confirm_save_pulang"] = False
                                    
                                    # Auto refresh
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error("❌ Gagal menyimpan data! Silakan coba lagi.")
                                    st.session_state["confirm_save_pulang"] = False
                    
                    with col_conf2:
                        if st.button("❌ BATAL", use_container_width=True, type="secondary", key="confirm_no_pulang"):
                            st.session_state["confirm_save_pulang"] = False
                            st.info("Dibatalkan. Data tidak disimpan.")
                            st.rerun()
                else:
                    # INITIAL SAVE BUTTON
                    if st.button("💾 SIMPAN ABSEN PULANG", use_container_width=True, type="primary", key="save_pulang"):
                        st.session_state["confirm_save_pulang"] = True
                        st.rerun()
    
    # ===== TAB RIWAYAT (Keep existing code) =====
    with tab2:
        st.markdown("### 📋 Riwayat Absensi")
        
        if attendance_list:
            sorted_attendance = sorted(attendance_list, key=lambda x: x.get("date", ""), reverse=True)
            
            for att in sorted_attendance[:30]:
                date_display = att.get("date", "Unknown")
                hadir = att.get("hadir", 0)
                total = att.get("total_workers", 0)
                pct = (hadir / total * 100) if total > 0 else 0
                ot_hours = att.get("overtime_hours", 0)
                
                with st.expander(f"📅 {date_display} | Hadir: {hadir}/{total} ({pct:.0f}%) | ⏰ OT: {ot_hours:.1f}h"):
                    col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
                    col_sum1.metric("✅ Hadir", att.get("hadir", 0))
                    col_sum2.metric("❌ Tidak Hadir", att.get("tidak_hadir", 0))
                    col_sum3.metric("📝 Izin", att.get("izin", 0))
                    col_sum4.metric("🏥 Sakit", att.get("sakit", 0))
                    
                    if ot_hours > 0:
                        st.info(f"⏰ Total Overtime: {ot_hours:.1f} jam")
                    
                    st.markdown("---")
                    st.markdown("**Detail:**")
                    
                    records = att.get("records", {})
                    for worker_id, record in records.items():
                        status = record.get("status", "Unknown")
                        
                        if status == "Hadir":
                            badge_color = "#10B981"
                            icon = "✅"
                        elif status == "Tidak Hadir":
                            badge_color = "#EF4444"
                            icon = "❌"
                        elif status == "Izin":
                            badge_color = "#3B82F6"
                            icon = "📝"
                        else:
                            badge_color = "#F59E0B"
                            icon = "🏥"
                        
                        ot_text = ""
                        if status == "Hadir":
                            ot = calculate_overtime_hours(record.get("check_in", "08:00"), record.get("check_out", "16:00"))
                            if ot > 0:
                                ot_text = f" ⏰ {ot:.1f}h"
                        
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #374151;">
                            <span>{icon} <strong>{record.get('name', 'Unknown')}</strong></span>
                            <span>{record.get('check_in', '-')} → {record.get('check_out', '-')}{ot_text}</span>
                            <span style="background: {badge_color}; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.85em;">{status}</span>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("📝 Belum ada data absensi")
    
    # ===== TAB LAPORAN (Keep existing code) =====
    with tab3:
        st.markdown("### 📊 Laporan Kehadiran")
        
        if attendance_list:
            col_rep1, col_rep2 = st.columns(2)
            with col_rep1:
                start_date = st.date_input("Dari Tanggal", datetime.date.today() - datetime.timedelta(days=30), key="report_start")
            with col_rep2:
                end_date = st.date_input("Sampai Tanggal", datetime.date.today(), key="report_end")
            
            filtered = [a for a in attendance_list if start_date <= datetime.datetime.strptime(a.get("date", "2000-01-01"), "%Y-%m-%d").date() <= end_date]
            
            if filtered:
                total_days = len(filtered)
                avg_hadir = sum(a.get("hadir", 0) for a in filtered) / total_days
                avg_pct = (avg_hadir / len(workers) * 100) if workers else 0
                total_overtime_hours = sum(a.get("overtime_hours", 0) for a in filtered)
                
                col_rsum1, col_rsum2, col_rsum3, col_rsum4 = st.columns(4)
                col_rsum1.metric("📅 Total Hari", total_days)
                col_rsum2.metric("📊 Rata-rata Hadir", f"{avg_hadir:.1f}")
                col_rsum3.metric("📈 Rata-rata %", f"{avg_pct:.1f}%")
                col_rsum4.metric("⏰ Total Overtime", f"{total_overtime_hours:.1f}h")
                
                st.markdown("---")
                st.markdown("#### 👷 Statistik Per Pekerja")
                
                worker_stats = {}
                for worker in workers:
                    worker_id = worker.get("id", str(workers.index(worker)))
                    worker_stats[worker_id] = {
                        "name": worker.get("name", "Unknown"),
                        "hadir": 0,
                        "tidak_hadir": 0,
                        "izin": 0,
                        "sakit": 0,
                        "overtime_hours": 0
                    }
                
                for att in filtered:
                    records = att.get("records", {})
                    for worker_id, record in records.items():
                        if worker_id in worker_stats:
                            status = record.get("status", "")
                            if status == "Hadir":
                                worker_stats[worker_id]["hadir"] += 1
                                ot = calculate_overtime_hours(record.get("check_in", "08:00"), record.get("check_out", "16:00"))
                                worker_stats[worker_id]["overtime_hours"] += ot
                            elif status == "Tidak Hadir":
                                worker_stats[worker_id]["tidak_hadir"] += 1
                            elif status == "Izin":
                                worker_stats[worker_id]["izin"] += 1
                            elif status == "Sakit":
                                worker_stats[worker_id]["sakit"] += 1
                
                stats_data = []
                for worker_id, stats in worker_stats.items():
                    pct = (stats["hadir"] / total_days * 100) if total_days > 0 else 0
                    stats_data.append({
                        "Nama": stats["name"],
                        "Hadir": stats["hadir"],
                        "Tidak Hadir": stats["tidak_hadir"],
                        "Izin": stats["izin"],
                        "Sakit": stats["sakit"],
                        "Overtime (jam)": f"{stats['overtime_hours']:.1f}",
                        "% Kehadiran": f"{pct:.1f}%"
                    })
                
                stats_df = pd.DataFrame(stats_data)
                st.dataframe(stats_df, use_container_width=True, hide_index=True)
                
                csv_data = stats_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Laporan (CSV)",
                    data=csv_data,
                    file_name=f"laporan_absensi_{start_date}_{end_date}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("Tidak ada data dalam rentang tanggal tersebut")
        else:
            st.info("📝 Belum ada data absensi")

# ===== MENU: DATABASE - WITH WORKERS TAB =====
elif st.session_state["menu"] == "Database":
    st.header("💾 DATABASE MANAGEMENT")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Buyers", "📦 Products", "🏭 Suppliers", "👷 Pekerja Harian"])
    
    # ===== TAB: BUYERS =====
    with tab1:
        st.subheader("👥 Manage Buyers")
        buyers = st.session_state["buyers"]
        
        if buyers:
            for idx, buyer in enumerate(buyers):
                with st.expander(f"👤 {buyer['name']}"):
                    st.write(f"**Alamat:** {buyer.get('address', '-')}")
                    st.write(f"**Contact:** {buyer.get('contact', '-')}")
                    if st.button("🗑️ Hapus", key=f"del_buyer_{idx}"):
                        buyers.pop(idx)
                        st.session_state["buyers"] = buyers
                        save_buyers(buyers)
                        st.rerun()
        
        st.markdown("---")
        st.markdown("### ➕ Add New Buyer")
        with st.form("add_buyer_form", clear_on_submit=True):
            new_name = st.text_input("Nama Buyer *")
            new_address = st.text_area("Alamat", height=80)
            new_contact = st.text_input("Contact")
            
            if st.form_submit_button("➕ Add Buyer", use_container_width=True, type="primary"):
                if new_name:
                    buyers.append({"name": new_name, "address": new_address, "contact": new_contact, "profile": ""})
                    st.session_state["buyers"] = buyers
                    save_buyers(buyers)
                    st.success(f"✅ Buyer '{new_name}' ditambahkan!")
                    st.rerun()
    
    # ===== TAB: PRODUCTS =====
    with tab2:
        st.subheader("📦 Manage Products")
        products = st.session_state["products"]
        
        if products:
            st.info(f"📦 {len(products)} products in database")
            for idx, product in enumerate(products):
                with st.expander(f"📦 {product.get('name', 'N/A')}"):
                    col_p1, col_p2, col_p3 = st.columns([2, 2, 1])
                    with col_p1:
                        st.write(f"**Material:** {product.get('material', '-')}")
                        st.write(f"**Finishing:** {product.get('finishing', '-')}")
                        st.write(f"**Product Size:** {product.get('product_size_p', 0)} x {product.get('product_size_l', 0)} x {product.get('product_size_t', 0)} cm")
                    with col_p2:
                        st.write(f"**Packing Size:** {product.get('packing_size_p', 0)} x {product.get('packing_size_l', 0)} x {product.get('packing_size_t', 0)} cm")
                    with col_p3:
                        image_path = product.get("image_path", "")
                        if image_path and os.path.exists(image_path):
                            st.image(image_path, width=100)
                        if st.button("🗑️ Delete", key=f"del_prod_{idx}"):
                            products.pop(idx)
                            st.session_state["products"] = products
                            save_products(products)
                            st.rerun()
        
        st.markdown("---")
        st.markdown("### ➕ Add New Product")
        
        with st.form("add_product_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                new_prod_name = st.text_input("Nama Produk *")
                new_prod_material = st.text_input("Material")
                new_prod_finishing = st.text_input("Finishing")
            with col2:
                st.markdown("**Product Size (cm)**")
                c1, c2, c3 = st.columns(3)
                np_p = c1.number_input("P", min_value=0.0,value=None, step=0.1, key="np_p", placeholder="0.00")
                np_l = c2.number_input("L", min_value=0.0,value=None, step=0.1, key="np_l", placeholder="0.00")
                np_t = c3.number_input("T", min_value=0.0,value=None, step=0.1, key="np_t", placeholder="0.00")
                
                st.markdown("**Packing Size (cm)**")
                c4, c5, c6 = st.columns(3)
                npack_p = c4.number_input("P", min_value=0.0,value=None, step=0.1, key="npack_p", placeholder="0.00")
                npack_l = c5.number_input("L", min_value=0.0,value=None, step=0.1, key="npack_l", placeholder="0.00")
                npack_t = c6.number_input("T", min_value=0.0,value=None, step=0.1, key="npack_t", placeholder="0.00")
            
            new_prod_desc = st.text_area("Description", height=60)
            new_prod_image = st.file_uploader("Upload Gambar", type=['jpg', 'jpeg', 'png'])
            
            if st.form_submit_button("➕ Add Product", use_container_width=True, type="primary"):
                if new_prod_name:
                    image_path = ""
                    if new_prod_image:
                        image_path = save_product_image(new_prod_image, new_prod_name)
                    
                    new_product = {
                        "name": new_prod_name,
                        "material": new_prod_material,
                        "finishing": new_prod_finishing,
                        "product_size_p": np_p,
                        "product_size_l": np_l,
                        "product_size_t": np_t,
                        "packing_size_p": npack_p,
                        "packing_size_l": npack_l,
                        "packing_size_t": npack_t,
                        "description": new_prod_desc,
                        "image_path": image_path,
                        "is_knockdown": False,
                        "knockdown_pieces": []
                    }
                    products.append(new_product)
                    st.session_state["products"] = products
                    save_products(products)
                    st.success(f"✅ Product '{new_prod_name}' ditambahkan!")
                    st.rerun()
    
    # ===== TAB: SUPPLIERS =====
    with tab3:
        st.subheader("🏭 Manage Suppliers")
        suppliers = st.session_state["suppliers"]
        
        if suppliers:
            for idx, supplier in enumerate(suppliers):
                with st.expander(f"🏭 {supplier.get('name', 'N/A')}"):
                    st.write(f"**Alamat:** {supplier.get('address', '-')}")
                    st.write(f"**Spesialisasi:** {supplier.get('specialization', '-')}")
                    st.write(f"**Contact:** {supplier.get('contact', '-')}")
                    if st.button("🗑️ Hapus", key=f"del_supp_{idx}"):
                        suppliers.pop(idx)
                        st.session_state["suppliers"] = suppliers
                        save_suppliers(suppliers)
                        st.rerun()
        
        st.markdown("### ➕ Add New Supplier")
        with st.form("add_supplier_form", clear_on_submit=True):
            new_supp_name = st.text_input("Nama Supplier *",placeholder="")
            new_supp_address = st.text_area("Alamat", height=80,placeholder="")
            new_supp_spec = st.text_input("Spesialisasi",placeholder="")
            new_supp_contact = st.text_input("Contact",placeholder="")
            
            if st.form_submit_button("➕ Add Supplier", use_container_width=True, type="primary"):
                if new_supp_name:
                    suppliers.append({
                        "name": new_supp_name,
                        "address": new_supp_address,
                        "specialization": new_supp_spec,
                        "contact": new_supp_contact
                    })
                    st.session_state["suppliers"] = suppliers
                    save_suppliers(suppliers)
                    st.success(f"✅ Supplier '{new_supp_name}' ditambahkan!")
                    st.rerun()
    
    # ===== TAB: PEKERJA HARIAN - NEW =====
    with tab4:
        st.subheader("👷 Manage Pekerja Harian")
        workers = st.session_state["workers"]
        
        if workers:
            st.info(f"👷 {len(workers)} pekerja terdaftar")
            
            for idx, worker in enumerate(workers):
                with st.expander(f"👤 {worker.get('name', 'N/A')} - {worker.get('position', '-')}"):
                    col_w1, col_w2, col_w3 = st.columns([2, 2, 1])
                    with col_w1:
                        st.write(f"**Nama:** {worker.get('name', '-')}")
                        st.write(f"**Posisi:** {worker.get('position', '-')}")
                    with col_w2:
                        st.write(f"**No. HP:** {worker.get('phone', '-')}")
                        st.write(f"**Alamat:** {worker.get('address', '-')}")
                    with col_w3:
                        if st.button("🗑️ Hapus", key=f"del_worker_{idx}"):
                            workers.pop(idx)
                            st.session_state["workers"] = workers
                            save_workers(workers)
                            st.success("Pekerja dihapus!")
                            st.rerun()
        else:
            st.info("👷 Belum ada pekerja terdaftar")
        
        st.markdown("---")
        st.markdown("### ➕ Tambah Pekerja Baru")
        
        with st.form("add_worker_form", clear_on_submit=True):
            col_nw1, col_nw2 = st.columns(2)
            with col_nw1:
                new_worker_name = st.text_input("Nama Pekerja *", placeholder="Nama lengkap")
                new_worker_position = st.selectbox("Posisi", [
                    "Tukang Kayu", "Tukang Finishing", "Helper", "Packing", "QC", "Lainnya"
                ])
            with col_nw2:
                new_worker_phone = st.text_input("No. HP", placeholder="08xxxxxxxxxx")
                new_worker_address = st.text_input("Alamat", placeholder="Alamat singkat")
            
            if st.form_submit_button("➕ Tambah Pekerja", use_container_width=True, type="primary"):
                if new_worker_name:
                    # Generate unique ID
                    worker_id = f"WRK-{len(workers)+1:03d}"
                    
                    new_worker = {
                        "id": worker_id,
                        "name": new_worker_name,
                        "position": new_worker_position,
                        "phone": new_worker_phone,
                        "address": new_worker_address,
                        "joined_date": str(datetime.date.today())
                    }
                    workers.append(new_worker)
                    st.session_state["workers"] = workers
                    if save_workers(workers):
                        st.success(f"✅ Pekerja '{new_worker_name}' berhasil ditambahkan!")
                        st.rerun()
                else:
                    st.warning("⚠️ Nama pekerja harus diisi!")
        
        # Bulk import option
        st.markdown("---")
        st.markdown("### 📋 Import Cepat (Bulk)")
        st.caption("Masukkan nama pekerja, satu per baris")
        
        bulk_names = st.text_area("Daftar Nama", placeholder="Budi\nAndi\nSiti\n...", height=100, key="bulk_workers")
        bulk_position = st.selectbox("Posisi Default", ["Tukang Kayu", "Tukang Finishing", "Helper", "Packing", "QC"], key="bulk_position")
        
        if st.button("📤 Import Semua", use_container_width=True):
            if bulk_names:
                names = [n.strip() for n in bulk_names.split("\n") if n.strip()]
                added = 0
                for name in names:
                    worker_id = f"WRK-{len(workers)+1:03d}"
                    workers.append({
                        "id": worker_id,
                        "name": name,
                        "position": bulk_position,
                        "phone": "",
                        "address": "",
                        "joined_date": str(datetime.date.today())
                    })
                    added += 1
                
                st.session_state["workers"] = workers
                if save_workers(workers):
                    st.success(f"✅ {added} pekerja berhasil ditambahkan!")
                    st.rerun()

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

                                if row.get('Is Knockdown', False):
                                    try:
                                        knockdown_pieces = json.loads(row.get('Knockdown Pieces', '[]'))
                                        if knockdown_pieces:
                                            st.markdown("---")
                                            st.markdown("**🔧 Knockdown Pieces:**")
                                            for piece_idx, piece in enumerate(knockdown_pieces):
                                                st.markdown(f"""
                                                <div style="background: #1F2937; padding: 8px; margin: 4px 0; border-radius: 4px; border-left: 3px solid #3B82F6;">
                                                    <strong>{piece_idx + 1}. {piece['name']}</strong> (x{piece['qty_per_set']}) - 
                                                    {piece['p']:.2f} × {piece['l']:.2f} × {piece['t']:.2f} cm = {piece['cbm']:.6f} m³
                                                </div>
                                                """, unsafe_allow_html=True)
                                    except:
                                        pass
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
                        items_df = pd.DataFrame(container['items'])
                        if not items_df.empty:
                            display_df = items_df[['Order ID', 'Buyer', 'Produk', 'Qty', 'Total CBM']]
                            display_df['Total CBM'] = display_df['Total CBM'].apply(lambda x: f"{x:.6f} m³")
                            display_df['Qty'] = display_df['Qty'].apply(lambda x: f"{x:,} pcs")
                            
                            st.dataframe(display_df, use_container_width=True, hide_index=True)
                            
                            # Summary statistics
                            st.markdown("---")
                            col_sum1, col_sum2, col_sum3 = st.columns(3)
                            with col_sum1:
                                st.metric("Total Orders", len(container['items']))
                            with col_sum2:
                                unique_buyers = items_df['Buyer'].nunique()
                                st.metric("Unique Buyers", unique_buyers)
                            with col_sum3:
                                unique_products = items_df['Produk'].nunique()
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

#===== MENU: UPDATE PROGRESS =====

elif st.session_state["menu"] == "Progress":
    st.header("⚙️ UPDATE PROGRESS PRODUKSI")
    
    df = st.session_state["data_produksi"]
    
    if df.empty:
        st.warning("📝 Belum ada order untuk diupdate.")
    else:
        st.markdown("### 📦 Pilih Order untuk Update")
        
        col_select1, col_select2 = st.columns(2)
        
        with col_select1:
            buyers_list = ["-- Pilih Buyer --"] + sorted(df["Buyer"].unique().tolist())
            selected_buyer = st.selectbox("1️⃣ Pilih Buyer", buyers_list, key="progress_select_buyer")
        
        with col_select2:
            if selected_buyer and selected_buyer != "-- Pilih Buyer --":
                buyer_df = df[df["Buyer"] == selected_buyer]
                products_list = ["-- Pilih Produk --"] + sorted(buyer_df["Produk"].unique().tolist())
                selected_product = st.selectbox("2️⃣ Pilih Produk", products_list, key="progress_select_product")
            else:
                st.selectbox("2️⃣ Pilih Produk", ["-- Pilih Buyer Terlebih Dahulu --"], disabled=True, key="progress_select_product_disabled")
                selected_product = None
        
        st.markdown("---")
        
        if selected_buyer and selected_buyer != "-- Pilih Buyer --" and selected_product and selected_product != "-- Pilih Produk --":
            df_filtered = df[(df["Buyer"] == selected_buyer) & (df["Produk"] == selected_product)]
            
            if df_filtered.empty:
                st.warning("⚠️ Tidak ada order yang sesuai dengan pilihan Anda.")
            else:
                stage_to_progress = {
                    "Pre Order": 0, "Order di Supplier": 10, "Warehouse": 20,
                    "Fitting 1": 30, "Amplas": 40, "Revisi 1": 50,
                    "Spray": 60, "Fitting 2": 70, "Revisi Fitting 2": 80,
                    "Packaging": 90, "Pengiriman": 100
                }
                stages_list = get_tracking_stages()
            
                for order_idx_in_filtered, (idx, order_data) in enumerate(df_filtered.iterrows()):
                    order_id = order_data["Order ID"]
                    
                    # CHECK IF FROZEN - TAMBAHKAN INI
                    is_frozen = order_data.get("Is Frozen", False)
                    
                    if is_frozen:
                        st.error(f"🔒 **Order {order_id} is FROZEN!**")
                        st.warning(f"⚠️ This order has been locked by Owner and cannot be modified.")
                        st.info(f"**Frozen Reason:** {order_data.get('Frozen Reason', 'No reason provided')}")
                        st.info(f"**Frozen By:** {order_data.get('Frozen By', 'Owner')} on {order_data.get('Frozen At', 'N/A')}")
                        st.markdown("---")
                        continue  # Skip this frozen order
                            
                stage_to_progress = {
                    "Pre Order": 0, "Order di Supplier": 10, "Warehouse": 20,
                    "Fitting 1": 30, "Amplas": 40, "Revisi 1": 50,
                    "Spray": 60, "Fitting 2": 70, "Revisi Fitting 2": 80,
                    "Packaging": 90, "Pengiriman": 100
                }
                stages_list = get_tracking_stages()

                for order_idx_in_filtered, (idx, order_data) in enumerate(df_filtered.iterrows()):
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
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        # st.markdown("""
        # <div style='background-color: #1E3A8A; padding: 15px; border-radius: 8px; margin-bottom: 25px;'>
        #     <h3 style='color: white; text-align: center; margin: 0;'>📋 STATUS TRACKING PER TAHAPAN</h3>
        # </div>
        # """, unsafe_allow_html=True)
        
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
        
        sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
        
        total_orders_filtered = len(df_track_filtered)
        pending_count = 0
        ongoing_count = 0
        done_count = 0
        
        for idx, row in df_track_filtered.iterrows():
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
        
        for idx, row in df_track_filtered.iterrows():
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
                        original_idx = df_track_filtered[df_track_filtered['Order ID'] == row['Order ID']].index[0]
                        
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
                        df_items = pd.DataFrame(items)
                        df_items["Harga Total"] = df_items["Harga Total"].apply(lambda x: f"Rp {x:,.0f}")
                        df_items["Harga per Unit"] = df_items["Harga per Unit"].apply(lambda x: f"Rp {x:,.0f}")
                        
                        st.dataframe(
                            df_items[["Nama Barang", "Jumlah per Pcs", "Jumlah Total", "Harga per Unit", "Harga Total"]],
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
            df = st.session_state["data_produksi"]
            buyers = df["Buyer"].unique().tolist() if not df.empty else []
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

# ===== MENU: DATABASE - ENHANCED WITH PRODUCTS & SUPPLIERS =====
elif st.session_state["menu"] == "Database":
    st.header("💾 DATABASE MANAGEMENT")
    
    tab1, tab2, tab3 = st.tabs(["👥 Buyers Database", "📦 Products Database", "🏭 Suppliers Database"])
    
    ###SAMA SEPERTI CODE SEBELUMNYA UNTUK TAB BUYERS###
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
        st.subheader("📦 Manage Products - Enhanced Database")
        
        products = st.session_state["products"]
        
        if "edit_product_mode" not in st.session_state:
            st.session_state["edit_product_mode"] = False
            st.session_state["edit_product_idx"] = None
        
        # ===== EDIT MODE - UPDATED FORMAT =====
        if st.session_state["edit_product_mode"] and st.session_state["edit_product_idx"] is not None:
            idx = st.session_state["edit_product_idx"]
            selected_product = products[idx]
            
            st.markdown("### ✏️ Edit Product")
            st.markdown(f"**Editing: {selected_product.get('name', 'N/A')}**")
            
            # Product type selection
            edit_is_knockdown = st.checkbox(
                "🔧 Produk Knockdown", 
                value=selected_product.get("is_knockdown", False),
                key="edit_is_knockdown_check"
            )
            
            st.markdown("---")
            
            with st.container():
                col_e1, col_e2, col_e3 = st.columns([1, 1, 1])
                
                with col_e1:
                    st.markdown("**Product Information**")
                    edit_name = st.text_input("Nama Produk *", value=selected_product.get("name", ""), key="edit_prod_name")
                    edit_material = st.text_input("Material", value=selected_product.get("material", ""), key="edit_material")
                    edit_finishing = st.text_input("Finishing", value=selected_product.get("finishing", ""), key="edit_finishing")
                    
                    # Image upload
                    edit_image_upload = st.file_uploader(
                        "Upload Gambar Produk", 
                        type=['jpg', 'jpeg', 'png'], 
                        key="edit_image_upload"
                    )
                    
                    # Show current image
                    current_image = selected_product.get("image_path", "")
                    if current_image and os.path.exists(current_image):
                        st.image(current_image, caption="Current Image", width=150)
                        st.caption("↑ Gambar saat ini (bisa override dengan upload baru)")
                
                with col_e2:
                    st.markdown("**Product Size (cm)**")
                    col_ps1, col_ps2, col_ps3 = st.columns(3)
                    with col_ps1:
                        edit_prod_p = st.number_input(
                            "P", 
                            min_value=0.0, 
                            value=float(selected_product.get("product_size_p", 0)),
                            format="%.2f", 
                            step=0.01,
                            key="edit_prod_p"
                        )
                    with col_ps2:
                        edit_prod_l = st.number_input(
                            "L", 
                            min_value=0.0, 
                            value=float(selected_product.get("product_size_l", 0)),
                            format="%.2f", 
                            step=0.01,
                            key="edit_prod_l"
                        )
                    with col_ps3:
                        edit_prod_t = st.number_input(
                            "T", 
                            min_value=0.0, 
                            value=float(selected_product.get("product_size_t", 0)),
                            format="%.2f", 
                            step=0.01,
                            key="edit_prod_t"
                        )
                    
                    # Calculate product CBM
                    edit_prod_cbm = calculate_cbm(edit_prod_p, edit_prod_l, edit_prod_t)
                    if edit_prod_cbm > 0:
                        st.success(f"📦 Product CBM: **{edit_prod_cbm:.6f} m³**")
                    else:
                        st.info("📦 Product CBM: 0.000000 m³")
                
                with col_e3:
                    if not edit_is_knockdown:
                        st.markdown("**Packing Size (cm)**")
                        col_pack1, col_pack2, col_pack3 = st.columns(3)
                        with col_pack1:
                            edit_pack_p = st.number_input(
                                "P", 
                                min_value=0.0, 
                                value=float(selected_product.get("packing_size_p", 0)),
                                format="%.2f", 
                                step=0.01,
                                key="edit_pack_p"
                            )
                        with col_pack2:
                            edit_pack_l = st.number_input(
                                "L", 
                                min_value=0.0, 
                                value=float(selected_product.get("packing_size_l", 0)),
                                format="%.2f", 
                                step=0.01,
                                key="edit_pack_l"
                            )
                        with col_pack3:
                            edit_pack_t = st.number_input(
                                "T", 
                                min_value=0.0, 
                                value=float(selected_product.get("packing_size_t", 0)),
                                format="%.2f", 
                                step=0.01,
                                key="edit_pack_t"
                            )
                        
                        edit_pack_cbm = calculate_cbm(edit_pack_p, edit_pack_l, edit_pack_t)
                        if edit_pack_cbm > 0:
                            st.success(f"📦 Packing CBM: **{edit_pack_cbm:.6f} m³**")
                        else:
                            st.info("📦 Packing CBM: 0.000000 m³")
                    else:
                        st.markdown("**🔧 Knockdown Pieces**")
                        st.caption("Edit pieces di bawah")
            
            edit_description = st.text_area(
                "Description", 
                value=selected_product.get("description", ""),
                height=80,
                key="edit_description"
            )
            
            # Knockdown pieces management for edit
            if edit_is_knockdown:
                if "edit_knockdown_pieces" not in st.session_state:
                    st.session_state["edit_knockdown_pieces"] = selected_product.get("knockdown_pieces", []).copy()
                
                st.markdown("---")
                st.markdown("### 🔧 Kelola Knockdown Pieces")
                
                with st.expander("➕ Tambah Piece Baru", expanded=False):
                    col_kd1, col_kd2, col_kd3, col_kd4 = st.columns([2, 1, 2, 1])
                    
                    with col_kd1:
                        edit_piece_name = st.text_input("Nama Piece", placeholder="Contoh: Body, Door", key="edit_piece_name")
                    
                    with col_kd2:
                        edit_piece_qty = st.number_input("Qty per Set", min_value=1, value=1, key="edit_piece_qty")
                    
                    with col_kd3:
                        st.caption("**Packing Size (cm)**")
                        col_kd_p1, col_kd_p2, col_kd_p3 = st.columns(3)
                        with col_kd_p1:
                            edit_piece_p = st.number_input("P", min_value=0.0, value=0.0, format="%.2f", key="edit_piece_p", step=0.01)
                        with col_kd_p2:
                            edit_piece_l = st.number_input("L", min_value=0.0, value=0.0, format="%.2f", key="edit_piece_l", step=0.01)
                        with col_kd_p3:
                            edit_piece_t = st.number_input("T", min_value=0.0, value=0.0, format="%.2f", key="edit_piece_t", step=0.01)
                    
                    with col_kd4:
                        edit_piece_cbm = calculate_cbm(edit_piece_p, edit_piece_l, edit_piece_t) * edit_piece_qty
                        st.metric("CBM", f"{edit_piece_cbm:.6f}")
                        
                        if st.button("➕ Add", use_container_width=True, type="primary", key="edit_add_piece_btn"):
                            if edit_piece_name and edit_piece_cbm > 0:
                                new_piece = {
                                    "name": edit_piece_name,
                                    "qty_per_set": edit_piece_qty,
                                    "p": edit_piece_p,
                                    "l": edit_piece_l,
                                    "t": edit_piece_t,
                                    "cbm": edit_piece_cbm
                                }
                                st.session_state["edit_knockdown_pieces"].append(new_piece)
                                st.success(f"✅ Piece '{edit_piece_name}' ditambahkan!")
                                st.rerun()
                            else:
                                st.warning("⚠️ Nama dan dimensi harus diisi!")
                
                # Display pieces
                if st.session_state["edit_knockdown_pieces"]:
                    st.markdown("#### 📋 Pieces dalam Produk")
                    
                    for piece_idx, piece in enumerate(st.session_state["edit_knockdown_pieces"]):
                        st.markdown(f"""
                        <div class="knockdown-piece">
                            <span class="piece-badge">Piece {piece_idx + 1}</span>
                            <strong style="margin-left: 10px; color: #60A5FA;">{piece['name']}</strong>
                            <span style="color: #9CA3AF; margin-left: 10px;">x{piece['qty_per_set']} pcs</span>
                            <br>
                            <small style="color: #D1D5DB;">
                                Size: {piece['p']:.2f} × {piece['l']:.2f} × {piece['t']:.2f} cm | 
                                CBM: {piece['cbm']:.6f} m³
                            </small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col_piece1, col_piece2 = st.columns([4, 1])
                        with col_piece2:
                            if st.button("🗑️ Hapus", key=f"edit_remove_piece_{piece_idx}", use_container_width=True):
                                st.session_state["edit_knockdown_pieces"].pop(piece_idx)
                                st.rerun()
            
            st.markdown("---")
            
            # Action buttons
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("💾 Simpan Perubahan", use_container_width=True, type="primary", key="edit_submit_product"):
                    if edit_name:
                        # Handle image
                        final_image_path = selected_product.get("image_path", "")
                        if edit_image_upload:
                            final_image_path = save_product_image(edit_image_upload, edit_name)
                        
                        # Get knockdown pieces
                        final_knockdown_pieces = []
                        if edit_is_knockdown:
                            final_knockdown_pieces = st.session_state.get("edit_knockdown_pieces", [])
                        
                        # Update product
                        products[idx] = {
                            "name": edit_name,
                            "material": edit_material,
                            "finishing": edit_finishing,
                            "product_size_p": edit_prod_p,
                            "product_size_l": edit_prod_l,
                            "product_size_t": edit_prod_t,
                            "packing_size_p": edit_pack_p if not edit_is_knockdown else 0.0,
                            "packing_size_l": edit_pack_l if not edit_is_knockdown else 0.0,
                            "packing_size_t": edit_pack_t if not edit_is_knockdown else 0.0,
                            "is_knockdown": edit_is_knockdown,
                            "knockdown_pieces": final_knockdown_pieces,
                            "image_path": final_image_path,
                            "description": edit_description
                        }
                        
                        st.session_state["products"] = products
                        if save_products(products):
                            st.success(f"✅ Product '{edit_name}' berhasil diupdate!")
                            st.session_state["edit_product_mode"] = False
                            st.session_state["edit_product_idx"] = None
                            if "edit_knockdown_pieces" in st.session_state:
                                del st.session_state["edit_knockdown_pieces"]
                            st.rerun()
                    else:
                        st.warning("⚠️ Nama produk tidak boleh kosong")
            
            with col_btn2:
                if st.button("❌ Batal", use_container_width=True, type="secondary", key="edit_cancel_product"):
                    st.session_state["edit_product_mode"] = False
                    st.session_state["edit_product_idx"] = None
                    if "edit_knockdown_pieces" in st.session_state:
                        del st.session_state["edit_knockdown_pieces"]
                    st.rerun()
            
            st.markdown("---")
        
        # ===== PRODUCT LIST =====
        st.markdown("### Current Products Database")
        if products:
            st.info(f"📦 {len(products)} products in database")
            
            for idx, product in enumerate(products):
                knockdown_badge = " 🔧" if product.get('is_knockdown', False) else ""
                with st.expander(
                    f"📦 {product.get('name', 'N/A')}{knockdown_badge}",
                    expanded=False
                ):
                    col_p1, col_p2, col_p3 = st.columns([2, 2, 1])
                    
                    with col_p1:
                        st.write(f"**Material:** {product.get('material', '-')}")
                        st.write(f"**Finishing:** {product.get('finishing', '-')}")
                        
                        # Display sizes
                        prod_p = product.get('product_size_p', 0)
                        prod_l = product.get('product_size_l', 0)
                        prod_t = product.get('product_size_t', 0)
                        st.write(f"**Product Size:** {prod_p:.2f} x {prod_l:.2f} x {prod_t:.2f} cm")
                        
                        prod_cbm = calculate_cbm(prod_p, prod_l, prod_t)
                        st.write(f"**Product CBM:** {prod_cbm:.6f} m³")
                    
                    with col_p2:
                        if not product.get("is_knockdown", False):
                            pack_p = product.get('packing_size_p', 0)
                            pack_l = product.get('packing_size_l', 0)
                            pack_t = product.get('packing_size_t', 0)
                            st.write(f"**Packing Size:** {pack_p:.2f} x {pack_l:.2f} x {pack_t:.2f} cm")
                            
                            pack_cbm = calculate_cbm(pack_p, pack_l, pack_t)
                            st.write(f"**Packing CBM:** {pack_cbm:.6f} m³")
                        else:
                            pieces = product.get("knockdown_pieces", [])
                            st.write(f"**Type:** Knockdown")
                            st.write(f"**Pieces:** {len(pieces)} parts")
                            
                            if pieces:
                                total_cbm = sum([p.get("cbm", 0) for p in pieces])
                                st.write(f"**Total CBM per Set:** {total_cbm:.6f} m³")
                        
                        desc = product.get('description', '-')
                        st.write(f"**Description:** {desc[:50]}..." if len(desc) > 50 else f"**Description:** {desc}")
                    
                    with col_p3:
                        image_path = product.get("image_path", "")
                        if image_path and os.path.exists(image_path):
                            st.image(image_path, width=100)
                        else:
                            st.info("No image")
                        
                        if st.button("✏️ Edit", key=f"edit_prod_{idx}", use_container_width=True):
                            st.session_state["edit_product_mode"] = True
                            st.session_state["edit_product_idx"] = idx
                            st.rerun()
                        
                        if st.button("🗑️ Delete", key=f"del_prod_{idx}", use_container_width=True, type="secondary"):
                            if st.session_state.get(f"confirm_del_prod_{idx}", False):
                                product_name = products[idx].get("name", "")
                                products.pop(idx)
                                st.session_state["products"] = products
                                if save_products(products):
                                    st.success(f"✅ Product '{product_name}' deleted!")
                                    del st.session_state[f"confirm_del_prod_{idx}"]
                                    st.rerun()
                            else:
                                st.session_state[f"confirm_del_prod_{idx}"] = True
                                st.warning("⚠️ Click again to confirm!")
                                st.rerun()
                    
                    # Show knockdown pieces if applicable
                    if product.get("is_knockdown", False):
                        pieces = product.get("knockdown_pieces", [])
                        if pieces:
                            st.markdown("---")
                            st.markdown("**🔧 Knockdown Pieces:**")
                            for piece_idx, piece in enumerate(pieces):
                                st.markdown(f"""
                                <div style="background: #1F2937; padding: 8px; margin: 4px 0; border-radius: 4px; border-left: 3px solid #3B82F6;">
                                    <strong>{piece_idx + 1}. {piece['name']}</strong> (x{piece['qty_per_set']}) - 
                                    {piece['p']:.2f} × {piece['l']:.2f} × {piece['t']:.2f} cm = {piece['cbm']:.6f} m³
                                </div>
                                """, unsafe_allow_html=True)
        else:
            st.info("Belum ada produk yang terdaftar")
        
        st.markdown("---")
        
        # ===== ADD NEW PRODUCT - UPDATED FORMAT =====
        st.markdown("### ➕ Add New Product")
        
        if "new_product_knockdown_pieces" not in st.session_state:
            st.session_state["new_product_knockdown_pieces"] = []
        
        # Product type selection
        new_is_knockdown = st.checkbox(
            "🔧 Produk Knockdown", 
            key="new_is_knockdown_check",
            help="Centang jika produk terdiri dari beberapa piece"
        )
        
        st.markdown("---")
        
        with st.container():
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                st.markdown("**Product Information**")
                new_name = st.text_input("Nama Produk *", placeholder="Dining Table Oslo", key="new_prod_name")
                new_material = st.text_input("Material", placeholder="Mahogany Solid", key="new_material")
                new_finishing = st.text_input("Finishing", placeholder="NC Dark Walnut - Matte", key="new_finishing")
                
                new_image_upload = st.file_uploader(
                    "Upload Gambar Produk", 
                    type=['jpg', 'jpeg', 'png'], 
                    key="new_image_upload"
                )
            
            with col2:
                st.markdown("**Product Size (cm)**")
                col_ps1, col_ps2, col_ps3 = st.columns(3)
                with col_ps1:
                    new_prod_p = st.number_input("P", min_value=0.0, value=None, format="%.2f", step=0.01, key="new_prod_p", placeholder="0.00")
                with col_ps2:
                    new_prod_l = st.number_input("L", min_value=0.0, value=None, format="%.2f", step=0.01, key="new_prod_l", placeholder="0.00")
                with col_ps3:
                    new_prod_t = st.number_input("T", min_value=0.0, value=None, format="%.2f", step=0.01, key="new_prod_t", placeholder="0.00")
                
                new_prod_cbm = calculate_cbm(new_prod_p, new_prod_l, new_prod_t) if new_prod_p else 0
                if new_prod_cbm > 0:
                    st.success(f"📦 Product CBM: **{new_prod_cbm:.6f} m³**")
                else:
                    st.info("📦 Product CBM: 0.000000 m³")
            
            with col3:
                if not new_is_knockdown:
                    st.markdown("**Packing Size (cm)**")
                    col_pack1, col_pack2, col_pack3 = st.columns(3)
                    with col_pack1:
                        new_pack_p = st.number_input("P", min_value=0.0, value=None, format="%.2f", step=0.01, key="new_pack_p", placeholder="0.00")
                    with col_pack2:
                        new_pack_l = st.number_input("L", min_value=0.0, value=None, format="%.2f", step=0.01, key="new_pack_l", placeholder="0.00")
                    with col_pack3:
                        new_pack_t = st.number_input("T", min_value=0.0, value=None, format="%.2f", step=0.01, key="new_pack_t", placeholder="0.00")
                    
                    new_pack_cbm = calculate_cbm(new_pack_p, new_pack_l, new_pack_t) if new_pack_p else 0
                    if new_pack_cbm > 0:
                        st.success(f"📦 Packing CBM: **{new_pack_cbm:.6f} m³**")
                    else:
                        st.info("📦 Packing CBM: 0.000000 m³")
                else:
                    st.markdown("**🔧 Knockdown Pieces**")
                    st.caption("Tambahkan pieces di bawah")
                    
                    if st.session_state["new_product_knockdown_pieces"]:
                        total_cbm_set = sum([p["cbm"] for p in st.session_state["new_product_knockdown_pieces"]])
                        st.success(f"📦 CBM per Set: **{total_cbm_set:.6f} m³**")
                        st.caption(f"✓ {len(st.session_state['new_product_knockdown_pieces'])} pieces")
                    else:
                        st.warning("⚠️ Belum ada piece")
        
        new_description = st.text_area("Description", placeholder="Deskripsi produk...", height=80, key="new_description")
        
        # Knockdown pieces management
        if new_is_knockdown:
            st.markdown("---")
            st.markdown("### 🔧 Kelola Knockdown Pieces")
            
            with st.expander("➕ Tambah Piece Baru", expanded=True):
                col_kd1, col_kd2, col_kd3, col_kd4 = st.columns([2, 1, 2, 1])
                
                with col_kd1:
                    new_piece_name = st.text_input("Nama Piece", placeholder="Body, Door, Shelf", key="new_piece_name")
                
                with col_kd2:
                    new_piece_qty = st.number_input("Qty per Set", min_value=1, value=1, key="new_piece_qty")
                
                with col_kd3:
                    st.caption("**Packing Size (cm)**")
                    col_kd_p1, col_kd_p2, col_kd_p3 = st.columns(3)
                    with col_kd_p1:
                        new_piece_p = st.number_input("P", min_value=0.0, value=0.0, format="%.2f", key="new_piece_p", step=0.01)
                    with col_kd_p2:
                        new_piece_l = st.number_input("L", min_value=0.0, value=0.0, format="%.2f", key="new_piece_l", step=0.01)
                    with col_kd_p3:
                        new_piece_t = st.number_input("T", min_value=0.0, value=0.0, format="%.2f", key="new_piece_t", step=0.01)
                
                with col_kd4:
                    new_piece_cbm = calculate_cbm(new_piece_p, new_piece_l, new_piece_t) * new_piece_qty
                    st.metric("CBM", f"{new_piece_cbm:.6f}")
                    
                    if st.button("➕ Add", use_container_width=True, type="primary", key="new_add_piece_btn"):
                        if new_piece_name and new_piece_cbm > 0:
                            new_piece = {
                                "name": new_piece_name,
                                "qty_per_set": new_piece_qty,
                                "p": new_piece_p,
                                "l": new_piece_l,
                                "t": new_piece_t,
                                "cbm": new_piece_cbm
                            }
                            st.session_state["new_product_knockdown_pieces"].append(new_piece)
                            st.success(f"✅ Piece '{new_piece_name}' ditambahkan!")
                            st.rerun()
                        else:
                            st.warning("⚠️ Nama dan dimensi harus diisi!")
            
            # Display pieces
            if st.session_state["new_product_knockdown_pieces"]:
                st.markdown("#### 📋 Pieces dalam Produk")
                
                for piece_idx, piece in enumerate(st.session_state["new_product_knockdown_pieces"]):
                    st.markdown(f"""
                    <div class="knockdown-piece">
                        <span class="piece-badge">Piece {piece_idx + 1}</span>
                        <strong style="margin-left: 10px; color: #60A5FA;">{piece['name']}</strong>
                        <span style="color: #9CA3AF; margin-left: 10px;">x{piece['qty_per_set']} pcs</span>
                        <br>
                        <small style="color: #D1D5DB;">
                            Size: {piece['p']:.2f} × {piece['l']:.2f} × {piece['t']:.2f} cm | 
                            CBM: {piece['cbm']:.6f} m³
                        </small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_piece1, col_piece2 = st.columns([4, 1])
                    with col_piece2:
                        if st.button("🗑️ Hapus", key=f"new_remove_piece_{piece_idx}", use_container_width=True):
                            st.session_state["new_product_knockdown_pieces"].pop(piece_idx)
                            st.rerun()
        
        st.markdown("---")
        
        # Submit button
        col_submit1, col_submit2 = st.columns(2)
        
        with col_submit1:
            if st.button("➕ Tambah Product", use_container_width=True, type="primary", key="new_submit_product"):
                if new_name:
                    # Check duplicate
                    existing_names = [p.get("name", "") for p in products]
                    if new_name in existing_names:
                        st.warning("⚠️ Produk sudah ada")
                    else:
                        # Validate knockdown
                        if new_is_knockdown and not st.session_state["new_product_knockdown_pieces"]:
                            st.warning("⚠️ Produk knockdown harus memiliki minimal 1 piece!")
                        else:
                            # Save image
                            final_image_path = ""
                            if new_image_upload:
                                final_image_path = save_product_image(new_image_upload, new_name)
                            
                            # Create product data
                            new_product_data = {
                                "name": new_name,
                                "material": new_material,
                                "finishing": new_finishing,
                                "product_size_p": new_prod_p if new_prod_p else 0.0,
                                "product_size_l": new_prod_l if new_prod_l else 0.0,
                                "product_size_t": new_prod_t if new_prod_t else 0.0,
                                "packing_size_p": new_pack_p if not new_is_knockdown and new_pack_p else 0.0,
                                "packing_size_l": new_pack_l if not new_is_knockdown and new_pack_l else 0.0,
                                "packing_size_t": new_pack_t if not new_is_knockdown and new_pack_t else 0.0,
                                "is_knockdown": new_is_knockdown,
                                "knockdown_pieces": st.session_state["new_product_knockdown_pieces"].copy() if new_is_knockdown else [],
                                "image_path": final_image_path,
                                "description": new_description
                            }
                            
                            products.append(new_product_data)
                            st.session_state["products"] = products
                            
                            if save_products(products):
                                st.success(f"✅ Product '{new_name}' berhasil ditambahkan!")
                                st.session_state["new_product_knockdown_pieces"] = []
                                st.balloons()
                                st.rerun()
                else:
                    st.warning("⚠️ Nama produk tidak boleh kosong")
        
        with col_submit2:
            if st.button("🗑️ Clear Form", use_container_width=True, type="secondary", key="new_clear_product"):
                st.session_state["new_product_knockdown_pieces"] = []
                st.rerun()
    with tab3:
        st.subheader("🏭 Manage Suppliers")
        
        suppliers = st.session_state["suppliers"]
        
        if "edit_supplier_mode" not in st.session_state:
            st.session_state["edit_supplier_mode"] = False
            st.session_state["edit_supplier_idx"] = None
        
        # EDIT MODE
        if st.session_state["edit_supplier_mode"] and st.session_state["edit_supplier_idx"] is not None:
            idx = st.session_state["edit_supplier_idx"]
            selected_supplier = suppliers[idx]
            
            st.markdown("### ✏️ Edit Supplier")
            with st.form("edit_supplier_form"):
                st.markdown(f"**Editing: {selected_supplier.get('name', 'N/A')}**")
                col1, col2 = st.columns(2)
                with col1:
                    edit_name = st.text_input("Nama Supplier *", value=selected_supplier.get("name", ""))
                    edit_address = st.text_area("Alamat Supplier", value=selected_supplier.get("address", ""), height=100)
                with col2:
                    edit_specialization = st.text_area(
                        "Spesialisasi", 
                        value=selected_supplier.get("specialization", ""),
                        height=100,
                        help="Contoh: Meja kayu, lemari knockdown"
                    )
                    edit_contact = st.text_input("Contact", value=selected_supplier.get("contact", ""))
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    update_supplier = st.form_submit_button("💾 Update", use_container_width=True, type="primary")
                with col_btn2:
                    delete_supplier = st.form_submit_button("🗑️ Delete", use_container_width=True, type="secondary")
                with col_btn3:
                    cancel_edit = st.form_submit_button("❌ Cancel", use_container_width=True)
                
                if update_supplier:
                    if edit_name:
                        suppliers[idx] = {
                            "name": edit_name,
                            "address": edit_address,
                            "specialization": edit_specialization,
                            "contact": edit_contact
                        }
                        st.session_state["suppliers"] = suppliers
                        if save_suppliers(suppliers):
                            st.success(f"✅ Supplier '{edit_name}' berhasil diupdate!")
                            st.session_state["edit_supplier_mode"] = False
                            st.session_state["edit_supplier_idx"] = None
                            st.rerun()
                    else:
                        st.warning("⚠️ Nama supplier tidak boleh kosong")
                
                if delete_supplier:
                    supplier_name = suppliers[idx].get("name", "")
                    suppliers.pop(idx)
                    st.session_state["suppliers"] = suppliers
                    if save_suppliers(suppliers):
                        st.success(f"✅ Supplier '{supplier_name}' berhasil dihapus!")
                        st.session_state["edit_supplier_mode"] = False
                        st.session_state["edit_supplier_idx"] = None
                        st.rerun()
                
                if cancel_edit:
                    st.session_state["edit_supplier_mode"] = False
                    st.session_state["edit_supplier_idx"] = None
                    st.rerun()
            
            st.markdown("---")
        
        # SUPPLIER LIST
        st.markdown("### Current Suppliers Database")
        if suppliers:
            st.info(f"🏭 {len(suppliers)} suppliers in database")
            
            header_cols = st.columns([2, 2.5, 2.5, 1.5, 0.8])
            header_cols[0].markdown("**Nama Supplier**")
            header_cols[1].markdown("**Alamat**")
            header_cols[2].markdown("**Spesialisasi**")
            header_cols[3].markdown("**Contact**")
            header_cols[4].markdown("**Action**")
            
            for idx, supplier in enumerate(suppliers):
                row_cols = st.columns([2, 2.5, 2.5, 1.5, 0.8])
                row_cols[0].write(supplier.get("name", "-"))
                row_cols[1].write(supplier.get("address", "-")[:40] + "..." if len(supplier.get("address", "")) > 40 else supplier.get("address", "-"))
                row_cols[2].write(supplier.get("specialization", "-")[:40] + "..." if len(supplier.get("specialization", "")) > 40 else supplier.get("specialization", "-"))
                row_cols[3].write(supplier.get("contact", "-"))
                
                with row_cols[4]:
                    if st.button("✏️", key=f"edit_supp_{idx}", use_container_width=True):
                        st.session_state["edit_supplier_mode"] = True
                        st.session_state["edit_supplier_idx"] = idx
                        st.rerun()
                
                st.markdown("<div style='margin: 5px 0; border-bottom: 1px solid #374151;'></div>", unsafe_allow_html=True)
        else:
            st.info("Belum ada supplier yang terdaftar")
        
        st.markdown("---")
        
        # ADD NEW SUPPLIER
        st.markdown("### ➕ Add New Supplier")
        with st.form("add_supplier_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                new_supplier_name = st.text_input("Nama Supplier *", placeholder="UD Jaya Makmur")
                new_supplier_address = st.text_area(
                    "Alamat Supplier", 
                    placeholder="Jl. Kenanga No. 45, Jepara",
                    height=100
                )
            with col2:
                new_supplier_specialization = st.text_area(
                    "Spesialisasi", 
                    placeholder="Meja kayu, lemari knockdown, material mahogany",
                    height=100
                )
                new_supplier_contact = st.text_input("Contact", placeholder="Budi / +62812345678")
            
            submit_supplier = st.form_submit_button("➕ Add Supplier", use_container_width=True, type="primary")
            
            if submit_supplier:
                if new_supplier_name:
                    existing_names = [s.get("name", "") for s in suppliers]
                    if new_supplier_name not in existing_names:
                        new_supplier_data = {
                            "name": new_supplier_name,
                            "address": new_supplier_address,
                            "specialization": new_supplier_specialization,
                            "contact": new_supplier_contact
                        }
                        suppliers.append(new_supplier_data)
                        st.session_state["suppliers"] = suppliers
                        if save_suppliers(suppliers):
                            st.success(f"✅ Supplier '{new_supplier_name}' berhasil ditambahkan!")
                            st.rerun()
                    else:
                        st.warning("⚠️ Supplier sudah ada")
                else:
                    st.warning("⚠️ Nama supplier tidak boleh kosong")

# ===== MENU: ANALYTICS =====
elif st.session_state["menu"] == "Analytics":
    st.header("📈 ANALISIS & LAPORAN")
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        # Ensure Due Date is datetime for comparisons
        df_analysis = df.copy()
        df_analysis['Due Date'] = pd.to_datetime(df_analysis['Due Date'])
        
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "👥 By Buyer", "📦 By Product"])
        
        with tab1:
            st.subheader("Performance Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            total_qty = df_analysis["Qty"].sum()
            # Convert today to Timestamp for comparison
            today_ts = pd.Timestamp(datetime.date.today())
            on_time_orders = len(df_analysis[df_analysis["Due Date"] >= today_ts])
            completion_rate = (df_analysis["Progress"].str.rstrip('%').astype('float').mean())
            total_buyers = df_analysis["Buyer"].nunique()
            
            col1.metric("Total Quantity", f"{total_qty:,} pcs")
            col2.metric("On-Time Orders", on_time_orders)
            col3.metric("Avg Completion", f"{completion_rate:.1f}%")
            col4.metric("Total Buyers", total_buyers)
            
            st.markdown("---")
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                priority_count = df_analysis["Prioritas"].value_counts()
                fig_priority = px.bar(x=priority_count.index, y=priority_count.values,
                                   title="Orders by Priority")
                st.plotly_chart(fig_priority, use_container_width=True)
            
            with col_chart2:
                stage_count = df_analysis["Proses Saat Ini"].value_counts()
                fig_stage = px.pie(values=stage_count.values, names=stage_count.index,
                                     title="Orders by Stage")
                st.plotly_chart(fig_stage, use_container_width=True)
        
        with tab2:
            st.subheader("Analysis by Buyer")
            buyer_stats = df_analysis.groupby("Buyer").agg({
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
            product_stats = df_analysis.groupby("Produk").agg({
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
            csv_data = df_analysis.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"ppic_report_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_exp2:
            json_data = df_analysis.to_json(orient='records', indent=2, date_format='iso')
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
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            filter_buyers = st.multiselect("Filter Buyer", df["Buyer"].unique(), default=df["Buyer"].unique())
        with col_filter2:
            filter_priority = st.multiselect("Filter Priority", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
        
        df_filtered = df[df["Buyer"].isin(filter_buyers) & df["Prioritas"].isin(filter_priority)].copy()
        
        if not df_filtered.empty:
            df_filtered['Progress_Num'] = df_filtered['Progress'].str.rstrip('%').astype('float')
            df_filtered['Order Date'] = pd.to_datetime(df_filtered['Order Date'])
            df_filtered['Due Date'] = pd.to_datetime(df_filtered['Due Date'])
            df_filtered['Duration'] = (df_filtered['Due Date'] - df_filtered['Order Date']).dt.days
            
            gantt_data = []
            
            for idx, row in df_filtered.iterrows():
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
                    y1=len(df_filtered) - 0.5,
                    line=dict(color="#EF4444", width=2, dash="dash")
                )
                
                fig.update_layout(
                    height=max(450, len(df_filtered) * 70),
                    xaxis_title="Timeline",
                    yaxis_title="Orders",
                    hovermode='closest'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                st.subheader("📋 Order Timeline Summary")
                
                summary_df = df_filtered[["Order ID", "Buyer", "Produk", "Order Date", "Due Date", 
                                         "Progress", "Prioritas"]].copy()
                summary_df["Order Date"] = summary_df["Order Date"].dt.strftime('%Y-%m-%d')
                summary_df["Due Date"] = summary_df["Due Date"].dt.strftime('%Y-%m-%d')
                
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
        else:
            st.warning("Tidak ada data sesuai filter")
    else:
        st.info("📝 Belum ada data untuk membuat Gantt Chart.")


# ===== MENU: FROZEN ZONE (REPLACE ENTIRE SECTION) =====
elif st.session_state["menu"] == "Frozen":
    st.header("❄️ FROZEN ZONE - DATE LOCKING SYSTEM")
    st.caption("🔒 Lock specific dates to prevent NEW order creation")
    
    tab1, tab2 = st.tabs(["🔒 Manage Frozen Dates", "📊 Frozen Dates Report"])
    
    with tab1:
        st.markdown("### ❄️ Freeze/Unfreeze Dates")
        
        st.markdown("""
        <div style='background: #DBEAFE; border: 2px solid #3B82F6; border-radius: 8px; padding: 15px; margin: 15px 0;'>
            <h4 style='color: #1E40AF; margin: 0 0 10px 0;'>ℹ️ HOW IT WORKS</h4>
            <p style='color: #1E3A8A; margin: 0; font-size: 0.9rem;'>
                When a date is <strong>FROZEN</strong>:
            </p>
            <ul style='color: #1E3A8A; margin: 10px 0 0 20px; font-size: 0.9rem;'>
                <li>❌ <strong>Cannot create NEW orders</strong> with that Order Date or Due Date</li>
                <li>✅ <strong>Can still update progress</strong> of existing orders</li>
                <li>✅ <strong>Can still edit</strong> existing orders</li>
            </ul>
            <p style='color: #1E3A8A; margin: 10px 0 0 0; font-size: 0.85rem; font-style: italic;'>
                💡 Use this to prevent new work instructions on closed dates (month-end, audits, etc)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Freeze new date
        st.markdown("#### 🆕 Freeze New Date")
        
        col_freeze1, col_freeze2 = st.columns([2, 1])
        
        with col_freeze1:
            with st.container():
                col_date1, col_date2 = st.columns(2)
                
                with col_date1:
                    freeze_date = st.date_input(
                        "Select Date to Freeze",
                        datetime.date.today(),
                        key="freeze_date_input"
                    )
                
                with col_date2:
                    freeze_mode = st.radio(
                        "Freeze Mode",
                        ["Single Date", "Date Range"],
                        key="freeze_mode",
                        horizontal=True
                    )
                
                if freeze_mode == "Date Range":
                    freeze_end_date = st.date_input(
                        "End Date (Range)",
                        freeze_date + datetime.timedelta(days=7),
                        key="freeze_end_date"
                    )
                
                freeze_reason = st.text_area(
                    "Reason for Freezing *",
                    placeholder="Example: Month-end closing, Audit period, Holiday shutdown, System maintenance...",
                    height=80,
                    key="freeze_reason_input"
                )
        
        with col_freeze2:
            st.markdown("**Preview**")
            
            if freeze_mode == "Single Date":
                st.info(f"📅 Date: {freeze_date}")
                days_count = 1
            else:
                st.info(f"📅 From: {freeze_date}")
                st.info(f"📅 To: {freeze_end_date}")
                days_count = (freeze_end_date - freeze_date).days + 1
            
            st.metric("Days to Freeze", days_count)
            
            st.markdown("---")
            st.caption("**Effect:**")
            st.caption("❌ Block new orders")
            st.caption("✅ Allow progress updates")
            st.caption("✅ Allow edits")
        
        if st.button("🔒 FREEZE DATE(S)", use_container_width=True, type="primary", key="freeze_dates_btn"):
            if freeze_reason:
                frozen_dates = st.session_state["frozen_dates"]
                
                # Generate list of dates to freeze
                dates_to_freeze = []
                if freeze_mode == "Single Date":
                    dates_to_freeze = [freeze_date]
                else:
                    current_date = freeze_date
                    while current_date <= freeze_end_date:
                        dates_to_freeze.append(current_date)
                        current_date += datetime.timedelta(days=1)
                
                # Add each date to frozen list
                added_count = 0
                existing_count = 0
                
                for date in dates_to_freeze:
                    date_str = str(date)
                    
                    # Check if already frozen
                    already_frozen = False
                    for frozen in frozen_dates:
                        if frozen.get("date") == date_str:
                            already_frozen = True
                            existing_count += 1
                            break
                    
                    if not already_frozen:
                        new_frozen = {
                            "date": date_str,
                            "reason": freeze_reason,
                            "frozen_by": st.session_state.get("user_name", "Owner"),
                            "frozen_at": str(datetime.datetime.now())
                        }
                        frozen_dates.append(new_frozen)
                        added_count += 1
                
                st.session_state["frozen_dates"] = frozen_dates
                
                if save_frozen_dates(frozen_dates):
                    if added_count > 0:
                        st.success(f"✅ {added_count} date(s) successfully frozen!")
                    if existing_count > 0:
                        st.warning(f"⚠️ {existing_count} date(s) were already frozen")
                    st.balloons()
                    st.rerun()
            else:
                st.warning("⚠️ Please provide a reason for freezing!")
        
        st.markdown("---")
        
        # List of frozen dates
        st.markdown("#### 📋 Currently Frozen Dates")
        
        frozen_dates = st.session_state["frozen_dates"]
        
        if not frozen_dates:
            st.info("📝 No dates are currently frozen")
        else:
            # Sort by date
            sorted_frozen = sorted(frozen_dates, key=lambda x: x.get("date", ""), reverse=True)
            
            st.info(f"🔒 **{len(sorted_frozen)}** dates currently frozen")
            
            # Search/filter
            col_search1, col_search2 = st.columns(2)
            with col_search1:
                search_frozen_date = st.text_input("🔍 Search Date", key="search_frozen_date", placeholder="YYYY-MM-DD")
            with col_search2:
                show_past = st.checkbox("Show Past Dates", value=False, key="show_past_frozen")
            
            # Filter
            filtered_frozen = sorted_frozen
            if search_frozen_date:
                filtered_frozen = [f for f in filtered_frozen if search_frozen_date in f.get("date", "")]
            
            if not show_past:
                today = str(datetime.date.today())
                filtered_frozen = [f for f in filtered_frozen if f.get("date", "") >= today]
            
            st.caption(f"Showing {len(filtered_frozen)} of {len(sorted_frozen)} frozen dates")
            
            # Display frozen dates
            for idx, frozen in enumerate(filtered_frozen):
                date_str = frozen.get("date", "Unknown")
                reason = frozen.get("reason", "-")
                frozen_by = frozen.get("frozen_by", "Owner")
                frozen_at = frozen.get("frozen_at", "-")
                
                # Check if past date
                try:
                    frozen_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    is_past = frozen_date < datetime.date.today()
                except:
                    is_past = False
                
                # Card styling
                if is_past:
                    card_style = "background: #374151; border: 1px solid #6B7280; border-radius: 8px; padding: 15px; margin: 8px 0;"
                    date_badge = f"🕐 <span style='background: #6B7280; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85em;'>{date_str}</span>"
                else:
                    card_style = "background: #1E3A8A; border: 2px solid #3B82F6; border-radius: 8px; padding: 15px; margin: 8px 0;"
                    date_badge = f"❄️ <span style='background: #3B82F6; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 0.9em;'>{date_str}</span>"
                
                st.markdown(f"<div style='{card_style}'>", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown(date_badge, unsafe_allow_html=True)
                    st.caption(f"**Reason:** {reason}")
                
                with col2:
                    st.caption(f"**Frozen By:** {frozen_by}")
                    st.caption(f"**Frozen At:** {frozen_at}")
                
                with col3:
                    if st.button("🔓 Unfreeze", key=f"unfreeze_date_{idx}", use_container_width=True, type="secondary"):
                        # Find and remove from list
                        frozen_dates_list = st.session_state["frozen_dates"]
                        frozen_dates_list = [f for f in frozen_dates_list if f.get("date") != date_str]
                        
                        st.session_state["frozen_dates"] = frozen_dates_list
                        
                        if save_frozen_dates(frozen_dates_list):
                            st.success(f"✅ Date {date_str} unfrozen!")
                            st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📊 Frozen Dates Report")
        
        frozen_dates = st.session_state["frozen_dates"]
        
        if not frozen_dates:
            st.info("📝 No frozen dates in database")
        else:
            # Metrics
            col_met1, col_met2, col_met3, col_met4 = st.columns(4)
            
            total_frozen = len(frozen_dates)
            today = datetime.date.today()
            
            future_frozen = len([f for f in frozen_dates if datetime.datetime.strptime(f.get("date", "2000-01-01"), "%Y-%m-%d").date() >= today])
            past_frozen = total_frozen - future_frozen
            
            # Count orders that WOULD BE affected (orders with those dates)
            df = st.session_state["data_produksi"]
            affected_orders = 0
            
            if not df.empty:
                frozen_date_strs = [f.get("date") for f in frozen_dates]
                for idx, row in df.iterrows():
                    order_date_str = str(row["Order Date"])
                    due_date_str = str(row["Due Date"])
                    
                    if order_date_str in frozen_date_strs or due_date_str in frozen_date_strs:
                        affected_orders += 1
            
            col_met1.metric("Total Frozen Dates", total_frozen)
            col_met2.metric("Future Dates", future_frozen)
            col_met3.metric("Past Dates", past_frozen)
            col_met4.metric("Orders with Frozen Dates", affected_orders)
            
            st.caption("💡 Orders with frozen dates can still be updated/edited, but NO NEW orders can be created with these dates")
            
            st.markdown("---")
            
            # Table view
            report_data = []
            for frozen in frozen_dates:
                report_data.append({
                    "Date": frozen.get("date", "-"),
                    "Reason": frozen.get("reason", "-"),
                    "Frozen By": frozen.get("frozen_by", "-"),
                    "Frozen At": frozen.get("frozen_at", "-")
                })
            
            report_df = pd.DataFrame(report_data)
            report_df = report_df.sort_values("Date", ascending=False)
            
            st.dataframe(report_df, use_container_width=True, hide_index=True)
            
            # Export
            csv_frozen = report_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Frozen Dates Report",
                data=csv_frozen,
                file_name=f"frozen_dates_report_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.markdown("---")
            
            # Bulk unfreeze
            st.markdown("#### 🗑️ Bulk Operations")
            
            col_bulk1, col_bulk2 = st.columns(2)
            
            with col_bulk1:
                if st.button("🗑️ Clear All Past Dates", use_container_width=True, type="secondary"):
                    if st.session_state.get("confirm_clear_past", False):
                        frozen_dates_list = st.session_state["frozen_dates"]
                        today_str = str(datetime.date.today())
                        
                        frozen_dates_list = [f for f in frozen_dates_list if f.get("date", "") >= today_str]
                        
                        st.session_state["frozen_dates"] = frozen_dates_list
                        
                        if save_frozen_dates(frozen_dates_list):
                            st.success("✅ All past frozen dates cleared!")
                            del st.session_state["confirm_clear_past"]
                            st.rerun()
                    else:
                        st.session_state["confirm_clear_past"] = True
                        st.warning("⚠️ Click again to confirm!")
                        st.rerun()
            
            with col_bulk2:
                if st.button("🗑️ Clear ALL Frozen Dates", use_container_width=True, type="secondary"):
                    if st.session_state.get("confirm_clear_all", False):
                        st.session_state["frozen_dates"] = []
                        
                        if save_frozen_dates([]):
                            st.success("✅ All frozen dates cleared!")
                            del st.session_state["confirm_clear_all"]
                            st.rerun()
                    else:
                        st.session_state["confirm_clear_all"] = True
                        st.warning("⚠️ Click again to confirm!")
                        st.rerun()
st.markdown("---")
st.caption(f"© 2025 PPIC-DSS System | Enhanced Database Management v12.0")
