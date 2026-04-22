import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any

from components.ui_helpers import icon_header as _icon_header, fa_callout as _fa_callout
from data.loaders import load_5_tables
from data.filters import clean_numeric, apply_global_filters
from config import (
    TEAL   as _TEAL,
    ORANGE as _ORANGE,
    BLUE   as _BLUE,
    SLATE  as _SLATE,
    DARK   as _DARK,
    AMBER  as _AMBER,
    GREEN  as _GREEN,
    INDIGO as _INDIGO,
    RED    as _RED,
    RATING_BINS   as _RATING_BINS,
    RATING_LABELS as _RATING_LABELS,
    RATING_COLORS as _RATING_COLORS,
    EBAY_TIERS    as _EBAY_TIERS,
    EBAY_COLORS   as _EBAY_COLORS,
    get_chart_palette as _get_palette,
)


def _hex_to_rgba(hex_color: str, alpha: float = 0.15) -> str:
    """Convert #rrggbb to rgba(r,g,b,alpha)."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"



# Section 1 — Tiki: Rating Tier × Average Sales (Objective 7)
def render_tiki_rating_sales(
    df_fact_tiki: pd.DataFrame,
    df_product: pd.DataFrame,
    df_category: pd.DataFrame,
) -> None:
    _pal = _get_palette()
    _TEAL = _pal["teal"]; _ORANGE = _pal["orange"]; _BLUE = _pal["blue"]
    _SLATE = _pal["slate"]; _AMBER = _pal["amber"]; _INDIGO = _pal["indigo"]
    _icon_header("fa-solid fa-star", "1. Tiki — Rating Tier & Average Sales Performance")

    if df_fact_tiki.empty:
        _fa_callout("fa-solid fa-circle-exclamation", _ORANGE,
                    "No Tiki listings match the current global filters.")
        return

    # Data prep
    df = df_fact_tiki.merge(df_product[["product_id", "category_id"]], on="product_id", how="left")
    df = df.merge(df_category, on="category_id", how="left")
    df = df[df["category"] != "Unknown"]
    df["rating_average"] = pd.to_numeric(df["rating_average"], errors="coerce")
    df["quantity_sold"]  = pd.to_numeric(df["quantity_sold"],  errors="coerce")
    df.dropna(subset=["rating_average", "quantity_sold"], inplace=True)
    df["Rating_Tier"] = pd.cut(df["rating_average"], bins=_RATING_BINS, labels=_RATING_LABELS)

    all_cats = sorted(df["category"].dropna().unique().tolist())

    # Shared dropdown — controls both Chart A and Chart B (Gestalt: Proximity)
    selected_cat = st.selectbox(
        "Select a Category to Analyse",
        options=["All Categories"] + all_cats,
        index=0,
        help="Filter both charts by product category.",
    )

    df_sel = df.copy() if selected_cat == "All Categories" else df[df["category"] == selected_cat].copy()

    # Aggregate for Chart A
    agg = (
        df_sel.groupby("Rating_Tier", observed=True)
        .agg(Avg_Sold=("quantity_sold", "mean"), Count=("product_id", "count"))
        .reset_index()
    )
    agg["Rating_Tier"] = pd.Categorical(agg["Rating_Tier"].astype(str), categories=_RATING_LABELS, ordered=True)
    agg = agg.sort_values("Rating_Tier")

    max_idx  = agg["Avg_Sold"].idxmax() if not agg.empty else None
    max_tier = str(agg.loc[max_idx, "Rating_Tier"]) if max_idx is not None else "-"
    max_val  = agg["Avg_Sold"].max() if not agg.empty else 0

    # KPI cards
    total  = len(df_sel)
    no_rat = int((df_sel["rating_average"] == 0).sum())
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Products", f"{total:,}")
    m2.metric("Products Without Rating", f"{no_rat:,}",
              delta=f"{no_rat/total*100:.1f}%", delta_color="inverse")
    m3.metric("Top Sales Tier", max_tier,
              delta=f"{max_val:,.1f} avg units/product", delta_color="off")

    # Chart A — Bar Chart: Avg Qty Sold per Rating Tier
    st.markdown("##### Chart A — Average Quantity Sold per Product by Rating Tier")

    # Highlight top tier, fade others (Gestalt: Similarity + Continuity)
    bar_colors_a = [
        _RATING_COLORS.get(str(t), _SLATE) if str(t) == max_tier
        else "rgba(148,163,184,0.40)"
        for t in agg["Rating_Tier"]
    ]

    fig_a = go.Figure(go.Bar(
        x=agg["Rating_Tier"],
        y=agg["Avg_Sold"],
        marker_color=bar_colors_a,
        text=agg["Avg_Sold"].apply(lambda v: f"{v:,.1f}"),
        textposition="outside",
        textfont=dict(size=11, family="Inter"),
        customdata=agg["Count"],
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Avg Sold: <b>%{y:,.1f}</b> units/product<br>"
            "Products: %{customdata:,}<extra></extra>"
        ),
    ))

    # Enclosure: highlight top tier box (Gestalt: Enclosure)
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
            text=f"Avg Qty Sold per Product by Rating Tier"
                 f"{'' if selected_cat == 'All Categories' else f' — {selected_cat}'}",
            font=dict(size=13, family="Inter"),
        ),
        xaxis=dict(title="Rating Tier", showgrid=False),
        yaxis=dict(title="Avg Qty Sold (per product)", showgrid=False),
        margin=dict(t=60, b=20, l=0, r=0),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
    )

    with st.container(border=True):
        st.plotly_chart(fig_a, width='stretch')

    # Chart B — Grouped Bar: Rating Tier × Top 5 Categories
    st.markdown("##### Chart B — Grouped Bar: Avg Qty Sold per Product by Rating Tier across Categories")

    top_n_cats = (
        df[df["category"].notna()]
        .groupby("category")["product_id"].count()
        .nlargest(5)
        .index.tolist()
    )

    df_grouped = df[df["category"].isin(top_n_cats)].copy()
    agg_grouped = (
        df_grouped.groupby(["Rating_Tier", "category"], observed=True)["quantity_sold"]
        .mean()
        .reset_index()
        .rename(columns={"quantity_sold": "Avg_Sold"})
    )
    agg_grouped["Rating_Tier"] = pd.Categorical(
        agg_grouped["Rating_Tier"].astype(str), categories=_RATING_LABELS, ordered=True
    )
    agg_grouped = agg_grouped.sort_values("Rating_Tier")

    fig_b = go.Figure()

    # Each category uses a distinct color; selected category pops out (Gestalt: Similarity + Proximity)
    cat_palette = [_TEAL, _ORANGE, _BLUE, _AMBER, _INDIGO]
    for i, cat in enumerate(top_n_cats):
        cat_data = agg_grouped[agg_grouped["category"] == cat]
        y_vals = [
            cat_data.loc[cat_data["Rating_Tier"] == tier, "Avg_Sold"].values[0]
            if tier in cat_data["Rating_Tier"].values else 0
            for tier in _RATING_LABELS
        ]
        is_selected = (selected_cat == "All Categories" or selected_cat == cat)
        color = cat_palette[i % len(cat_palette)] if is_selected else "rgba(148,163,184,0.25)"

        fig_b.add_trace(go.Bar(
            name=cat,
            x=_RATING_LABELS,
            y=y_vals,
            marker_color=color,
            text=[f"{v:,.1f}" if v > 0 else "" for v in y_vals],
            textposition="outside",
            textfont=dict(size=9, family="Inter"),
            opacity=1.0 if is_selected else 0.4,
        ))

    fig_b.update_layout(
        template="plotly_white",
        barmode="group",
        title=dict(
            text="Avg Qty Sold per Product by Rating Tier — Top 5 Categories (Grouped)",
            font=dict(size=13, family="Inter"),
        ),
        xaxis=dict(title="Rating Tier", showgrid=False),
        yaxis=dict(title="Avg Qty Sold (per product)", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(family="Inter", size=10)),
        margin=dict(t=70, b=20, l=0, r=0),
        height=440,
        paper_bgcolor="rgba(0,0,0,0)",
    )

    with st.container(border=True):
        st.plotly_chart(fig_b, width='stretch')

    # Insights expander
    with st.expander("Chart Insights & Actionable Recommendations"):
        if not agg.empty and max_idx is not None:
            low_tier  = str(agg.loc[agg["Avg_Sold"].idxmin(), "Rating_Tier"])
            low_val   = agg["Avg_Sold"].min()
            gap_pct   = ((max_val - low_val) / max(low_val, 1)) * 100
            st.markdown(
                '<i class="fa-solid fa-circle-info" style="color:#0d9488;'
                'margin-right:0.4rem;"></i>**How to read these charts:** '
                'Products are grouped into 4 rating tiers (No Rating / Low 1–3 / Average 3–4 / High 4–5). '
                'Chart A shows **average quantity sold per product** for the selected category. '
                'Chart B compares all top 5 categories side-by-side. '
                'Use the dropdown above to filter by category.',
                unsafe_allow_html=True,
            )
            st.divider()
            st.markdown(
                '<i class="fa-solid fa-magnifying-glass" style="color:#0d9488;'
                'margin-right:0.4rem;"></i>**Chart Analysis**',
                unsafe_allow_html=True,
            )
            st.write(f"""
**Trend:** Average sales increase monotonically with rating tier — the **{max_tier}** tier
leads at **{max_val:,.1f} units/product**, {gap_pct:.0f}% above the lowest tier (**{low_tier}**: {low_val:,.1f} units/product).
This confirms a clear positive relationship between product rating and consumer purchasing behaviour.

**Outlier / Cold-start:** **{no_rat:,}** products ({no_rat/total*100:.1f}% of the selection)
carry zero rating — these are trapped in a cold-start cycle: no rating → low visibility → no sales.
This pool actively suppresses overall platform conversion rate.

**Difference across categories (Chart B):** Not all categories benefit equally from high ratings.
Categories with high competition rely more heavily on social proof, while niche categories may
convert despite lower ratings. Use Chart B to identify where rating improvements yield the highest ROI.
""")
            st.markdown(
                '<i class="fa-solid fa-lightbulb" style="color:#f59e0b;'
                'margin-right:0.4rem;"></i>**Recommended Next Steps**',
                unsafe_allow_html=True,
            )
            st.write(f"""
* **Priority action:** Launch post-purchase review campaigns targeting **No Rating** and **Low (1–3)**
  products — even 1 verified review can move a product out of the cold-start pool.
* **Seller strategy:** Products in the **{max_tier}** tier convert at {max_val:,.1f} avg units — prioritise
  inventory replenishment and promotional spend for this segment.
* **Platform insight:** With {no_rat/total*100:.1f}% of listings having no rating, Tiki could improve
  overall GMV by implementing an automated post-delivery review request system.
""")
            st.markdown(
                '<i class="fa-solid fa-arrow-right-long" style="color:#0d9488;margin-right:0.4rem;"></i>'
                '<em>For discount and pricing analysis — navigate to <strong>Tab: Pricing &amp; Promotions</strong></em>',
                unsafe_allow_html=True,
            )
        else:
            st.info("Insufficient data to generate insights for the current filter selection.")


# Section 2 — eBay: Seller Feedback Score × Price (Objective 8)
def render_ebay_trust_boxplot(
    df_fact_ebay: pd.DataFrame,
    df_seller: pd.DataFrame,
) -> None:
    _pal = _get_palette()
    _TEAL = _pal["teal"]; _ORANGE = _pal["orange"]; _BLUE = _pal["blue"]
    _SLATE = _pal["slate"]; _AMBER = _pal["amber"]; _INDIGO = _pal["indigo"]
    _icon_header(
        "fa-solid fa-shield-halved",
        "2. eBay — Seller Trust Tier & Price Distribution",
        color=_ORANGE)

    if df_fact_ebay.empty:
        _fa_callout("fa-solid fa-circle-exclamation", _ORANGE,
                    "No eBay listings match the current global filters.")
        return

    # Data prep — stratify sellers into 4 trust tiers by feedback_score
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

    # Aggregate stats per tier
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

    # KPI cards — one per tier, ordered Newcomer → Elite
    col1, col2, col3, col4 = st.columns(4)
    for col_widget, tier in zip([col1, col2, col3, col4], _EBAY_TIERS):
        if tier in tier_stats.index and not pd.isna(tier_stats.loc[tier, "Median"]):
            col_widget.metric(
                label=tier,
                value=f"{tier_stats.loc[tier, 'Median'] / 1_000_000:.1f}M VND",
                delta=f"{int(tier_stats.loc[tier, 'Count']):,} listings",
                delta_color="off",
            )

    # Chart A — Bar Chart: Median Price per Seller Tier
    st.markdown("##### Chart A — Median Listing Price by Seller Feedback Score Tier")

    median_vals = tier_stats["Median"].values

    # Highlight tier with highest median; others faded (Gestalt: Similarity + Continuity)
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

    # Enclosure: highlight highest median tier (Gestalt: Enclosure)
    fig_a.add_vrect(
        x0=max_tier, x1=max_tier,
        fillcolor="#ede9fe", opacity=0.45,
        line_width=2, line_color=_INDIGO,
        annotation_text="Highest Median",
        annotation_position="top left",
        annotation_font=dict(size=10, color=_INDIGO),
    )

    # Trend line connecting median points (Gestalt: Connection)
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
        st.plotly_chart(fig_a, width='stretch')

    # Chart B — Stratified Boxplot: Price Dispersion by Seller Tier
    st.markdown("##### Chart B — Stratified Boxplot: Price Dispersion by Seller Tier")

    fig_b = go.Figure()

    # Each tier uses its own color (Gestalt: Similarity + Continuity + Closure)
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

    # Enclosure around Elite tier (Gestalt: Enclosure)
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
        st.plotly_chart(fig_b, width='stretch')

    # Insights expander
    with st.expander("Chart Insights & Actionable Recommendations"):
        valid = tier_stats.dropna(subset=["Median"])
        if len(valid) >= 2:
            low_med        = valid.loc[min_tier, "Median"] / 1_000_000
            high_med       = valid.loc[max_tier, "Median"] / 1_000_000
            price_gap      = high_med - low_med
            widest_iqr_val = iqr_stats.loc[widest_tier, "IQR"] / 1e6 if widest_tier in iqr_stats.index else 0
            st.markdown(
                '<i class="fa-solid fa-circle-info" style="color:#f97316;'
                'margin-right:0.4rem;"></i>**How to read these charts:** '
                'Sellers are stratified into 4 tiers by <code>feedback_score</code> '
                '(Newcomer 1–500 / Established 501–5K / Reputable 5K–50K / Elite 50K+). '
                'Chart A shows <strong>median price</strong> per tier. '
                'Chart B shows the full <strong>price distribution (IQR + outliers)</strong> via Stratified Boxplot.',
                unsafe_allow_html=True,
            )
            st.divider()
            st.markdown(
                '<i class="fa-solid fa-magnifying-glass" style="color:#0d9488;'
                'margin-right:0.4rem;"></i>**Chart Analysis**',
                unsafe_allow_html=True,
            )
            st.write(f"""
**Trend (Chart A):** Median listing price increases progressively with seller trust tier.
**{min_tier}** sellers price at a median of **{low_med:.2f}M VND**, while **{max_tier}** sellers
command **{high_med:.2f}M VND** — a gap of **{price_gap:.2f}M VND** (+{price_gap/max(low_med,0.01)*100:.0f}%).
This confirms that higher trust unlocks a pricing premium, reflecting perceived product quality and service reliability.

**Outlier / Dispersion (Chart B — Boxplot):** The **{widest_tier}** tier exhibits the widest IQR
(**{widest_iqr_val:.2f}M VND**), indicating heterogeneous inventory — a mix of budget and premium
products within the same seller cohort. The **Elite (50K+)** tier shows the tightest distribution,
signalling disciplined, strategy-driven pricing behaviour.

**Difference between tiers:** The IQR narrows as trust level increases, suggesting that elite sellers
have converged on a professional pricing model, while lower-tier sellers compete across a wider
price spectrum to compensate for lower credibility signals.
""")
            st.markdown(
                '<i class="fa-solid fa-lightbulb" style="color:#f59e0b;'
                'margin-right:0.4rem;"></i>**Recommended Strategy**',
                unsafe_allow_html=True,
            )
            st.write(f"""
* **Buyers — budget purchases:** Newcomer/Established tiers ({low_med:.2f}M median) may surface
  competitive deals but carry higher price variance — always cross-check item condition and
  seller feedback percentage before committing.
* **Buyers — high-value electronics:** Reputable/Elite sellers ({high_med:.2f}M median) demonstrate
  consistent pricing and are lower-risk procurement channels for premium products.
* **Sellers — reputation building:** Moving from Newcomer to Established tier alone can justify
  a higher price anchor. Accumulate verified feedback systematically to unlock the pricing premium.
* **Cross-reference:** Use `seller_feedback_percent` (positive rate) alongside `feedback_score`
  to filter legacy accounts with high scores but poor recent performance.
""")
            st.markdown(
                '<i class="fa-solid fa-arrow-right-long" style="color:#f97316;margin-right:0.4rem;"></i>'
                '<em>For price distribution and shipping cost breakdown — navigate to <strong>Tab: Pricing &amp; Promotions</strong></em>',
                unsafe_allow_html=True,
            )
        else:
            st.info("Insufficient data to generate insights for the current filter selection.")


# Main render function — invoked by app.py
def render(filters: Dict[str, Any]) -> None:
    """
    Trust & Reputation tab — two sections answering Objectives 7 & 8.
    Section 1: Tiki rating tiers × average sales (Obj 7)
    Section 2: eBay seller trust tiers × price distribution (Obj 8)
    """
    _icon_header("fa-solid fa-shield-halved", "Trust &amp; Reputation", level=2)

    with st.expander("About this tab"):
        st.markdown(
            "This tab analyses **how trust signals shape market outcomes** across two platforms. "
            "On **Tiki** (B2C), product ratings drive consumer purchase decisions — "
            "we measure whether higher-rated products sell more on average. "
            "On **eBay** (C2C/B2C hybrid), seller feedback score stratifies pricing power — "
            "we measure whether trusted sellers command a price premium and how tightly they price. "
            "Read Section 1 (Tiki) then Section 2 (eBay) to follow the analytical narrative."
        )

    try:
        df_fact_tiki, df_fact_ebay, df_product, df_category, df_seller = load_5_tables()
    except Exception as e:
        st.error(f"Error loading datasets: {e}. Please check routing in `../data/processed/`.")
        return

    df_fact_tiki = clean_numeric(df_fact_tiki, ["price"])
    df_fact_ebay = clean_numeric(df_fact_ebay, ["Total_Cost_VND"])

    df_tiki_filtered, df_ebay_filtered = apply_global_filters(df_fact_tiki, df_fact_ebay, filters)

    st.divider()

    with st.container():
        render_tiki_rating_sales(df_tiki_filtered, df_product, df_category)

    st.divider()

    with st.container():
        render_ebay_trust_boxplot(df_ebay_filtered, df_seller)

    st.divider()
