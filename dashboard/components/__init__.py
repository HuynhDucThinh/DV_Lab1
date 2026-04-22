"""components — Reusable Streamlit UI building blocks."""

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
