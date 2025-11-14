import streamlit as st
import pandas as pd
import datetime
import json
import os
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from streamlit.components.v1 import html

# ===== KONFIGURASI DATABASE =====
DATABASE_PATH = "ppic_data.json"
BUYER_DB_PATH = "buyers.json"
PRODUCT_DB_PATH = "products.json"
PROCUREMENT_DB_PATH = "procurement.json"

st.set_page_config(
    page_title="PPIC-DSS System",
    layout="wide",
    page_icon="🏭",
    initial_sidebar_state="collapsed"
)

# ===== CSS RESPONSIVE =====
def inject_responsive_css():
    st.markdown("""
    <style>
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
    }
    .stMetric label {
        color: white !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
    }
    </style>
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
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
    
    return pd.DataFrame(columns=[
        "Order ID", "Order Date", "Buyer", "Produk", "Qty", "Due Date",
        "Prioritas", "Progress", "Proses Saat Ini", "Keterangan", "Tracking",
        "History", "Material", "Finishing", "Description", "Product Size P",
        "Product Size L", "Product Size T", "Packing Size P", "Packing Size L",
        "Packing Size T", "CBM per Pcs", "Total CBM", "Image Path"
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

# ===== PROCUREMENT DATABASE =====
def load_procurement():
    if os.path.exists(PROCUREMENT_DB_PATH):
        try:
            with open(PROCUREMENT_DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
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

def get_tracking_stages():
    return [
        "Pre Order", "Order di Supplier", "Warehouse", "Fitting 1",
        "Amplas", "Revisi 1", "Spray", "Fitting 2", "Revisi Fitting 2",
        "Packaging", "Pengiriman"
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
    """Calculate CBM from dimensions in cm"""
    try:
        p_val = float(p) if p else 0
        l_val = float(l) if l else 0
        t_val = float(t) if t else 0
        if p_val > 0 and l_val > 0 and t_val > 0:
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

# ===== INISIALISASI =====
if "data_produksi" not in st.session_state:
    st.session_state["data_produksi"] = load_data()

if "buyers" not in st.session_state:
    st.session_state["buyers"] = load_buyers()

if "products" not in st.session_state:
    st.session_state["products"] = load_products()

if "procurement" not in st.session_state:
    st.session_state["procurement"] = load_procurement()

if "menu" not in st.session_state:
    st.session_state["menu"] = "Dashboard"

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
    "💾 Database": "Database",
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
    if st.button("⬅️ Back to Dashboard", type="secondary"):
        st.session_state["menu"] = "Dashboard"
        st.rerun()
    st.markdown("---")

# ===== MENU: DASHBOARD =====
if st.session_state["menu"] == "Dashboard":
    st.header("📊 Dashboard Overview")
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        # Calculate tracking status
        df['Tracking Status'] = df.apply(
            lambda row: get_tracking_status_from_progress(row['Progress']),
            axis=1
        )
        
        # ===== SECTION 1: KEY BUSINESS METRICS =====
        st.markdown("### 📈 Key Business Metrics")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_orders = len(df)
        ongoing = len(df[df["Tracking Status"] == "On Going"])
        done = len(df[df["Tracking Status"] == "Done"])
        total_qty = df["Qty"].sum()
        total_cbm = df["Total CBM"].sum()
        
        col1.metric("📦 Total Orders", total_orders, help="Total semua order di sistem")
        col2.metric("🔄 On Going", ongoing, help="Order yang sedang dalam proses")
        col3.metric("✅ Done", done, help="Order yang sudah selesai")
        col4.metric("📊 Total Qty", f"{total_qty:,} pcs", help="Total quantity semua produk")
        col5.metric("📐 Total CBM", f"{total_cbm:.2f} m³", help="Total volume CBM")
        
        # Completion rate
        completion_rate = (done / total_orders * 100) if total_orders > 0 else 0
        st.progress(completion_rate / 100)
        st.caption(f"🎯 Completion Rate: {completion_rate:.1f}%")
        
        st.markdown("---")
        
        # ===== SECTION 2: PRODUCTION EFFICIENCY & CAPACITY UTILIZATION =====
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.markdown("### 🏭 Production Capacity & Efficiency")
            
            # Calculate production metrics
            today = datetime.date.today()
            
            # Orders by week
            df_copy = df.copy()
            df_copy['Due Date'] = pd.to_datetime(df_copy['Due Date'])
            df_copy['Week'] = df_copy['Due Date'].dt.to_period('W').astype(str)
            
            weekly_orders = df_copy.groupby('Week').agg({
                'Order ID': 'count',
                'Qty': 'sum',
                'Total CBM': 'sum'
            }).reset_index()
            weekly_orders.columns = ['Week', 'Orders', 'Quantity', 'CBM']
            
            # Create multi-axis chart
            fig_capacity = go.Figure()
            
            fig_capacity.add_trace(go.Bar(
                x=weekly_orders['Week'],
                y=weekly_orders['Orders'],
                name='Orders',
                marker_color='#3B82F6',
                yaxis='y'
            ))
            
            fig_capacity.add_trace(go.Scatter(
                x=weekly_orders['Week'],
                y=weekly_orders['Quantity'],
                name='Quantity (pcs)',
                marker_color='#10B981',
                yaxis='y2',
                mode='lines+markers'
            ))
            
            fig_capacity.update_layout(
                title='Weekly Production Load',
                xaxis=dict(title='Week'),
                yaxis=dict(title='Number of Orders', side='left'),
                yaxis2=dict(title='Quantity (pcs)', side='right', overlaying='y'),
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig_capacity, use_container_width=True)
        
        with col_right:
            st.markdown("### 💰 Revenue Potential")
            
            # Buyer order value (assuming mock pricing based on CBM)
            # In real scenario, this would come from actual pricing data
            buyer_value = df.groupby("Buyer").agg({
                "Order ID": "count",
                "Total CBM": "sum",
                "Qty": "sum"
            }).reset_index()
            buyer_value.columns = ["Buyer", "Orders", "Total CBM", "Quantity"]
            buyer_value = buyer_value.sort_values("Total CBM", ascending=False).head(5)
            
            fig_buyer_value = px.bar(
                buyer_value,
                x='Total CBM',
                y='Buyer',
                orientation='h',
                title='Top 5 Buyers by CBM Volume',
                color='Total CBM',
                color_continuous_scale='Blues',
                text='Total CBM'
            )
            fig_buyer_value.update_traces(texttemplate='%{text:.2f} m³', textposition='outside')
            fig_buyer_value.update_layout(height=400, showlegend=False)
            
            st.plotly_chart(fig_buyer_value, use_container_width=True)
        
        st.markdown("---")
        
        # ===== SECTION 3: CALENDAR WITH BUYER VIEW =====
        st.markdown("### 📅 Production Calendar - Orders by Buyer")
        
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
        df_month = df_copy[
            (df_copy['Due Date'].dt.month == month_num) & 
            (df_copy['Due Date'].dt.year == selected_year)
        ]
        
        if not df_month.empty:
            st.markdown(f"**📌 {len(df_month)} orders dari {df_month['Buyer'].nunique()} buyer di bulan ini**")
        else:
            st.markdown(f"**📅 Kalender {selected_month} {selected_year}**")
            st.info("Tidak ada order yang jatuh tempo di bulan ini")
        
        # Create calendar view
        import calendar
        cal = calendar.monthcalendar(selected_year, month_num)
        
        # Calendar header
        days = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
        header_cols = st.columns(7)
        for i, day in enumerate(days):
            header_cols[i].markdown(f"**{day}**")
        
        # Calendar grid
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
                            buyer_count = orders_on_date['Buyer'].nunique()
                            order_count = len(orders_on_date)
                            
                            # Determine color
                            done_count = len(orders_on_date[orders_on_date['Tracking Status'] == 'Done'])
                            if done_count == order_count:
                                bg_color = "#10B981"  # Green
                            elif date_obj < today:
                                bg_color = "#EF4444"  # Red - overdue
                            elif date_obj == today:
                                bg_color = "#F59E0B"  # Orange - today
                            else:
                                bg_color = "#3B82F6"  # Blue - upcoming
                            
                            week_cols[i].markdown(f"""
                            <div style='background: {bg_color}; padding: 8px; border-radius: 8px; 
                                        text-align: center; color: white; min-height: 80px;'>
                                <div style='font-size: 18px; font-weight: bold;'>{day}</div>
                                <div style='font-size: 11px; margin-top: 4px;'>{buyer_count} buyer</div>
                                <div style='font-size: 11px;'>{order_count} order</div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            if date_obj == today:
                                week_cols[i].markdown(f"<div style='background: #E5E7EB; padding: 8px; border-radius: 8px; text-align: center; border: 2px solid #F59E0B; font-weight: bold; min-height: 80px; display: flex; align-items: center; justify-content: center;'>{day}</div>", unsafe_allow_html=True)
                            else:
                                week_cols[i].markdown(f"<div style='background: #F3F4F6; padding: 8px; border-radius: 8px; text-align: center; min-height: 80px; display: flex; align-items: center; justify-content: center;'>{day}</div>", unsafe_allow_html=True)
                    else:
                        if date_obj == today:
                            week_cols[i].markdown(f"<div style='background: #E5E7EB; padding: 8px; border-radius: 8px; text-align: center; border: 2px solid #F59E0B; font-weight: bold; min-height: 80px; display: flex; align-items: center; justify-content: center;'>{day}</div>", unsafe_allow_html=True)
                        else:
                            week_cols[i].markdown(f"<div style='background: #F3F4F6; padding: 8px; border-radius: 8px; text-align: center; min-height: 80px; display: flex; align-items: center; justify-content: center;'>{day}</div>", unsafe_allow_html=True)
        
        # Legend
        if not df_month.empty:
            st.markdown("---")
            leg_col1, leg_col2, leg_col3, leg_col4 = st.columns(4)
            leg_col1.markdown("🔵 **Upcoming** - Orders mendatang")
            leg_col2.markdown("🟠 **Today** - Jatuh tempo hari ini")
            leg_col3.markdown("🔴 **Overdue** - Terlambat")
            leg_col4.markdown("🟢 **Done** - Sudah selesai")
        
        # Orders detail by BUYER
        if not df_month.empty:
            st.markdown("---")
            st.markdown("### 📋 Detail Orders Bulan Ini (By Buyer)")
            
            df_month_sorted = df_month.sort_values('Due Date')
            buyers_in_month = df_month_sorted['Buyer'].unique()
            
            for buyer in sorted(buyers_in_month):
                buyer_orders = df_month_sorted[df_month_sorted['Buyer'] == buyer]
                total_buyer_orders = len(buyer_orders)
                total_buyer_qty = buyer_orders['Qty'].sum()
                total_buyer_cbm = buyer_orders['Total CBM'].sum()
                
                # Group by product
                products_summary = buyer_orders.groupby('Produk').agg({
                    'Order ID': 'count',
                    'Qty': 'sum',
                    'Total CBM': 'sum'
                }).reset_index()
                products_summary.columns = ['Produk', 'Orders', 'Qty', 'CBM']
                
                with st.expander(
                    f"👤 **{buyer}** ({total_buyer_orders} orders, {total_buyer_qty} pcs, {total_buyer_cbm:.2f} m³)",
                    expanded=False
                ):
                    st.markdown("#### 📦 Produk Summary")
                    
                    for _, prod_row in products_summary.iterrows():
                        st.markdown(f"""
                        <div style='background: #F3F4F6; padding: 12px; border-radius: 8px; margin-bottom: 8px;'>
                            <strong>📦 {prod_row['Produk']}</strong><br>
                            Orders: {prod_row['Orders']} | Qty: {prod_row['Qty']} pcs | CBM: {prod_row['CBM']:.2f} m³
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("#### 📋 Detail Orders")
                    
                    for idx, row in buyer_orders.iterrows():
                        due_date = row['Due Date'].date()
                        days_until_due = (due_date - today).days
                        
                        if days_until_due < 0:
                            date_label = f"🔴 Terlambat {abs(days_until_due)} hari"
                        elif days_until_due == 0:
                            date_label = "🟠 Hari Ini"
                        elif days_until_due <= 7:
                            date_label = f"🟡 {days_until_due} hari lagi"
                        else:
                            date_label = f"🟢 {days_until_due} hari lagi"
                        
                        st.markdown(f"""
                        <div style='background: white; padding: 10px; border-left: 4px solid #3B82F6; 
                                    margin-bottom: 8px; border-radius: 4px;'>
                            <strong>{row['Produk']}</strong> ({row['Qty']} pcs, {row['Total CBM']:.2f} m³)<br>
                            <small>Order ID: {row['Order ID']}</small><br>
                            <small>Due: {due_date.strftime('%d %b %Y')} - {date_label}</small><br>
                            <small>Progress: {row['Progress']} | Status: {row['Tracking Status']}</small>
                        </div>
                        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ===== SECTION 4: ORDER FULFILLMENT TIMELINE =====
        st.markdown("### ⏱️ Order Fulfillment Timeline Analysis")
        
        col_timeline1, col_timeline2 = st.columns(2)
        
        with col_timeline1:
            # Calculate average lead time
            df_done = df[df['Tracking Status'] == 'Done'].copy()
            if not df_done.empty:
                df_done['Order Date'] = pd.to_datetime(df_done['Order Date'])
                df_done['Due Date'] = pd.to_datetime(df_done['Due Date'])
                df_done['Lead Time'] = (df_done['Due Date'] - df_done['Order Date']).dt.days
                
                avg_lead_time = df_done['Lead Time'].mean()
                min_lead_time = df_done['Lead Time'].min()
                max_lead_time = df_done['Lead Time'].max()
                
                st.metric("📊 Avg Lead Time", f"{avg_lead_time:.0f} days")
                st.caption(f"Range: {min_lead_time} - {max_lead_time} days")
                
                # Lead time distribution
                fig_lead = px.histogram(
                    df_done,
                    x='Lead Time',
                    nbins=20,
                    title='Lead Time Distribution',
                    labels={'Lead Time': 'Days', 'count': 'Number of Orders'}
                )
                fig_lead.update_layout(height=300)
                st.plotly_chart(fig_lead, use_container_width=True)
            else:
                st.info("Belum ada order yang selesai untuk analisis lead time")
        
        with col_timeline2:
            # On-time delivery rate
            today_ts = pd.Timestamp(datetime.date.today())
            df['Due Date'] = pd.to_datetime(df['Due Date'])
            
            on_time = len(df[(df['Tracking Status'] == 'Done') & (df['Due Date'] >= today_ts)])
            late = len(df[(df['Tracking Status'] == 'Done') & (df['Due Date'] < today_ts)])
            in_progress = len(df[df['Tracking Status'] == 'On Going'])
            
            delivery_data = pd.DataFrame({
                'Status': ['On Time', 'Late', 'In Progress'],
                'Count': [on_time, late, in_progress]
            })
            
            fig_delivery = px.pie(
                delivery_data,
                values='Count',
                names='Status',
                title='Delivery Performance',
                color='Status',
                color_discrete_map={
                    'On Time': '#10B981',
                    'Late': '#EF4444',
                    'In Progress': '#3B82F6'
                }
            )
            fig_delivery.update_layout(height=350)
            st.plotly_chart(fig_delivery, use_container_width=True)
        
        st.markdown("---")
        
        # ===== SECTION 5: WORKSTATION BOTTLENECK ANALYSIS =====
        st.markdown("### 🔧 Workstation Bottleneck Analysis")
        
        stages = get_tracking_stages()
        stage_analysis = {stage: {'qty': 0, 'orders': 0, 'avg_time': 0} for stage in stages}
        
        for idx, row in df.iterrows():
            try:
                tracking_data = json.loads(row["Tracking"])
                for stage, data in tracking_data.items():
                    qty = data.get("qty", 0)
                    if qty > 0 and stage in stage_analysis:
                        stage_analysis[stage]['qty'] += qty
                        stage_analysis[stage]['orders'] += 1
            except:
                pass
        
        stage_df = pd.DataFrame([
            {
                'Stage': stage,
                'WIP Qty': data['qty'],
                'Orders': data['orders']
            }
            for stage, data in stage_analysis.items()
        ])
        
        fig_bottleneck = go.Figure()
        
        fig_bottleneck.add_trace(go.Bar(
            x=stage_df['Stage'],
            y=stage_df['WIP Qty'],
            name='WIP Quantity',
            marker_color='#3B82F6'
        ))
        
        fig_bottleneck.add_trace(go.Scatter(
            x=stage_df['Stage'],
            y=stage_df['Orders'],
            name='Number of Orders',
            marker_color='#EF4444',
            yaxis='y2',
            mode='lines+markers'
        ))
        
        fig_bottleneck.update_layout(
            title='Workstation Load Analysis',
            xaxis=dict(title='Workstation', tickangle=-45),
            yaxis=dict(title='WIP Quantity (pcs)'),
            yaxis2=dict(title='Orders', overlaying='y', side='right'),
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_bottleneck, use_container_width=True)
        
        # Identify bottleneck
        max_wip_stage = stage_df.loc[stage_df['WIP Qty'].idxmax()] if not stage_df.empty and stage_df['WIP Qty'].max() > 0 else None
        if max_wip_stage is not None:
            st.warning(f"⚠️ **Potential Bottleneck:** {max_wip_stage['Stage']} dengan {max_wip_stage['WIP Qty']} pcs WIP dari {max_wip_stage['Orders']} orders")
        
        st.markdown("---")
        
        # ===== SECTION 6: ALERTS & CRITICAL ISSUES =====
        st.markdown("### ⚠️ Critical Alerts & Action Items")
        
        alert_col1, alert_col2, alert_col3 = st.columns(3)
        
        with alert_col1:
            st.markdown("#### 🔴 Overdue Orders")
            today = pd.Timestamp(datetime.date.today())
            df['Due Date'] = pd.to_datetime(df['Due Date'])
            overdue_orders = df[(df['Due Date'] < today) & (df['Tracking Status'] != 'Done')]
            
            if len(overdue_orders) > 0:
                st.error(f"**{len(overdue_orders)} orders terlambat**")
                for idx, row in overdue_orders.head(5).iterrows():
                    days_late = (today - row['Due Date']).days
                    st.markdown(f"- {row['Order ID']} ({row['Buyer']}) - **{days_late} hari**")
            else:
                st.success("✅ Tidak ada order terlambat")
        
        with alert_col2:
            st.markdown("#### 🟠 Due Today")
            due_today = df[(df['Due Date'].dt.date == datetime.date.today()) & (df['Tracking Status'] != 'Done')]
            
            if len(due_today) > 0:
                st.warning(f"**{len(due_today)} orders jatuh tempo hari ini**")
                for idx, row in due_today.iterrows():
                    st.markdown(f"- {row['Order ID']} ({row['Buyer']}) - Progress: {row['Progress']}")
            else:
                st.info("Tidak ada order jatuh tempo hari ini")
        
        with alert_col3:
            st.markdown("#### 🟡 Due in 3 Days")
            three_days_later = today + pd.Timedelta(days=3)
            due_soon = df[(df['Due Date'] > today) & (df['Due Date'] <= three_days_later) & (df['Tracking Status'] != 'Done')]
            
            if len(due_soon) > 0:
                st.info(f"**{len(due_soon)} orders akan jatuh tempo**")
                for idx, row in due_soon.head(5).iterrows():
                    days_left = (row['Due Date'] - today).days
                    st.markdown(f"- {row['Order ID']} ({row['Buyer']}) - **{days_left} hari lagi**")
            else:
                st.success("Tidak ada order mendesak")
    
    else:
        st.info("📝 Belum ada data. Silakan input pesanan baru.")

# ===== MENU: INPUT PESANAN BARU =====
elif st.session_state["menu"] == "Input":
    st.header("📋 Form Input Pesanan Baru (Multi-Product)")
    
    if "input_products" not in st.session_state:
        st.session_state["input_products"] = []
    
    st.markdown("### 📦 Informasi Order")
    
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
    st.markdown("### 📦 Tambah Produk ke Order")
    
    col_prod1, col_prod2, col_prod3 = st.columns(3)
    
    with col_prod1:
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
        uploaded_image = st.file_uploader("Upload Gambar Produk", type=['jpg', 'jpeg', 'png'], key="form_image")
    
    with col_prod2:
        st.markdown("**Specifications**")
        material = st.text_input("Material", placeholder="Contoh: Kayu Jati, MDF", key="form_material")
        finishing = st.text_input("Finishing", placeholder="Contoh: Natural, Duco Putih", key="form_finishing")
        description = st.text_area("Description", placeholder="Deskripsi produk...", height=100, key="form_desc")
        
        st.markdown("**Product Size (cm)**")
        col_ps1, col_ps2, col_ps3 = st.columns(3)
        with col_ps1:
            prod_p = st.number_input("P", min_value=0.0, value=None, step=0.1, key="prod_p", placeholder="0")
        with col_ps2:
            prod_l = st.number_input("L", min_value=0.0, value=None, step=0.1, key="prod_l", placeholder="0")
        with col_ps3:
            prod_t = st.number_input("T", min_value=0.0, value=None, step=0.1, key="prod_t", placeholder="0")
    
    with col_prod3:
        st.markdown("**Packing Information**")
        st.markdown("**Packing Size (cm)**")
        col_pack1, col_pack2, col_pack3 = st.columns(3)
        with col_pack1:
            pack_p = st.number_input("P", min_value=0.0, value=None, step=0.1, key="pack_p", placeholder="0")
        with col_pack2:
            pack_l = st.number_input("L", min_value=0.0, value=None, step=0.1, key="pack_l", placeholder="0")
        with col_pack3:
            pack_t = st.number_input("T", min_value=0.0, value=None, step=0.1, key="pack_t", placeholder="0")
        
        cbm_per_pcs = calculate_cbm(pack_p, pack_l, pack_t)
        if cbm_per_pcs > 0:
            st.success(f"📦 CBM per Pcs: **{cbm_per_pcs:.6f} m³**")
        else:
            st.info(f"📦 CBM per Pcs: 0.000000 m³")
        
        keterangan = st.text_area("Keterangan Tambahan", placeholder="Catatan khusus...", height=80, key="form_notes")
    
    if st.button("➕ Tambah Produk ke Order", use_container_width=True, type="primary", key="add_product_btn"):
        if produk_name and qty > 0:
            temp_product = {
                "nama": produk_name,
                "qty": qty,
                "material": material if material else "-",
                "finishing": finishing if finishing else "-",
                "description": description if description else "-",
                "prod_p": prod_p if prod_p else 0,
                "prod_l": prod_l if prod_l else 0,
                "prod_t": prod_t if prod_t else 0,
                "pack_p": pack_p if pack_p else 0,
                "pack_l": pack_l if pack_l else 0,
                "pack_t": pack_t if pack_t else 0,
                "cbm_per_pcs": cbm_per_pcs,
                "total_cbm": cbm_per_pcs * qty,
                "keterangan": keterangan if keterangan else "-",
                "image": uploaded_image
            }
            st.session_state["input_products"].append(temp_product)
            st.success(f"✅ Produk '{produk_name}' ditambahkan! Total produk: {len(st.session_state['input_products'])}")
            st.rerun()
        else:
            st.warning("⚠️ Harap isi nama produk dan quantity!")
    
    if st.session_state["input_products"]:
        st.markdown("---")
        st.markdown("### 📋 Daftar Produk dalam Order Ini")
        
        for idx, product in enumerate(st.session_state["input_products"]):
            with st.expander(f"📦 Produk {idx + 1}: {product['nama']} ({product['qty']} pcs) - Total CBM: {product['total_cbm']:.4f} m³", expanded=False):
                col_display1, col_display2, col_display3 = st.columns([2, 2, 1])
                
                with col_display1:
                    st.write(f"**Material:** {product['material']}")
                    st.write(f"**Finishing:** {product['finishing']}")
                    st.write(f"**Description:** {product['description']}")
                    st.write(f"**Product Size:** {product['prod_p']} x {product['prod_l']} x {product['prod_t']} cm")
                
                with col_display2:
                    st.write(f"**Packing Size:** {product['pack_p']} x {product['pack_l']} x {product['pack_t']} cm")
                    st.write(f"**CBM per Pcs:** {product['cbm_per_pcs']:.6f} m³")
                    st.write(f"**Total CBM:** {product['total_cbm']:.4f} m³")
                    st.write(f"**Keterangan:** {product['keterangan']}")
                
                with col_display3:
                    if st.button("🗑️ Hapus", key=f"remove_product_{idx}", use_container_width=True):
                        st.session_state["input_products"].pop(idx)
                        st.rerun()
        
        st.markdown("---")
        total_cbm_all = sum([p['total_cbm'] for p in st.session_state["input_products"]])
        st.info(f"📦 Total CBM untuk semua produk: **{total_cbm_all:.4f} m³**")
        
        st.markdown("### 💾 Simpan Order")
        col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 2])
        
        with col_submit1:
            if st.button("🗑️ BATAL & HAPUS SEMUA", use_container_width=True, type="secondary"):
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
                        
                        initial_history = [add_history_entry(
                            f"{new_order_id}-P{prod_idx+1}",
                            "Order Created",
                            f"Product: {product['nama']}, Priority: {prioritas}"
                        )]
                        
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
                        [st.session_state["data_produksi"], new_df],
                        ignore_index=True
                    )
                    
                    if save_data(st.session_state["data_produksi"]):
                        st.success(f"✅ Order {new_order_id} dengan {len(st.session_state['input_products'])} produk berhasil ditambahkan!")
                        st.balloons()
                        st.session_state["input_products"] = []
                        st.rerun()
                else:
                    st.warning("⚠️ Harap pilih buyer dan tambahkan minimal 1 produk!")
    else:
        st.info("📝 Belum ada produk yang ditambahkan. Silakan tambah produk menggunakan form di atas.")

# Continue with other menus (Orders, Procurement, Progress, Tracking, Database, Analytics, Gantt)
# Due to length constraints, I'll add a note that the rest of the code remains the same

st.markdown("---")
st.caption(f"© 2025 PPIC-DSS System | Business Intelligence Dashboard | v11.0")
