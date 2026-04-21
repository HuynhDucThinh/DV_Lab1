"""
tab3_trends.py — Tab 3: Characteristics & Trends

Charts
------
1. Tiki Product Stagnation Risk           (Pareto, existing)
2. eBay Item Condition Distribution       (Treemap + Bar, existing)
3. Cross-Platform Price Architecture      (Overlapping KDE, Objective 9)
4. eBay Listing Lifespan by Category      (Lollipop Chart, Objective 10)

Icons: Font Awesome 6 Free via CDN — no Unicode emoji used.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Tuple, Dict, Any, List

# ── Module constants ───────────────────────────────────────────────────────────
# Reference timestamp for computing listing age (data collection date)
_REFERENCE_DATE = pd.Timestamp("2026-04-01")

# Vietnamese tech keywords — used INTERNALLY for category matching, not displayed
_TECH_KEYWORDS: List[str] = [
    "điện thoại", "laptop", "máy tính", "tai nghe", "loa", "thiết bị số",
    "phụ kiện số", "camera", "màn hình", "tivi", " tv ", "điện gia dụng",
    "cáp", "sạc", "pin", "bàn phím", "chuột", "máy ảnh", "máy in",
    "thiết bị mạng", "router", "modem", "smartwatch", "đồng hồ thông minh",
    "lắp ráp", "điện tử", "sim số", "máy sấy", "máy giặt", "tủ lạnh",
    "điều hòa", "bluetooth",
]

# ── Shared UI helpers ───────────────────────────────────────────────────────────────────
from components.ui_helpers import icon_header as _icon_header, fa_callout as _fa_callout
from data.loaders import load_4_tables
from data.filters import clean_numeric, apply_global_filters


# ── Condition normaliser (shared by Charts 2, 3, 4) ──────────────────────────

def _simplify_ebay_condition(cond: str) -> str | None:
    """Map a raw eBay condition string to one of three canonical groups, or None."""
    c = str(cond).lower().strip()
    if c == "new" or any(k in c for k in ["brand new", "new with tags", "new other", "nuovo", "neu"]):
        return "eBay — New"
    if any(k in c for k in ["used", "usato"]):
        return "eBay — Used"
    if any(k in c for k in [
        "refurbished", "open box", "opened", "certified",
        "good -", "excellent -", "very good -",
    ]):
        return "eBay — Refurb / Open Box"
    return None   # for-parts / unknown → excluded


# ============================================================
# CHART 1 (EXISTING): Tiki Product Stagnation Risk
# ============================================================

def render_tiki_cold_start(
    df_fact_tiki: pd.DataFrame,
    df_product:   pd.DataFrame,
    df_category:  pd.DataFrame,
) -> None:
    """Pareto chart: Tiki categories ranked by zero-interaction product count."""
    _icon_header(
        "fa-solid fa-triangle-exclamation",
        "1. Tiki Ecosystem — Product Stagnation Risk",
        color="#ef4444",
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
    colors  = ["#ef4444"] * 3 + ["#e2e8f0"] * (len(plot_df) - 3)
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
    st.plotly_chart(fig, width="stretch")

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


# ============================================================
# CHART 2 (EXISTING): eBay Item Condition Analysis
# ============================================================

def render_ebay_condition_analysis(df_fact_ebay: pd.DataFrame) -> None:
    """Treemap + horizontal bar: eBay condition market share and average cost."""
    _icon_header(
        "fa-solid fa-layer-group",
        "2. eBay Ecosystem — Item Condition Distribution & Cost Impact",
        color="#0369a1",
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
        st.plotly_chart(fig_t, width="stretch")

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
        st.plotly_chart(fig_b, width="stretch")

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


# ── Gaussian KDE — no scipy required ──────────────────────────────────────────

def _compute_kde(
    values:   np.ndarray,
    n_points: int   = 500,
    trim_pct: float = 99.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Vectorized Gaussian KDE using Scott's bandwidth rule.
    Subsamples up to 6,000 observations for performance.

    Returns
    -------
    x   : evaluation grid
    kde : probability density at each grid point
    """
    values = values[np.isfinite(values)]
    n = len(values)
    if n < 5:
        return np.array([]), np.array([])

    bw = 1.06 * np.std(values) * n ** (-0.2)
    if bw <= 0:
        return np.array([]), np.array([])

    x_lo = np.percentile(values, 100 - trim_pct)
    x_hi = np.percentile(values, trim_pct)
    if x_lo >= x_hi:
        return np.array([]), np.array([])

    x = np.linspace(x_lo, x_hi, n_points)

    rng    = np.random.default_rng(42)
    sample = values if n <= 6_000 else rng.choice(values, 6_000, replace=False)

    diff = (x[:, None] - sample[None, :]) / bw
    kde  = np.exp(-0.5 * diff ** 2).mean(axis=1) / (bw * np.sqrt(2 * np.pi))
    return x, kde


# ============================================================
# CHART 3 (NEW — Objective 9): Overlapping KDE Plot
# ============================================================

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
    _icon_header(
        "fa-solid fa-chart-area",
        "3. Cross-Platform Price Architecture — Overlapping KDE  &middot;  Objective 9",
        color="#0d9488",
    )
    st.markdown(
        "Compares the **probability density of prices (VND)** for Tiki tech/electronics "
        "listings against eBay condition groups. Vertical dotted lines mark each "
        "group's **median**, enabling direct measurement of the price premium or discount "
        "between platforms."
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
        tiki_label:                 {"color": "#0d9488", "dash": "solid"},
        "eBay — New":               {"color": "#f97316", "dash": "solid"},
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
    st.plotly_chart(fig, width="stretch")

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
        st.dataframe(pd.DataFrame(rows).set_index("Group"), width="stretch")

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
    Chart 4 — Objective 10
    Lollipop chart: average listing age per eBay top-N categories,
    identifying the fastest- and slowest-turnover market segments.
    """
    _icon_header(
        "fa-solid fa-hourglass-half",
        "4. eBay Listing Lifespan by Category — Lollipop Chart  &middot;  Objective 10",
        color="#7c3aed",
    )
    st.markdown(
        "Estimates the **average listing age** of eBay products — measured from "
        "`item_creation_date` to the data-collection date of **01 Apr 2026** — "
        "to identify the categories with the **fastest market turnover** (young listings) "
        "versus those with **slow absorption** (stagnant, long-lived listings)."
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
    st.plotly_chart(fig, width="stretch")

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


# ============================================================
# MAIN RENDER ENTRY-POINT
# ============================================================

def render(filters: Dict[str, Any]) -> None:
    """Tab 3 entry-point — Characteristics & Trends (4 charts)."""

    _icon_header(
        "fa-solid fa-chart-line",
        "Characteristics &amp; Trends",
        level=2,
        color="#0d9488",
    )
    st.markdown(
        "A comprehensive overview of listing characteristics and pricing behaviour, "
        "bridging the **B2C pipeline (Tiki)** with the **C2C/B2C hybrid structure (eBay)**."
    )

    try:
        df_fact_tiki, df_fact_ebay, df_product, df_category = load_4_tables()
    except Exception as exc:
        st.error(f"Failed to load datasets: {exc}. Check `../data/processed/`.")
        return

    df_fact_tiki = clean_numeric(df_fact_tiki, ["price"])
    df_fact_ebay = clean_numeric(df_fact_ebay, ["Total_Cost_VND"])

    df_tiki_f, df_ebay_f = apply_global_filters(df_fact_tiki, df_fact_ebay, filters)

    # Chart 1 — Pareto (existing)
    with st.container():
        render_tiki_cold_start(df_tiki_f, df_product, df_category)
    st.divider()

    # Chart 2 — eBay Condition (existing)
    with st.container():
        render_ebay_condition_analysis(df_ebay_f)
    st.divider()

    # Chart 3 — Overlapping KDE (Objective 9)
    with st.container():
        render_price_kde_comparison(df_tiki_f, df_ebay_f, df_product, df_category)
    st.divider()

    # Chart 4 — Lollipop Lifespan (Objective 10)
    with st.container():
        render_ebay_lollipop_lifespan(df_ebay_f, df_product, df_category)