import streamlit as st
from sidebar import render_sidebar
from tabs import tab1_pricing, tab2_trust, tab3_trends

# Configure page settings (must be the first Streamlit command)
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main() -> None:
    """Main function to render the E-commerce Dashboard."""
    
    # 1. Render sidebar and retrieve filters
    filters = render_sidebar()

    # 2. Render global header and KPI metrics
    st.title("🛍️ E-commerce Multi-Platform Dashboard")
    st.markdown("Comprehensive insights into pricing, trust, and platform trends across Tiki and eBay.")
    
    # Example static metrics; ideally, these should be dynamically computed from data
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Products", value="25,744")
    col2.metric(label="Total Sellers (eBay)", value="6,858")
    col3.metric(label="Avg. Price (VND)", value="1.2M")
    
    st.divider()

    # 3. Initialize and render tabs
    tab_pricing, tab_trust, tab_trends = st.tabs([
        "📊 Pricing & Promotions",
        "🤝 Trust & Reputation",
        "📈 Characteristics & Trends"
    ])

    # with tab_pricing:
    #     tab1_pricing.render(filters)
        
    # with tab_trust:
    #     tab2_trust.render(filters)

    with tab_trends:
        tab3_trends.render(filters)

if __name__ == "__main__":
    main()