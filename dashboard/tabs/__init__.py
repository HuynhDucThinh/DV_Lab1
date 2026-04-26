"""tabs — Individual dashboard tab renderers."""

# Path bootstrap (Streamlit Cloud fix)
# Ensures dashboard/ is at sys.path[0] and flushes Python's internal
# path_importer_cache (via importlib.invalidate_caches) so that any
# namespace-package ghost cached for repo-root/data/ is fully evicted.
# Called here so the fix is active before any tab submodule is imported.
import sys as _sys, os as _os, importlib as _il
_DASHBOARD_DIR = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _DASHBOARD_DIR not in _sys.path:
    _sys.path.insert(0, _DASHBOARD_DIR)
_stale = ("data", "data.loaders", "data.filters", "config", "styles")
for _mod in _stale:
    _sys.modules.pop(_mod, None)
_il.invalidate_caches()   # ← KEY: flushes sys.path_importer_cache
del _sys, _os, _il, _DASHBOARD_DIR, _stale, _mod

# NOTE: We do NOT eagerly import tab submodules here.
# navigation.py already does 'from tabs import tab0_overview, ...' lazily
# inside render_tab_content(), so tabs are imported on-demand at call time,
# after sys.path is fully set up.  Eager imports here would trigger module-
# level 'from data.loaders import ...' before path_importer_cache is warm.

__all__ = [
    "tab0_overview", "tab1_pricing", "tab2_trust",
    "tab3_trends",  "tab4_ml",       "tab5_summary",
]
