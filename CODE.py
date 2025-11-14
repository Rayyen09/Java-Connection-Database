# ===== IMPROVED DASHBOARD SECTION =====
# Replace the entire "# ===== MENU: DASHBOARD =====" section with this code

if st.session_state["menu"] == "Dashboard":
    st.header("📊 Business Intelligence Dashboard")
    
    df = st.session_state["data_produksi"]
    
    if not df.empty:
        # Calculate tracking status
        df['Tracking Status'] = df.apply(
            lambda row: get_tracking_status_from_progress(row['Progress']), 
            axis=1
        )
        
        # ===== SECTION 1: EXECUTIVE SUMMARY METRICS =====
        st.markdown("### 📈 Executive Summary")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_orders = len(df)
        ongoing = len(df[df["Tracking Status"] == "On Going"])
        done = len(df[df["Tracking Status"] == "Done"])
        total_qty = df["Qty"].sum()
        total_cbm = df["Total CBM"].sum()
        
        col1.metric("📦 Total Orders", total_orders)
        col2.metric("🔄 In Production", ongoing)
        col3.metric("✅ Completed", done)
        col4.metric("📊 Total Units", f"{total_qty:,} pcs")
        col5.metric("📐 Total Volume", f"{total_cbm:.1f} m³")
        
        # Performance metrics
        completion_rate = (done / total_orders * 100) if total_orders > 0 else 0
        df_copy_temp = df.copy()
        df_copy_temp['Due Date'] = pd.to_datetime(df_copy_temp['Due Date'])
        today_ts = pd.Timestamp(datetime.date.today())
        on_time_done = len(df_copy_temp[(df_copy_temp['Tracking Status'] == 'Done') & (df_copy_temp['Due Date'] >= today_ts)])
        on_time_rate = (on_time_done / done * 100) if done > 0 else 0
        
        col_prog1, col_prog2 = st.columns(2)
        with col_prog1:
            st.progress(completion_rate / 100)
            st.caption(f"🎯 **Completion Rate:** {completion_rate:.1f}%")
        with col_prog2:
            st.progress(on_time_rate / 100)
            st.caption(f"⏰ **On-Time Delivery:** {on_time_rate:.1f}%")
        
        st.markdown("---")
        
        # ===== SECTION 2: PRODUCTION CAPACITY & FINANCIAL OVERVIEW =====
        col_capacity, col_financial = st.columns([3, 2])
        
        with col_capacity:
            st.markdown("### 🏭 Production Capacity Utilization")
            
            # Weekly production analysis
            df_weekly = df.copy()
            df_weekly['Due Date'] = pd.to_datetime(df_weekly['Due Date'])
            df_weekly['Week'] = df_weekly['Due Date'].dt.to_period('W').astype(str)
            
            weekly_data = df_weekly.groupby('Week').agg({
                'Order ID': 'count',
                'Qty': 'sum',
                'Total CBM': 'sum'
            }).reset_index()
            weekly_data.columns = ['Week', 'Orders', 'Quantity', 'CBM']
            
            # Limit to next 8 weeks
            weekly_data = weekly_data.head(8)
            
            fig_capacity = go.Figure()
            
            fig_capacity.add_trace(go.Bar(
                x=weekly_data['Week'],
                y=weekly_data['Orders'],
                name='Orders',
                marker_color='#3B82F6',
                yaxis='y'
            ))
            
            fig_capacity.add_trace(go.Scatter(
                x=weekly_data['Week'],
                y=weekly_data['Quantity'],
                name='Quantity (pcs)',
                marker_color='#10B981',
                yaxis='y2',
                mode='lines+markers',
                line=dict(width=3)
            ))
            
            fig_capacity.update_layout(
                xaxis=dict(title='Week'),
                yaxis=dict(title='Orders', side='left'),
                yaxis2=dict(title='Quantity (pcs)', side='right', overlaying='y'),
                hovermode='x unified',
                height=350,
                showlegend=True,
                legend=dict(x=0, y=1.1, orientation='h')
            )
            
            st.plotly_chart(fig_capacity, use_container_width=True)
        
        with col_financial:
            st.markdown("### 💰 Revenue Potential by Buyer")
            
            # Top buyers by CBM (proxy for revenue)
            buyer_value = df.groupby("Buyer").agg({
                "Order ID": "count",
                "Total CBM": "sum",
                "Qty": "sum"
            }).reset_index()
            buyer_value.columns = ["Buyer", "Orders", "Total CBM", "Quantity"]
            buyer_value = buyer_value.sort_values("Total CBM", ascending=False).head(5)
            
            fig_buyer_value = px.bar(
                buyer_value,
                y='Buyer',
                x='Total CBM',
                orientation='h',
                color='Total CBM',
                color_continuous_scale='Greens',
                text='Total CBM'
            )
            fig_buyer_value.update_traces(texttemplate='%{text:.1f} m³', textposition='outside')
            fig_buyer_value.update_layout(
                height=350, 
                showlegend=False,
                xaxis_title="CBM Volume",
                yaxis_title="",
                yaxis={'categoryorder':'total ascending'}
            )
            
            st.plotly_chart(fig_buyer_value, use_container_width=True)
        
        st.markdown("---")
        
        # ===== SECTION 3: CALENDAR BY BUYER =====
        st.markdown("### 📅 Production Schedule Calendar")
        
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
        df_month = df.copy()
        df_month['Due Date'] = pd.to_datetime(df_month['Due Date'])
        df_month = df_month[
            (df_month['Due Date'].dt.month == month_num) & 
            (df_month['Due Date'].dt.year == selected_year)
        ]
        
        if not df_month.empty:
            total_orders_month = len(df_month)
            total_buyers_month = df_month['Buyer'].nunique()
            total_cbm_month = df_month['Total CBM'].sum()
            
            st.markdown(f"**📌 {total_orders_month} orders | {total_buyers_month} buyers | {total_cbm_month:.1f} m³ CBM**")
        else:
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
                            
                            # Color based on status
                            done_count = len(orders_on_date[orders_on_date['Tracking Status'] == 'Done'])
                            if done_count == order_count:
                                bg_color = "#10B981"  # All done
                            elif date_obj < today:
                                bg_color = "#EF4444"  # Overdue
                            elif date_obj == today:
                                bg_color = "#F59E0B"  # Today
                            else:
                                bg_color = "#3B82F6"  # Upcoming
                            
                            week_cols[i].markdown(f"""
                            <div style='background-color: {bg_color}; padding: 8px; border-radius: 5px; text-align: center;'>
                                <strong style='color: white; font-size: 16px;'>{day}</strong><br>
                                <span style='color: white; font-size: 11px;'>{buyer_count} buyer</span><br>
                                <span style='color: white; font-size: 11px;'>{order_count} order</span>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            if date_obj == today:
                                week_cols[i].markdown(f"<div style='padding: 8px; text-align: center; border: 2px solid #3B82F6; border-radius: 5px;'><strong>{day}</strong></div>", unsafe_allow_html=True)
                            else:
                                week_cols[i].markdown(f"<div style='padding: 8px; text-align: center;'>{day}</div>", unsafe_allow_html=True)
                    else:
                        if date_obj == today:
                            week_cols[i].markdown(f"<div style='padding: 8px; text-align: center; border: 2px solid #3B82F6; border-radius: 5px;'><strong>{day}</strong></div>", unsafe_allow_html=True)
                        else:
                            week_cols[i].markdown(f"<div style='padding: 8px; text-align: center;'>{day}</div>", unsafe_allow_html=True)
        
        # Legend
        if not df_month.empty:
            st.markdown("---")
            leg_col1, leg_col2, leg_col3, leg_col4 = st.columns(4)
            leg_col1.markdown("🔵 **Upcoming** - Orders mendatang")
            leg_col2.markdown("🟠 **Today** - Jatuh tempo hari ini")
            leg_col3.markdown("🔴 **Overdue** - Terlambat")
            leg_col4.markdown("🟢 **Done** - Sudah selesai")
        
        # DETAIL ORDERS BY BUYER WITH PRODUCT DROPDOWN
        if not df_month.empty:
            st.markdown("---")
            st.markdown("### 📋 Detail Orders - By Buyer")
            
            df_month_sorted = df_month.sort_values('Due Date')
            buyers_in_month = df_month_sorted['Buyer'].unique()
            
            for buyer in sorted(buyers_in_month):
                buyer_orders = df_month_sorted[df_month_sorted['Buyer'] == buyer]
                total_buyer_orders = len(buyer_orders)
                total_buyer_qty = buyer_orders['Qty'].sum()
                total_buyer_cbm = buyer_orders['Total CBM'].sum()
                
                # Count products
                products_summary = buyer_orders.groupby('Produk').agg({
                    'Order ID': 'count',
                    'Qty': 'sum',
                    'Total CBM': 'sum'
                }).reset_index()
                products_summary.columns = ['Produk', 'Orders', 'Qty', 'CBM']
                
                with st.expander(
                    f"👤 **{buyer}** | {total_buyer_orders} orders | {total_buyer_qty} pcs | {total_buyer_cbm:.2f} m³",
                    expanded=False
                ):
                    # Product-level summary
                    st.markdown("#### 📦 Products Summary")
                    for _, prod_row in products_summary.iterrows():
                        prod_orders = buyer_orders[buyer_orders['Produk'] == prod_row['Produk']]
                        
                        with st.expander(
                            f"📦 {prod_row['Produk']} ({prod_row['Orders']} orders, {prod_row['Qty']} pcs, {prod_row['CBM']:.2f} m³)",
                            expanded=False
                        ):
                            for idx, order_row in prod_orders.iterrows():
                                due_date = order_row['Due Date'].date()
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
                                    <strong style='color: #60A5FA;'>Order ID: {order_row['Order ID']}</strong><br>
                                    <span style='color: #D1D5DB;'>Qty: {order_row['Qty']} pcs | CBM: {order_row['Total CBM']:.2f} m³</span><br>
                                    <span style='color: #D1D5DB;'>Due: {due_date.strftime('%d %b %Y')} - {date_label}</span><br>
                                    <span style='color: #D1D5DB;'>Progress: {order_row['Progress']} | {order_row['Tracking Status']}</span>
                                </div>
                                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ===== SECTION 4: WORKSTATION BOTTLENECK ANALYSIS =====
        st.markdown("### 🔧 Workstation Analysis & Bottlenecks")
        
        stages = get_tracking_stages()
        stage_analysis = {stage: {'qty': 0, 'orders': 0} for stage in stages}
        
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
            marker_color='#3B82F6',
            yaxis='y'
        ))
        
        fig_bottleneck.add_trace(go.Scatter(
            x=stage_df['Stage'],
            y=stage_df['Orders'],
            name='Orders Count',
            marker_color='#EF4444',
            yaxis='y2',
            mode='lines+markers',
            line=dict(width=3)
        ))
        
        fig_bottleneck.update_layout(
            xaxis=dict(title='', tickangle=-45),
            yaxis=dict(title='WIP Quantity (pcs)'),
            yaxis2=dict(title='Number of Orders', overlaying='y', side='right'),
            height=400,
            hovermode='x unified',
            showlegend=True,
            legend=dict(x=0, y=1.1, orientation='h')
        )
        
        st.plotly_chart(fig_bottleneck, use_container_width=True)
        
        # Identify bottleneck
        if not stage_df.empty and stage_df['WIP Qty'].max() > 0:
            max_wip_stage = stage_df.loc[stage_df['WIP Qty'].idxmax()]
            st.warning(f"⚠️ **Potential Bottleneck:** {max_wip_stage['Stage']} with {int(max_wip_stage['WIP Qty'])} pcs WIP from {int(max_wip_stage['Orders'])} orders")
        
        st.markdown("---")
        
        # ===== SECTION 5: ORDER FULFILLMENT TIMELINE =====
        col_timeline1, col_timeline2 = st.columns(2)
        
        with col_timeline1:
            st.markdown("### ⏱️ Lead Time Analysis")
            
            df_done = df[df['Tracking Status'] == 'Done'].copy()
            if not df_done.empty:
                df_done['Order Date'] = pd.to_datetime(df_done['Order Date'])
                df_done['Due Date'] = pd.to_datetime(df_done['Due Date'])
                df_done['Lead Time'] = (df_done['Due Date'] - df_done['Order Date']).dt.days
                
                avg_lead = df_done['Lead Time'].mean()
                min_lead = df_done['Lead Time'].min()
                max_lead = df_done['Lead Time'].max()
                
                col_lead1, col_lead2, col_lead3 = st.columns(3)
                col_lead1.metric("Avg", f"{avg_lead:.0f} days")
                col_lead2.metric("Min", f"{min_lead} days")
                col_lead3.metric("Max", f"{max_lead} days")
                
                # Distribution
                fig_lead = px.histogram(
                    df_done,
                    x='Lead Time',
                    nbins=15,
                    labels={'Lead Time': 'Days', 'count': 'Orders'}
                )
                fig_lead.update_layout(height=250, showlegend=False)
                st.plotly_chart(fig_lead, use_container_width=True)
            else:
                st.info("No completed orders yet")
        
        with col_timeline2:
            st.markdown("### 🎯 Delivery Performance")
            
            df['Due Date'] = pd.to_datetime(df['Due Date'])
            today_ts = pd.Timestamp(datetime.date.today())
            
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
                color='Status',
                color_discrete_map={
                    'On Time': '#10B981',
                    'Late': '#EF4444',
                    'In Progress': '#3B82F6'
                },
                hole=0.4
            )
            fig_delivery.update_traces(textposition='inside', textinfo='percent+label')
            fig_delivery.update_layout(height=350, showlegend=True)
            st.plotly_chart(fig_delivery, use_container_width=True)
        
        st.markdown("---")
        
        # ===== SECTION 6: CRITICAL ALERTS =====
        st.markdown("### ⚠️ Critical Alerts & Action Items")
        
        alert_col1, alert_col2, alert_col3 = st.columns(3)
        
        with alert_col1:
            st.markdown("#### 🔴 Overdue Orders")
            today_ts = pd.Timestamp(datetime.date.today())
            overdue = df[(df['Due Date'] < today_ts) & (df['Tracking Status'] != 'Done')]
            
            if len(overdue) > 0:
                st.error(f"**{len(overdue)} orders terlambat**")
                for idx, row in overdue.head(5).iterrows():
                    days_late = (today_ts - row['Due Date']).days
                    st.markdown(f"- {row['Order ID']} ({row['Buyer']}) - **{days_late} hari**")
            else:
                st.success("✅ No overdue orders")
        
        with alert_col2:
            st.markdown("#### 🟠 Due Today")
            due_today = df[(df['Due Date'].dt.date == datetime.date.today()) & (df['Tracking Status'] != 'Done')]
            
            if len(due_today) > 0:
                st.warning(f"**{len(due_today)} orders due today**")
                for idx, row in due_today.iterrows():
                    st.markdown(f"- {row['Order ID']} - {row['Progress']}")
            else:
                st.info("No orders due today")
        
        with alert_col3:
            st.markdown("#### 🟡 Due in 3 Days")
            three_days = today_ts + pd.Timedelta(days=3)
            due_soon = df[(df['Due Date'] > today_ts) & (df['Due Date'] <= three_days) & (df['Tracking Status'] != 'Done')]
            
            if len(due_soon) > 0:
                st.info(f"**{len(due_soon)} orders due soon**")
                for idx, row in due_soon.head(5).iterrows():
                    days_left = (row['Due Date'] - today_ts).days
                    st.markdown(f"- {row['Order ID']} - **{days_left} days**")
            else:
                st.success("No urgent orders")
    
    else:
        st.info("📝 Belum ada data. Silakan input pesanan baru.")
