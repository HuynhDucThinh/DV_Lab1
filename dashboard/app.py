"""
app.py — Dashboard entry point / pure orchestrator.

Responsibility: wire the modules together in the correct order.
All UI logic lives in components/ and styles/.

Render sequence:
  1. Global CSS + Font Awesome
  2. Colorblind body class (JS, no reload)
  3. Session state: consume query-param actions (cb= / sb=)
  4. Sidebar (rendered only when visible; provides filters)
  5. Hero banner
  6. Show Panel trigger (only when sidebar hidden)
  7. Tab content
  8. Footer
"""

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from styles import GLOBAL_CSS, FA_HTML, SHIMMER

from components.header     import inject_colorblind_class, render_hero, render_show_panel
from components.sidebar    import render_sidebar
from components.navigation import consume_header_actions, _get_active_tab, render_tab_content
from components.footer     import render_footer


# ── Default filters used when sidebar is hidden ───────────────────────────────
_DEFAULT_FILTERS: dict = {
    "platform":    ["Tiki", "eBay"],
    "price_range": (0, 10_000_000),
}

st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/svgs/solid/chart-column.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    # 1. Global CSS + icons
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    st.html(FA_HTML)

    # 2. Colorblind body class
    inject_colorblind_class()

    # 3. Query-param actions (cb=toggle, sb=toggle)
    consume_header_actions()

    # 4. Sidebar state + filters
    sidebar_hidden = bool(st.session_state.get("sidebar_hidden", False))
    filters = render_sidebar() if not sidebar_hidden else _DEFAULT_FILTERS

    # 5. Active tab
    active_tab = _get_active_tab()

    # 6. Hero banner
    render_hero()

    # 7. Show Panel trigger (invisible; hover top-left to reveal)
    if sidebar_hidden:
        render_show_panel()

    # 7. Tab content
    render_tab_content(active_tab, filters)

    # 8. Footer
    render_footer()


if __name__ == "__main__":
    main()