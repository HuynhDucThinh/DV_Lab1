"""
repo-root/data/__init__.py — Streamlit Cloud path shim.

Sets __path__ to dashboard/data/ so Python resolves
data.loaders → dashboard/data/loaders.py
data.filters → dashboard/data/filters.py
"""
import os as _os, sys as _sys

_HERE    = _os.path.dirname(_os.path.abspath(__file__))
_DB_DATA = _os.path.normpath(_os.path.join(_HERE, "..", "dashboard", "data"))
_DB      = _os.path.dirname(_DB_DATA)

if _DB not in _sys.path:
    _sys.path.insert(0, _DB)

# This is the only line that matters:
# redirect ALL submodule lookups to dashboard/data/
__path__ = [_DB_DATA]
