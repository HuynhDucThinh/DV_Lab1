"""tabs — Individual dashboard tab renderers."""

# ── Path bootstrap (Streamlit Cloud fix) ─────────────────────────────────────
# Mirror of components/__init__.py bootstrap.
# Ensures dashboard/ is on sys.path and any stale namespace-package for
# repo-root data/ (no __init__.py) is evicted before tab modules run their
# module-level imports (from data.loaders import …, from config import …).
import sys as _sys, os as _os
_DASHBOARD_DIR = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _DASHBOARD_DIR not in _sys.path:
    _sys.path.insert(0, _DASHBOARD_DIR)
_stale = ("data", "data.loaders", "data.filters", "config", "styles")
for _mod in _stale:
    _sys.modules.pop(_mod, None)
del _sys, _os, _DASHBOARD_DIR, _stale, _mod
# ─────────────────────────────────────────────────────────────────────────────

from . import tab0_overview, tab1_pricing, tab2_trust, tab3_trends, tab4_ml, tab5_summary

__all__ = ["tab0_overview", "tab1_pricing", "tab2_trust", "tab3_trends", "tab4_ml", "tab5_summary"]

