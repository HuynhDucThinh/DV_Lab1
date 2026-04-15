import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, Any

# DƯỚI LÀ MẪU THÔI NHA
# LÚC LÀM THÌ CẦN CHỈNH SỬA LẠI CHO PHÙ HỢP VỚI DỮ LIỆU VÀ MỤC ĐÍCH PHÂN TÍCH CỦA TAB 1 (GIÁ CẢ VÀ KHUYẾN MÃI)

@st.cache_data
def load_tiki_data() -> pd.DataFrame:
    """Loads and caches Tiki fact data for performance optimization."""
    try:
        df = pd.read_csv("../data/processed/fact_tiki_listings.csv", dtype={'product_id': str})
        return df
    except FileNotFoundError:
        st.error("❌ Data not found. Please verify the file path: `../data/processed/fact_tiki_listings.csv`")
        return pd.DataFrame()

def render_discount_impact(df: pd.DataFrame) -> None:
    """Renders insights related to the impact of discounts on sales."""
    st.subheader("Impact of Discount Rates on Best Seller Status")
    st.markdown("This analysis visualizes how discount tiers influence product sales performance.")
    
    if df.empty:
        st.info("Data not available to render this section.")
        return

    # Aggregate data by Discount Segment to find the ratio of Best Sellers
    if 'Discount_Segment' in df.columns and 'Is_Best_Seller' in df.columns:
        agg_df = df.groupby('Discount_Segment')['Is_Best_Seller'].mean().reset_index()
        agg_df['Is_Best_Seller'] *= 100
        agg_df.rename(columns={'Is_Best_Seller': 'Best_Seller_Percentage'}, inplace=True)
        
        # Visualize Bar Chart
        fig = px.bar(
            agg_df, x='Discount_Segment', y='Best_Seller_Percentage',
            title='Likelihood of Becoming a Best Seller by Discount Segment',
            labels={'Discount_Segment': 'Discount Segment', 'Best_Seller_Percentage': 'Probability (%)'},
            text_auto=True,
            color='Best_Seller_Percentage',
            color_continuous_scale="Viridis"
        )
        
        fig.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Missing required columns for discount aggregation.")

def render(filters: Dict[str, Any]) -> None:
    """Main rendering entrypoint for Tab 1: Pricing Analysis."""
    st.header("📊 Pricing & Promotional Strategies")
    st.markdown("Explore strategic pricing models and assess the efficiency of promotional campaigns designed to capture market share.")

    # Load Data
    df_tiki = load_tiki_data()

    # Layout structuring
    with st.container():
        render_discount_impact(df_tiki)