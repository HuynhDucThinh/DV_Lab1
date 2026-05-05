"""tabs — Individual dashboard tab renderers."""

# Path bootstrap (Streamlit Cloud fix)
# ROOT (dv_lab1/) must be at sys.path[0] so that `from data.loaders import ...`
# in all tab files resolves to dv_lab1/data/loaders.py (root package),
# NOT dv_lab1/dashboard/data/loaders.py (dashboard-local package).
# DASHBOARD (dv_lab1/dashboard/) is kept in path for styles/, components/, config etc.
import sys as _sys, os as _os, importlib as _il
_DASHBOARD_DIR = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_ROOT_DIR      = _os.path.dirname(_DASHBOARD_DIR)
for _p in [_DASHBOARD_DIR, _ROOT_DIR]:
    if _p in _sys.path:
        _sys.path.remove(_p)
_sys.path.insert(0, _DASHBOARD_DIR)   # index 1: dashboard/ for local modules
_sys.path.insert(0, _ROOT_DIR)        # index 0: dv_lab1/ → data.loaders resolves here
_stale = ("data", "data.loaders", "data.filters", "config", "styles")
for _mod in _stale:
    _sys.modules.pop(_mod, None)
_il.invalidate_caches()   # flushes sys.path_importer_cache
del _sys, _os, _il, _DASHBOARD_DIR, _ROOT_DIR, _stale, _mod

# NOTE: We do NOT eagerly import tab submodules here.
# navigation.py already does 'from tabs import tab0_overview, ...' lazily
# inside render_tab_content(), so tabs are imported on-demand at call time,
# after sys.path is fully set up.  Eager imports here would trigger module-
# level 'from data.loaders import ...' before path_importer_cache is warm.

__all__ = [
    "tab0_overview", "tab1_pricing", "tab2_trust",
    "tab3_trends",  "tab4_ml",       "tab5_summary",
]
