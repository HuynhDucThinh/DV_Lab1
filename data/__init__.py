"""
Compatibility shim — repo-root/data/__init__.py
================================================
WHY THIS FILE EXISTS
--------------------
Streamlit Cloud adds the *repo root* (/mount/src/dv_lab1/) to sys.path.
Because this directory has no __init__.py, Python treats it as a
**namespace package** — a deeply-cached internal object that cannot be
fully evicted by sys.modules.pop() or importlib.invalidate_caches().

Adding this __init__.py converts repo-root/data/ into a **regular package**
and gives us a hook to redirect all attribute lookups to the real
implementation in dashboard/data/.

HOW IT WORKS
------------
1. Insert dashboard/ at sys.path[0].
2. Flush Python's path-importer cache.
3. Pop the partially-initialised shim from sys.modules.
4. Re-import 'data' — Python now finds dashboard/data/ first.
5. Register the real module as sys.modules['data'] and
   re-export all its public names into this module's namespace.
"""
import sys as _sys, os as _os, importlib as _il

# ── Step 1: make sure dashboard/ is at the front of sys.path ─────────────────
_DASHBOARD = _os.path.normpath(
    _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "dashboard")
)
if _DASHBOARD not in _sys.path:
    _sys.path.insert(0, _DASHBOARD)

# ── Step 2: flush Python's internal directory-scanner cache ──────────────────
_il.invalidate_caches()

# ── Step 3 + 4: replace this shim with the real data package ─────────────────
_sys.modules.pop("data", None)          # remove partially-initialised shim
_sys.modules.pop("data.loaders", None)  # clean up any stale submodule refs
_sys.modules.pop("data.filters", None)

_real_data = _il.import_module("data")  # now resolves to dashboard/data/

# ── Step 5: make sys.modules['data'] point to the real package ───────────────
_sys.modules[__name__] = _real_data

# Re-export everything so "from data import X" still works on the rare
# code-path that holds a reference to this shim module object.
globals().update(
    {k: v for k, v in vars(_real_data).items() if not k.startswith("__")}
)
