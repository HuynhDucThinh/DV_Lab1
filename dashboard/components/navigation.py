import streamlit as st

# Tab definitions: (key, svg_icon_html, label)
# All SVGs use shadcn/lucide design language (stroke-based, 24x24 viewBox)
TAB_ITEMS = [
    (
        "overview",
        """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="7" height="7" rx="1"/>
          <rect x="14" y="3" width="7" height="7" rx="1"/>
          <rect x="3" y="14" width="7" height="7" rx="1"/>
          <rect x="14" y="14" width="7" height="7" rx="1"/>
        </svg>""",
        "Overview",
    ),
    (
        "pricing",
        """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="2" x2="12" y2="22"/>
          <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
        </svg>""",
        "Pricing",
    ),
    (
        "trust",
        """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          <path d="m9 12 2 2 4-4"/>
        </svg>""",
        "Trust",
    ),
    (
        "trends",
        """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
          <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
          <polyline points="16 7 22 7 22 13"/>
        </svg>""",
        "Trends",
    ),
    (
        "ml",
        """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="3"/>
          <path d="M12 2v3M12 19v3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12"/>
          <path d="M2 12h3M19 12h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12"/>
        </svg>""",
        "ML",
    ),
    (
        "summary",
        """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 3h18v18H3z" rx="2"/>
          <path d="M8 17l4-8 4 8"/>
          <path d="M10.5 13h3"/>
        </svg>""",
        "Summary",
    ),
]

# Tab key → shadcn tabs label mapping (for backward compat with ui.tabs)
TAB_KEY_TO_LABEL = {
    "overview": "Overview",
    "pricing":  "Pricing & Promotions",
    "trust":    "Trust & Reputation",
    "trends":   "Characteristics & Trends",
    "ml":       "Machine Learning",
    "summary":  "Summary & Conclusion",
}

LABEL_TO_TAB_KEY = {v: k for k, v in TAB_KEY_TO_LABEL.items()}


def _get_active_tab() -> str:
    """Read active tab from query params, falling back to session_state."""
    valid = {k for k, _, _ in TAB_ITEMS}
    default = "overview"

    raw_tab = None
    if hasattr(st, "query_params"):
        raw_tab = st.query_params.get("tab")
    else:
        raw_tab = st.experimental_get_query_params().get("tab", [None])[0]

    if isinstance(raw_tab, list):
        raw_tab = raw_tab[0] if raw_tab else None

    if raw_tab in valid:
        st.session_state["active_tab"] = raw_tab
    elif "active_tab" not in st.session_state:
        st.session_state["active_tab"] = default

    return st.session_state.get("active_tab", default)


def consume_header_actions() -> None:
    """
    Process one-shot query-param actions:
      ?cb=toggle  → flip colorblind_mode
      ?sb=toggle  → flip sidebar_hidden
    Both params are cleared after being consumed to avoid sticky state.
    """
    use_modern_qp = hasattr(st, "query_params")

    if use_modern_qp:
        cb_action = st.query_params.get("cb")
        sb_action = st.query_params.get("sb")
    else:
        params = st.experimental_get_query_params()
        cb_action = params.get("cb", [None])[0]
        sb_action = params.get("sb", [None])[0]

    changed = False

    if cb_action == "toggle":
        st.session_state["colorblind_mode"] = not bool(
            st.session_state.get("colorblind_mode", False)
        )
        changed = True

    if sb_action == "toggle":
        st.session_state["sidebar_hidden"] = not bool(
            st.session_state.get("sidebar_hidden", False)
        )
        changed = True

    if changed:
        if use_modern_qp:
            try:
                st.query_params.clear()
            except Exception:
                pass
        else:
            st.experimental_set_query_params()



def render_navigation() -> str:
    """
    Inject the hover-expand nav rail into the DOM.
    Returns the active tab key.
    """
    active_tab = _get_active_tab()

    items_html = []
    for key, icon_svg, label in TAB_ITEMS:
        active_cls = " is-active" if key == active_tab else ""
        items_html.append(
            f"<a class='ec-nav-item{active_cls}' href='?tab={key}' target='_self' title='{label}'>"
            f"<span class='ec-nav-icon'>{icon_svg}</span>"
            f"<span class='ec-nav-label'>{label}</span>"
            f"</a>"
        )

    # Sentinel div: CSS uses :has(._ec-nav-sentinel) to scope column padding
    st.markdown(
        "<div class='_ec-nav-sentinel' style='min-height:500px;width:72px;'></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='ec-nav-host'><nav class='ec-nav'>{''.join(items_html)}</nav></div>",
        unsafe_allow_html=True,
    )

    return active_tab


def render_tab_content(active_tab: str, filters: dict) -> None:
    """
    Dispatch rendering to the correct tab module based on active_tab key.
    Falls back to overview if the key is unknown.
    """
    from tabs import tab0_overview, tab1_pricing, tab2_trust, tab3_trends, tab4_ml, tab5_summary

    tab_map = {
        "overview": lambda: tab0_overview.render(filters),
        "pricing":  lambda: tab1_pricing.render(filters),
        "trust":    lambda: tab2_trust.render(filters),
        "trends":   lambda: tab3_trends.render(filters),
        "ml":       lambda: tab4_ml.render(filters),
        "summary":  lambda: tab5_summary.render(filters),
    }
    fn = tab_map.get(active_tab)
    if fn:
        fn()
    else:
        tab0_overview.render(filters)
