"""components — Reusable Streamlit UI building blocks."""

# Path bootstrap (Streamlit Cloud fix)
# Streamlit Cloud sets CWD = repo root, not dashboard/.  We insert dashboard/
# at sys.path[0] AND evict any stale namespace-package ghost that Python may
# have already cached for the repo-root data/ folder (no __init__.py there).
import sys as _sys, os as _os, importlib as _il
_DASHBOARD_DIR = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _DASHBOARD_DIR not in _sys.path:
    _sys.path.insert(0, _DASHBOARD_DIR)
# Evict stale namespace-package cache entries, then invalidate Python's
# internal path_importer_cache so the new sys.path entry is picked up.
_stale = ("data", "data.loaders", "data.filters", "config", "styles")
for _mod in _stale:
    _sys.modules.pop(_mod, None)
_il.invalidate_caches()   # ← flushes sys.path_importer_cache
del _sys, _os, _il, _DASHBOARD_DIR, _stale, _mod

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
