"""
config.py — Shared constants for the dashboard.

All palette values and the processed-data directory are defined here once
so every module imports from this single source of truth.
"""

# ── Data directory (relative to dashboard/ after os.chdir in app.py) ─────────
DATA_DIR = "../data/processed"

# ── Colour palette ────────────────────────────────────────────────────────────
TEAL   = "#0d9488"
ORANGE = "#f97316"
BLUE   = "#3b82f6"
PURPLE = "#7c3aed"
RED    = "#ef4444"
AMBER  = "#f59e0b"
GREEN  = "#22c55e"
SLATE  = "#94a3b8"
DARK   = "#0f172a"
WHITE  = "#ffffff"
