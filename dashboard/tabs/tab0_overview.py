"""
tab0_overview.py — Overview Tab  (redesigned — v2)

Design language aligned with tab3_trends.py:
  • Font Awesome 6 icons on every heading
  • Per-chart metric rows (st.metric)
  • Expandable "Insights & Recommendations" after each chart
  • Hero KPI banner at the top of the tab
  • _fa_callout() for highlighted insight boxes
  • Error-safe data loading with try/except

Four analytical sections
────────────────────────
  1. Platform Landscape   — Donut (share) + Top-8 Tiki Category bar
  2. Price Distribution   — Side-by-side box plots (Tiki vs eBay)
  3. eBay Condition Mix   — Grouped bar chart
  4. Key Market Signals   — Three inline KPI stat cards
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, Tuple

from components.ui_helpers import icon_header as _icon_header, fa_callout as _fa_callout, stat_card as _stat_card
from data.loaders import load_4_tables

# ── Palette (referenced by chart functions below) ──────────────────────────────
_TEAL   = "#0d9488"
_ORANGE = "#f97316"
_BLUE   = "#3b82f6"
_PURPLE = "#7c3aed"
_RED    = "#ef4444"
_SLATE  = "#94a3b8"
_DARK   = "#0f172a"
_BG     = "#ffffff"
_AMBER  = "#f59e0b"
_GREEN  = "#22c55e"

# ── Condition simplifier ──────────────────────────────────────────────────────

def _simplify_condition(cond: str) -> str | None:
    c = str(cond).lower().strip()
    if c == "new" or any(k in c for k in ["brand new", "new with tags", "new other"]):
        return "New"
    if any(k in c for k in ["used", "usato"]):
        return "Used"
    if any(k in c for k in [
        "refurbished", "open box", "opened", "certified",
        "good -", "excellent -", "very good -",
    ]):
        return "Refurbished"
    return None


# ── Hero banner ───────────────────────────────────────────────────────────────

def _render_hero(n_tiki: int, n_ebay: int, df_t: pd.DataFrame, df_e: pd.DataFrame) -> None:
    """Full-width KPI hero strip — first thing the user sees."""
    total      = n_tiki + n_ebay
    tiki_share = n_tiki / max(total, 1) * 100
    ebay_share = n_ebay / max(total, 1) * 100

    tiki_med = (
        df_t["price"].median() / 1_000_000
        if not df_t.empty and "price" in df_t.columns else 0.0
    )
    ebay_med = (
        df_e["Total_Cost_VND"].median() / 1_000_000
        if not df_e.empty and "Total_Cost_VND" in df_e.columns else 0.0
    )

    h1, h2, h3, h4 = st.columns(4)
    h1.metric("Total Listings",   f"{total:,}",            f"Tiki {tiki_share:.0f}% — eBay {ebay_share:.0f}%")
    h2.metric("Tiki Listings",    f"{n_tiki:,}",           "B2C marketplace")
    h3.metric("eBay Listings",    f"{n_ebay:,}",           "C2C / B2C hybrid")
    h4.metric("Median Price Gap", f"{abs(tiki_med - ebay_med):.1f}M VND",
              f"Tiki {tiki_med:.1f}M — eBay {ebay_med:.1f}M")


# ── Chart 1 helpers ──────────────────────────────────────────────────────────

def _chart_platform_donut(n_tiki: int, n_ebay: int) -> None:
    total = n_tiki + n_ebay
    fig = go.Figure(go.Pie(
        labels=["Tiki", "eBay"],
        values=[n_tiki, n_ebay],
        hole=0.65,
        marker=dict(colors=[_TEAL, _ORANGE], line=dict(color="#fff", width=2)),
        textinfo="label+percent",
        textfont=dict(size=12, family="Inter"),
        direction="clockwise",
    ))
    fig.update_layout(
        title=dict(text="Product Share by Platform", font=dict(size=13, family="Inter")),
        showlegend=False,
        margin=dict(t=50, b=10, l=10, r=10),
        height=290,
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text=f"<b>{total:,}</b><br><span style='font-size:10px'>listings</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=_DARK, family="Inter"),
        )],
    )
    st.plotly_chart(fig, width="stretch")


def _chart_tiki_categories(df_merged: pd.DataFrame) -> None:
    top = (
        df_merged[df_merged["category"] != "Unknown"]["category"]
        .value_counts()
        .head(8)
    )
    if top.empty:
        st.info("No category data available.")
        return

    colors = [_TEAL] + [f"rgba(13,148,136,{0.85 - i*0.09:.2f})" for i in range(1, 8)]

    fig = go.Figure(go.Bar(
        y=top.index.tolist(),
        x=top.values,
        orientation="h",
        marker=dict(color=colors[:len(top)]),
        text=top.values,
        textposition="outside",
        textfont=dict(size=11, family="Inter"),
    ))
    fig.update_layout(
        title=dict(text="Top 8 Tiki Categories — Listing Count", font=dict(size=13, family="Inter")),
        template="plotly_white",
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(autorange="reversed", showgrid=False),
        margin=dict(t=50, b=10, l=10, r=60),
        height=290,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")


# ── Chart 2 ──────────────────────────────────────────────────────────────────

def _chart_price_boxplot(tiki_p: np.ndarray, ebay_p: np.ndarray) -> None:
    rng    = np.random.default_rng(42)
    tiki_s = rng.choice(tiki_p, min(4_000, len(tiki_p)), replace=False) if len(tiki_p) else np.array([])
    ebay_s = rng.choice(ebay_p, min(4_000, len(ebay_p)), replace=False) if len(ebay_p) else np.array([])

    fig = go.Figure()
    if len(tiki_s):
        fig.add_trace(go.Box(
            y=tiki_s, name="Tiki",
            marker_color=_TEAL, line_color=_TEAL,
            boxmean=True, boxpoints="outliers",
            fillcolor="rgba(13,149,136,0.12)",
        ))
    if len(ebay_s):
        fig.add_trace(go.Box(
            y=ebay_s, name="eBay",
            marker_color=_ORANGE, line_color=_ORANGE,
            boxmean=True, boxpoints="outliers",
            fillcolor="rgba(249,115,22,0.12)",
        ))
    fig.update_layout(
        title=dict(text="Price Distribution — Tiki vs eBay (VND)", font=dict(size=13, family="Inter")),
        template="plotly_white",
        yaxis=dict(title="Price (VND)", showgrid=True, gridcolor="#f1f5f9"),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(family="Inter")),
        margin=dict(t=55, b=20, l=20, r=20),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")


# ── Chart 3 ──────────────────────────────────────────────────────────────────

def _chart_ebay_conditions(df_e: pd.DataFrame) -> None:
    df_e = df_e.copy()
    df_e["_cond"] = df_e["condition"].apply(_simplify_condition)
    counts = df_e["_cond"].dropna().value_counts().reset_index()
    counts.columns = ["Condition", "Count"]

    cmap = {"New": _BLUE, "Used": _SLATE, "Refurbished": _PURPLE}
    fig = px.bar(
        counts, x="Condition", y="Count",
        color="Condition", color_discrete_map=cmap,
        text="Count",
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=12, family="Inter"),
        marker_line_width=0,
    )
    fig.update_layout(
        title=dict(text="eBay Listings by Item Condition", font=dict(size=13, family="Inter")),
        template="plotly_white",
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(title="Listings", showgrid=True, gridcolor="#f1f5f9"),
        showlegend=False,
        margin=dict(t=50, b=15, l=20, r=20),
        height=310,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")


# ── Signal computation ────────────────────────────────────────────────────────

def _compute_signals(
    df_t: pd.DataFrame,
    df_e: pd.DataFrame,
    df_p: pd.DataFrame,
    df_c: pd.DataFrame,
) -> dict:
    # Stagnation risk (Tiki)
    if not df_t.empty and "quantity_sold" in df_t.columns:
        merged = (
            df_t
            .merge(df_p[["product_id", "category_id"]], on="product_id", how="left")
            .merge(df_c, on="category_id", how="left")
        )
        merged["category"] = merged["category"].fillna("Unknown")
        valid  = merged[merged["category"] != "Unknown"]
        cold   = valid[(valid["quantity_sold"] == 0) & (valid["review_count"] == 0)]
        stag   = len(cold) / max(len(valid), 1) * 100
    else:
        stag = 0.0

    # Tiki discount rate
    disc     = pd.to_numeric(df_t.get("discount_rate", pd.Series(dtype=float)), errors="coerce")
    disc_pct = (disc > 0).mean() * 100 if len(disc) else 0.0

    # eBay "New" share
    if not df_e.empty:
        conds   = df_e["condition"].apply(_simplify_condition)
        valid_e = conds.dropna()
        new_pct = (valid_e == "New").mean() * 100 if len(valid_e) else 0.0
    else:
        new_pct = 0.0

    return {"stag": stag, "disc": disc_pct, "new": new_pct}


# ── Main render ───────────────────────────────────────────────────────────────

def render(filters: Dict[str, Any]) -> None:
    """Overview tab — redesigned with tab3-aligned design language."""


    # ── Tab title ─────────────────────────────────────────────────────────────
    _icon_header(
        "fa-solid fa-gauge-high",
        "Market Overview Dashboard",
        level=2,
        color=_TEAL,
    )
    st.markdown(
        "A high-level summary of the **Tiki × eBay** e-commerce ecosystem — "
        "covering listing volumes, price architectures, item condition dynamics, "
        "and real-time market health signals."
    )

    # ── Load data ─────────────────────────────────────────────────────────────
    try:
        df_t_raw, df_e_raw, df_p, df_c = load_4_tables()
    except Exception as exc:
        st.error(f"Failed to load datasets: {exc}. Verify that `../data/processed/` is accessible.")
        return

    # Apply global sidebar filters
    platforms = filters.get("platform", ["Tiki", "eBay"])
    lo, hi    = filters.get("price_range", (0, 50_000_000))

    df_t = df_t_raw.copy()
    df_t["price"] = pd.to_numeric(df_t["price"], errors="coerce")
    df_t = (
        df_t[(df_t["price"] >= lo) & (df_t["price"] <= hi)].copy()
        if "Tiki" in platforms else df_t.iloc[0:0]
    )

    df_e = df_e_raw.copy()
    df_e["Total_Cost_VND"] = pd.to_numeric(df_e["Total_Cost_VND"], errors="coerce")
    df_e = (
        df_e[(df_e["Total_Cost_VND"] >= lo) & (df_e["Total_Cost_VND"] <= hi)].copy()
        if "eBay" in platforms else df_e.iloc[0:0]
    )

    # ── Hero KPI banner ───────────────────────────────────────────────────────
    st.markdown("---")
    _render_hero(len(df_t), len(df_e), df_t, df_e)
    st.markdown("---")

    # =====================================================================
    # SECTION 1 · Platform Landscape
    # =====================================================================
    _icon_header("fa-solid fa-chart-pie", "1. Platform Landscape", color=_TEAL)
    st.markdown(
        "Distribution of total listings across **Tiki** (B2C) and **eBay** (C2C/B2C hybrid), "
        "alongside the top Tiki product categories within the current filter scope."
    )

    # Metric row
    total = len(df_t) + len(df_e)
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Listings", f"{total:,}")
    m2.metric("Tiki Share", f"{len(df_t)/max(total,1)*100:.1f}%", f"{len(df_t):,} products")
    m3.metric("eBay Share",  f"{len(df_e)/max(total,1)*100:.1f}%", f"{len(df_e):,} products")

    col_donut, col_cats = st.columns([4, 6])

    with col_donut:
        with st.container(border=True):
            _chart_platform_donut(len(df_t), len(df_e))

    with col_cats:
        with st.container(border=True):
            if df_t.empty:
                st.info("No Tiki data in the current price range.")
            else:
                merged_t = (
                    df_t
                    .merge(df_p[["product_id", "category_id"]], on="product_id", how="left")
                    .merge(df_c, on="category_id", how="left")
                )
                merged_t["category"] = merged_t["category"].fillna("Unknown")
                _chart_tiki_categories(merged_t)

                with st.expander("Chart Insights & Recommendations"):
                    top_cat = (
                        merged_t[merged_t["category"] != "Unknown"]["category"]
                        .value_counts()
                        .head(3)
                    )
                    if not top_cat.empty:
                        st.markdown(
                            '<i class="fa-solid fa-magnifying-glass" style="color:#0d9488;'
                            'margin-right:0.4rem;"></i>**Key Findings**',
                            unsafe_allow_html=True,
                        )
                        names = top_cat.index.tolist()
                        st.markdown(
                            f"- The three most-listed categories on Tiki are "
                            f"**{names[0]}**, **{names[1]}**, and **{names[2]}**.\n"
                            f"- These top 3 account for "
                            f"**{top_cat.sum() / max(len(merged_t[merged_t['category'] != 'Unknown']), 1) * 100:.1f}%** "
                            f"of all categorised Tiki listings in scope."
                        )
                        st.markdown(
                            '<i class="fa-solid fa-lightbulb" style="color:#f59e0b;'
                            'margin-right:0.4rem;"></i>**Strategic Implication**',
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f"- High listing concentration in **{names[0]}** signals strong "
                            f"consumer demand — but also heightened price competition. "
                            f"Focus inventory differentiation here.\n"
                            f"- Lower-volume categories may offer untapped margin opportunities "
                            f"with less saturation."
                        )

    st.divider()

    # =====================================================================
    # SECTION 2 · Price Distribution
    # =====================================================================
    _icon_header("fa-solid fa-scale-balanced", "2. Price Distribution Comparison", color=_ORANGE)
    st.markdown(
        "Side-by-side box plots showing the **spread, median, and outlier structure** "
        "of prices on Tiki vs eBay. Diamonds (◆) represent the **mean**."
    )

    tiki_p = df_t["price"].dropna().values
    ebay_p = df_e["Total_Cost_VND"].dropna().values

    # Metric row
    p1, p2, p3 = st.columns(3)
    p1.metric(
        "Tiki Median Price",
        f"{np.median(tiki_p)/1e6:.2f}M VND" if len(tiki_p) else "N/A",
        f"{len(tiki_p):,} listings",
        delta_color="off",
    )
    p2.metric(
        "eBay Median Price",
        f"{np.median(ebay_p)/1e6:.2f}M VND" if len(ebay_p) else "N/A",
        f"{len(ebay_p):,} listings",
        delta_color="off",
    )
    if len(tiki_p) and len(ebay_p):
        gap = (np.median(ebay_p) - np.median(tiki_p)) / 1e6
        dirn = "eBay higher" if gap > 0 else "Tiki higher"
        p3.metric("Median Gap", f"{abs(gap):.2f}M VND", dirn)
    else:
        p3.metric("Median Gap", "N/A")

    with st.container(border=True):
        if len(tiki_p) == 0 and len(ebay_p) == 0:
            st.info("No price data available for the current filter selection.")
        else:
            _chart_price_boxplot(tiki_p, ebay_p)

    with st.expander("Chart Insights & Recommendations"):
        if len(tiki_p) and len(ebay_p):
            t_med, e_med = np.median(tiki_p), np.median(ebay_p)
            t_iqr = np.percentile(tiki_p, 75) - np.percentile(tiki_p, 25)
            e_iqr = np.percentile(ebay_p, 75) - np.percentile(ebay_p, 25)
            st.markdown(
                '<i class="fa-solid fa-magnifying-glass" style="color:#0d9488;'
                'margin-right:0.4rem;"></i>**Statistical Findings**',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"- **Tiki median**: {t_med/1e6:.2f}M VND · IQR: {t_iqr/1e6:.2f}M VND\n"
                f"- **eBay median**: {e_med/1e6:.2f}M VND · IQR: {e_iqr/1e6:.2f}M VND\n"
                f"- {'eBay listings carry a **price premium**' if e_med > t_med else 'Tiki listings are **priced higher overall**'} "
                f"on median by **{abs(e_med - t_med)/1e6:.2f}M VND**.\n"
                f"- {'eBay shows a wider IQR — greater pricing heterogeneity.' if e_iqr > t_iqr else 'Tiki shows a wider IQR — more pricing diversity.'}"
            )
            st.markdown(
                '<i class="fa-solid fa-lightbulb" style="color:#f59e0b;'
                'margin-right:0.4rem;"></i>**Pricing Strategy**',
                unsafe_allow_html=True,
            )
            st.markdown(
                "- Use the **IQR band** as the target price anchor for new listings — "
                "products priced beyond Q3 risk poor conversion without strong brand equity.\n"
                "- Outliers above the upper fence should be audited for pricing errors "
                "or legitimate premium positioning."
            )

    st.divider()

    # =====================================================================
    # SECTION 3 · eBay Condition Mix
    # =====================================================================
    _icon_header("fa-solid fa-layer-group", "3. eBay Item Condition Mix", color=_BLUE)
    st.markdown(
        "Breakdown of eBay listings by **item condition** (New · Used · Refurbished). "
        "Condition mix directly impacts price expectations and buyer trust signals."
    )

    if not df_e.empty:
        df_e_cond = df_e.copy()
        df_e_cond["_cond"] = df_e_cond["condition"].apply(_simplify_condition)
        cond_counts = df_e_cond["_cond"].dropna().value_counts()
        total_cond  = cond_counts.sum()
        dominant    = cond_counts.index[0] if not cond_counts.empty else "N/A"
        dom_pct     = cond_counts.iloc[0] / max(total_cond, 1) * 100 if not cond_counts.empty else 0.0

        # Metric row
        c1, c2, c3 = st.columns(3)
        c1.metric("Valid Condition Listings", f"{total_cond:,}")
        c2.metric("Dominant Condition", dominant)
        c3.metric("Dominant Share", f"{dom_pct:.1f}%")

        with st.container(border=True):
            _chart_ebay_conditions(df_e)

        with st.expander("Chart Insights & Recommendations"):
            st.markdown(
                '<i class="fa-solid fa-magnifying-glass" style="color:#0d9488;'
                'margin-right:0.4rem;"></i>**Market Composition**',
                unsafe_allow_html=True,
            )
            findings = []
            for cond, cnt in cond_counts.items():
                findings.append(f"- **{cond}**: {cnt:,} listings ({cnt/max(total_cond,1)*100:.1f}%)")
            st.markdown("\n".join(findings))
            st.markdown(
                '<i class="fa-solid fa-lightbulb" style="color:#f59e0b;'
                'margin-right:0.4rem;"></i>**Sourcing Recommendation**',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"- A **{dominant}**-dominant marketplace suggests buyers are primarily "
                f"seeking {'risk-free, warranty-backed products' if dominant == 'New' else 'value-priced alternatives'}.\n"
                "- **Refurbished** listings often carry the best margin potential "
                "if certification quality is assured — consider sourcing from verified eBay sellers.\n"
                "- Cross-validate condition labels against seller feedback scores (>98%) "
                "before committing to bulk procurement."
            )
    else:
        _fa_callout(
            "fa-solid fa-circle-exclamation", _ORANGE,
            "No eBay data available in the current filter range — adjust the sidebar."
        )

    st.divider()

    # =====================================================================
    # SECTION 4 · Key Market Signals
    # =====================================================================
    _icon_header("fa-solid fa-signal", "4. Key Market Signals", color=_PURPLE)
    st.markdown(
        "Three headline KPIs distilled from the full dataset — quick-reference "
        "health indicators for both platforms."
    )

    sig = _compute_signals(df_t, df_e, df_p, df_c)

    s1, s2, s3 = st.columns(3)
    with s1:
        _stat_card(
            fa_class="fa-solid fa-triangle-exclamation",
            label="Tiki Stagnation Risk",
            value=f"{sig['stag']:.1f}%",
            desc="Products with zero sales and no reviews — high recovery priority",
            accent=_RED,
        )
    with s2:
        _stat_card(
            fa_class="fa-solid fa-tag",
            label="Tiki Active Discounts",
            value=f"{sig['disc']:.1f}%",
            desc="Listings currently running a promotional price",
            accent=_TEAL,
        )
    with s3:
        _stat_card(
            fa_class="fa-solid fa-star",
            label="eBay New Condition",
            value=f"{sig['new']:.1f}%",
            desc="Share of new-condition eBay listings in scope",
            accent=_BLUE,
        )

    # Contextual callouts based on signal thresholds
    st.markdown("")
    if sig["stag"] > 30:
        _fa_callout(
            "fa-solid fa-circle-exclamation", _RED,
            f"<strong>Alert:</strong> Stagnation risk of <strong>{sig['stag']:.1f}%</strong> "
            "exceeds the recommended 30% threshold. Immediate category-level intervention is advised."
        )
    elif sig["stag"] > 15:
        _fa_callout(
            "fa-solid fa-triangle-exclamation", _AMBER,
            f"<strong>Warning:</strong> Stagnation at <strong>{sig['stag']:.1f}%</strong> — "
            "monitor closely and initiate promotional campaigns in the top-risk categories."
        )
    else:
        _fa_callout(
            "fa-solid fa-circle-check", _GREEN,
            f"<strong>Healthy:</strong> Stagnation risk of <strong>{sig['stag']:.1f}%</strong> "
            "is within acceptable bounds. Continue current engagement strategies."
        )

    if sig["disc"] > 50:
        _fa_callout(
            "fa-solid fa-fire", _ORANGE,
            f"<strong>High Discount Pressure:</strong> {sig['disc']:.1f}% of Tiki listings are "
            "discounted — this may signal over-supply or heightened competitive pressure."
        )
