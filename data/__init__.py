"""
repo-root/data/__init__.py — Streamlit Cloud compatibility shim.

Streamlit Cloud adds the repo root to sys.path, so Python may resolve
`data` to this directory instead of dashboard/data/.

Fix: redirect __path__ to dashboard/data/ so that every submodule
lookup (data.loaders, data.filters) resolves to the real files.
Then exec the real __init__.py — since __package__ is already 'data'
and __path__ now points to dashboard/data/, relative imports inside
the exec'd code work correctly.
"""
import os as _os, sys as _sys

_HERE    = _os.path.dirname(_os.path.abspath(__file__))
_DB_DATA = _os.path.normpath(_os.path.join(_HERE, "..", "dashboard", "data"))
_DB      = _os.path.dirname(_DB_DATA)

# Make sure dashboard/ is importable (needed by config.py inside loaders.py)
if _DB not in _sys.path:
    _sys.path.insert(0, _DB)

# KEY FIX: tell Python that this package's submodules live in dashboard/data/
# so `from data.loaders import …` finds dashboard/data/loaders.py directly.
__path__ = [_DB_DATA]

# Populate this namespace by running the real dashboard/data/__init__.py.
# __package__ == 'data' here, and __path__ == [dashboard/data/],
# so `from .loaders import …` inside the file resolves correctly.
exec(  # noqa: S102
    compile(
        open(_os.path.join(_DB_DATA, "__init__.py")).read(),
        _os.path.join(_DB_DATA, "__init__.py"),
        "exec",
    )
)
