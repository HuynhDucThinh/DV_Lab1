import os
import sys
import importlib

# On Streamlit Cloud the CWD is the repo root, not dashboard/.
# Inserting dashboard/ at index 0 ensures all sibling packages
# (data, components, styles, config) are importable regardless of CWD.
_DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
if _DASHBOARD_DIR not in sys.path:
    sys.path.insert(0, _DASHBOARD_DIR)
os.chdir(_DASHBOARD_DIR)

# Clear any stale 'data' package that Streamlit may have cached from the
# repo root before dashboard/ was inserted.  After this, the next
# `from data.loaders import …` finds dashboard/data/ (sys.path[0]) first.
for _k in list(sys.modules):
    if _k == "data" or _k.startswith("data."):
        sys.modules.pop(_k)
importlib.invalidate_caches()

import streamlit as st

from styles import GLOBAL_CSS, FA_HTML, SHIMMER

from components.header     import inject_colorblind_class, render_hero, render_show_panel
from components.sidebar    import render_sidebar
from components.navigation import consume_header_actions, _get_active_tab, render_tab_content
from components.footer     import render_footer

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
    st.markdown(FA_HTML, unsafe_allow_html=True)

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