"""
app.py — Dashboard entry point.

Responsibilities (only):
  1. Set Streamlit page config
  2. Inject global assets (FA, CSS)
  3. Render sidebar → receive filter dict
  4. Render hero banner + KPI cards
  5. Delegate to tab modules

All CSS/HTML strings live in  styles/
UI helpers live in             components/ui_helpers.py
Data loaders live in           data/loaders.py
"""

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import streamlit_shadcn_ui as ui

from styles       import GLOBAL_CSS, FA_HTML, HERO_HTML, KPI_HEADER, TAB_HEADER, SHIMMER
from components.sidebar import render_sidebar
from data.loaders       import load_kpi_data
from tabs import tab0_overview, tab1_pricing, tab2_trust, tab3_trends

st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/svgs/solid/chart-column.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    # Global CSS (includes FA + Inter @import)
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    # 2. Sidebar filters
    filters = render_sidebar()

    # 3. Hero banner
    st.markdown(HERO_HTML, unsafe_allow_html=True)

    # 4. KPI metric cards
    st.markdown(KPI_HEADER, unsafe_allow_html=True)
    kpi = load_kpi_data()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        ui.metric_card(
            title="Total Listings",
            content=f"{kpi['total']:,}",
            description="Tiki + eBay combined",
            key="kpi_total",
        )
    with c2:
        ui.metric_card(
            title="eBay Unique Sellers",
            content=f"{kpi['sellers']:,}",
            description="Active vendors on platform",
            key="kpi_sellers",
        )
    with c3:
        ui.metric_card(
            title="Median Price",
            content=f"{kpi['median_price'] / 1e6:.1f}M VND",
            description="Cross-platform median",
            key="kpi_price",
        )
    with c4:
        ui.metric_card(
            title="Tiki Promotions",
            content=f"{kpi['disc_pct']:.1f}%",
            description="Listings with active discount",
            key="kpi_disc",
        )

    # Animated shimmer divider
    st.markdown(SHIMMER, unsafe_allow_html=True)

    # 5. Navigation tabs
    st.markdown(TAB_HEADER, unsafe_allow_html=True)
    selected = ui.tabs(
        options=[
            "Overview",
            "Pricing & Promotions",
            "Trust & Reputation",
            "Characteristics & Trends",
        ],
        default_value="Overview",
        key="nav_tabs",
    )

    # Thin teal accent line below tabs
    st.markdown(
        '<div style="height:3px;border-radius:2px;'
        'background:linear-gradient(90deg,#0d9488,#14b8a6,rgba(13,148,136,0));'
        'margin-bottom:1rem;"></div>',
        unsafe_allow_html=True,
    )

    # 6. Render selected tab
    if selected == "Overview":
        tab0_overview.render(filters)
    elif selected == "Pricing & Promotions":
        tab1_pricing.render(filters)
    elif selected == "Trust & Reputation":
        tab2_trust.render(filters)
    else:
        tab3_trends.render(filters)


if __name__ == "__main__":
    main()