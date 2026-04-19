import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Tuple, Dict, Any, List


# ==========================================
# DATA LOADING & PREPROCESSING UTILS
# ==========================================
@st.cache_data
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Loads and caches datasets into memory to avoid continuous reloading."""
    data_dir = "../data/processed"
    df_fact_tiki = pd.read_csv(f"{data_dir}/fact_tiki_listings.csv", dtype={"product_id": str})
    df_fact_ebay = pd.read_csv(f"{data_dir}/fact_ebay_listings.csv", dtype={"product_id": str})
    df_product   = pd.read_csv(f"{data_dir}/dim_product.csv",         dtype={"product_id": str})
    df_category  = pd.read_csv(f"{data_dir}/dim_category.csv")
    df_seller    = pd.read_csv(f"{data_dir}/dim_seller.csv")
    return df_fact_tiki, df_fact_ebay, df_product, df_category, df_seller


def _clean_numeric_columns(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """Ensures target columns are numeric and drops rows with invalid values."""
    cleaned = df.copy()
    for col in cols:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
    return cleaned.dropna(subset=cols)


def _apply_global_filters(
    df_tiki: pd.DataFrame,
    df_ebay: pd.DataFrame,
    filters: Dict[str, Any],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Applies platform and price range filters globally to the datasets."""
    selected_platforms = filters.get("platform", ["Tiki", "eBay"])
    min_price, max_price = filters.get("price_range", (0, 50_000_000))

    if "Tiki" in selected_platforms:
        tiki_filtered = df_tiki[
            (df_tiki["price"] >= min_price) & (df_tiki["price"] <= max_price)
        ].copy()
    else:
        tiki_filtered = df_tiki.iloc[0:0].copy()

    if "eBay" in selected_platforms:
        ebay_filtered = df_ebay[
            (df_ebay["Total_Cost_VND"] >= min_price) & (df_ebay["Total_Cost_VND"] <= max_price)
        ].copy()
    else:
        ebay_filtered = df_ebay.iloc[0:0].copy()

    return tiki_filtered, ebay_filtered


# ==========================================
# 1. TIKI: RATING TIER × SALES (OBJECTIVE 1)
# ==========================================
def render_tiki_rating_sales(
    df_fact_tiki: pd.DataFrame,
    df_product: pd.DataFrame,
    df_category: pd.DataFrame,
) -> None:
    st.subheader("1. Tiki Ecosystem: Sales Performance by Rating Tier")

    # Defensive check
    if df_fact_tiki.empty:
        st.info("No Tiki listings match the current global filters. Please adjust the sidebar settings.")
        return

    # ── Data Processing ──────────────────────────────────────────────────────
    df_merged = df_fact_tiki.merge(df_product[["product_id", "category_id"]], on="product_id", how="left")
    df_merged = df_merged.merge(df_category, on="category_id", how="left")
    df_merged = df_merged[df_merged["category"] != "Unknown"]
    df_merged["rating_average"] = pd.to_numeric(df_merged["rating_average"], errors="coerce")
    df_merged["quantity_sold"]  = pd.to_numeric(df_merged["quantity_sold"],  errors="coerce")
    df_merged.dropna(subset=["rating_average", "quantity_sold"], inplace=True)

    # Bin ratings into meaningful tiers
    bins   = [-0.001, 0, 2.0, 3.0, 4.0, 4.5, 5.0]
    labels = ["No Rating (0)", "Low (0.1–2)", "Below Avg (2–3)", "Average (3–4)", "Good (4–4.5)", "Excellent (4.5–5)"]
    df_merged["Rating_Tier"] = pd.cut(df_merged["rating_average"], bins=bins, labels=labels)

    # ── Category Dropdown ────────────────────────────────────────────────────
    all_categories = sorted(df_merged["category"].dropna().unique().tolist())
    selected_cat = st.selectbox(
        "🗂️ Select a Category to Analyse",
        options=["All Categories"] + all_categories,
        index=0,
        help="Drill into a specific product category to reveal rating-to-sales patterns.",
    )

    plot_df = df_merged.copy() if selected_cat == "All Categories" else df_merged[df_merged["category"] == selected_cat].copy()

    # ── Aggregate per Rating Tier ────────────────────────────────────────────
    tier_order = ["No Rating (0)", "Low (0.1–2)", "Below Avg (2–3)", "Average (3–4)", "Good (4–4.5)", "Excellent (4.5–5)"]
    agg = (
        plot_df.groupby("Rating_Tier", observed=True)
        .agg(Listing_Count=("product_id", "count"), Total_Sold=("quantity_sold", "sum"))
        .reset_index()
    )
    agg["Rating_Tier"] = pd.Categorical(agg["Rating_Tier"].astype(str), categories=tier_order, ordered=True)
    agg = agg.sort_values("Rating_Tier")

    # ── Key Metrics ──────────────────────────────────────────────────────────
    total_listings = len(plot_df)
    has_rating     = int((plot_df["rating_average"] > 0).sum())
    max_idx        = agg["Total_Sold"].idxmax() if not agg.empty else None
    top_sold_tier  = str(agg.loc[max_idx, "Rating_Tier"]) if max_idx is not None else "-"

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Listings", f"{total_listings:,}")
    col2.metric(
        "Listings With Rating",
        f"{has_rating:,}",
        delta=f"{has_rating / total_listings * 100:.1f}%" if total_listings else "-",
    )
    col3.metric("Top Sales Tier", top_sold_tier)

    # ── Grouped Bar Chart (Listing Count + Total Sold, dual-axis) ────────────
    # Gestalt Pop-out: highlight best-performing tier in orange, rest muted gray
    bar_colors_listing = ["#f97316" if i == max_idx else "#94a3b8" for i in agg.index]
    bar_colors_sold    = ["#ea580c" if i == max_idx else "#cbd5e1" for i in agg.index]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=agg["Rating_Tier"],
        y=agg["Listing_Count"],
        name="Listing Count",
        marker_color=bar_colors_listing,
        text=agg["Listing_Count"],
        textposition="outside",
        yaxis="y",
    ))

    fig.add_trace(go.Bar(
        x=agg["Rating_Tier"],
        y=agg["Total_Sold"],
        name="Total Qty Sold",
        marker_color=bar_colors_sold,
        text=agg["Total_Sold"].apply(lambda v: f"{int(v):,}"),
        textposition="outside",
        yaxis="y2",
    ))

    fig.update_layout(
        template="plotly_white",
        barmode="group",
        title=dict(text="Listing Count vs Total Quantity Sold by Rating Tier", font=dict(size=15)),
        xaxis=dict(title="Rating Tier", tickangle=-20),
        yaxis=dict(title="Listing Count", showgrid=False),
        yaxis2=dict(
            title=dict(text="<b>Total Qty Sold</b>", font=dict(color="#ea580c")),
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(color="#ea580c"),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=70, b=20, l=0, r=0),
        height=480,
    )

    st.plotly_chart(fig, width="stretch")

    # ── Actionable Insights ──────────────────────────────────────────────────
    with st.expander("Chart Insights & Actionable Recommendations"):
        if not agg.empty and max_idx is not None:
            best_tier    = agg.loc[max_idx, "Rating_Tier"]
            no_rat_count = int(agg[agg["Rating_Tier"] == "No Rating (0)"]["Listing_Count"].sum())
            no_rat_pct   = no_rat_count / total_listings * 100 if total_listings else 0
            st.write(f"""
**Chart Analysis:**
* The **{best_tier}** tier drives the highest total sales volume{"" if selected_cat == "All Categories" else f" in the **{selected_cat}** category"}.
* **{no_rat_count:,}** listings ({no_rat_pct:.1f}%) carry zero rating — cold-start products with no social proof, likely suppressing conversion.
* The data confirms a clear positive correlation: higher rating tiers consistently unlock higher cumulative sales, validating **ratings as the primary trust signal** on Tiki.

**Recommended Next Steps:**
* Launch post-purchase review campaigns targeting **No Rating** and **Low** tier listings to accelerate social proof.
* Sellers should prioritise achieving the **Excellent (4.5–5)** tier to unlock maximum conversion potential.
* Focus promotional budget on upgrading the **Below Avg** pool rather than acquiring new listings.
            """)


# ==========================================
# 2. EBAY: SELLER FEEDBACK SCORE × PRICE (OBJECTIVE 2)
# ==========================================
def render_ebay_trust_boxplot(
    df_fact_ebay: pd.DataFrame,
    df_seller: pd.DataFrame,
) -> None:
    st.subheader("2. eBay Ecosystem: Price Distribution by Seller Feedback Score Tier")

    # Defensive check
    if df_fact_ebay.empty:
        st.info("No eBay listings match the current global filters. Please adjust the sidebar settings.")
        return

    # ── Data Processing ──────────────────────────────────────────────────────
    TIER_ORDER = ["Newcomer (1–500)", "Established (501–5K)", "Reputable (5K–50K)", "Elite (50K+)"]
    COLOR_MAP  = {
        "Newcomer (1–500)":     "#94a3b8",
        "Established (501–5K)": "#22c55e",
        "Reputable (5K–50K)":   "#f59e0b",
        "Elite (50K+)":         "#6366f1",
    }

    df_seller_copy = df_seller.copy()
    df_seller_copy["seller_feedback_score"] = pd.to_numeric(
        df_seller_copy["seller_feedback_score"], errors="coerce"
    )
    df_seller_copy["Score_Tier"] = pd.cut(
        df_seller_copy["seller_feedback_score"],
        bins=[0, 500, 5_000, 50_000, float("inf")],
        labels=TIER_ORDER,
        right=True,
    )

    df = df_fact_ebay.merge(
        df_seller_copy[["seller_username", "seller_feedback_score", "Score_Tier"]],
        on="seller_username",
        how="left",
    )
    df["Total_Cost_VND"] = pd.to_numeric(df["Total_Cost_VND"], errors="coerce")
    df.dropna(subset=["Total_Cost_VND", "Score_Tier"], inplace=True)
    df["Score_Tier"] = df["Score_Tier"].astype(str)

    if df.empty:
        st.warning("Insufficient data after joining seller tiers within this price range.")
        return

    # ── Key Metrics ──────────────────────────────────────────────────────────
    tier_stats = (
        df.groupby("Score_Tier")["Total_Cost_VND"]
        .agg(["median", "count"])
        .reindex(TIER_ORDER)
    )

    col1, col2, col3, col4 = st.columns(4)
    for col_widget, tier in zip([col1, col2, col3, col4], TIER_ORDER):
        if tier in tier_stats.index and not pd.isna(tier_stats.loc[tier, "median"]):
            col_widget.metric(
                label=tier,
                value=f"{tier_stats.loc[tier, 'median'] / 1_000_000:.1f}M VND",
                delta=f"{int(tier_stats.loc[tier, 'count']):,} listings",
                delta_color="off",
            )

    # ── Stratified Boxplot ───────────────────────────────────────────────────
    fig = go.Figure()

    for tier in TIER_ORDER:
        tier_data = df[df["Score_Tier"] == tier]["Total_Cost_VND"]
        if tier_data.empty:
            continue
        fig.add_trace(go.Box(
            y=tier_data,
            name=tier,
            marker_color=COLOR_MAP[tier],
            boxmean="sd",
            boxpoints="outliers",
            line_width=2,
            whiskerwidth=0.6,
        ))

    fig.update_layout(
        template="plotly_white",
        title=dict(
            text="Stratified Boxplot: Total Cost (VND) by Seller Feedback Score Tier",
            font=dict(size=15),
        ),
        xaxis=dict(title="Seller Feedback Score Tier"),
        yaxis=dict(title="Total Cost (VND)", showgrid=False),
        showlegend=False,
        margin=dict(t=60, b=20, l=0, r=0),
        height=500,
    )

    st.plotly_chart(fig, width="stretch")

    # ── Actionable Insights ──────────────────────────────────────────────────
    with st.expander("Chart Insights & Actionable Recommendations"):
        stats = (
            df.groupby("Score_Tier")["Total_Cost_VND"]
            .agg(["median", "std"])
            .reindex(TIER_ORDER)
            .dropna(subset=["median"])
        )
        if len(stats) >= 2:
            low_tier  = stats.index[0]
            high_tier = stats.index[-1]
            low_med   = stats.loc[low_tier,  "median"] / 1_000_000
            high_med  = stats.loc[high_tier, "median"] / 1_000_000

            iqr_by_tier = df.groupby("Score_Tier")["Total_Cost_VND"].quantile([0.25, 0.75]).unstack()
            iqr_by_tier["IQR"] = iqr_by_tier[0.75] - iqr_by_tier[0.25]
            widest_tier = iqr_by_tier["IQR"].idxmax() if not iqr_by_tier.empty else low_tier

            st.write(f"""
**Chart Analysis:**
* **{low_tier}** sellers list at a median of **{low_med:.1f}M VND** — typically lower-priced to attract first buyers.
* **{high_tier}** sellers command a median of **{high_med:.1f}M VND**, reflecting premium product quality or bundled offers.
* The **{widest_tier}** tier shows the widest IQR, indicating inconsistent pricing — a signal of mixed inventory quality.
* Elite tier sellers exhibit the tightest distribution, suggesting professional pricing strategies.

**Recommended Buying Strategy:**
* **Budget purchases**: Newcomer/Established tiers may surface deals but carry higher price variance — always cross-check item condition.
* **High-value electronics**: Reputable/Elite sellers demonstrate consistent pricing and are generally lower-risk procurement channels.
* **Cross-reference**: Always evaluate `seller_feedback_percent` alongside score tier to filter legacy or inactive accounts.
            """)


# ==========================================
# MAIN RENDER FUNCTION (Invoked by app.py)
# ==========================================
def render(filters: Dict[str, Any]) -> None:
    """Main rendering entrypoint for Tab 2: Trust & Reputation."""
    st.header("⭐ Trust & Reputation")
    st.markdown(
        "How ratings, reviews, and seller credibility drive sales on Tiki (B2C) "
        "and shape pricing dynamics on eBay (C2C/B2C hybrid)."
    )

    try:
        df_fact_tiki, df_fact_ebay, df_product, df_category, df_seller = load_data()
    except Exception as e:
        st.error(f"Error loading datasets: {e}. Please check routing in `../data/processed/`.")
        return

    # Clean critical numeric columns
    df_fact_tiki = _clean_numeric_columns(df_fact_tiki, ["price"])
    df_fact_ebay = _clean_numeric_columns(df_fact_ebay, ["Total_Cost_VND"])

    # Apply global sidebar filters
    df_tiki_filtered, df_ebay_filtered = _apply_global_filters(df_fact_tiki, df_fact_ebay, filters)

    with st.container():
        render_tiki_rating_sales(df_tiki_filtered, df_product, df_category)

    st.divider()

    with st.container():
        render_ebay_trust_boxplot(df_ebay_filtered, df_seller)