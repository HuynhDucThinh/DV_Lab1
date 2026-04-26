"""
Compatibility shim — repo-root/data/loaders.py
================================================
Streamlit Cloud puts the repo root on sys.path, so Python resolves
`data` as this package (repo-root/data/) instead of dashboard/data/.

This shim loads the *real* loaders.py directly from dashboard/data/
using importlib so there is no circular-import risk, then re-exports
every public function into this module's namespace.
"""
import os as _os, sys as _sys, importlib.util as _ilu

_REAL_FILE = _os.path.normpath(
    _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                  "..", "dashboard", "data", "loaders.py")
)

# Make sure dashboard/ is on sys.path (needed by loaders.py → config.py)
_DASHBOARD = _os.path.dirname(_os.path.dirname(_REAL_FILE))
if _DASHBOARD not in _sys.path:
    _sys.path.insert(0, _DASHBOARD)

# Load the real module without touching sys.modules['data.loaders']
_spec = _ilu.spec_from_file_location("_data_loaders_real", _REAL_FILE)
_mod  = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Re-export everything
load_tiki_ebay = _mod.load_tiki_ebay  # noqa: F401
load_4_tables  = _mod.load_4_tables   # noqa: F401
load_5_tables  = _mod.load_5_tables   # noqa: F401
load_kpi_data  = _mod.load_kpi_data   # noqa: F401
