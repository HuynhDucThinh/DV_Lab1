"""
Compatibility shim — repo-root/data/filters.py
================================================
Streamlit Cloud puts the repo root on sys.path, so Python resolves
`data` as this package (repo-root/data/) instead of dashboard/data/.

This shim loads the *real* filters.py directly from dashboard/data/
using importlib so there is no circular-import risk, then re-exports
every public function into this module's namespace.
"""
import os as _os, sys as _sys, importlib.util as _ilu

_REAL_FILE = _os.path.normpath(
    _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                  "..", "dashboard", "data", "filters.py")
)

# Make sure dashboard/ is on sys.path
_DASHBOARD = _os.path.dirname(_os.path.dirname(_REAL_FILE))
if _DASHBOARD not in _sys.path:
    _sys.path.insert(0, _DASHBOARD)

# Load the real module without touching sys.modules['data.filters']
_spec = _ilu.spec_from_file_location("_data_filters_real", _REAL_FILE)
_mod  = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Re-export everything
clean_numeric            = _mod.clean_numeric             # noqa: F401
apply_global_filters     = _mod.apply_global_filters      # noqa: F401
simplify_ebay_condition  = _mod.simplify_ebay_condition   # noqa: F401
simplify_condition_short = _mod.simplify_condition_short  # noqa: F401
