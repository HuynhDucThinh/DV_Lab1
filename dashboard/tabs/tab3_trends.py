import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Tuple, Dict, Any


@st.cache_data
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Loads and caches datasets into memory to avoid continuous reloading."""
    data_dir = "../data/processed"
    df_fact_tiki = pd.read_csv(f"{data_dir}/fact_tiki_listings.csv", dtype={'product_id': str})
    df_fact_ebay = pd.read_csv(f"{data_dir}/fact_ebay_listings.csv", dtype={'product_id': str})
    df_product = pd.read_csv(f"{data_dir}/dim_product.csv", dtype={'product_id': str})
    df_category = pd.read_csv(f"{data_dir}/dim_category.csv")
    return df_fact_tiki, df_fact_ebay, df_product, df_category


# 1. TIKI COLD-START (OBJECTIVE 1)
def render_tiki_cold_start(df_fact_tiki: pd.DataFrame, df_product: pd.DataFrame, df_category: pd.DataFrame) -> None:
    st.subheader("1. Tiki Ecosystem: Product Stagnation Risk (Cold-Start)")
    
    # 1. Data Processing
    df_merged = df_fact_tiki.merge(df_product[['product_id', 'category_id']], on='product_id')
    df_merged = df_merged.merge(df_category, on='category_id')
    
    # Filter out 'Unknown' categories before analysis to ensure data integrity
    df_merged = df_merged[df_merged['category'] != 'Unknown']
    
    # Isolate cold-start products (0 sold, 0 reviews)
    cold_start_df = df_merged[(df_merged['quantity_sold'] == 0) & (df_merged['review_count'] == 0)]
    
    # Calculate cumulative percentage for the Pareto chart
    cat_counts = cold_start_df['category'].value_counts().reset_index()
    cat_counts.columns = ['Category', 'Count']
    cat_counts['Cumulative_Perc'] = 100 * cat_counts['Count'].cumsum() / cat_counts['Count'].sum()
    
    # Extract Top 20 to eliminate long-tail noise
    top_n = 20
    plot_df = cat_counts.head(top_n).copy()
    
    # Gestalt Principle: Pop-out (Top 3 in Red, remainder in Muted Gray)
    colors = ['#ef4444'] * 3 + ['#e2e8f0'] * (len(plot_df) - 3)
    line_color = "#334155" # Dark gray for the Pareto line and secondary Y-axis
    
    # 2. Display Key Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Identified Products", f"{len(df_merged):,}")
    col2.metric("Cold-Start Products", f"{len(cold_start_df):,}", delta="Action Required", delta_color="inverse")
    risk_ratio = (len(cold_start_df)/len(df_merged))*100 if len(df_merged) > 0 else 0
    col3.metric("Risk Ratio", f"{risk_ratio:.1f}%")

    # 3. Render Pareto Chart
    fig = go.Figure()
    
    # Bar Trace (Volume)
    fig.add_trace(go.Bar(
        x=plot_df['Category'], 
        y=plot_df['Count'], 
        name="Stagnant Volume", 
        marker_color=colors,
        text=plot_df['Count'],
        textposition='outside'
    ))
    
    # Line Trace (Cumulative Percentage)
    fig.add_trace(go.Scatter(
        x=plot_df['Category'], 
        y=plot_df['Cumulative_Perc'], 
        name="Cumulative %", 
        yaxis="y2", 
        line=dict(color=line_color, width=2, dash='dot'),
        mode="lines+markers",
        marker=dict(color=line_color, size=6)
    ))
    
    # Layout Configuration: Applying Color-Coded Dual Axes and Touching Bars
    fig.update_layout(
        template="plotly_white", 
        margin=dict(t=40, b=0, l=0, r=0),
        bargap=0.02, # Touching bars to group elements visually
        xaxis_tickangle=-45,
        yaxis=dict(
            title="Product Count", 
            showgrid=False
        ),
        yaxis2=dict(
            title=dict(
                text="<b>Cumulative %</b>",
                font=dict(color=line_color)
            ), 
            overlaying="y", 
            side="right", 
            range=[0, 105], 
            showgrid=False,
            tickfont=dict(color=line_color)
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=550
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # 4. Actionable Insights
    with st.expander("Chart Insights & Actionable Recommendations"):
        if len(plot_df) >= 3:
            st.write(f"""
            **Chart Analysis:**
            * After filtering out data noise, the top 3 highest-risk categories are: **{plot_df.iloc[0]['Category']}**, **{plot_df.iloc[1]['Category']}**, and **{plot_df.iloc[2]['Category']}**.
            * The top 20 categories alone account for **{plot_df.iloc[-1]['Cumulative_Perc']:.1f}%** of the total stagnant inventory on the platform.
            
            **Recommended Next Steps:**
            To optimize operational efficiency, rather than distributing the marketing budget evenly, the team should perform a root-cause analysis focusing on the **{plot_df.iloc[0]['Category']}** category. This will help determine whether the primary barrier is pricing or a lack of promotional campaigns.
            """)

# ==========================================
# 2. CROSS-PLATFORM PRICE (OBJECTIVE 2)
# ==========================================
def render_cross_platform_kde(df_fact_tiki: pd.DataFrame, df_fact_ebay: pd.DataFrame, df_product: pd.DataFrame) -> None:
    st.subheader("2. Cross-platform Pricing Index: Tech & Electronics Segments")
    
    # Selecting standard technology related domains
    tiki_tech = df_fact_tiki[['product_id', 'price']].assign(Platform='Tiki (New)')
    ebay_tech = df_fact_ebay[['product_id', 'Total_Cost_VND', 'condition']].rename(columns={'Total_Cost_VND': 'price'})
    ebay_tech['Platform'] = 'eBay (' + ebay_tech['condition'] + ')'
    
    df_combine = pd.concat([tiki_tech, ebay_tech[['product_id', 'price', 'Platform']]]).dropna(subset=['price'])
    
    # Overlapping KDE Plot
    fig = px.histogram(
        df_combine, x="price", color="Platform",
        marginal="violin", # Adds marginal violin plots
        histnorm='probability density', barmode="overlay",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(
        template="plotly_white", 
        xaxis_title="Standardized Price (VND)", 
        yaxis_title="Allocation Density"
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 3. EBAY ECOSYSTEM (OBJECTIVE 3 & 4)
# ==========================================
def render_ebay_ecosystem(df_fact_ebay: pd.DataFrame, df_product: pd.DataFrame, df_category: pd.DataFrame) -> None:
    st.subheader("3. eBay Ecosystem: Hardware Conditions & Freight Strategy")
    
    # 3.1 Treemap & Bar Chart (Objective 3)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Market Share by Item Condition**")
        condition_counts = df_fact_ebay['condition'].value_counts().reset_index()
        condition_counts.columns = ['condition', 'count']
        fig_tree = px.treemap(
            condition_counts, path=['condition'], values='count',
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig_tree.update_layout(margin=dict(t=0, l=0, r=0, b=0))
        st.plotly_chart(fig_tree, use_container_width=True)
        
    with col2:
        st.markdown("**Impact on Total Costs (VND)**")
        condition_cost = df_fact_ebay.groupby('condition')['Total_Cost_VND'].median().reset_index()
        fig_bar = px.bar(
            condition_cost, x='condition', y='Total_Cost_VND', 
            text_auto='.2s', color_discrete_sequence=['#94a3b8']
        )
        fig_bar.update_layout(
            template="plotly_white", xaxis_title="Item Condition", 
            yaxis_title="Median Cost (VND)"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # 3.2 Lollipop Chart (Objective 4: Platform Freeship Ratios)
    st.markdown("**Freight Strategic Policy: Free-shipping Penetration Across Top 5 Categories**")
    
    # Extract Top 5 Categories on eBay
    df_merged_ebay = df_fact_ebay.merge(df_product[['product_id', 'category_id']], on='product_id').merge(df_category, on='category_id')
    top5_cats = df_merged_ebay['category'].value_counts().head(5).index
    df_top5 = df_merged_ebay[df_merged_ebay['category'].isin(top5_cats)].copy()
    
    # Calculate percentage for free shipping distributions
    df_top5['is_freeship'] = (df_top5['shipping_cost'] == 0)
    freeship_stats = (df_top5.groupby('category')['is_freeship'].mean() * 100).sort_values().reset_index()
    freeship_stats.columns = ['category', 'Freeship_Percent']
    
    # Render Lollipop Chart
    fig_lol = go.Figure()
    
    # Candy Head (Scatter markers)
    fig_lol.add_trace(go.Scatter(
        x=freeship_stats['Freeship_Percent'], 
        y=freeship_stats['category'], 
        mode='markers+text', 
        marker=dict(color='#10b981', size=14), # Positive green signal
        text=freeship_stats['Freeship_Percent'].apply(lambda x: f"{x:.1f}%"),
        textposition="middle right",
        name="Free Delivery Ratio"
    ))
    
    # Candy Stick (Plot shapes for bars)
    for i, row in freeship_stats.iterrows():
        fig_lol.add_shape(
            type='line', 
            x0=0, x1=row['Freeship_Percent'], 
            y0=row['category'], y1=row['category'], 
            line=dict(color='lightgray', width=3)
        )
        
    fig_lol.update_layout(
        template="plotly_white", 
        xaxis_title="Proportion of Eligible Free Shipping (%)", 
        yaxis_title="", 
        xaxis=dict(range=[0, max(freeship_stats['Freeship_Percent']) + 15]), # Enhance label padding constraints
        height=350,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig_lol, use_container_width=True)
    
    # Mini insight footprint
    st.info("💡 **Commercial Insight:** Free shipping quotas indicate competition parameters. Greater percentages typically signify heavy merchant competition forcing logistics costs absorption directly as part of pricing structures.")

# ==========================================
# MAIN RENDER FUNCTION (Invoked by app.py)
# ==========================================
def render(filters: Dict[str, Any]) -> None:
    """Main rendering entrypoint for Tab 3: Characteristics & Trends."""
    st.header("📈 Characteristics & Trends")
    st.markdown("A definitive overview of listing capacities bridging B2C pipelines (Tiki) juxtaposed alongside standard C2C structures (eBay).")
    
    try:
        df_fact_tiki, df_fact_ebay, df_product, df_category = load_data()
    except Exception as e:
        st.error(f"❌ Error loading datasets: {e}. Please navigate the exact routing in `../data/processed/`.")
        return

    # Visual blocks mapping
    with st.container():
        render_tiki_cold_start(df_fact_tiki, df_product, df_category)
        
    st.divider() # Refined thematic separation boundary
    
    with st.container():
        render_cross_platform_kde(df_fact_tiki, df_fact_ebay, df_product)
        
    st.divider()
    
    with st.container():
        render_ebay_ecosystem(df_fact_ebay, df_product, df_category)