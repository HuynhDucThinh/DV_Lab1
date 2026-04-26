"""
Compatibility shim — repo-root/data/__init__.py
================================================
Streamlit Cloud adds the repo root to sys.path.  Python therefore
resolves `import data` to THIS package (repo-root/data/) instead of
dashboard/data/.

Strategy: load dashboard/data/__init__.py directly via importlib.util
(no circular-import risk), register it as sys.modules['data'], and
re-export all public names so that both

    from data import load_4_tables
    from data.loaders import load_4_tables

continue to work.  The submodule shims (loaders.py / filters.py) next
to this file handle the dotted-submodule case.
"""
import os as _os, sys as _sys, importlib.util as _ilu

_REAL_INIT = _os.path.normpath(
    _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                  "..", "dashboard", "data", "__init__.py")
)
_DASHBOARD = _os.path.dirname(_os.path.dirname(_REAL_INIT))

if _DASHBOARD not in _sys.path:
    _sys.path.insert(0, _DASHBOARD)

# Load real package init without name collision
_spec = _ilu.spec_from_file_location("_data_real", _REAL_INIT)
_mod  = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Re-export all public names
globals().update({k: v for k, v in vars(_mod).items() if not k.startswith("__")})
