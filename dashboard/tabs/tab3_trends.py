import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Tuple, Dict, Any

from components.ui_helpers    import icon_header as _icon_header, fa_callout as _fa_callout
from components.chart_helpers import compute_kde as _compute_kde, age_to_color as _age_to_color
from data.filters import (
    clean_numeric, apply_global_filters,
    simplify_ebay_condition as _simplify_ebay_condition,
)
from config import (
    REFERENCE_DATE as _REFERENCE_DATE, TECH_KEYWORDS as _TECH_KEYWORDS,
    get_chart_palette as _get_palette,
)



# Section 1 -- Tiki Product Stagnation Risk (Obj 5)
def render_tiki_cold_start(
    df_fact_tiki: pd.DataFrame,
    df_product:   pd.DataFrame,
    df_category:  pd.DataFrame,
) -> None:
    """Pareto chart: Tiki categories ranked by zero-interaction product count."""
    _pal = _get_palette()
    _TEAL = _pal["teal"]; _ORANGE = _pal["orange"]; _RED = _pal["red"]
    _icon_header(
        "fa-solid fa-triangle-exclamation",
        "1. Tiki Ecosystem — Product Stagnation Risk",
        color=_RED,
    )

    if df_fact_tiki.empty:
        st.info("No Tiki listings match the current filters. Adjust the sidebar.")
        return

    df = (
        df_fact_tiki
        .merge(df_product[["product_id", "category_id"]], on="product_id")
        .merge(df_category, on="category_id")
    )
    df = df[df["category"] != "Unknown"]

    cold = df[(df["quantity_sold"] == 0) & (df["review_count"] == 0)]
    if cold.empty:
        st.success("No zero-interaction products found within the current price range.")
        return

    cat_counts = cold["category"].value_counts().reset_index()
    cat_counts.columns = ["Category", "Count"]
    cat_counts["Cumulative_Pct"] = (
        100 * cat_counts["Count"].cumsum() / cat_counts["Count"].sum()
    )
    plot_df = cat_counts.head(20).copy()
    colors  = [_RED] * 3 + ["#e2e8f0"] * (len(plot_df) - 3)
    lc      = "#334155"

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Products Analyzed", f"{len(df):,}")
    c2.metric(
        "Zero-Interaction Products", f"{len(cold):,}",
        delta="Action Required", delta_color="inverse",
    )
    risk = len(cold) / len(df) * 100 if len(df) else 0
    c3.metric("Stagnation Risk Ratio", f"{risk:.1f}%")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=plot_df["Category"], y=plot_df["Count"],
        name="Stagnant Volume", marker_color=colors,
        text=plot_df["Count"], textposition="outside",
    ))
    fig.add_trace(go.Scatter(
        x=plot_df["Category"], y=plot_df["Cumulative_Pct"],
        name="Cumulative %", yaxis="y2",
        line=dict(color=lc, width=2, dash="dot"),
        mode="lines+markers", marker=dict(color=lc, size=6),
    ))
    fig.update_layout(
        template="plotly_white",
        margin=dict(t=40, b=0, l=0, r=0), bargap=0.02, xaxis_tickangle=-35,
        yaxis=dict(title="Product Count", showgrid=False),
        yaxis2=dict(
            title=dict(text="Cumulative %", font=dict(color=lc)),
            overlaying="y", side="right", range=[0, 105],
            showgrid=False, tickfont=dict(color=lc),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=550,
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Chart Insights & Actionable Recommendations"):
        if len(plot_df) >= 3:
            top3 = plot_df.iloc[:3]["Category"].tolist()
            cum  = plot_df.iloc[-1]["Cumulative_Pct"]
            st.markdown(
                '<i class="fa-solid fa-magnifying-glass" style="color:#0d9488;'
                'margin-right:0.4rem;"></i>**Chart Analysis**',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"- The top 3 highest-risk categories are **{top3[0]}**, "
                f"**{top3[1]}**, and **{top3[2]}**.\n"
                f"- The top 20 categories account for **{cum:.1f}%** of all "
                "stagnant inventory within the current filter scope."
            )
            st.markdown(
                '<i class="fa-solid fa-lightbulb" style="color:#f59e0b;'
                'margin-right:0.4rem;"></i>**Recommended Next Steps**',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"- Conduct a root-cause analysis on **{top3[0]}** to determine "
                "whether the bottleneck is pricing or lack of promotional exposure.\n"
                "- Concentrate recovery resources where the Pareto curve is steepest "
                "rather than spreading the marketing budget evenly."
            )


    # Chart 1B — Bubble Chart: Risk Matrix (Volume vs Stagnation Rate)
    st.markdown("##### Chart B — Risk Matrix: Product Volume vs Stagnation Rate (Bubble Chart)")

    bubble_df = (
        df.assign(is_cold=lambda x: (x["quantity_sold"] == 0) & (x["review_count"] == 0))
        .groupby("category")["is_cold"]
        .agg(cold_count="sum", total="count")
        .reset_index()
    )
    bubble_df["rate"] = bubble_df["cold_count"] / bubble_df["total"] * 100
    bubble_df = bubble_df[bubble_df["total"] >= 10].reset_index(drop=True)

    if not bubble_df.empty:
        zone_cfg = [
            ("Critical (>50%)",  bubble_df[bubble_df["rate"] >  50], "#dc2626", "circle"),
            ("Warning (30-50%)", bubble_df[(bubble_df["rate"] > 30) & (bubble_df["rate"] <= 50)], "#d97706", "circle"),
            ("Healthy (<30%)",   bubble_df[bubble_df["rate"] <= 30], "#16a34a", "circle"),
        ]

        high_risk  = bubble_df[bubble_df["rate"] >  50]
        warn_risk  = bubble_df[(bubble_df["rate"] > 30) & (bubble_df["rate"] <= 50)]
        b1, b2, b3 = st.columns(3)
        b1.metric("Critical categories (>50%)", f"{len(high_risk)}")
        b2.metric("Warning categories (30-50%)", f"{len(warn_risk)}", delta_color="inverse")
        b3.metric("Healthy categories (<30%)",
                  f"{len(bubble_df) - len(high_risk) - len(warn_risk)}")

        fig_bubble = go.Figure()
        for label, sub, color, symbol in zone_cfg:
            if sub.empty:
                continue
            fig_bubble.add_trace(go.Scatter(
                x=sub["total"],
                y=sub["rate"],
                mode="markers",
                name=label,
                marker=dict(
                    size=sub["cold_count"].clip(lower=1) ** 0.45 * 5,
                    color=color,
                    opacity=0.80,
                    symbol=symbol,
                    line=dict(color="white", width=1.5),
                ),
                customdata=sub[["category", "cold_count", "rate"]].values,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Total products: %{x:,}<br>"
                    "Stagnation rate: <b>%{customdata[2]:.1f}%</b><br>"
                    "Stagnant products: %{customdata[1]:,}<extra></extra>"
                ),
            ))

        fig_bubble.add_hline(
            y=30, line_dash="dash", line_color="#d97706", line_width=1.5,
            annotation_text="Warning 30%", annotation_position="top right",
            annotation_font=dict(size=10, color="#d97706"),
        )
        fig_bubble.add_hline(
            y=50, line_dash="dash", line_color="#dc2626", line_width=1.5,
            annotation_text="Critical 50%", annotation_position="top right",
            annotation_font=dict(size=10, color="#dc2626"),
        )
        fig_bubble.update_layout(
            template="plotly_white",
            title=dict(
                text="Risk Matrix: Total Products vs Stagnation Rate (bubble size ≈ stagnant product count)",
                font=dict(size=13, family="Inter"),
            ),
            xaxis=dict(title="Total Products in Category", showgrid=True, gridcolor="#f1f5f9"),
            yaxis=dict(title="Stagnation Rate (%)", showgrid=True, gridcolor="#f1f5f9"),
            legend=dict(
                title=dict(text="Risk Zone", font=dict(size=11)),
                orientation="v", x=1.01, y=1,
                font=dict(family="Inter", size=11),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#e2e8f0", borderwidth=1,
            ),
            margin=dict(t=60, b=20, l=10, r=120),
            height=500,
            paper_bgcolor="rgba(0,0,0,0)",
        )
        with st.container(border=True):
            st.plotly_chart(fig_bubble, width='stretch')

        with st.expander("Chart 1B Insights & Actionable Recommendations"):
            top_crit = high_risk.nlargest(1, "cold_count") if not high_risk.empty else pd.DataFrame()
            top_vol  = bubble_df.nlargest(1, "total").iloc[0]
            st.markdown(
                '<i class="fa-solid fa-circle-info" style="color:#0d9488;'
                'margin-right:0.4rem;"></i>**How to read this chart:** '
                'Each bubble represents one product category. '
                '<strong>X-axis</strong> = total products listed (category size). '
                '<strong>Y-axis</strong> = stagnation rate (% with zero sales &amp; reviews). '
                '<strong>Bubble size</strong> ≈ absolute count of stagnant products. '
                'Colour legend on the right shows risk zones.',
                unsafe_allow_html=True,
            )
            st.divider()
            st.markdown(
                '<i class="fa-solid fa-magnifying-graph" style="color:#0d9488;'
                'margin-right:0.4rem;"></i>**Chart Analysis**',
                unsafe_allow_html=True,
            )
            st.write(f"""
**Trend:** Stagnation risk is not proportional to category size. This matrix simultaneously
shows volume (X) and severity (Y), revealing risk patterns invisible in the Pareto chart above.

**Critical zone (red, >50% rate):** {len(high_risk)} categor{"y" if len(high_risk)==1 else "ies"} have
more than half their inventory completely inactive.
**Warning zone (orange, 30-50%):** {len(warn_risk)} categor{"y" if len(warn_risk)==1 else "ies"} are approaching critical status.

**Quadrant analysis:**
- **Top-right (large + high rate):** Highest business impact — large volume means even a small
  rate reduction yields many active products recovered.
- **Top-left (small + high rate):** Disproportionately severe stagnation for a niche category —
  consider whether the category has sufficient demand to justify continued listings.
- **Bottom-right (large + healthy):** Benchmark categories — study what drives their performance.
""")
            st.markdown(
                '<i class="fa-solid fa-lightbulb" style="color:#f59e0b;'
                'margin-right:0.4rem;"></i>**Recommended Actions**',
                unsafe_allow_html=True,
            )
            st.write("""
* **Red bubbles (top-right):** Prioritise immediately — audit pricing, listing quality,
  and platform visibility. Even a 10% rate recovery has the largest absolute impact.
* **Orange bubbles:** Launch targeted review-incentive campaigns to generate first
  interactions and break the cold-start cycle before they cross the critical threshold.
* **Green bubbles (bottom-right):** Extract best practices and replicate strategy
  across underperforming categories.
""")
            st.markdown(
                '<i class="fa-solid fa-arrow-right-long" style="color:#ef4444;margin-right:0.4rem;"></i>'
                '<em>Use Chart 1A (Pareto) for absolute scale — Chart 1B (Risk Matrix) for prioritisation.</em>',
                unsafe_allow_html=True,
            )
    else:
        st.info("Insufficient data for bubble chart (min. 10 products per category).")


# Section 2 — eBay Item Condition Analysis

def render_ebay_condition_analysis(df_fact_ebay: pd.DataFrame) -> None:
    """Treemap + horizontal bar: eBay condition market share and average cost."""
    _pal = _get_palette()
    _TEAL = _pal["teal"]; _ORANGE = _pal["orange"]; _BLUE = _pal["blue"]
    _icon_header(
        "fa-solid fa-layer-group",
        "2. eBay Ecosystem — Item Condition Distribution & Cost Impact",
        color=_BLUE,
    )

    if df_fact_ebay.empty:
        st.info("No eBay listings match the current filters. Adjust the sidebar.")
        return

    df = df_fact_ebay.copy()
    df["Standard_Condition"] = df["condition"].apply(
        lambda c: _simplify_ebay_condition(str(c)) or "Other/Parts"
    )
    df = df[df["Standard_Condition"] != "Other/Parts"]

    if df.empty:
        st.warning("Insufficient valid condition data within the selected price range.")
        return

    mkt = df["Standard_Condition"].value_counts().reset_index()
    mkt.columns = ["Condition", "Count"]
    total     = mkt["Count"].sum()
    dominant  = mkt.iloc[0]["Condition"]
    dom_pct   = mkt.iloc[0]["Count"] / total * 100

    cost = (
        df.groupby("Standard_Condition")["Total_Cost_VND"]
        .mean().reset_index()
        .rename(columns={"Standard_Condition": "Condition", "Total_Cost_VND": "Avg_Cost"})
        .sort_values("Avg_Cost")
    )
    cmap = {c: ("#1f77b4" if c == dominant else "#e2e8f0") for c in mkt["Condition"]}

    c1, c2, c3 = st.columns(3)
    c1.metric("Valid Listings", f"{total:,}")
    c2.metric("Dominant Condition", dominant)
    c3.metric("Dominant Share", f"{dom_pct:.1f}%")

    col_tree, col_bar = st.columns(2)
    with col_tree:
        st.markdown("**Market Share by Item Condition**")
        fig_t = px.treemap(
            mkt, path=["Condition"], values="Count",
            color="Condition", color_discrete_map=cmap,
        )
        fig_t.update_traces(
            textinfo="label+percent root", textfont_size=14,
            marker=dict(line=dict(color="white", width=2)),
        )
        fig_t.update_layout(margin=dict(t=0, l=0, r=0, b=0))
        st.plotly_chart(fig_t, use_container_width=True)

    with col_bar:
        st.markdown("**Average Total Cost by Condition (VND)**")
        fig_b = px.bar(
            cost, y="Condition", x="Avg_Cost",
            orientation="h", text_auto=".2s",
            color="Condition", color_discrete_map=cmap,
        )
        fig_b.update_layout(
            template="plotly_white",
            xaxis=dict(
                title="Average Total Cost (VND)", showgrid=False,
                showticklabels=False, zeroline=True,
                zerolinewidth=2, zerolinecolor="#cbd5e1",
            ),
            yaxis=dict(title="", showgrid=False),
            showlegend=False, margin=dict(t=0, l=0, r=50, b=0),
        )
        fig_b.update_traces(
            textposition="outside",
            textfont=dict(size=12, color="#334155"), cliponaxis=False,
        )
        st.plotly_chart(fig_b, use_container_width=True)

    with st.expander("Chart Insights & Actionable Recommendations"):
        if not cost.empty:
            lowest  = cost.iloc[0]["Condition"]
            highest = cost.iloc[-1]["Condition"]
            st.markdown(
                '<i class="fa-solid fa-magnifying-glass" style="color:#0d9488;'
                'margin-right:0.4rem;"></i>**Chart Analysis**',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"- **{dominant}** captures **{dom_pct:.1f}%** of market share.\n"
                f"- **{lowest}** carries the lowest average cost; "
                f"**{highest}** commands the highest.\n"
                "- This suggests distinct buyer demographics across the condition spectrum."
            )
            st.markdown(
                '<i class="fa-solid fa-lightbulb" style="color:#f59e0b;'
                'margin-right:0.4rem;"></i>**Sourcing Strategy**',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"- Stock **{lowest}** items for entry-level product lines.\n"
                f"- Source **{highest}** items aggressively for the premium segment.\n"
                "- Cross-validate listings with seller feedback scores before procurement."
            )


    # Chart 2C — ECDF: Cumulative Price Distribution by Item Condition
    st.markdown("##### Chart B — Cumulative Price Distribution by Condition (ECDF)")

    cond_palette = {
        "eBay — New":               "#1f77b4",
        "eBay — Used":              "#94a3b8",
        "eBay — Refurb / Open Box": "#8b5cf6",
    }

    fig_ecdf = go.Figure()
    ecdf_stats: dict = {}
    for cond, color in cond_palette.items():
        cond_data = df[df["Standard_Condition"] == cond]["Total_Cost_VND"].dropna()
        if len(cond_data) < 2:
            continue
        sorted_vals = np.sort(cond_data.values / 1e6)
        ecdf_y = np.arange(1, len(sorted_vals) + 1) / len(sorted_vals)
        fig_ecdf.add_trace(go.Scatter(
            x=sorted_vals,
            y=ecdf_y * 100,
            mode="lines",
            name=cond,
            line=dict(color=color, width=2.5),
            hovertemplate=(
                f"<b>{cond}</b><br>"
                "Price: %{x:.2f}M VND<br>"
                "Cumulative: %{y:.1f}% of listings<extra></extra>"
            ),
        ))
        med = float(np.median(sorted_vals))
        p80 = float(np.percentile(sorted_vals, 80))
        ecdf_stats[cond] = {"median": med, "p80": p80, "n": len(sorted_vals)}
        fig_ecdf.add_vline(
            x=med, line_dash="dot", line_color=color, line_width=1.5, opacity=0.7,
            annotation_text=f"{med:.1f}M (50%)",
            annotation_font=dict(size=9, color=color),
            annotation_position="top right",
        )

    trim_pct_ecdf = df["Total_Cost_VND"].quantile(0.98) / 1e6
    fig_ecdf.update_layout(
        template="plotly_white",
        title=dict(
            text="Empirical CDF: What % of listings cost ≤ X? (by Item Condition)",
            font=dict(size=13, family="Inter"),
        ),
        xaxis=dict(
            title="Total Cost (Million VND)",
            showgrid=True, gridcolor="#f1f5f9",
            range=[0, trim_pct_ecdf],
        ),
        yaxis=dict(
            title="Cumulative % of Listings",
            showgrid=True, gridcolor="#f1f5f9",
            ticksuffix="%", range=[0, 103],
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            font=dict(family="Inter", size=11),
        ),
        margin=dict(t=70, b=20, l=10, r=10),
        height=440,
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    with st.container(border=True):
        st.plotly_chart(fig_ecdf, width='stretch')

    with st.expander("Chart 2C Insights & Actionable Recommendations"):
        if ecdf_stats:
            st.markdown(
                '<i class="fa-solid fa-circle-info" style="color:#0369a1;'
                'margin-right:0.4rem;"></i>**How to read this chart:** '
                'The Y-axis answers: <em>"What % of listings cost ≤ X VND?"</em> '
                'A curve rising steeply at low X means most listings are affordable. '
                'Dotted vertical lines mark the <strong>median</strong> of each condition. '
                'Hover anywhere to compare all three conditions at the same price point.',
                unsafe_allow_html=True,
            )
            st.divider()

            # Derive key stats from runtime data
            sorted_conds = sorted(ecdf_stats.items(), key=lambda x: x[1]["median"])
            cheapest_cond, cheapest_s = sorted_conds[0]
            priciest_cond, priciest_s = sorted_conds[-1]
            median_gap = priciest_s["median"] - cheapest_s["median"]

            # Find steepest (most price-concentrated) = smallest p80 - median gap
            spread = {c: s["p80"] - s["median"] for c, s in ecdf_stats.items()}
            most_concentrated = min(spread, key=spread.get)
            widest_spread     = max(spread, key=spread.get)

            st.markdown(
                '<i class="fa-solid fa-magnifying-glass" style="color:#0d9488;'
                'margin-right:0.4rem;"></i>**Chart Analysis**',
                unsafe_allow_html=True,
            )
            stat_lines = "\n".join(
                f"- **{c}**: median = **{s['median']:.2f}M VND** | "
                f"80th percentile = **{s['p80']:.2f}M VND** | "
                f"N = {s['n']:,} listings"
                for c, s in ecdf_stats.items()
            )
            st.write(f"""
**Trend:** The ECDF curves show the cumulative price accumulation for each condition group.
A curve that reaches 50% sooner (further left) indicates a **cheaper** condition group overall.

{stat_lines}

**Median gap:** The spread between the cheapest (**{cheapest_cond}** at {cheapest_s['median']:.2f}M)
and priciest (**{priciest_cond}** at {priciest_s['median']:.2f}M) is **{median_gap:.2f}M VND**.

**Price concentration:** **{most_concentrated}** has the steepest curve slope — prices cluster
tightly, making procurement costs highly predictable. **{widest_spread}** has the widest
spread between median and P80, indicating greater pricing variability within that group.

**Difference from Chart 2B (Bar):** Chart 2B showed only `mean` per condition — easily skewed
by expensive outliers. Chart 2C shows the full price ladder: for any budget threshold you can
read exactly how many listings are reachable without needing a single summary statistic.
""")
            st.markdown(
                '<i class="fa-solid fa-lightbulb" style="color:#f59e0b;'
                'margin-right:0.4rem;"></i>**Procurement Strategy**',
                unsafe_allow_html=True,
            )
            st.write(f"""
* Set a **budget ceiling** on the X-axis and read each curve's Y-value to know what % of
  listings are within reach per condition — without relying on misleading averages.
* **{most_concentrated}** offers the highest price predictability (steep curve) — best
  suited for bulk procurement with fixed budgets.
* Where ECDF curves **cross**: at that price, both conditions cover the same % of listings
  — prefer the higher-quality condition at no additional cumulative cost.
* Use this chart alongside Chart 2B (mean bar) to spot conditions where outliers
  significantly inflate the average above the median.
""")
            st.markdown(
                '<i class="fa-solid fa-arrow-right-long" style="color:#0369a1;margin-right:0.4rem;"></i>'
                '<em>For seller-level price analysis — navigate to <strong>Tab: Trust &amp; Reputation</strong></em>',
                unsafe_allow_html=True,
            )
        else:
            st.info("Insufficient data to generate ECDF insights.")


# Section 3 -- Cross-Platform KDE (Obj 9) -- compute_kde from components.chart_helpers

# Section 3 -- Overlapping KDE Plot (Objective 9)

def render_price_kde_comparison(
    df_tiki:     pd.DataFrame,
    df_ebay:     pd.DataFrame,
    df_product:  pd.DataFrame,
    df_category: pd.DataFrame,
) -> None:
    """
    Chart 3 — Objective 9
    Overlapping KDE: normalized price density (VND) of Tiki tech products
    vs eBay condition groups, to measure median divergence and segment advantage.
    """
    _pal = _get_palette()
    _TEAL = _pal["teal"]; _ORANGE = _pal["orange"]
    _icon_header(
        "fa-solid fa-chart-area",
        "3. Cross-Platform Price Architecture — Overlapping KDE",
        color=_TEAL,
    )

    # Filter Tiki → tech/electronics
    tiki_cat = (
        df_tiki
        .merge(df_product[["product_id", "category_id"]], on="product_id", how="left")
        .merge(df_category, on="category_id", how="left")
    )
    tiki_cat["_cat_l"] = tiki_cat["category"].fillna("").str.lower()
    tech_mask  = tiki_cat["_cat_l"].apply(lambda c: any(kw in c for kw in _TECH_KEYWORDS))
    df_tech    = tiki_cat[tech_mask].copy()
    tiki_label = "Tiki — Tech & Electronics" if not df_tech.empty else "Tiki — All Products"
    if df_tech.empty:
        df_tech = tiki_cat.copy()

    # Simplify eBay conditions
    df_ebay = df_ebay.copy()
    df_ebay["Group"] = df_ebay["condition"].apply(_simplify_ebay_condition)
    ebay_v = df_ebay.dropna(subset=["Group"])

    # Controls
    ctrl_l, ctrl_r = st.columns([1, 2])
    with ctrl_l:
        scale = st.radio(
            "X-axis scale",
            ["Linear", "Log (Logarithmic)"],
            horizontal=True,
            help="Logarithmic scale is preferable for right-skewed price distributions.",
        )
    with ctrl_r:
        trim_pct = st.slider(
            "Trim top outliers — display bottom X% of prices",
            min_value=80, max_value=100, value=98, step=1,
            help="Removes extreme upper-tail values to improve KDE readability.",
        )

    use_log = scale.startswith("Log")

    GROUP_CFG: Dict[str, Dict] = {
        tiki_label:                 {"color": _TEAL,    "dash": "solid"},
        "eBay — New":               {"color": _ORANGE,  "dash": "solid"},
        "eBay — Used":              {"color": "#94a3b8", "dash": "dash"},
        "eBay — Refurb / Open Box": {"color": "#8b5cf6", "dash": "dot"},
    }

    group_data: Dict[str, np.ndarray] = {
        tiki_label: df_tech["price"].dropna().values,
    }
    for grp in ["eBay — New", "eBay — Used", "eBay — Refurb / Open Box"]:
        v = ebay_v[ebay_v["Group"] == grp]["Total_Cost_VND"].dropna().values
        if len(v) >= 5:
            group_data[grp] = v

    if len(group_data) < 2:
        st.warning("Not enough data for KDE. Try widening the Price Range filter.")
        return

    # Metrics row
    m_cols = st.columns(len(group_data))
    for col_w, (grp, vals) in zip(m_cols, group_data.items()):
        col_w.metric(
            label=grp,
            value=f"{np.median(vals) / 1_000_000:.1f}M VND",
            delta=f"{len(vals):,} products",
            delta_color="off",
        )

    # KDE figure
    fig   = go.Figure()
    y_max = 0.0

    for grp, vals in group_data.items():
        cfg = GROUP_CFG.get(grp, {"color": "#64748b", "dash": "solid"})

        x_kde, y_kde = _compute_kde(vals, n_points=500, trim_pct=float(trim_pct))
        if len(x_kde) == 0:
            continue

        x_plot = np.log10(np.clip(x_kde, 1, None)) if use_log else x_kde
        y_plot = y_kde
        y_max  = max(y_max, float(y_plot.max()))

        # Shaded fill under curve
        fig.add_trace(go.Scatter(
            x=np.concatenate([x_plot, x_plot[::-1]]),
            y=np.concatenate([y_plot, np.zeros(len(y_plot))]),
            fill="toself", fillcolor=cfg["color"], opacity=0.12,
            line=dict(width=0), showlegend=False, hoverinfo="skip",
        ))
        # KDE line
        fig.add_trace(go.Scatter(
            x=x_plot, y=y_plot,
            mode="lines", name=grp,
            line=dict(color=cfg["color"], width=2.5, dash=cfg["dash"]),
            hovertemplate=(
                f"<b>{grp}</b><br>"
                f"{'Log₁₀ Price' if use_log else 'Price (VND)'}: %{{x:,.3f}}<br>"
                "Density: %{y:.2e}<extra></extra>"
            ),
        ))
        # Median vertical annotation
        med   = np.median(vals)
        x_med = np.log10(max(med, 1)) if use_log else med
        y_med = float(np.interp(x_med, x_plot, y_plot))
        fig.add_vline(x=x_med, line_dash="dot", line_color=cfg["color"],
                      line_width=1.5, opacity=0.65)
        fig.add_annotation(
            x=x_med, y=y_med + y_max * 0.07,
            text=f"<b>{med / 1_000_000:.1f}M</b>",
            showarrow=False,
            font=dict(size=9, color=cfg["color"]),
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor=cfg["color"], borderwidth=1, borderpad=3,
        )

    x_title = "Log₁₀ (Price — VND)" if use_log else "Price (VND)"
    fig.update_layout(
        template="plotly_white",
        title=dict(
            text="Price Density Distribution: Tiki Tech vs eBay Condition Groups",
            font=dict(size=15),
        ),
        xaxis=dict(title=x_title, showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(title="Probability Density (KDE)", showgrid=False),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(255,255,255,0.9)", bordercolor="#e2e8f0", borderwidth=1,
        ),
        margin=dict(t=80, l=20, r=20, b=50),
        height=500, hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Descriptive Statistics & Competitive Analysis"):
        rows = []
        for grp, vals in group_data.items():
            cap = np.percentile(vals, trim_pct)
            v   = vals[vals <= cap]
            iqr = np.percentile(v, 75) - np.percentile(v, 25)
            rows.append({
                "Group":          grp,
                "N":              f"{len(v):,}",
                "Median (M VND)": f"{np.median(v) / 1e6:.2f}",
                "Mean (M VND)":   f"{np.mean(v)   / 1e6:.2f}",
                "P25 (M VND)":    f"{np.percentile(v, 25) / 1e6:.2f}",
                "P75 (M VND)":    f"{np.percentile(v, 75) / 1e6:.2f}",
                "IQR (M VND)":    f"{iqr / 1e6:.2f}",
            })
        st.dataframe(pd.DataFrame(rows).set_index("Group"), use_container_width=True)

        grp_list = list(group_data.keys())
        tiki_med = np.median(group_data[grp_list[0]])
        ebay_new = next((k for k in grp_list if "New" in k), None)
        if ebay_new:
            e_med = np.median(group_data[ebay_new])
            pct   = (e_med - tiki_med) / tiki_med * 100 if tiki_med else 0
            dirn  = "higher" if pct > 0 else "lower"
            adv   = (
                "eBay holds the premium-segment pricing advantage."
                if pct > 0 else
                "Tiki is more price-competitive in this segment."
            )
            st.info(
                f"**Key Finding:** The median price of **{ebay_new}** is "
                f"**{abs(pct):.1f}% {dirn}** than **{grp_list[0]}** "
                f"({e_med / 1e6:.1f}M vs {tiki_med / 1e6:.1f}M VND). {adv}"
            )


# ============================================================
# CHART 4 (NEW — Objective 10): Lollipop Chart
# ============================================================

def _age_to_color(norm_val: float) -> str:
    """Return an RGB color interpolating green (fast) → red (stagnant)."""
    r = int(34  + norm_val * (220 - 34))
    g = int(197 - norm_val * (197 - 50))
    b = int(94  - norm_val * 94)
    return f"rgb({r},{g},{b})"


def render_ebay_lollipop_lifespan(
    df_fact_ebay: pd.DataFrame,
    df_product:   pd.DataFrame,
    df_category:  pd.DataFrame,
) -> None:
    """
    Chart 4 
    Lollipop chart: average listing age per eBay top-N categories,
    identifying the fastest- and slowest-turnover market segments.
    """
    _pal = _get_palette()
    _TEAL = _pal["teal"]; _ORANGE = _pal["orange"]; _INDIGO = _pal["indigo"]
    _icon_header(
        "fa-solid fa-hourglass-half",
        "4. eBay Listing Lifespan by Category — Lollipop Chart",
        color=_INDIGO,
    )
   
    if df_fact_ebay.empty:
        st.info("No eBay listings match the current filters. Adjust the sidebar.")
        return

    # ── Compute listing age (timezone-safe) ───────────────────────────────────
    df = df_fact_ebay.copy()
    df["item_creation_date"] = (
        pd.to_datetime(df["item_creation_date"], errors="coerce", utc=True)
        .dt.tz_convert(None)   # strip timezone → tz-naive for arithmetic
    )
    df["listing_age_days"] = (_REFERENCE_DATE - df["item_creation_date"]).dt.days
    df = df[(df["listing_age_days"] >= 0) & df["listing_age_days"].notna()]

    if df.empty:
        st.warning(
            "Listing age could not be computed — `item_creation_date` "
            "is unavailable or entirely NaT in the dataset."
        )
        return

    # ── Resolve product categories via dim_product → dim_category ─────────────
    df = (
        df
        .merge(df_product[["product_id", "category_id"]], on="product_id", how="left")
        .merge(df_category, on="category_id", how="left")
    )
    df["category"] = df["category"].fillna("Unknown")

    unknown_ratio = (df["category"] == "Unknown").mean()

    if unknown_ratio > 0.60:
        # Fallback: group by condition if category coverage is insufficient
        _fa_callout(
            "fa-solid fa-circle-info", "#3b82f6",
            "Category coverage for eBay listings is limited — "
            "displaying by <strong>item condition group</strong> instead."
        )
        df["_group"] = df["condition"].apply(
            lambda c: _simplify_ebay_condition(str(c)) or "Other"
        )
        df = df[df["_group"] != "Other"]
        group_col   = "_group"
        group_label = "Item Condition Group"
    else:
        df = df[df["category"] != "Unknown"]
        group_col   = "category"
        group_label = "Product Category"

    if df.empty:
        st.warning("Insufficient data after removing unclassified entries.")
        return

    # ── Controls ──────────────────────────────────────────────────────────────
    ctrl_l, ctrl_r = st.columns(2)
    with ctrl_l:
        top_n = st.slider(
            f"Number of {group_label}s to display (Top N by listing count)",
            min_value=5, max_value=20, value=10, step=1,
        )
    with ctrl_r:
        agg_choice = st.radio(
            "Aggregation metric",
            ["Mean", "Median"],
            horizontal=True,
        )

    # ── Aggregate ─────────────────────────────────────────────────────────────
    top_groups = df[group_col].value_counts().head(top_n).index.tolist()
    df_top     = df[df[group_col].isin(top_groups)].copy()
    agg_fn     = "mean" if agg_choice == "Mean" else "median"

    result = (
        pd.DataFrame({
            "avg_age_days":  df_top.groupby(group_col)["listing_age_days"].agg(agg_fn),
            "listing_count": df_top.groupby(group_col).size(),
        })
        .reindex(top_groups)
        .dropna()
        .sort_values("avg_age_days", ascending=True)
    )

    if result.empty:
        st.info("Not enough data to render the Lollipop Chart.")
        return

    # ── Color gradient ─────────────────────────────────────────────────────────
    r_min, r_max = result["avg_age_days"].min(), result["avg_age_days"].max()
    norms  = ((result["avg_age_days"] - r_min) / (r_max - r_min + 1e-9)).values
    colors = [_age_to_color(n) for n in norms]

    # ── Key metrics ────────────────────────────────────────────────────────────
    overall_avg  = df["listing_age_days"].mean()
    fastest_grp  = result.index[0]
    slowest_grp  = result.index[-1]
    n_groups     = len(result)
    chart_height = max(400, n_groups * 52)

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Fastest Turnover",
        fastest_grp[:32] + ("..." if len(fastest_grp) > 32 else ""),
        f"{result['avg_age_days'].iloc[0]:.0f} days",
    )
    c2.metric(
        "Slowest Turnover",
        slowest_grp[:32] + ("..." if len(slowest_grp) > 32 else ""),
        f"{result['avg_age_days'].iloc[-1]:.0f} days",
        delta_color="inverse",
    )
    c3.metric("eBay Platform Average", f"{overall_avg:.0f} days")

    # ── Lollipop figure ────────────────────────────────────────────────────────
    fig = go.Figure()

    # Stem lines (horizontal shapes)
    for i, age in enumerate(result["avg_age_days"].values):
        fig.add_shape(
            type="line",
            x0=0, x1=age, y0=i, y1=i,
            line=dict(color=colors[i], width=2.8),
            layer="below",
        )

    # Invisible bar trace — anchors y-axis tick position
    fig.add_trace(go.Bar(
        x=[0] * n_groups, y=list(range(n_groups)),
        orientation="h",
        marker_color="rgba(0,0,0,0)",
        showlegend=False, hoverinfo="skip",
    ))

    # Lollipop balls with inline value labels
    fig.add_trace(go.Scatter(
        x=result["avg_age_days"].values,
        y=list(range(n_groups)),
        mode="markers+text",
        marker=dict(size=17, color=colors, line=dict(color="white", width=2)),
        text=[
            f"  <b>{v:.0f}</b> days  ({c:,} listings)"
            for v, c in zip(result["avg_age_days"], result["listing_count"])
        ],
        textposition="middle right",
        textfont=dict(size=11, color="#1e293b"),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            f"{agg_choice} age: %{{x:.0f}} days<br>"
            "Listings: %{customdata[1]:,}<extra></extra>"
        ),
        customdata=list(zip(result.index, result["listing_count"])),
        showlegend=False,
    ))

    # Platform average reference line
    fig.add_vline(
        x=overall_avg,
        line_dash="dash", line_color="#6366f1", line_width=1.8,
        annotation_text=f"  eBay avg: {overall_avg:.0f} days",
        annotation_position="top",
        annotation_font=dict(color="#6366f1", size=10),
    )

    fig.update_layout(
        template="plotly_white",
        title=dict(
            text=f"eBay Listing Lifespan — Top {top_n} {group_label}s ({agg_choice})",
            font=dict(size=15),
        ),
        xaxis=dict(
            title=f"{agg_choice} listing age (days)",
            showgrid=True, gridcolor="#f1f5f9", zeroline=False,
            range=[-3, result["avg_age_days"].max() * 1.45],
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(n_groups)),
            ticktext=[f"<b>{g}</b>" for g in result.index],
            showgrid=False, automargin=True,
        ),
        bargap=0.6,
        margin=dict(t=70, l=20, r=20, b=40),
        height=chart_height,
        plot_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Colour legend — CSS spans + FA icons, no Unicode emoji
    st.markdown(
        '<small style="color:#64748b;">'
        '<span style="color:#22c55e;"><i class="fa-solid fa-circle"></i></span>'
        '&nbsp;<strong>Green</strong>&nbsp;= new listing / fast turnover'
        '&nbsp;&nbsp;|&nbsp;&nbsp;'
        '<span style="color:#ef4444;"><i class="fa-solid fa-circle"></i></span>'
        '&nbsp;<strong>Red</strong>&nbsp;= stagnant listing / slow turnover'
        '&nbsp;&nbsp;|&nbsp;&nbsp;'
        '<span style="color:#6366f1;"><i class="fa-solid fa-grip-lines"></i></span>'
        '&nbsp;<strong>Dashed purple</strong>&nbsp;= eBay platform average'
        '</small>',
        unsafe_allow_html=True,
    )

    with st.expander("In-Depth Analysis & Strategic Recommendations"):
        diff  = result["avg_age_days"].iloc[-1] - result["avg_age_days"].iloc[0]
        f_s   = fastest_grp[:30] + ("..." if len(fastest_grp) > 30 else "")
        s_s   = slowest_grp[:30] + ("..." if len(slowest_grp) > 30 else "")

        st.markdown(
            '<i class="fa-solid fa-circle-info" style="color:#3b82f6;margin-right:0.4rem;"></i>'
            '**Methodology**',
            unsafe_allow_html=True,
        )
        st.markdown(
            "- **Listing age** = `01 Apr 2026` minus `item_creation_date` per product.\n"
            "- A **high value** indicates a long-lived listing — the item is hard to sell.\n"
            "- A **low value** signals recent creation or rapid sales — high market demand."
        )
        st.markdown(
            '<i class="fa-solid fa-magnifying-glass" style="color:#0d9488;margin-right:0.4rem;"></i>'
            '**Key Findings**',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"- The spread between the fastest (**{fastest_grp}**, "
            f"{result['avg_age_days'].iloc[0]:.0f} days) "
            f"and slowest (**{slowest_grp}**, "
            f"{result['avg_age_days'].iloc[-1]:.0f} days) "
            f"categories is **{diff:.0f} days**, revealing significant "
            f"non-uniformity in market absorption rates.\n"
            f"- Categories to the **left of the purple reference line** "
            f"({overall_avg:.0f} days) outperform the platform average in turnover speed.\n"
            "- Categories to the **right** require active pricing or promotional intervention."
        )
        st.markdown(
            '<i class="fa-solid fa-lightbulb" style="color:#f59e0b;margin-right:0.4rem;"></i>'
            '**Strategic Recommendations**',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"- **{f_s}** (fast turnover): Scale inventory proactively and "
            "exploit the demand window to maximise revenue.\n"
            f"- **{s_s}** (slow turnover): Run A/B price tests, upgrade listing "
            "photography, and introduce time-limited flash sales or bundle promotions.\n"
            "- Allocate marketing budget **inversely proportional** to average listing age "
            "to maximise ROI across the entire category portfolio."
        )


# Main render entry-point — invoked by app.py

def render(filters: Dict[str, Any]) -> None:
    """
    Characteristics & Trends tab — 4 sections answering Objectives 5, 6, 9 & 10.
    Section 1: Tiki stagnation risk — Pareto + Rate % (Obj 5)
    Section 2: eBay condition distribution + cost impact — Treemap, Bar, Boxplot (Obj 6)
    Section 3: Cross-platform price KDE — Overlapping density curves (Obj 9)
    Section 4: eBay listing lifespan — Lollipop chart (Obj 10)
    """
    # ── Lazy imports ──────────────────────────────────────────────────────────
    from data.loaders import load_4_tables
    # ─────────────────────────────────────────────────────────────────────────
    _icon_header(
        "fa-solid fa-chart-line",
        "Characteristics &amp; Trends",
        level=2,
        color="#0d9488",
    )

    with st.expander("About this tab"):
        st.markdown(
            "This tab provides a comprehensive overview of **listing characteristics and market behaviour** "
            "across both platforms. Four analytical sections answer distinct research questions:\n\n"
            "- **Section 1 (Tiki):** Which product categories carry the highest stagnation risk? "
            "Analysed by absolute volume (Pareto) and normalised rate (%) side-by-side.\n"
            "- **Section 2 (eBay):** How does item condition (New / Used / Refurb) shape market share "
            "and final buyer cost? Visualised via Treemap, average cost bar, and full price distribution (Boxplot).\n"
            "- **Section 3 (Cross-platform):** How do price density curves differ between Tiki tech products "
            "and eBay condition groups? KDE overlap reveals median divergence and segment advantage.\n"
            "- **Section 4 (eBay):** Which categories have the fastest vs slowest listing turnover? "
            "Lollipop chart ranked by average listing age, colour-coded green (fast) to red (slow).\n\n"
            "Read top-to-bottom to follow the analytical narrative from **Tiki risk signals** "
            "through **eBay market structure** to **cross-platform price dynamics**."
        )


    try:
        df_fact_tiki, df_fact_ebay, df_product, df_category = load_4_tables()
    except Exception as exc:
        st.error(f"Failed to load datasets: {exc}. Check `../data/processed/`.")
        return

    df_fact_tiki = clean_numeric(df_fact_tiki, ["price"])
    df_fact_ebay = clean_numeric(df_fact_ebay, ["Total_Cost_VND"])

    df_tiki_f, df_ebay_f = apply_global_filters(df_fact_tiki, df_fact_ebay, filters)

    st.divider()

    # Section 1 — Tiki Stagnation Risk (Obj 5)
    with st.container():
        render_tiki_cold_start(df_tiki_f, df_product, df_category)
    st.divider()

    # Section 2 — eBay Condition Analysis (Obj 6)
    with st.container():
        render_ebay_condition_analysis(df_ebay_f)
    st.divider()

    # Section 3 — Cross-Platform KDE (Obj 9)
    with st.container():
        render_price_kde_comparison(df_tiki_f, df_ebay_f, df_product, df_category)
    st.divider()

    # Section 4 — eBay Listing Lifespan (Obj 10)
    with st.container():
        render_ebay_lollipop_lifespan(df_ebay_f, df_product, df_category)

    st.divider()