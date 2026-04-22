import streamlit as st
import streamlit_shadcn_ui as ui

from data.loaders import load_kpi_data
from styles import KPI_HEADER


def render_kpi_cards() -> None:
    """
    Render the Platform KPIs section:
      • Section label (KPI_HEADER HTML)
      • 4-column metric card row: Total Listings, eBay Sellers, Median Price, Tiki Promotions
    """
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
