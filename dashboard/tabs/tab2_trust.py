import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any

# DƯỚI LÀ MẪU THÔI NHA
# LÚC LÀM THÌ CẦN CHỈNH SỬA LẠI CHO PHÙ HỢP VỚI DỮ LIỆU VÀ MỤC ĐÍCH PHÂN TÍCH CỦA TAB 2 (ĐÁNH GIÁ ĐỘ TIN CẬY VÀ UY TÍN CỦA NGƯỜI BÁN TRÊN EBAY)

@st.cache_data
def load_seller_data() -> pd.DataFrame:
    """Loads and caches seller trust profiles from eBay."""
    try:
        df = pd.read_csv("../data/processed/dim_seller.csv")
        return df
    except FileNotFoundError:
        st.error("❌ Data not found. Please verify the file path: `../data/processed/dim_seller.csv`")
        return pd.DataFrame()

def render_trust_levels(df: pd.DataFrame) -> None:
    """Renders the analysis of seller trust levels distribution."""
    st.subheader("Distribution of Trust Levels")
    st.markdown("Examine how eBay categorizes sellers into High vs Normal/Low trust levels based on feedback scores.")
    
    if df.empty:
        st.info("Data not available to render this section.")
        return

    # Pie Chart for trust levels
    if 'Trust_Level' in df.columns:
        trust_counts = df['Trust_Level'].value_counts().reset_index()
        trust_counts.columns = ['Trust_Level', 'Count']
        
        fig = px.pie(
            trust_counts, names='Trust_Level', values='Count', hole=0.4,
            title="Proportion of Seller Trust Classification",
            color='Trust_Level',
            color_discrete_map={'High Trust': '#10b981', 'Normal/Low Trust': '#ef4444'}
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig, use_container_width=True)

def render_feedback_distribution(df: pd.DataFrame) -> None:
    """Renders a visualization to show the feedback percentage distribution."""
    st.subheader("Seller Feedback Percentage Distribution")
    st.markdown("Analyze the distribution corresponding to the average feedback rating sellers received.")
    
    if df.empty:
        return

    if 'seller_feedback_percent' in df.columns:
        fig = px.histogram(
            df, x='seller_feedback_percent',
            title='Density of Seller Feedback Scores (%)',
            marginal="box",
            nbins=30,
            color_discrete_sequence=['#4f46e5']
        )
        fig.update_layout(
            template="plotly_white",
            xaxis_title="Feedback Percentage (%)",
            yaxis_title="Count of Sellers",
            margin=dict(l=0, r=0, t=50, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

def render(filters: Dict[str, Any]) -> None:
    """Main rendering entrypoint for Tab 2: Trust & Reputation."""
    st.header("🤝 Trust & Reputation Tracking")
    st.markdown("Analyze seller integrity, scoring trends, and platform trust mechanisms ensuring secure commerce.")

    # Load Data
    df_seller = load_seller_data()

    # Layout structuring
    col1, col2 = st.columns(2)
    with col1:
        render_trust_levels(df_seller)
        
    with col2:
        render_feedback_distribution(df_seller)