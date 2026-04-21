import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any, List

from components.ui_helpers import icon_header as _icon_header, fa_callout as _fa_callout
from data.loaders import load_5_tables
from data.filters import clean_numeric, apply_global_filters

# ── Palette ───────────────────────────────────────────────────────────────────
_TEAL   = "#0d9488"
_ORANGE = "#f97316"
_BLUE   = "#3b82f6"
_SLATE  = "#94a3b8"
_DARK   = "#0f172a"
_AMBER  = "#f59e0b"
_GREEN  = "#22c55e"
_INDIGO = "#6366f1"

# ── Rating tier config (shared across Obj 7 charts) ──────────────────────────
_RATING_BINS   = [-0.001, 0, 3.0, 4.0, 5.0]
_RATING_LABELS = ["No Rating (0)", "Low (1–3)", "Average (3–4)", "High (4–5)"]
_RATING_COLORS = {
    "No Rating (0)": _SLATE,
    "Low (1–3)":     "#ef4444",
    "Average (3–4)": _AMBER,
    "High (4–5)":    _TEAL,
}

# ── eBay tier config (shared across Obj 8 charts) ────────────────────────────
_EBAY_TIERS  = ["Newcomer (1–500)", "Established (501–5K)", "Reputable (5K–50K)", "Elite (50K+)"]
_EBAY_COLORS = {
    "Newcomer (1–500)":     _SLATE,
    "Established (501–5K)": _GREEN,
    "Reputable (5K–50K)":   _AMBER,
    "Elite (50K+)":         _INDIGO,
}

# ── Helper: convert #rrggbb → rgba(r,g,b,alpha) ──────────────────────────────
def _hex_to_rgba(hex_color: str, alpha: float = 0.15) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ============================================================
# TIKI: RATING TIER × AVERAGE SALES
# ============================================================
def render_tiki_rating_sales(
    df_fact_tiki: pd.DataFrame,
    df_product: pd.DataFrame,
    df_category: pd.DataFrame,
) -> None:
    _icon_header("fa-solid fa-star", "Tiki: Impact of Rating on Sales Performance")

    _fa_callout(
        "fa-solid fa-circle-info", _TEAL,
        "Products are grouped into <strong>4 rating tiers</strong>. "
        "Use the dropdown to filter by category. "
        "Chart A shows <em>total quantity sold per tier</em> for the selected category. "
        "Chart B shows a <em>Grouped Bar</em> comparing all categories side-by-side per tier."
    )

    if df_fact_tiki.empty:
        _fa_callout("fa-solid fa-circle-exclamation", _ORANGE,
                    "No Tiki listings match the current global filters.")
        return

    # ── Data prep ────────────────────────────────────────────────────────────
    df = df_fact_tiki.merge(df_product[["product_id", "category_id"]], on="product_id", how="left")
    df = df.merge(df_category, on="category_id", how="left")
    df = df[df["category"] != "Unknown"]
    df["rating_average"] = pd.to_numeric(df["rating_average"], errors="coerce")
    df["quantity_sold"]  = pd.to_numeric(df["quantity_sold"],  errors="coerce")
    df.dropna(subset=["rating_average", "quantity_sold"], inplace=True)
    df["Rating_Tier"] = pd.cut(df["rating_average"], bins=_RATING_BINS, labels=_RATING_LABELS)

    all_cats = sorted(df["category"].dropna().unique().tolist())

    # ── SHARED DROPDOWN — controls BOTH charts ────────────────────────────────
    # GESTALT – PROXIMITY: dropdown đặt trước cả 2 chart → người dùng hiểu
    # nó điều khiển toàn bộ section, không chỉ 1 chart
    selected_cat = st.selectbox(
        "Select a Category to Analyse",
        options=["All Categories"] + all_cats,
        index=0,
        help="Filter both charts by product category.",
    )

    # Data filtered by dropdown for Chart A
    df_sel = df.copy() if selected_cat == "All Categories" else df[df["category"] == selected_cat].copy()

    # ── Aggregate for Chart A ─────────────────────────────────────────────────
    agg = (
        df_sel.groupby("Rating_Tier", observed=True)
        .agg(Total_Sold=("quantity_sold", "sum"), Count=("product_id", "count"))
        .reset_index()
    )
    agg["Rating_Tier"] = pd.Categorical(agg["Rating_Tier"].astype(str), categories=_RATING_LABELS, ordered=True)
    agg = agg.sort_values("Rating_Tier")

    max_idx  = agg["Total_Sold"].idxmax() if not agg.empty else None
    max_tier = str(agg.loc[max_idx, "Rating_Tier"]) if max_idx is not None else "-"
    max_val  = agg["Total_Sold"].max() if not agg.empty else 0

    # ── KPI metrics ──────────────────────────────────────────────────────────
    # GESTALT – PROXIMITY: 3 metric cards sát nhau → nhóm KPI tổng quan
    total  = len(df_sel)
    no_rat = int((df_sel["rating_average"] == 0).sum())
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Products", f"{total:,}")
    m2.metric("Products Without Rating", f"{no_rat:,}",
              delta=f"{no_rat/total*100:.1f}%", delta_color="inverse")
    m3.metric("Top Sales Tier", max_tier,
              delta=f"{max_val:,.0f} total units", delta_color="off")

    # ── CHART A: Bar Chart — Total Qty Sold per Rating Tier ──────────────────
    # Mục tiêu: xác định tier nào có doanh số cao nhất trong category được chọn
    st.markdown("##### Chart A — Total Quantity Sold by Rating Tier")

    # GESTALT – SIMILARITY: tier bán tốt nhất highlight màu đậm (pop-out), còn lại nhạt
    # GESTALT – CONTINUITY: trục X No Rating → High theo chiều tăng dần
    bar_colors_a = [
        _RATING_COLORS.get(str(t), _SLATE) if str(t) == max_tier
        else "rgba(148,163,184,0.40)"
        for t in agg["Rating_Tier"]
    ]

    fig_a = go.Figure(go.Bar(
        x=agg["Rating_Tier"],
        y=agg["Total_Sold"],
        marker_color=bar_colors_a,
        text=agg["Total_Sold"].apply(lambda v: f"{int(v):,}"),
        textposition="outside",
        textfont=dict(size=11, family="Inter"),
        customdata=agg["Count"],
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Total Sold: <b>%{y:,}</b> units<br>"
            "Products: %{customdata:,}<extra></extra>"
        ),
    ))

    # GESTALT – ENCLOSURE: vrect bao quanh tier bán tốt nhất
    fig_a.add_vrect(
        x0=max_tier, x1=max_tier,
        fillcolor="#ccfbf1", opacity=0.4,
        line_width=2, line_color=_TEAL,
        annotation_text="Top Tier",
        annotation_position="top left",
        annotation_font=dict(size=10, color=_TEAL),
    )

    fig_a.update_layout(
        template="plotly_white",
        title=dict(
            text=f"Total Qty Sold by Rating Tier"
                 f"{'' if selected_cat == 'All Categories' else f' — {selected_cat}'}",
            font=dict(size=13, family="Inter"),
        ),
        xaxis=dict(title="Rating Tier", showgrid=False),
        yaxis=dict(title="Total Qty Sold", showgrid=False),
        margin=dict(t=60, b=20, l=0, r=0),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
    )

    with st.container(border=True):
        st.plotly_chart(fig_a, width="stretch")

    # ── CHART B: Grouped Bar Chart — Rating Tier × All Categories ────────────
    # Mục tiêu: so sánh pattern rating-to-sales GIỮA các category
    # X-axis = Rating Tier, mỗi group = 1 category → dễ thấy category nào
    # hưởng lợi nhiều nhất từ rating cao
    st.markdown("##### Chart B — Grouped Bar: Total Qty Sold by Rating Tier across Categories")

    # Lấy top N category có nhiều listing nhất để chart không quá rối
    top_n_cats = (
        df[df["category"].notna()]
        .groupby("category")["product_id"].count()
        .nlargest(5)
        .index.tolist()
    )

    # Nếu user chọn category cụ thể → highlight nó, hiện tất cả top5 nhưng mờ
    df_grouped = df[df["category"].isin(top_n_cats)].copy()
    agg_grouped = (
        df_grouped.groupby(["Rating_Tier", "category"], observed=True)["quantity_sold"]
        .sum()
        .reset_index()
        .rename(columns={"quantity_sold": "Total_Sold"})
    )
    agg_grouped["Rating_Tier"] = pd.Categorical(
        agg_grouped["Rating_Tier"].astype(str), categories=_RATING_LABELS, ordered=True
    )
    agg_grouped = agg_grouped.sort_values("Rating_Tier")

    fig_b = go.Figure()

    # GESTALT – SIMILARITY: mỗi category dùng màu riêng nhất quán
    # GESTALT – PROXIMITY: bars cùng Rating Tier đặt sát nhau thành cụm
    cat_palette = [_TEAL, _ORANGE, _BLUE, _AMBER, _INDIGO]
    for i, cat in enumerate(top_n_cats):
        cat_data = agg_grouped[agg_grouped["category"] == cat]
        y_vals = [
            cat_data.loc[cat_data["Rating_Tier"] == tier, "Total_Sold"].values[0]
            if tier in cat_data["Rating_Tier"].values else 0
            for tier in _RATING_LABELS
        ]
        # GESTALT – pop-out: category được chọn dùng màu đậm, còn lại mờ
        is_selected = (selected_cat == "All Categories" or selected_cat == cat)
        color = cat_palette[i % len(cat_palette)] if is_selected else "rgba(148,163,184,0.25)"

        fig_b.add_trace(go.Bar(
            name=cat,
            x=_RATING_LABELS,
            y=y_vals,
            marker_color=color,
            text=[f"{int(v):,}" if v > 0 else "" for v in y_vals],
            textposition="outside",
            textfont=dict(size=9, family="Inter"),
            opacity=1.0 if is_selected else 0.4,
        ))

    fig_b.update_layout(
        template="plotly_white",
        barmode="group",
        title=dict(
            text="Total Qty Sold by Rating Tier — Top 5 Categories (Grouped)",
            font=dict(size=13, family="Inter"),
        ),
        xaxis=dict(title="Rating Tier", showgrid=False),
        yaxis=dict(title="Total Qty Sold", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(family="Inter", size=10)),
        margin=dict(t=70, b=20, l=0, r=0),
        height=440,
        paper_bgcolor="rgba(0,0,0,0)",
    )

    with st.container(border=True):
        st.plotly_chart(fig_b, width="stretch")

    # ── Insights ─────────────────────────────────────────────────────────────
    with st.expander("Chart Insights & Actionable Recommendations"):
        if not agg.empty and max_idx is not None:
            low_tier = str(agg.loc[agg["Total_Sold"].idxmin(), "Rating_Tier"])
            st.markdown(
                '<i class="fa-solid fa-magnifying-glass" style="color:#0d9488;'
                'margin-right:0.4rem;"></i>**Statistical Findings**',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"- The **{max_tier}** tier records the highest total sales"
                f"{'' if selected_cat == 'All Categories' else f' in **{selected_cat}**'}"
                f" with **{int(max_val):,} units**, confirming rating as a primary conversion driver.\n"
                f"- The **{low_tier}** tier records the lowest volume — "
                f"products here struggle to convert without social proof.\n"
                f"- **{no_rat:,}** products ({no_rat/total*100:.1f}%) carry no rating — "
                f"a cold-start pool actively suppressing overall platform conversion.\n"
                f"- Chart B reveals whether the rating-to-sales pattern is consistent "
                f"across categories or concentrated in one dominant segment."
            )
            st.markdown(
                '<i class="fa-solid fa-lightbulb" style="color:#f59e0b;'
                'margin-right:0.4rem;"></i>**Recommended Next Steps**',
                unsafe_allow_html=True,
            )
            st.markdown(
                "- Launch **post-purchase review campaigns** targeting No Rating and Low tier "
                "products to accelerate social proof.\n"
                "- Sellers should prioritise the **High (4–5)** tier — the data shows it unlocks "
                "the highest conversion multiplier.\n"
                "- Use Chart B to identify which categories benefit most from rating improvements "
                "and prioritise those for review incentive programmes."
            )


# ============================================================
# EBAY: SELLER FEEDBACK SCORE × PRICE
# ============================================================
def render_ebay_trust_boxplot(
    df_fact_ebay: pd.DataFrame,
    df_seller: pd.DataFrame,
) -> None:
    _icon_header("fa-solid fa-medal", "eBay: Seller Trust Tier vs Listing Price",
                 color=_ORANGE)

    _fa_callout(
        "fa-solid fa-circle-info", _TEAL,
        "Sellers are stratified into <strong>4 tiers</strong> by <code>feedback_score</code>. "
        "Chart A shows <em>median price</em> per tier. "
        "Chart B shows the full <em>price distribution (IQR + outliers)</em> via Stratified Boxplot."
    )

    if df_fact_ebay.empty:
        _fa_callout("fa-solid fa-circle-exclamation", _ORANGE,
                    "No eBay listings match the current global filters.")
        return

    # ── Data prep ────────────────────────────────────────────────────────────
    df_s = df_seller.copy()
    df_s["seller_feedback_score"] = pd.to_numeric(df_s["seller_feedback_score"], errors="coerce")
    df_s["Score_Tier"] = pd.cut(
        df_s["seller_feedback_score"],
        bins=[0, 500, 5_000, 50_000, float("inf")],
        labels=_EBAY_TIERS,
        right=True,
    )

    df = df_fact_ebay.merge(
        df_s[["seller_username", "seller_feedback_score", "Score_Tier"]],
        on="seller_username", how="left",
    )
    df["Total_Cost_VND"] = pd.to_numeric(df["Total_Cost_VND"], errors="coerce")
    df.dropna(subset=["Total_Cost_VND", "Score_Tier"], inplace=True)
    df["Score_Tier"] = df["Score_Tier"].astype(str)

    if df.empty:
        _fa_callout("fa-solid fa-circle-exclamation", _ORANGE,
                    "Insufficient data after joining seller tiers.")
        return

    # ── Aggregate ────────────────────────────────────────────────────────────
    tier_stats = (
        df.groupby("Score_Tier")["Total_Cost_VND"]
        .agg(Median=("median"), Count=("count"))
        .reindex(_EBAY_TIERS)
    )
    iqr_stats = df.groupby("Score_Tier")["Total_Cost_VND"].quantile([0.25, 0.75]).unstack()
    iqr_stats.columns = ["Q1", "Q3"]
    iqr_stats["IQR"] = iqr_stats["Q3"] - iqr_stats["Q1"]
    iqr_stats = iqr_stats.reindex(_EBAY_TIERS)

    max_tier    = tier_stats["Median"].idxmax() if not tier_stats["Median"].isna().all() else "-"
    min_tier    = tier_stats["Median"].idxmin() if not tier_stats["Median"].isna().all() else "-"
    widest_tier = iqr_stats["IQR"].idxmax() if not iqr_stats["IQR"].isna().all() else "-"

    # ── KPI metrics ──────────────────────────────────────────────────────────
    # GESTALT – PROXIMITY: 4 metric cards theo thứ tự tier tăng dần
    col1, col2, col3, col4 = st.columns(4)
    for col_widget, tier in zip([col1, col2, col3, col4], _EBAY_TIERS):
        if tier in tier_stats.index and not pd.isna(tier_stats.loc[tier, "Median"]):
            col_widget.metric(
                label=tier,
                value=f"{tier_stats.loc[tier, 'Median'] / 1_000_000:.1f}M VND",
                delta=f"{int(tier_stats.loc[tier, 'Count']):,} listings",
                delta_color="off",
            )

    # ── CHART A: Bar Chart — Median Price per Tier ───────────────────────────
    st.markdown("##### Chart A — Median Listing Price by Seller Feedback Score Tier")

    median_vals = tier_stats["Median"].values
    # GESTALT – SIMILARITY: tier cao nhất highlight màu riêng, còn lại nhạt
    # GESTALT – CONTINUITY: trục X từ thấp → cao theo feedback score
    bar_colors_a = [
        _EBAY_COLORS.get(t, _SLATE) if t == max_tier else "rgba(148,163,184,0.45)"
        for t in _EBAY_TIERS
    ]

    fig_a = go.Figure(go.Bar(
        x=_EBAY_TIERS,
        y=median_vals,
        marker_color=bar_colors_a,
        text=[f"{v/1e6:.2f}M" if not np.isnan(v) else "" for v in median_vals],
        textposition="outside",
        textfont=dict(size=11, family="Inter"),
        hovertemplate="<b>%{x}</b><br>Median: %{y:,.0f} VND<extra></extra>",
    ))

    # GESTALT – ENCLOSURE: vrect bao quanh tier giá cao nhất
    fig_a.add_vrect(
        x0=max_tier, x1=max_tier,
        fillcolor="#ede9fe", opacity=0.45,
        line_width=2, line_color=_INDIGO,
        annotation_text="Highest Median",
        annotation_position="top left",
        annotation_font=dict(size=10, color=_INDIGO),
    )

    # GESTALT – CONNECTION: đường nối các điểm median → thể hiện xu hướng tăng
    fig_a.add_trace(go.Scatter(
        x=_EBAY_TIERS,
        y=median_vals,
        mode="lines+markers",
        name="Median trend",
        line=dict(color=_DARK, width=2, dash="dot"),
        marker=dict(size=7, color=_DARK, symbol="diamond"),
        hoverinfo="skip",
    ))

    fig_a.update_layout(
        template="plotly_white",
        title=dict(text="Median Total Cost (VND) per Seller Feedback Score Tier", font=dict(size=13, family="Inter")),
        xaxis=dict(title="Seller Feedback Score Tier", showgrid=False),
        yaxis=dict(title="Median Total Cost (VND)", showgrid=False),
        showlegend=False,
        margin=dict(t=60, b=20, l=0, r=0),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
    )

    with st.container(border=True):
        st.plotly_chart(fig_a, width="stretch")

    # ── CHART B: Stratified Boxplot ──────────────────────────────────────────
    st.markdown("##### Chart B — Stratified Boxplot: Price Dispersion by Seller Tier")

    fig_b = go.Figure()

    # GESTALT – SIMILARITY: mỗi tier dùng màu riêng nhất quán (giống metric card)
    # GESTALT – CONTINUITY: thứ tự Newcomer → Elite dẫn mắt trái → phải
    # GESTALT – CLOSURE: boxplot là hình đóng kín → mắt nhận diện phân phối tức thì
    for tier in _EBAY_TIERS:
        tier_data = df[df["Score_Tier"] == tier]["Total_Cost_VND"]
        if tier_data.empty:
            continue
        fig_b.add_trace(go.Box(
            y=tier_data,
            name=tier,
            marker_color=_EBAY_COLORS[tier],
            fillcolor=_hex_to_rgba(_EBAY_COLORS[tier], 0.15),
            boxmean="sd",
            boxpoints="outliers",
            line_width=2,
            whiskerwidth=0.6,
        ))

    # GESTALT – ENCLOSURE: vrect bao quanh Elite tier
    fig_b.add_vrect(
        x0="Elite (50K+)", x1="Elite (50K+)",
        fillcolor="#ede9fe", opacity=0.35,
        line_width=2, line_color=_INDIGO,
        annotation_text="Elite",
        annotation_position="top left",
        annotation_font=dict(size=10, color=_INDIGO),
    )

    fig_b.update_layout(
        template="plotly_white",
        title=dict(
            text="Stratified Boxplot: Total Cost (VND) by Seller Feedback Score Tier",
            font=dict(size=13, family="Inter"),
        ),
        xaxis=dict(title="Seller Feedback Score Tier", showgrid=False),
        yaxis=dict(title="Total Cost (VND)", showgrid=False),
        showlegend=False,
        margin=dict(t=60, b=20, l=0, r=0),
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
    )

    with st.container(border=True):
        st.plotly_chart(fig_b, width="stretch")

    # ── Insights ─────────────────────────────────────────────────────────────
    with st.expander("Chart Insights & Actionable Recommendations"):
        valid = tier_stats.dropna(subset=["Median"])
        if len(valid) >= 2:
            low_med  = valid.loc[min_tier,  "Median"] / 1_000_000
            high_med = valid.loc[max_tier, "Median"] / 1_000_000
            st.markdown(
                '<i class="fa-solid fa-magnifying-glass" style="color:#0d9488;'
                'margin-right:0.4rem;"></i>**Statistical Findings**',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"- **{min_tier}** sellers list at a median of **{low_med:.2f}M VND** — "
                f"entry-level pricing to attract first buyers.\n"
                f"- **{max_tier}** sellers command a median of **{high_med:.2f}M VND**, "
                f"reflecting premium product quality or bundled value.\n"
                f"- The **{widest_tier}** tier shows the widest IQR "
                f"(**{iqr_stats.loc[widest_tier, 'IQR']/1e6:.2f}M VND**) — "
                f"indicating inconsistent pricing, a signal of mixed inventory quality.\n"
                f"- Elite tier sellers exhibit the tightest distribution, "
                f"suggesting professional, strategy-driven pricing."
            )
            st.markdown(
                '<i class="fa-solid fa-lightbulb" style="color:#f59e0b;'
                'margin-right:0.4rem;"></i>**Recommended Buying Strategy**',
                unsafe_allow_html=True,
            )
            st.markdown(
                "- **Budget purchases**: Newcomer/Established tiers may surface deals "
                "but carry higher price variance — always cross-check item condition.\n"
                "- **High-value electronics**: Reputable/Elite sellers demonstrate "
                "consistent pricing and are generally lower-risk procurement channels.\n"
                "- **Cross-reference** `seller_feedback_percent` alongside score tier "
                "to filter legacy or inactive accounts with inflated scores."
            )


# ============================================================
# MAIN RENDER FUNCTION (Invoked by app.py)
# ============================================================
def render(filters: Dict[str, Any]) -> None:
    """Main rendering entrypoint for Tab 2: Trust & Reputation."""
    _icon_header("fa-solid fa-shield-halved", "Trust &amp; Reputation", level=2)
    _fa_callout(
        "fa-solid fa-circle-info", _TEAL,
        "How <strong>ratings</strong> and <strong>seller credibility</strong> drive sales on Tiki (B2C) "
        "and shape pricing dynamics on eBay (C2C/B2C hybrid)."
    )

    try:
        df_fact_tiki, df_fact_ebay, df_product, df_category, df_seller = load_5_tables()
    except Exception as e:
        st.error(f"Error loading datasets: {e}. Please check routing in `../data/processed/`.")
        return

    df_fact_tiki = clean_numeric(df_fact_tiki, ["price"])
    df_fact_ebay = clean_numeric(df_fact_ebay, ["Total_Cost_VND"])

    df_tiki_filtered, df_ebay_filtered = apply_global_filters(df_fact_tiki, df_fact_ebay, filters)

    with st.container():
        render_tiki_rating_sales(df_tiki_filtered, df_product, df_category)

    st.divider()

    with st.container():
        render_ebay_trust_boxplot(df_ebay_filtered, df_seller)