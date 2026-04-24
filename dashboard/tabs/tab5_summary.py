import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any

from components.ui_helpers import icon_header as _icon_header
from data.loaders import load_5_tables
from data.filters import clean_numeric, apply_global_filters
from config import TEAL as _TEAL, ORANGE as _ORANGE, SLATE as _SLATE, get_chart_palette as _get_palette

# Helpers 

def _safe_mean(series: pd.Series) -> float:
    vals = pd.to_numeric(series, errors="coerce").dropna()
    return float(vals.mean()) if not vals.empty else 0.0


def _safe_pct(mask: pd.Series) -> float:
    return float(mask.mean() * 100) if not mask.empty else 0.0


def _compute_metrics(
    df_tiki: pd.DataFrame,
    df_ebay: pd.DataFrame,
) -> Dict[str, Dict[str, float]]:
    """
    Compute 6 normalised benchmark metrics for each platform.
    All values are scaled to 0–100 for radar chart compatibility.
    """
    metrics: Dict[str, Dict[str, float]] = {"Tiki": {}, "eBay": {}}

    # 1. Median Price (normalised: share of max)
    tiki_med = float(df_tiki["price"].median()) if not df_tiki.empty else 0
    ebay_med = float(df_ebay["Total_Cost_VND"].median()) if not df_ebay.empty else 0
    max_med = max(tiki_med, ebay_med, 1)
    metrics["Tiki"]["Median Price (normalised)"] = round(tiki_med / max_med * 100, 1)
    metrics["eBay"]["Median Price (normalised)"] = round(ebay_med / max_med * 100, 1)

    # 2. Discount Rate (Tiki only; eBay ~ 0)
    tiki_disc = 0.0
    if "discount_rate" in df_tiki.columns and not df_tiki.empty:
        tiki_disc = _safe_pct(pd.to_numeric(df_tiki["discount_rate"], errors="coerce") > 0)
    metrics["Tiki"]["Listings with Discount %"] = round(tiki_disc, 1)
    metrics["eBay"]["Listings with Discount %"] = 0.0

    # 3. Best Seller conversion (Tiki; eBay N/A → 0)
    tiki_bs = 0.0
    if "Is_Best_Seller" in df_tiki.columns and not df_tiki.empty:
        tiki_bs = _safe_pct(pd.to_numeric(df_tiki["Is_Best_Seller"], errors="coerce").fillna(0) == 1)
    metrics["Tiki"]["Best Seller Conversion %"] = round(tiki_bs, 1)
    metrics["eBay"]["Best Seller Conversion %"] = 0.0

    # 4. Free Shipping %
    ebay_free = 0.0
    if "shipping_cost" in df_ebay.columns and not df_ebay.empty:
        ship = pd.to_numeric(df_ebay["shipping_cost"], errors="coerce").fillna(0)
        ebay_free = _safe_pct(ship == 0)
    metrics["Tiki"]["Free Shipping %"] = 100.0
    metrics["eBay"]["Free Shipping %"] = round(ebay_free, 1)

    # 5. Seller Trust / Rating completeness
    tiki_rated = 0.0
    if "rating" in df_tiki.columns and not df_tiki.empty:
        tiki_rated = _safe_pct(pd.to_numeric(df_tiki["rating"], errors="coerce") > 0)
    ebay_trust = 0.0
    if "seller_feedback_percent" in df_ebay.columns and not df_ebay.empty:
        ebay_trust = _safe_mean(df_ebay["seller_feedback_percent"])
    metrics["Tiki"]["Rating / Trust Score %"] = round(tiki_rated, 1)
    metrics["eBay"]["Rating / Trust Score %"] = round(ebay_trust, 1)

    # 6. Active Listings
    tiki_active = 0.0
    if not df_tiki.empty:
        qs = pd.to_numeric(df_tiki.get("quantity_sold", 0), errors="coerce").fillna(0)
        rv = pd.to_numeric(df_tiki.get("review_count", 0), errors="coerce").fillna(0)
        tiki_active = _safe_pct((qs > 0) | (rv > 0))
    metrics["Tiki"]["Active Listings %"] = round(tiki_active, 1)
    metrics["eBay"]["Active Listings %"] = 100.0

    return metrics


# Chart 1: Radar

def _render_radar(
    metrics: Dict[str, Dict[str, float]],
    selected_dims: list[str],
) -> None:
    _pal = _get_palette()
    _TEAL_P = _pal["teal"]; _ORANGE_P = _pal["orange"]
    _icon_header("fa-solid fa-circle-nodes", "1. Platform Profile — Radar Overview", color=_TEAL_P)

    dims = selected_dims
    fig = go.Figure()

    colors = {"Tiki": _TEAL_P, "eBay": _ORANGE_P}
    for platform, data in metrics.items():
        vals = [data.get(d, 0) for d in dims] + [data.get(dims[0], 0)]
        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=dims + [dims[0]],
            fill="toself",
            name=platform,
            line_color=colors[platform],
            fillcolor=colors[platform],
            opacity=0.25,
            line=dict(width=2.5),
        ))

    fig.update_layout(
        template="plotly_white",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 105],
                tickfont=dict(size=10),
                gridcolor="rgba(0,0,0,0.08)",
            ),
            angularaxis=dict(tickfont=dict(size=11)),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        margin=dict(t=40, l=60, r=60, b=60),
        height=480,
        title=dict(
            text="Multi-Dimension Platform Comparison (0–100 scale)",
            font=dict(size=14),
            x=0.5,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Chart 1 — Radar Interpretation"):
        st.markdown(
            '<i class="fa-solid fa-circle-info" style="color:#0369a1;margin-right:0.4rem;"></i>'
            "**How to read:** Each axis = one analytical dimension (0–100 scale). "
            "A larger shaded area = the platform performs better on that dimension overall. "
            "Overlap areas = where both platforms are comparable.",
            unsafe_allow_html=True,
        )
        st.divider()
        tiki = metrics["Tiki"]
        ebay = metrics["eBay"]
        tiki_wins = [d for d in dims if tiki.get(d, 0) >= ebay.get(d, 0)]
        ebay_wins = [d for d in dims if ebay.get(d, 0) > tiki.get(d, 0)]
        st.write(f"""
**Tiki leads on:** {', '.join(tiki_wins) or 'None'}

**eBay leads on:** {', '.join(ebay_wins) or 'None'}

**Interpretation:** Each platform has a distinct competitive profile.
Tiki's strength lies in domestic trust signals and discount-driven promotions,
while eBay excels in product-condition diversity and cross-border seller credibility.
""")


# Chart 2: Benchmark Bar

def _render_benchmark_bar(
    metrics: Dict[str, Dict[str, float]],
    selected_dims: list[str],
) -> None:
    _pal = _get_palette()
    _TEAL = _pal["teal"]; _ORANGE = _pal["orange"]
    _icon_header("fa-solid fa-chart-bar", "2. Key Metrics Benchmark — Tiki vs eBay", color=_ORANGE)

    dims = selected_dims
    tiki_vals = [metrics["Tiki"].get(d, 0) for d in dims]
    ebay_vals = [metrics["eBay"].get(d, 0) for d in dims]

    # Short labels for y-axis
    short_labels = [d.replace("\n", " ") for d in dims]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=short_labels,
        x=tiki_vals,
        name="Tiki",
        orientation="h",
        marker_color=_TEAL,
        text=[f"{v:.1f}" for v in tiki_vals],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        y=short_labels,
        x=ebay_vals,
        name="eBay",
        orientation="h",
        marker_color=_ORANGE,
        text=[f"{v:.1f}" for v in ebay_vals],
        textposition="outside",
    ))
    fig.update_layout(
        template="plotly_white",
        barmode="group",
        title=dict(
            text="Platform Benchmark (0–100 scale per metric)",
            font=dict(size=14),
            x=0.5,
        ),
        xaxis=dict(
            title=dict(text="Score (0–100)", standoff=12),
            range=[0, 125],
        ),
        yaxis=dict(title=None, autorange="reversed"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.06)",
            borderwidth=1,
            font=dict(size=12),
        ),
        margin=dict(t=80, l=20, r=80, b=50),
        height=max(320, len(dims) * 72),
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Chart 2 — Benchmark Analysis"):
        st.markdown(
            '<i class="fa-solid fa-magnifying-glass" style="color:#0d9488;margin-right:0.4rem;"></i>'
            "**How to read:** Grouped horizontal bars compare both platforms side-by-side "
            "on each metric. All values are on a 0–100 scale for direct comparison.",
            unsafe_allow_html=True,
        )
        st.divider()
        lines = []
        for d, tv, ev in zip(short_labels, tiki_vals, ebay_vals):
            winner = "Tiki" if tv >= ev else "eBay"
            diff = abs(tv - ev)
            lines.append(f"- **{d}**: {winner} leads by {diff:.1f} pts ({tv:.1f} vs {ev:.1f})")
        st.write("**Per-metric winner:**\n" + "\n".join(lines))
        st.write("""
**Overall:** Use this benchmark to identify where each platform has structural advantages.
Sellers should position their strategy according to the platform's native strengths.
Buyers can use this to choose the platform that best aligns with their purchasing priorities.
""")


# Main render

def render(filters: Dict[str, Any]) -> None:
    """Main rendering entrypoint for Tab 4: Summary & Conclusion."""
    _icon_header("fa-solid fa-flag-checkered", "Summary &amp; Conclusion", level=2)

    with st.expander("About this tab"):
        st.markdown("""
This tab synthesises the findings from **all four analytical objectives** into a
platform-level comparison between **Tiki** and **eBay**.

Two complementary charts present the complete picture:

- **Section 1 — Radar Chart:** Multi-dimensional platform profile — see at a glance
  which platform excels on pricing, promotions, trust, and activity metrics.
- **Section 2 — Benchmark Bar:** Side-by-side numeric comparison of the same metrics
  for precise, data-backed conclusions.

Read top-to-bottom: **KPI overview → select dimensions → radar profile → numeric benchmark → final conclusion**.
""")

    try:
        df_tiki, df_ebay, df_product, df_category, df_seller = load_5_tables()
    except Exception as exc:
        st.error(f"Error loading datasets: {exc}")
        return

    df_tiki = clean_numeric(df_tiki, ["price"])
    df_ebay = clean_numeric(df_ebay, ["price", "shipping_cost", "Total_Cost_VND"])
    df_tiki_f, df_ebay_f = apply_global_filters(df_tiki, df_ebay, filters)

    # Compute all 6 benchmark metrics (always over full dimension set)
    all_metrics = _compute_metrics(df_tiki_f, df_ebay_f)
    all_dims = list(next(iter(all_metrics.values())).keys())

    # ── KPI row (always shown, before filter) ────────────────────────────────
    tiki_score_all = sum(all_metrics["Tiki"].values())
    ebay_score_all = sum(all_metrics["eBay"].values())
    overall_winner = "Tiki" if tiki_score_all >= ebay_score_all else "eBay"

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Tiki Listings", f"{len(df_tiki_f):,}")
    k2.metric("eBay Listings", f"{len(df_ebay_f):,}")
    k3.metric("Dimensions Analysed", f"{len(all_dims)}")
    k4.metric(
        "Overall Leader",
        overall_winner,
        delta=f"{abs(tiki_score_all - ebay_score_all):.0f} pts margin",
    )

    # ── Dimension filter panel (below KPI, above charts) ────────────────────
    st.markdown("#### Filter: Select Dimensions to Display")
    with st.container(border=True):
        selected_dims = st.multiselect(
            "Analytical dimensions",
            options=all_dims,
            default=all_dims,
            help="Both charts update simultaneously based on your selection.",
        )

    if not selected_dims:
        st.warning("Select at least one dimension to display the charts.")
        return

    st.divider()

    # ── Chart 1: Radar (full width) ──────────────────────────────────────────
    _render_radar(all_metrics, selected_dims)

    st.divider()

    # ── Chart 2: Benchmark Bar (full width) ──────────────────────────────────
    _render_benchmark_bar(all_metrics, selected_dims)

    st.divider()

    # ── Final conclusion ─────────────────────────────────────────────────────
    with st.expander("Final Conclusion — Research Summary"):
        st.markdown(
            '<i class="fa-solid fa-lightbulb" style="color:#f59e0b;margin-right:0.4rem;"></i>'
            "**Key Findings across all 4 objectives:**",
            unsafe_allow_html=True,
        )
        st.write("""
**Obj 1 & 2 — Tiki Pricing & Promotions:**
Tiki pricing is right-skewed, with the bulk of listings concentrated in the 0.5M–3M VND range.
Discount campaigns (20–50% tiers) show the highest Best Seller conversion rate — indicating
that moderate promotions outperform heavy discounting.

**Obj 3 & 4 — eBay Price Volatility & Shipping:**
eBay listings exhibit wide price variance across condition groups, with Refurbished/Open-Box
categories commanding premium prices. Shipping cost is a significant overhead — especially
in high-price categories — though the majority of listings offer free shipping.

**Obj 7 & 8 — Trust & Reputation (Tab 2):**
On Tiki, products with ratings above 4.0 show measurably higher sales volumes. On eBay,
Elite-tier sellers (50K+ feedback) consistently list at higher price points, confirming
that seller credibility commands a pricing premium.

**Obj 5 & 6 — Characteristics & Trends (Tab 3):**
A significant proportion of Tiki listings have zero sales and reviews — indicating cold-start
risk concentrated in specific categories. On eBay, New condition dominates listing volume,
but Refurbished listings represent the most price-volatile segment.

---

**Platform Recommendation:**
- **Sellers:** Tiki is optimal for discount-driven domestic sales; eBay suits multi-condition,
  globally-priced tech listings.
- **Buyers:** Tiki offers price transparency and domestic trust; eBay offers broader condition
  choice and competitive pricing for refurbished tech.
""")
