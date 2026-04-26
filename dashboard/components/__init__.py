"""components — Reusable Streamlit UI building blocks."""

# Path bootstrap (Streamlit Cloud fix)
# Streamlit Cloud adds the REPO ROOT to sys.path, not dashboard/.
# We must insert dashboard/ here so sibling packages (data, config, styles)
# are importable when this __init__ is first imported.
import sys as _sys, os as _os
_DASHBOARD_DIR = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _DASHBOARD_DIR not in _sys.path:
    _sys.path.insert(0, _DASHBOARD_DIR)
del _sys, _os, _DASHBOARD_DIR

from .ui_helpers  import icon_header, fa_callout, stat_card
from .sidebar     import render_sidebar
from .header      import inject_colorblind_class, render_hero, render_show_panel, render_header
from .kpi_cards   import render_kpi_cards
from .navigation  import (
    render_navigation, render_tab_content,
    consume_header_actions, _get_active_tab,
    TAB_ITEMS, TAB_KEY_TO_LABEL, LABEL_TO_TAB_KEY,
)
from .footer      import render_footer

__all__ = [
    # ui helpers
    "icon_header", "fa_callout", "stat_card",
    # sidebar
    "render_sidebar",
    # header
    "inject_colorblind_class", "render_hero", "render_show_panel", "render_header",
    # kpi
    "render_kpi_cards",
    # navigation / routing
    "render_navigation", "render_tab_content",
    "consume_header_actions", "_get_active_tab",
    "TAB_ITEMS", "TAB_KEY_TO_LABEL", "LABEL_TO_TAB_KEY",
    # footer
    "render_footer",
]
