import pandas as pd
from typing import List

# Data directory (relative to dashboard/ after os.chdir in app.py)
DATA_DIR = "../data/processed"

# Colour palette — normal
TEAL   = "#0d9488"
ORANGE = "#f97316"
BLUE   = "#3b82f6"
PURPLE = "#7c3aed"
RED    = "#ef4444"
AMBER  = "#f59e0b"
GREEN  = "#22c55e"
SLATE  = "#94a3b8"
INDIGO = "#6366f1"
DARK   = "#0f172a"
WHITE  = "#ffffff"

# Colour palette — Deuteranopia-safe (colorblind mode)
CB_TEAL   = "#0077bb"   # safe blue  (replaces teal)
CB_ORANGE = "#ee7733"   # safe orange
CB_BLUE   = "#0077bb"
CB_PURPLE = "#aa3377"   # safe magenta
CB_RED    = "#cc3311"
CB_AMBER  = "#ee7733"
CB_GREEN  = "#009988"   # safe teal-green
CB_SLATE  = "#94a3b8"   # neutral — unchanged
CB_INDIGO = "#0077bb"


def get_chart_palette() -> dict:
    """
    Return the active colour palette based on colorblind_mode session state.
    Call once per render function and unpack the keys you need.

    Usage::
        pal = get_chart_palette()
        bar_color = pal["teal"]
        accent     = pal["orange"]
    """
    import streamlit as st  # local import — avoids circular at module load
    cb = bool(st.session_state.get("colorblind_mode", False))
    if cb:
        return {
            "teal":   CB_TEAL,
            "orange": CB_ORANGE,
            "blue":   CB_BLUE,
            "purple": CB_PURPLE,
            "red":    CB_RED,
            "amber":  CB_AMBER,
            "green":  CB_GREEN,
            "slate":  CB_SLATE,
            "indigo": CB_INDIGO,
        }
    return {
        "teal":   TEAL,
        "orange": ORANGE,
        "blue":   BLUE,
        "purple": PURPLE,
        "red":    RED,
        "amber":  AMBER,
        "green":  GREEN,
        "slate":  SLATE,
        "indigo": INDIGO,
    }

# Reference date for listing-age calculations (data collection cut-off)
REFERENCE_DATE: pd.Timestamp = pd.Timestamp("2026-04-01")

# Vietnamese tech/electronics keywords used to filter Tiki categories
TECH_KEYWORDS: List[str] = [
    "điện thoại", "laptop", "máy tính", "tai nghe", "loa", "thiết bị số",
    "phụ kiện số", "camera", "màn hình", "tivi", " tv ", "điện gia dụng",
    "cáp", "sạc", "pin", "bàn phím", "chuột", "máy ảnh", "máy in",
    "thiết bị mạng", "router", "modem", "smartwatch", "đồng hồ thông minh",
    "lắp ráp", "điện tử", "sim số", "máy sấy", "máy giặt", "tủ lạnh",
    "điều hòa", "bluetooth",
]

# Tiki rating tier config (Objective 7)
RATING_BINS   = [-0.001, 0, 3.0, 4.0, 5.0]
RATING_LABELS = ["No Rating (0)", "Low (1–3)", "Average (3–4)", "High (4–5)"]
RATING_COLORS = {
    "No Rating (0)": SLATE,
    "Low (1–3)":     RED,
    "Average (3–4)": AMBER,
    "High (4–5)":    TEAL,
}

# eBay seller tier config (Objective 8)
EBAY_TIERS  = ["Newcomer (1–500)", "Established (501–5K)", "Reputable (5K–50K)", "Elite (50K+)"]
EBAY_COLORS = {
    "Newcomer (1–500)":     SLATE,
    "Established (501–5K)": GREEN,
    "Reputable (5K–50K)":   AMBER,
    "Elite (50K+)":         INDIGO,
}
