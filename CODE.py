import streamlit as st
import pandas as pd
import datetime
import json
import os
import plotly.express as px
import plotly.figure_factory as ff
from streamlit.components.v1 import html

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
    
    # Non-form inputs for real-time calculation
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
        
        uploaded_image = st.file_uploader("Upload Gambar Produk", 
                                         type=['jpg', 'jpeg', 'png'], 
                                         key="form_image")
    
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
        
        # Real-time CBM calculation
        cbm_per_pcs = calculate_cbm(pack_p, pack_l, pack_t)
        if cbm_per_pcs > 0:
            st.success(f"📦 CBM per Pcs: **{cbm_per_pcs:.6f} m³**")
        else:
            st.info(f"📦 CBM per Pcs: 0.000000 m³")
        
        keterangan = st.text_area("Keterangan Tambahan", 
                                 placeholder="Catatan khusus...", 
                                 height=80, 
                                 key="form_notes")
    
    # Add product button (outside form to prevent Enter submission)
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
                    st.warning("⚠️ Harap pilih buyer dan tambahkan minimal 1 produk!")
    
    else:
        st.info("📝 Belum ada produk yang ditambahkan. Silakan tambah produk menggunakan form di atas.")

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
    @media (max-width: 767px) {
        [data-testid="stSidebar"] {
            position: fixed;
            z-index: 999;
            width: 80vw !important;
        }
        .main .block-container {
            padding: 1rem 0.5rem !important;
        }
        h1 { font-size: 1.5rem !important; }
        .stButton button { width: 100% !important; }
    }
    @media (min-width: 768px) and (max-width: 1023px) {
        .main .block-container {
            padding: 1.5rem 1rem !important;
        }
    }
    .procurement-table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
    }
    .procurement-table th {
        background-color: #1E3A8A;
        color: white;
        padding: 12px;
        text-align: left;
        border: 1px solid #374151;
    }
    .procurement-table td {
        padding: 10px;
        border: 1px solid #374151;
    }
    .procurement-table input, .procurement-table select {
        width: 100%;
        padding: 8px;
        background-color: #1F2937;
        border: 1px solid #374151;
        color: white;
        border-radius: 4px;
    }
    /* Prevent form submission on Enter key */
    div[data-testid="stForm"] input {
        /* Allow Enter key to move to next field */
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
        "Prioritas", "Progress", "Proses Saat Ini", "Keterangan",
        "Tracking", "History", "Material", "Finishing", "Description",
        "Product Size P", "Product Size L", "Product Size T",
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
    
    # Updated status: On Going and Done only
    # On Going: Progress > 0% and < 100%
    # Done: Progress = 100%
    if progress_pct >= 100:
        return "Done"
    elif progress_pct > 0:
        return "On Going"
    else:
        return "On Going"  # Even 0% is considered On Going (Pre Order stage)

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

# Initialize dimension states for real-time CBM calculation
if "pack_p_val" not in st.session_state:
    st.session_state["pack_p_val"] = None
if "pack_l_val" not in st.session_state:
    st.session_state["pack_l_val"] = None
if "pack_t_val" not in st.session_state:
    st.session_state["pack_t_val"] = None

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
        
        # ===== SECTION 1: KEY METRICS =====
        st.markdown("### 📈 Key Performance Metrics")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_orders = len(df)
        ongoing = len(df[df["Tracking Status"] == "On Going"])
        done = len(df[df["Tracking Status"] == "Done"])
        total_qty = df["Qty"].sum()
        total_buyers = df["Buyer"].nunique()
        
        col1.metric("📦 Total Orders", total_orders, help="Total semua order di sistem")
        col2.metric("🔄 On Going", ongoing, help="Order yang sedang dalam proses")
        col3.metric("✅ Done", done, help="Order yang sudah selesai dikirim")
        col4.metric("📊 Total Qty", f"{total_qty:,} pcs", help="Total quantity semua produk")
        col5.metric("👥 Active Buyers", total_buyers, help="Jumlah buyer aktif")
        
        # Completion rate
        completion_rate = (done / total_orders * 100) if total_orders > 0 else 0
        st.progress(completion_rate / 100)
        st.caption(f"🎯 Completion Rate: {completion_rate:.1f}%")
        
        st.markdown("---")
        
        # ===== SECTION 2: CALENDAR & CHARTS =====
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown("### 📅 Production Calendar - Due Dates")
            
            # Prepare calendar data
            today = datetime.date.today()
            current_month = today.month
            current_year = today.year
            
            # Month selector
            col_month, col_year = st.columns(2)
            with col_month:
                months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                         "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                selected_month = st.selectbox("Bulan", months, index=current_month - 1, key="cal_month")
                month_num = months.index(selected_month) + 1
            
            with col_year:
                years = list(range(current_year - 1, current_year + 3))
                selected_year = st.selectbox("Tahun", years, index=1, key="cal_year")
            
            # Filter orders by selected month/year - ensure datetime type
            df_copy = df.copy()
            # Convert Due Date to datetime for filtering
            df_copy['Due Date'] = pd.to_datetime(df_copy['Due Date'])
            df_month = df_copy[(df_copy['Due Date'].dt.month == month_num) & 
                         (df_copy['Due Date'].dt.year == selected_year)]
            
            # Always show calendar, with or without orders
            if not df_month.empty:
                # Group by buyer and date
                st.markdown(f"**📌 {len(df_month)} orders dari {df_month['Buyer'].nunique()} buyer di bulan ini**")
            else:
                st.markdown(f"**📅 Kalender {selected_month} {selected_year}**")
                st.info("Tidak ada order yang jatuh tempo di bulan ini")
            
            # Create calendar view (always show)
            import calendar
            cal = calendar.monthcalendar(selected_year, month_num)
            
            # Create header
            days = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
            header_cols = st.columns(7)
            for i, day in enumerate(days):
                header_cols[i].markdown(f"**{day}**")
            
            # Create calendar grid
            for week in cal:
                week_cols = st.columns(7)
                for i, day in enumerate(week):
                    if day == 0:
                        week_cols[i].markdown("")
                    else:
                        date_obj = datetime.date(selected_year, month_num, day)
                        
                        # Check if there are orders on this date (only if df_month is not empty)
                        if not df_month.empty:
                            orders_on_date = df_month[df_month['Due Date'].dt.date == date_obj]
                            
                            if len(orders_on_date) > 0:
                                buyer_count = orders_on_date['Buyer'].nunique()
                                order_count = len(orders_on_date)
                                
                                # Determine color based on status
                                done_count = len(orders_on_date[orders_on_date['Tracking Status'] == 'Done'])
                                if done_count == order_count:
                                    bg_color = "#10B981"  # Green - all done
                                elif date_obj < today:
                                    bg_color = "#EF4444"  # Red - overdue
                                elif date_obj == today:
                                    bg_color = "#F59E0B"  # Orange - today
                                else:
                                    bg_color = "#3B82F6"  # Blue - upcoming
                                
                                week_cols[i].markdown(f"""
                                <div style='background-color: {bg_color}; padding: 8px; border-radius: 5px; text-align: center;'>
                                    <strong style='color: white; font-size: 16px;'>{day}</strong><br>
                                    <span style='color: white; font-size: 11px;'>{buyer_count} buyer</span><br>
                                    <span style='color: white; font-size: 11px;'>{order_count} order</span>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                # Regular day - no orders
                                if date_obj == today:
                                    week_cols[i].markdown(f"<div style='padding: 8px; text-align: center; border: 2px solid #3B82F6; border-radius: 5px;'><strong>{day}</strong></div>", unsafe_allow_html=True)
                                else:
                                    week_cols[i].markdown(f"<div style='padding: 8px; text-align: center;'>{day}</div>", unsafe_allow_html=True)
                        else:
                            # No orders in this month - show regular calendar
                            if date_obj == today:
                                week_cols[i].markdown(f"<div style='padding: 8px; text-align: center; border: 2px solid #3B82F6; border-radius: 5px;'><strong>{day}</strong></div>", unsafe_allow_html=True)
                            else:
                                week_cols[i].markdown(f"<div style='padding: 8px; text-align: center;'>{day}</div>", unsafe_allow_html=True)
            
            # Legend (only show if there are orders)
            if not df_month.empty:
                st.markdown("---")
                leg_col1, leg_col2, leg_col3, leg_col4 = st.columns(4)
                leg_col1.markdown("🔵 **Upcoming** - Orders mendatang")
                leg_col2.markdown("🟠 **Today** - Jatuh tempo hari ini")
                leg_col3.markdown("🔴 **Overdue** - Terlambat")
                leg_col4.markdown("🟢 **Done** - Sudah selesai")
            
            # Orders detail for selected month - GROUP BY BUYER
            if not df_month.empty:
                st.markdown("---")
                st.markdown("### 📋 Detail Orders Bulan Ini (By Buyer)")
                
                # Sort by due date
                df_month_sorted = df_month.sort_values('Due Date')
                
                # Group by buyer
                buyers_in_month = df_month_sorted['Buyer'].unique()
                
                for buyer in sorted(buyers_in_month):
                    buyer_orders = df_month_sorted[df_month_sorted['Buyer'] == buyer]
                    total_buyer_orders = len(buyer_orders)
                    total_buyer_qty = buyer_orders['Qty'].sum()
                    
                    with st.expander(f"👤 **{buyer}** ({total_buyer_orders} orders, {total_buyer_qty} pcs)", expanded=False):
                        for idx, row in buyer_orders.iterrows():
                            # FIX: Convert Timestamp to date for comparison
                            due_date = row['Due Date'].date() if isinstance(row['Due Date'], pd.Timestamp) else row['Due Date']
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
                            <div style='background-color: #1F2937; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #3B82F6;'>
                                <strong style='color: #60A5FA;'>{row['Produk']}</strong> ({row['Qty']} pcs)<br>
                                <span style='color: #D1D5DB;'>Order ID: {row['Order ID']}</span><br>
                                <span style='color: #D1D5DB;'>Due: {due_date.strftime('%d %b %Y')} - {date_label}</span><br>
                                <span style='color: #D1D5DB;'>Progress: {row['Progress']} | Status: {row['Tracking Status']}</span>
                            </div>
                            """, unsafe_allow_html=True)
        
        with col_right:
            st.markdown("### 📊 Status Distribution")
            
            # Status pie chart
            status_dist = df["Tracking Status"].value_counts()
            fig_status = px.pie(
                values=status_dist.values, 
                names=status_dist.index,
                color_discrete_map={"On Going": "#3B82F6", "Done": "#10B981"},
                hole=0.4
            )
            fig_status.update_traces(textposition='inside', textinfo='percent+label')
            fig_status.update_layout(showlegend=True, height=300)
            st.plotly_chart(fig_status, use_container_width=True)
            
            st.markdown("### 🎯 Priority Orders")
            priority_dist = df["Prioritas"].value_counts()
            fig_priority = px.bar(
                x=priority_dist.index, 
                y=priority_dist.values,
                color=priority_dist.index,
                color_discrete_map={"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}
            )
            fig_priority.update_layout(showlegend=False, height=300, xaxis_title="", yaxis_title="Jumlah")
            st.plotly_chart(fig_priority, use_container_width=True)
        
        st.markdown("---")
        
        # ===== SECTION 3: PRODUCTION PROGRESS =====
        st.markdown("### 🏭 Production Progress by Stage")
        
        # Calculate qty at each stage
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
        
        # Create horizontal bar chart
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
            height=400
        )
        st.plotly_chart(fig_stages, use_container_width=True)
        
        st.markdown("---")
        
        # ===== SECTION 4: TOP PERFORMERS =====
        col_top1, col_top2 = st.columns(2)
        
        with col_top1:
            st.markdown("### 👑 Top 5 Buyers by Orders")
            buyer_stats = df.groupby("Buyer").agg({
                "Order ID": "count",
                "Qty": "sum"
            }).rename(columns={"Order ID": "Orders", "Qty": "Total Qty"})
            buyer_stats = buyer_stats.sort_values("Orders", ascending=False).head(5)
            
            for buyer, stats in buyer_stats.iterrows():
                st.markdown(f"""
                <div style='background-color: #1F2937; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #3B82F6;'>
                    <strong style='color: #60A5FA;'>{buyer}</strong><br>
                    <span style='color: #D1D5DB;'>Orders: {stats['Orders']} | Qty: {stats['Total Qty']:,} pcs</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col_top2:
            st.markdown("### 🏆 Top 5 Products by Quantity")
            product_stats = df.groupby("Produk").agg({
                "Order ID": "count",
                "Qty": "sum"
            }).rename(columns={"Order ID": "Orders"})
            product_stats = product_stats.sort_values("Qty", ascending=False).head(5)
            
            for product, stats in product_stats.iterrows():
                st.markdown(f"""
                <div style='background-color: #1F2937; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #10B981;'>
                    <strong style='color: #34D399;'>{product}</strong><br>
                    <span style='color: #D1D5DB;'>Orders: {stats['Orders']} | Qty: {stats['Qty']:,} pcs</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ===== SECTION 5: RECENT ACTIVITY =====
        st.markdown("### 🕒 Recent Orders (Last 10)")
        recent_df = df.sort_values("Order Date", ascending=False).head(10)
        
        # Display as cards
        for idx, row in recent_df.iterrows():
            col_card1, col_card2, col_card3, col_card4 = st.columns([2, 2, 1, 1])
            
            with col_card1:
                st.markdown(f"**{row['Order ID']}**")
                st.caption(f"{row['Buyer']} | {row['Produk']}")
            
            with col_card2:
                st.caption(f"Order: {row['Order Date']}")
                st.caption(f"Due: {row['Due Date']}")
            
            with col_card3:
                progress_val = int(row['Progress'].rstrip('%'))
                st.progress(progress_val / 100)
                st.caption(f"{row['Progress']}")
            
            with col_card4:
                if row['Tracking Status'] == 'Done':
                    st.success("✅ Done")
                else:
                    st.info("🔄 On Going")
            
            st.divider()
        
        st.markdown("---")
        
        # ===== SECTION 6: ALERTS & NOTIFICATIONS =====
        st.markdown("### ⚠️ Alerts & Notifications")
        
        # Check for overdue orders - use date objects consistently
        today = datetime.date.today()
        
        # Create a copy and ensure Due Date is date type
        df_alerts = df.copy()
        df_alerts['Due Date'] = pd.to_datetime(df_alerts['Due Date']).dt.date
        
        overdue_orders = df_alerts[(df_alerts['Due Date'] < today) & (df_alerts['Tracking Status'] != 'Done')]
        
        if len(overdue_orders) > 0:
            st.error(f"🚨 **{len(overdue_orders)} orders terlambat!**")
            for idx, row in overdue_orders.iterrows():
                days_late = (today - row['Due Date']).days
                st.markdown(f"- {row['Order ID']} ({row['Buyer']}) - Terlambat {days_late} hari")
        
        # Check for due today
        due_today = df_alerts[(df_alerts['Due Date'] == today) & (df_alerts['Tracking Status'] != 'Done')]
        if len(due_today) > 0:
            st.warning(f"⏰ **{len(due_today)} orders jatuh tempo hari ini!**")
            for idx, row in due_today.iterrows():
                st.markdown(f"- {row['Order ID']} ({row['Buyer']}) - Progress: {row['Progress']}")
        
        # Check for due within 3 days
        three_days_later = today + datetime.timedelta(days=3)
        due_soon = df_alerts[(df_alerts['Due Date'] > today) & (df_alerts['Due Date'] <= three_days_later) & (df_alerts['Tracking Status'] != 'Done')]
        if len(due_soon) > 0:
            st.info(f"📅 **{len(due_soon)} orders akan jatuh tempo dalam 3 hari**")
        
        if len(overdue_orders) == 0 and len(due_today) == 0 and len(due_soon) == 0:
            st.success("✅ Semua order dalam kondisi baik!")
        
    else:
        st.info("📝 Belum ada data. Silakan input pesanan baru.")

# ===
