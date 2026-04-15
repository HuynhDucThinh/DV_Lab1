import streamlit as st
from typing import Dict, Any

def render_sidebar() -> Dict[str, Any]:
    """Renders the global sidebar filters and returns the selected parameters."""
    
    st.sidebar.header("🔍 Global Filters")
    st.sidebar.markdown("Use these filters to refine the analysis across all tabs.")

    # Platform selection filter
    platform = st.sidebar.multiselect(
        "Select Platform", ["Tiki", "eBay"], default=["Tiki", "eBay"],
        help="Choose one or both platforms for analysis."
    )
    
    # Price range selection filter
    price_range = st.sidebar.slider(
        "Price Range (VND)",
        min_value=0,
        max_value=50000000,
        value=(0, 10000000),
        step=500000,
        help="Filter products by price range."
    )
    
    # Return filter dictionary
    return {
        "platform": platform,
        "price_range": price_range
    }