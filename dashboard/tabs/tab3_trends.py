import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Tuple, Dict, Any, List

# DATA LOADING & PREPROCESSING UTILS
@st.cache_data
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Loads and caches datasets into memory to avoid continuous reloading."""
    data_dir = "../data/processed"
    df_fact_tiki = pd.read_csv(f"{data_dir}/fact_tiki_listings.csv", dtype={'product_id': str})
    df_fact_ebay = pd.read_csv(f"{data_dir}/fact_ebay_listings.csv", dtype={'product_id': str})
    df_product = pd.read_csv(f"{data_dir}/dim_product.csv", dtype={'product_id': str})
    df_category = pd.read_csv(f"{data_dir}/dim_category.csv")
    return df_fact_tiki, df_fact_ebay, df_product, df_category

def _clean_numeric_columns(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """Ensures target columns are numeric and drops rows with invalid values."""
    cleaned = df.copy()
    for col in cols:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
    return cleaned.dropna(subset=cols)

def _apply_global_filters(df_tiki: pd.DataFrame, df_ebay: pd.DataFrame, filters: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Applies platform and price range filters globally to the datasets."""
    selected_platforms = filters.get("platform", ["Tiki", "eBay"])
    min_price, max_price = filters.get("price_range", (0, 50_000_000))

    # Apply filters to Tiki
    if "Tiki" in selected_platforms:
        tiki_filtered = df_tiki[(df_tiki["price"] >= min_price) & (df_tiki["price"] <= max_price)].copy()
    else:
        tiki_filtered = df_tiki.iloc[0:0].copy() # Return empty dataframe keeping schema

    # Apply filters to eBay
    if "eBay" in selected_platforms:
        ebay_filtered = df_ebay[(df_ebay["Total_Cost_VND"] >= min_price) & (df_ebay["Total_Cost_VND"] <= max_price)].copy()
    else:
        ebay_filtered = df_ebay.iloc[0:0].copy()

    return tiki_filtered, ebay_filtered


# 1. TIKI COLD-START (OBJECTIVE 1)
def render_tiki_cold_start(df_fact_tiki: pd.DataFrame, df_product: pd.DataFrame, df_category: pd.DataFrame) -> None:
    st.subheader("1. Tiki Ecosystem: Product Stagnation Risk")
    
    # Defensive check: Prevent execution if global filters removed all data
    if df_fact_tiki.empty:
        st.info("No Tiki listings match the current global filters. Please adjust the sidebar settings.")
        return

    # Data Processing
    df_merged = df_fact_tiki.merge(df_product[['product_id', 'category_id']], on='product_id')
    df_merged = df_merged.merge(df_category, on='category_id')
    
    # Filter out 'Unknown' categories before analysis to ensure data integrity
    df_merged = df_merged[df_merged['category'] != 'Unknown']
    
    # Isolate cold-start products (0 sold, 0 reviews)
    cold_start_df = df_merged[(df_merged['quantity_sold'] == 0) & (df_merged['review_count'] == 0)]
    
    if cold_start_df.empty:
        st.success("Great! No cold-start products found within this price range.")
        return

    # Calculate cumulative percentage for the Pareto chart
    cat_counts = cold_start_df['category'].value_counts().reset_index()
    cat_counts.columns = ['Category', 'Count']
    cat_counts['Cumulative_Perc'] = 100 * cat_counts['Count'].cumsum() / cat_counts['Count'].sum()
    
    # Extract Top 20 to eliminate long-tail noise
    top_n = 20
    plot_df = cat_counts.head(top_n).copy()
    
    # Gestalt Principle: Pop-out (Top 3 in Red, remainder in Muted Gray)
    colors = ['#ef4444'] * 3 + ['#e2e8f0'] * (len(plot_df) - 3)
    line_color = "#334155" 
    
    # Display Key Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Identified Products", f"{len(df_merged):,}")
    col2.metric("Zero-Interaction Products", f"{len(cold_start_df):,}", delta="Action Required", delta_color="inverse")
    risk_ratio = (len(cold_start_df)/len(df_merged))*100 if len(df_merged) > 0 else 0
    col3.metric("Risk Ratio", f"{risk_ratio:.1f}%")

    # Render Pareto Chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=plot_df['Category'], 
        y=plot_df['Count'], 
        name="Stagnant Volume", 
        marker_color=colors,
        text=plot_df['Count'],
        textposition='outside'
    ))
    
    fig.add_trace(go.Scatter(
        x=plot_df['Category'], 
        y=plot_df['Cumulative_Perc'], 
        name="Cumulative %", 
        yaxis="y2", 
        line=dict(color=line_color, width=2, dash='dot'),
        mode="lines+markers",
        marker=dict(color=line_color, size=6)
    ))
    
    # Layout Configuration
    fig.update_layout(
        template="plotly_white", 
        margin=dict(t=40, b=0, l=0, r=0),
        bargap=0.02, 
        xaxis_tickangle=-35,
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
    
    st.plotly_chart(fig, width="stretch")

    # Actionable Insights
    with st.expander("Chart Insights & Actionable Recommendations"):
        if len(plot_df) >= 3:
            st.write(f"""
            **Chart Analysis:**
            * After filtering out data noise, the top 3 highest-risk categories are: **{plot_df.iloc[0]['Category']}**, **{plot_df.iloc[1]['Category']}**, and **{plot_df.iloc[2]['Category']}**.
            * The top 20 categories alone account for **{plot_df.iloc[-1]['Cumulative_Perc']:.1f}%** of the total stagnant inventory within the selected parameters.
            
            **Recommended Next Steps:**
            To optimize operational efficiency, rather than distributing the marketing budget evenly, the team should perform a root-cause analysis focusing on the **{plot_df.iloc[0]['Category']}** category. This will help determine whether the primary barrier is pricing or a lack of promotional campaigns.
            """)

# 2. EBAY CONDITION ANALYSIS (OBJECTIVE 2)
def render_ebay_condition_analysis(df_fact_ebay: pd.DataFrame) -> None:
    st.subheader("2. eBay Ecosystem: Condition Distribution & Cost Impact")
    
    # Defensive check
    if df_fact_ebay.empty:
        st.info("No eBay listings match the current global filters. Please adjust the sidebar settings.")
        return

    # Data Processing
    def categorize_condition(cond):
        cond = str(cond).lower()
        if any(keyword in cond for keyword in ['new', 'neu', 'nuovo']): 
            return 'New'
        elif any(keyword in cond for keyword in ['used', 'usato']): 
            return 'Used'
        elif any(keyword in cond for keyword in ['refurbished', 'open box', 'opened', 'certified', 'good - refurbished']): 
            return 'Refurbished / Open Box'
        return 'Other/Parts'

    df_fact_ebay['Standard_Condition'] = df_fact_ebay['condition'].apply(categorize_condition)
    df_clean = df_fact_ebay[df_fact_ebay['Standard_Condition'] != 'Other/Parts'].copy()

    if df_clean.empty:
        st.warning("Insufficient valid condition data within this price range.")
        return

    # Calculate Market Share
    df_market = df_clean['Standard_Condition'].value_counts().reset_index()
    df_market.columns = ['Condition', 'Count']
    total_listings = df_market['Count'].sum()
    
    dominant_segment = df_market.iloc[0]['Condition']
    dominant_perc = (df_market.iloc[0]['Count'] / total_listings) * 100 if total_listings > 0 else 0

    # Calculate Average Cost
    df_cost = df_clean.groupby('Standard_Condition')['Total_Cost_VND'].mean().reset_index()
    df_cost.columns = ['Condition', 'Total_Cost_VND'] 
    df_cost = df_cost.sort_values(by='Total_Cost_VND', ascending=True)

    # Gestalt Principle
    color_map = {
        cond: '#1f77b4' if cond == dominant_segment else '#e2e8f0' 
        for cond in df_market['Condition']
    }

    # Render Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Valid Listings", f"{total_listings:,}")
    col2.metric("Dominant Segment", dominant_segment)
    col3.metric("Dominant Share", f"{dominant_perc:.1f}%")

    # Render Charts
    col_tree, col_bar = st.columns(2)
    
    with col_tree:
        st.markdown("**Market Share by Item Condition**")
        fig_tree = px.treemap(
            df_market, 
            path=['Condition'], 
            values='Count',
            color='Condition',
            color_discrete_map=color_map
        )
        
        fig_tree.update_traces(
            textinfo="label+percent root", 
            textfont_size=14,
            marker=dict(line=dict(color='white', width=2)) 
        )
        fig_tree.update_layout(margin=dict(t=0, l=0, r=0, b=0))
        st.plotly_chart(fig_tree, width="stretch")
        
    with col_bar:
        st.markdown("**Impact on Average Cost (VND)**")
        fig_bar = px.bar(
            df_cost, 
            y='Condition',  
            x='Total_Cost_VND',      
            orientation='h',         
            text_auto='.2s',
            color='Condition',
            color_discrete_map=color_map
        )
        
        fig_bar.update_layout(
            template="plotly_white", 
            xaxis=dict(
                title="<b>Average Total Cost (VND)</b>",
                showgrid=False,       
                showticklabels=False, 
                zeroline=True,        
                zerolinewidth=2,
                zerolinecolor='#cbd5e1'
            ),
            yaxis=dict(
                title="",             
                showgrid=False
            ),
            showlegend=False,         
            margin=dict(t=0, l=0, r=50, b=0) 
        )
        
        fig_bar.update_traces(
            textposition='outside', 
            textfont=dict(size=12, color='#334155'),
            cliponaxis=False
        )
        st.plotly_chart(fig_bar, width="stretch")

    # Actionable Insights
    with st.expander("Chart Insights & Actionable Recommendations"):
        if not df_cost.empty:
            lowest_cost_cond = df_cost.iloc[0]['Condition']
            highest_cost_cond = df_cost.iloc[-1]['Condition']
            
            st.write(f"""
            **Chart Analysis:**
            * The **{dominant_segment}** segment leads the ecosystem within the filtered parameters, capturing **{dominant_perc:.1f}%** of the market share.
            * Interestingly, there is an inverse relationship in pricing dynamics: the **{lowest_cost_cond}** segment has the lowest average cost, whereas the **{highest_cost_cond}** segment commands the highest average cost.
            
            **Recommended Sourcing Strategy:**
            * Consumer behavior suggests a preference for '{lowest_cost_cond}' items in the budget-friendly tier, but a pivot to '{highest_cost_cond}' or 'Used' options for high-value premium items.
            * To maximize profit margins, retailers should focus on stocking **{lowest_cost_cond}** inventory for entry-level products, while aggressively sourcing **{highest_cost_cond}** items to capture the high-end market segment.
            """)

# ==========================================
# MAIN RENDER FUNCTION (Invoked by app.py)
# ==========================================
def render(filters: Dict[str, Any]) -> None:
    """Main rendering entrypoint for Tab 3: Characteristics & Trends."""
    st.header("📈 Characteristics & Trends")
    st.markdown("A definitive overview of listing capacities bridging B2C pipelines (Tiki) juxtaposed alongside standard C2C structures (eBay).")
    
    try:
        # Load raw datasets
        df_fact_tiki, df_fact_ebay, df_product, df_category = load_data()
    except Exception as e:
        st.error(f"Error loading datasets: {e}. Please check routing in `../data/processed/`.")
        return

    # Clean critical numeric columns to avoid filtering errors
    df_fact_tiki = _clean_numeric_columns(df_fact_tiki, ["price"])
    df_fact_ebay = _clean_numeric_columns(df_fact_ebay, ["Total_Cost_VND"])

    # Apply global filters explicitly mapped from Sidebar
    df_tiki_filtered, df_ebay_filtered = _apply_global_filters(df_fact_tiki, df_fact_ebay, filters)

    # Visual blocks mapping with filtered DataFrames
    with st.container():
        render_tiki_cold_start(df_tiki_filtered, df_product, df_category)
        
    st.divider()

    with st.container():
        render_ebay_condition_analysis(df_ebay_filtered)