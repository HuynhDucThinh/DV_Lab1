import streamlit as st
from typing import Dict, Any

from components.navigation import _get_active_tab

# Sidebar widget dark-theme overrides
_SIDEBAR_CSS = """
<style>
/* Label text (Platform / Price Range) */
section[data-testid="stSidebar"] label p {
  color: rgba(255,255,255,.48) !important;
  font-size: 0.74rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
}

/* Remove Streamlit's built-in top padding inside the sidebar scroll area */
section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
section[data-testid="stSidebar"] > div:first-child > div:first-child,
section[data-testid="stSidebar"] > div > div > div,
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
  padding-top: 0 !important;
  margin-top: 0 !important;
}

/* Multiselect outer container */
section[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {
  background: rgba(255,255,255,.07) !important;
  border: 1px solid rgba(255,255,255,.15) !important;
  border-radius: 10px !important;
  box-shadow: none !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"]:focus-within > div:first-child {
  border-color: #0d9488 !important;
  box-shadow: 0 0 0 2px rgba(13,148,136,.25) !important;
}
/* Chip/tag */
section[data-testid="stSidebar"] [data-baseweb="tag"] {
  background: rgba(13,148,136,.30) !important;
  border: 1px solid rgba(13,148,136,.55) !important;
  border-radius: 5px !important;
}
section[data-testid="stSidebar"] [data-baseweb="tag"] span {
  color: #5eead4 !important;
  font-weight: 700 !important;
  font-size: 0.74rem !important;
}
/* Remove red focus outline from baseweb */
section[data-testid="stSidebar"] [data-baseweb="select"] *:focus {
  outline: none !important;
  box-shadow: none !important;
}
/* Input inside multiselect */
section[data-testid="stSidebar"] [data-baseweb="select"] input {
  color: rgba(255,255,255,.85) !important;
  background: transparent !important;
}
/* Chevron SVG */
section[data-testid="stSidebar"] [data-baseweb="select"] svg {
  fill: rgba(255,255,255,.45) !important;
}

/* Slider thumb */
section[data-testid="stSidebar"] [role="slider"] {
  background: #0d9488 !important;
  border: 2px solid #fff !important;
  box-shadow: 0 0 0 3px rgba(13,148,136,.4) !important;
}
/* Slider tick labels */
section[data-testid="stSidebar"] [data-testid="stTickBarMin"],
section[data-testid="stSidebar"] [data-testid="stTickBarMax"] {
  color: rgba(255,255,255,.32) !important;
  font-size: 0.62rem !important;
}
/* Value bubble above thumb */
section[data-testid="stSidebar"] [data-testid="stThumbValue"] p {
  color: rgba(255,255,255,.55) !important;
  font-size: 0.66rem !important;
  background: transparent !important;
}

/* Help tooltip icon */
section[data-testid="stSidebar"] [data-testid="stTooltipIcon"] svg {
  fill: rgba(255,255,255,.22) !important;
}

/* Colorblind toggle button */
section[data-testid="stSidebar"] [data-testid="stButton"][aria-label] button,
section[data-testid="stSidebar"] button[kind="secondary"] {
  background: rgba(255,255,255,.06) !important;
  border: 1px solid rgba(255,255,255,.12) !important;
  color: rgba(255,255,255,.7) !important;
  border-radius: 10px !important;
  font-size: 0.78rem !important;
  font-weight: 600 !important;
  transition: background 0.18s, border-color 0.18s !important;
}
section[data-testid="stSidebar"] button[kind="secondary"]:hover {
  background: rgba(13,148,136,.18) !important;
  border-color: rgba(13,148,136,.45) !important;
  color: #5eead4 !important;
}
</style>
"""

# Tab navigation items: (key, fa_icon_class, label)
_NAV_ITEMS = [
    ("overview", "fa-solid fa-gauge-high",      "Overview"),
    ("pricing",  "fa-solid fa-tags",             "Pricing & Promotions"),
    ("trust",    "fa-solid fa-shield-halved",    "Trust & Reputation"),
    ("trends",   "fa-solid fa-chart-line",       "Characteristics & Trends"),
    ("ml",       "fa-solid fa-brain",            "Machine Learning"),
    ("summary",  "fa-solid fa-flag-checkered",   "Summary & Conclusion"),
]


def render_sidebar() -> Dict[str, Any]:
    """Render the premium dark-themed sidebar with navigation + filters."""

    # Inject widget-only CSS overrides
    st.sidebar.markdown(_SIDEBAR_CSS, unsafe_allow_html=True)

    # Brand header: logo+name (left) | ✕ Close (right)
    # Both in the same column row so ✕ appears level with "E-commerce Analytics"
    c_brand, c_close = st.sidebar.columns([5, 1])

    with c_brand:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:0.75rem;padding:0.55rem 0.3rem 0.4rem;">'
            '<div style="width:44px;height:44px;flex-shrink:0;'
            'background:linear-gradient(135deg,#0d9488,#0f766e);border-radius:12px;'
            'display:flex;align-items:center;justify-content:center;'
            'box-shadow:0 4px 16px rgba(13,148,136,.55),0 0 0 1px rgba(255,255,255,.1);">'
            '<i class="fa-solid fa-store" style="color:#fff;font-size:1.1rem;"></i>'
            '</div>'
            '<div>'
            '<div style="font-size:1rem;font-weight:800;color:#fff;'
            'line-height:1.15;letter-spacing:-0.02em;">E-commerce Analytics</div>'
            '<div style="font-size:0.66rem;color:rgba(255,255,255,.38);'
            'letter-spacing:0.05em;margin-top:0.1rem;">Multi-Platform Intelligence</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with c_close:
        # CSS to vertically center ✕ with the brand block height (~66px)
        st.markdown(
            '<style>'
            'section[data-testid="stSidebar"]'
            ' [data-testid="stHorizontalBlock"]'
            ' > [data-testid="stColumn"]:last-child {'
            '  display:flex !important;'
            '  align-items:center !important;'
            '  justify-content:flex-end !important;'
            '  padding-top:0.55rem !important;'
            '}'
            '</style>',
            unsafe_allow_html=True,
        )
        if st.button("✕", key="close_sidebar_btn", help="Close Panel"):
            st.session_state["sidebar_hidden"] = True
            st.rerun()

    # Platform badges — rendered below the brand row
    st.sidebar.markdown(
        '<div style="display:flex;gap:0.45rem;padding:0 0.6rem 0.8rem;">'
        '<div style="display:flex;align-items:center;gap:0.35rem;'
        'background:rgba(13,148,136,.18);border:1px solid rgba(13,148,136,.35);'
        'border-radius:20px;padding:0.24rem 0.72rem;'
        'font-size:0.68rem;font-weight:700;color:#5eead4;">'
        '<span style="width:5px;height:5px;border-radius:50%;'
        'background:#5eead4;flex-shrink:0;"></span>Tiki'
        '</div>'
        '<div style="display:flex;align-items:center;gap:0.35rem;'
        'background:rgba(249,115,22,.15);border:1px solid rgba(249,115,22,.3);'
        'border-radius:20px;padding:0.24rem 0.72rem;'
        'font-size:0.68rem;font-weight:700;color:#fb923c;">'
        '<span style="width:5px;height:5px;border-radius:50%;'
        'background:#fb923c;flex-shrink:0;"></span>eBay'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Thin gradient divider
    st.sidebar.markdown(
        '<div style="height:1px;background:linear-gradient(90deg,'
        'transparent,rgba(255,255,255,.09),transparent);'
        'margin:0 0 0.75rem;"></div>',
        unsafe_allow_html=True,
    )

    # Section label: NAVIGATION
    st.sidebar.markdown(
        '<div style="font-size:0.62rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:rgba(255,255,255,.28);'
        'display:flex;align-items:center;gap:0.45rem;margin-bottom:0.5rem;'
        'padding:0 0.6rem;">'
        '<i class="fa-solid fa-compass" style="color:rgba(255,255,255,.28);'
        'font-size:0.65rem;"></i>Navigation</div>',
        unsafe_allow_html=True,
    )

    # Navigation links
    active_tab = _get_active_tab()
    nav_rows = ""
    for key, icon, label in _NAV_ITEMS:
        is_active = active_tab == key
        bg      = "linear-gradient(135deg,#0d9488,#0a7c6e)" if is_active else "rgba(255,255,255,.04)"
        border  = "rgba(13,148,136,.5)" if is_active else "rgba(255,255,255,.07)"
        color   = "#ffffff" if is_active else "rgba(255,255,255,.6)"
        shadow  = "0 4px 14px rgba(13,148,136,.35)" if is_active else "none"
        nav_rows += (
            f"<a href='?tab={key}' target='_self' style='"
            f"display:flex;align-items:center;gap:0.6rem;"
            f"background:{bg};border:1px solid {border};border-radius:9px;"
            f"padding:0.52rem 0.75rem;margin-bottom:0.3rem;"
            f"text-decoration:none;color:{color};font-size:0.82rem;font-weight:700;"
            f"box-shadow:{shadow};transition:all .18s;'>"
            f"<i class='{icon}' style='font-size:0.85rem;width:16px;text-align:center;'></i>"
            f"{label}</a>"
        )

    st.sidebar.markdown(
        f'<div style="padding:0 0.6rem 0.2rem;">{nav_rows}</div>',
        unsafe_allow_html=True,
    )

    # thin gradient divider
    st.sidebar.markdown(
        '<div style="height:1px;background:linear-gradient(90deg,'
        'transparent,rgba(255,255,255,.09),transparent);'
        'margin:0.75rem 0 1rem;"></div>',
        unsafe_allow_html=True,
    )

    # Section label: GLOBAL FILTERS
    st.sidebar.markdown(
        '<div style="font-size:0.62rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:rgba(255,255,255,.28);'
        'display:flex;align-items:center;gap:0.45rem;margin-bottom:0.6rem;">'
        '<i class="fa-solid fa-sliders" style="color:rgba(255,255,255,.28);'
        'font-size:0.65rem;"></i>Global Filters</div>',
        unsafe_allow_html=True,
    )

    platform = st.sidebar.multiselect(
        "Platform",
        ["Tiki", "eBay"],
        default=["Tiki", "eBay"],
        help="Select one or both platforms.",
    )

    st.sidebar.markdown('<div style="margin-top:0.55rem;"></div>',
                        unsafe_allow_html=True)

    price_range = st.sidebar.slider(
        "Price Range (VND)",
        min_value=0,
        max_value=50_000_000,
        value=(0, 10_000_000),
        step=500_000,
        help="Filter all listings by total price.",
    )

    # Active scope summary
    lo_m, hi_m = price_range[0] / 1e6, price_range[1] / 1e6

    plat_parts = []
    if "Tiki" in platform:
        plat_parts.append(
            '<span style="color:#5eead4;font-weight:700;font-size:0.72rem;">'
            '<i class="fa-solid fa-circle" style="font-size:0.38rem;'
            'vertical-align:middle;margin-right:0.22rem;"></i>Tiki</span>'
        )
    if "eBay" in platform:
        plat_parts.append(
            '<span style="color:#fb923c;font-weight:700;font-size:0.72rem;">'
            '<i class="fa-solid fa-circle" style="font-size:0.38rem;'
            'vertical-align:middle;margin-right:0.22rem;"></i>eBay</span>'
        )
    platform_html = (
        ' <span style="color:rgba(255,255,255,.18);margin:0 0.25rem;">|</span> '.join(plat_parts)
        if plat_parts
        else '<span style="color:#ef4444;font-size:0.72rem;">None</span>'
    )

    st.sidebar.markdown(
        f"""
        <div style="
          background:linear-gradient(135deg,rgba(13,148,136,.13),rgba(13,148,136,.05));
          border:1px solid rgba(13,148,136,.22);
          border-radius:10px;padding:0.72rem 0.85rem;margin-top:0.75rem;
        ">
          <div style="font-size:0.61rem;font-weight:700;letter-spacing:0.09em;
                      text-transform:uppercase;color:rgba(255,255,255,.3);
                      margin-bottom:0.5rem;">
            <i class="fa-solid fa-filter" style="color:#0d9488;margin-right:0.35rem;"></i>
            Active Scope
          </div>
          <div style="display:flex;flex-direction:column;gap:0.35rem;">
            <div style="display:flex;align-items:center;justify-content:space-between;">
              <span style="font-size:0.68rem;color:rgba(255,255,255,.36);">
                <i class="fa-solid fa-layer-group" style="margin-right:0.3rem;"></i>Platform
              </span>
              <span>{platform_html}</span>
            </div>
            <div style="height:1px;background:rgba(255,255,255,.05);"></div>
            <div style="display:flex;align-items:center;justify-content:space-between;">
              <span style="font-size:0.68rem;color:rgba(255,255,255,.36);">
                <i class="fa-solid fa-tag" style="margin-right:0.3rem;"></i>Price
              </span>
              <span style="font-size:0.72rem;font-weight:600;
                           color:rgba(255,255,255,.75);">
                {lo_m:.1f}M &ndash; {hi_m:.1f}M&nbsp;VND
              </span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # thin gradient divider
    st.sidebar.markdown(
        '<div style="height:1px;background:linear-gradient(90deg,'
        'transparent,rgba(255,255,255,.09),transparent);'
        'margin:1rem 0;"></div>',
        unsafe_allow_html=True,
    )

    # Section label: DATASET
    st.sidebar.markdown(
        '<div style="font-size:0.62rem;font-weight:700;letter-spacing:0.12em;'
        'text-transform:uppercase;color:rgba(255,255,255,.28);'
        'display:flex;align-items:center;gap:0.45rem;margin-bottom:0.6rem;">'
        '<i class="fa-solid fa-database" style="color:rgba(255,255,255,.28);'
        'font-size:0.65rem;"></i>Dataset</div>',
        unsafe_allow_html=True,
    )

    _stats = [
        ("fa-solid fa-boxes-stacked", "#5eead4", "25,744",   "total listings"),
        ("fa-solid fa-layer-group",   "#fb923c", "2",        "platforms"),
        ("fa-solid fa-calendar-days", "#c4b5fd", "Apr 2026", "snapshot"),
        ("fa-solid fa-users",         "#93c5fd", "6,858",    "eBay sellers"),
    ]

    rows_html = ""
    for fa_cls, clr, val, lbl in _stats:
        rows_html += (
            f'<div style="display:flex;align-items:center;gap:0.6rem;'
            f'padding:0.42rem 0.65rem;border-radius:8px;margin-bottom:0.3rem;'
            f'background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.04);">'
            f'<div style="width:26px;height:26px;border-radius:7px;flex-shrink:0;'
            f'background:rgba(255,255,255,.07);'
            f'display:flex;align-items:center;justify-content:center;">'
            f'<i class="{fa_cls}" style="font-size:0.7rem;color:{clr};"></i>'
            f'</div>'
            f'<div>'
            f'<div style="font-size:0.82rem;font-weight:700;'
            f'color:rgba(255,255,255,.85);line-height:1.1;">{val}</div>'
            f'<div style="font-size:0.63rem;color:rgba(255,255,255,.33);">{lbl}</div>'
            f'</div></div>'
        )
    st.sidebar.markdown(rows_html, unsafe_allow_html=True)

    # Colorblind Mode Toggle
    st.sidebar.markdown(
        '<div style="height:1px;background:linear-gradient(90deg,'
        'transparent,rgba(255,255,255,.09),transparent);'
        'margin:1rem 0;"></div>',
        unsafe_allow_html=True,
    )

    cb_on = bool(st.session_state.get("colorblind_mode", False))
    #cb_label = "Mù màu: Bật" if cb_on else "Mù màu: Tắt"
    cb_label = "Coloblind mode: ON" if cb_on else "Coloblind mode: OFF"

    #cb_help  = "Nhấn để tắt chế độ mù màu" if cb_on else "Nhấn để bật chế độ mù màu (Deuteranopia-safe)"
    cb_help  = "Press to turn off colorblind mode" if cb_on else "Press to turn on colorblind mode (Deuteranopia-safe)"
    if st.sidebar.button(cb_label, key="cb_toggle_btn", help=cb_help, use_container_width=True):
        st.session_state["colorblind_mode"] = not cb_on
        st.rerun()

    # Footer
    st.sidebar.markdown(
        """
        <div style="margin-top:1.4rem;padding:0.85rem 0.5rem 0.6rem;
                    border-top:1px solid rgba(255,255,255,.06);text-align:center;">
          <div style="
            display:inline-flex;align-items:center;gap:0.4rem;
            background:rgba(13,148,136,.12);border:1px solid rgba(13,148,136,.2);
            border-radius:20px;padding:0.22rem 0.72rem;
            font-size:0.64rem;font-weight:700;color:#5eead4;margin-bottom:0.45rem;
          ">
            <span style="width:6px;height:6px;border-radius:50%;background:#22c55e;
                         box-shadow:0 0 0 2px rgba(34,197,94,.3);flex-shrink:0;"></span>
            Live Dashboard
          </div>
          <div style="font-size:0.62rem;color:rgba(255,255,255,.2);line-height:1.75;">
            <i class="fa-solid fa-code" style="margin-right:0.3rem;"></i>
            Data Visualization Lab &mdash; 2026<br>
            <i class="fa-solid fa-shield-halved" style="margin-right:0.3rem;"></i>
            Research &amp; Academic Use Only
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return {"platform": platform, "price_range": price_range}
