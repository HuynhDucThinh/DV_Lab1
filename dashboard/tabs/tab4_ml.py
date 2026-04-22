import streamlit as st
from typing import Dict, Any

from components.ui_helpers import icon_header as _icon_header


def render(filters: Dict[str, Any]) -> None:
    """Placeholder for Tab 4: Machine Learning — coming soon."""
    _icon_header("fa-solid fa-brain", "Machine Learning &amp; Predictive Insights", level=2)

    with st.expander("About this tab"):
        st.markdown("""
This tab will host **Machine Learning models** built on top of the Tiki and eBay datasets,
providing predictive and clustering insights as a **bonus analysis** component.

Planned features:

- **Best Seller Predictor (Tiki):** Logistic Regression / Random Forest to classify whether
  a listing will achieve Best Seller status based on price, discount rate, and category.
- **Price Cluster Analysis (eBay):** K-Means clustering to segment eBay listings into
  natural price-condition groupings.
- **Seller Trust Scoring:** Regression model to predict seller feedback score from
  listing characteristics.

> Models will be trained on the processed datasets and integrated with interactive
> parameter controls (feature selection, threshold sliders) once development is complete.
""")

    # ── Coming Soon Banner ───────────────────────────────────────────────────
    st.markdown("""
<div style="
    margin: 2.5rem auto;
    max-width: 620px;
    background: linear-gradient(135deg, rgba(13,148,136,.07) 0%, rgba(124,58,237,.06) 100%);
    border: 1.5px solid rgba(13,148,136,.2);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    text-align: center;
    backdrop-filter: blur(8px);
">
    <div style="font-size: 3rem; margin-bottom: 0.8rem;">🤖</div>
    <div style="
        font-size: 1.35rem;
        font-weight: 800;
        color: #0f766e;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    ">Machine Learning — Coming Soon</div>
    <div style="
        font-size: 0.88rem;
        color: #64748b;
        line-height: 1.7;
        max-width: 420px;
        margin: 0 auto;
    ">
        Predictive models and clustering analysis are currently under development.<br>
        This tab will be activated once model training and validation are complete.
    </div>
    <div style="
        margin-top: 1.4rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(13,148,136,.10);
        border: 1px solid rgba(13,148,136,.22);
        border-radius: 20px;
        padding: 0.35rem 1rem;
        font-size: 0.75rem;
        font-weight: 700;
        color: #0d9488;
        letter-spacing: 0.04em;
    ">
        <span style="
            width: 7px; height: 7px; border-radius: 50%;
            background: #0d9488;
            display: inline-block;
            animation: pulse-dot 1.4s infinite;
        "></span>
        IN DEVELOPMENT
    </div>
</div>
<style>
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(0.75); }
}
</style>
""", unsafe_allow_html=True)

    # ── Planned model cards ──────────────────────────────────────────────────
    st.markdown("#### Planned Models")
    c1, c2, c3 = st.columns(3)

    _model_card(c1,
        icon="fa-solid fa-tags",
        title="Best Seller Predictor",
        platform="Tiki",
        desc="Classify listings likely to achieve Best Seller status using price, discount rate, and category features.",
        algo="Logistic Regression + Random Forest",
        status="Planned",
        color="#0d9488",
    )
    _model_card(c2,
        icon="fa-solid fa-object-group",
        title="Price Clustering",
        platform="eBay",
        desc="Segment eBay listings into natural price-condition clusters to identify market tiers.",
        algo="K-Means (k=4–6)",
        status="Planned",
        color="#7c3aed",
    )
    _model_card(c3,
        icon="fa-solid fa-shield-halved",
        title="Trust Score Model",
        platform="eBay",
        desc="Predict seller feedback score from listing volume, shipping policy, and price tier.",
        algo="Gradient Boosting Regressor",
        status="Planned",
        color="#f97316",
    )


def _model_card(
    col,
    icon: str,
    title: str,
    platform: str,
    desc: str,
    algo: str,
    status: str,
    color: str,
) -> None:
    with col:
        st.markdown(f"""
<div style="
    background: rgba(255,255,255,.85);
    border: 1px solid rgba(0,0,0,.07);
    border-top: 3px solid {color};
    border-radius: 12px;
    padding: 1.2rem 1rem 1rem;
    height: 100%;
    backdrop-filter: blur(8px);
    box-shadow: 0 2px 8px rgba(0,0,0,.05);
">
    <div style="display:flex; align-items:center; gap:.5rem; margin-bottom:.6rem;">
        <i class="{icon}" style="color:{color}; font-size:1.1rem;"></i>
        <span style="font-weight:800; font-size:.88rem; color:#0f172a;">{title}</span>
    </div>
    <div style="
        font-size:.67rem; font-weight:700; text-transform:uppercase;
        letter-spacing:.06em; color:{color}; margin-bottom:.5rem;
    ">{platform}</div>
    <div style="font-size:.78rem; color:#475569; line-height:1.55; margin-bottom:.75rem;">{desc}</div>
    <div style="font-size:.70rem; color:#94a3b8;">
        <b>Algorithm:</b> {algo}
    </div>
    <div style="
        margin-top:.7rem; display:inline-block;
        background: rgba(0,0,0,.04); border-radius:10px;
        padding: 2px 8px; font-size:.65rem; font-weight:700;
        color:#94a3b8; text-transform:uppercase; letter-spacing:.05em;
    ">{status}</div>
</div>
""", unsafe_allow_html=True)
