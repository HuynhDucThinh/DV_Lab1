import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any

from components.ui_helpers import icon_header as _icon_header
from data.filters import simplify_condition_short as _simplify_condition
from config import (
    TEAL as _TEAL, ORANGE as _ORANGE, BLUE as _BLUE, PURPLE as _PURPLE,
    RED as _RED, SLATE as _SLATE, DARK as _DARK, AMBER as _AMBER,
    GREEN as _GREEN, get_chart_palette as _get_palette,
)

# Section 1 - Dataset Snapshot
def _render_dataset_snapshot(
    df_t: pd.DataFrame,
    df_e: pd.DataFrame,
    df_p: pd.DataFrame,
    df_c: pd.DataFrame,
    df_t_raw: pd.DataFrame,
    df_e_raw: pd.DataFrame,
) -> None:
    """EDA snapshot: shape, feature types, and completeness."""
    _pal = _get_palette()
    _TEAL = _pal["teal"]; _ORANGE = _pal["orange"]; _BLUE = _pal["blue"]
    _PURPLE = _pal["purple"]; _SLATE = _pal["slate"]; _AMBER = _pal["amber"]
    _RED = _pal["red"]; _GREEN = _pal["green"]

    _icon_header("fa-solid fa-database", "1. Dataset Snapshot", color=_TEAL)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Records", f"{len(df_t_raw) + len(df_e_raw):,}", "across both platforms")
    k2.metric("Tiki Listings", f"{len(df_t_raw):,}", f"{df_t_raw.shape[1]} features")
    k3.metric("eBay Listings", f"{len(df_e_raw):,}", f"{df_e_raw.shape[1]} features")
    k4.metric("Product Dim", f"{len(df_p):,}", f"{len(df_c):,} categories")

    col_t, col_e = st.columns(2)

    tiki_schema = {
        "price":            ("Numeric",     f"{df_t_raw['price'].notna().mean()*100:.0f}%"),
        "original_price":   ("Numeric",     f"{df_t_raw['original_price'].notna().mean()*100:.0f}%"),
        "discount_rate":    ("Numeric",     f"{df_t_raw['discount_rate'].notna().mean()*100:.0f}%"),
        "rating_average":   ("Numeric",     f"{df_t_raw['rating_average'].notna().mean()*100:.0f}%"),
        "review_count":     ("Numeric",     f"{df_t_raw['review_count'].notna().mean()*100:.0f}%"),
        "quantity_sold":    ("Numeric",     f"{df_t_raw['quantity_sold'].notna().mean()*100:.0f}%"),
        "Is_Best_Seller":   ("Binary",      f"{df_t_raw['Is_Best_Seller'].notna().mean()*100:.0f}%"),
        "Discount_Segment": ("Categorical", f"{df_t_raw['Discount_Segment'].notna().mean()*100:.0f}%"),
    }
    with col_t:
        with st.container(border=True):
            st.markdown(
                f'<span style="color:{_TEAL}"><i class="fa-solid fa-circle" style="font-size:0.7rem;"></i></span> '
                f'<strong>Tiki</strong> — <code>fact_tiki_listings.csv</code>  ·  {len(df_t_raw):,} rows',
                unsafe_allow_html=True,
            )
            rows = [{"Column": c, "Type": t, "Complete": p} for c, (t, p) in tiki_schema.items()]
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    ebay_meta = {
        "Total_Cost_VND":     ("Numeric",     df_e_raw.get("Total_Cost_VND", pd.Series())),
        "price":              ("Numeric",     df_e_raw.get("price", pd.Series())),
        "shipping_cost":      ("Numeric",     df_e_raw.get("shipping_cost", pd.Series())),
        "condition":          ("Categorical", df_e_raw.get("condition", pd.Series())),
        "seller_username":    ("Categorical", df_e_raw.get("seller_username", pd.Series())),
        "item_creation_date": ("DateTime",    df_e_raw.get("item_creation_date", pd.Series())),
    }
    ebay_schema = {
        col: (t, f"{s.notna().mean()*100:.0f}%" if len(s) else "N/A")
        for col, (t, s) in ebay_meta.items()
    }
    with col_e:
        with st.container(border=True):
            st.markdown(
                f'<span style="color:{_ORANGE}"><i class="fa-solid fa-circle" style="font-size:0.7rem;"></i></span> '
                f'<strong>eBay</strong> — <code>fact_ebay_listings.csv</code>  ·  {len(df_e_raw):,} rows',
                unsafe_allow_html=True,
            )
            rows_e = [{"Column": c, "Type": t, "Complete": p} for c, (t, p) in ebay_schema.items()]
            st.dataframe(pd.DataFrame(rows_e), hide_index=True, use_container_width=True)

    with st.expander("Chart Insights & Actionable Recommendations"):
        st.write("""
**Data Structure Analysis:**
* Tiki data is fully structured with clean numerical features — price, discount, sales volume, and review metrics are all available for quantitative analysis.
* eBay data introduces a **categorical condition dimension** (New / Used / Refurbished) and an explicit shipping cost, enabling cross-platform comparison on both price structure and product quality signals.
* The completeness column shows which features are reliable enough for downstream analysis — any column below 90% should be treated with caution.

**Recommended Next Steps:**
* Use `discount_rate` and `quantity_sold` together to quantify promotion effectiveness (Section 2 and Tab: Pricing).
* Use `condition` from eBay as a primary segmentation variable to explain price differences relative to Tiki (Section 4).
        """)

    st.divider()


# Section 2 - Platform Scale
def _render_platform_scale(
    df_t: pd.DataFrame,
    df_e: pd.DataFrame,
    df_p: pd.DataFrame,
    df_c: pd.DataFrame,
) -> None:
    _pal = _get_palette()
    _TEAL = _pal["teal"]; _ORANGE = _pal["orange"]; _BLUE = _pal["blue"]
    _PURPLE = _pal["purple"]; _SLATE = _pal["slate"]; _AMBER = _pal["amber"]
    _RED = _pal["red"]; _GREEN = _pal["green"]

    _icon_header("fa-solid fa-chart-pie", "2. Platform Scale & Market Structure", color=_TEAL)

    total = len(df_t) + len(df_e)
    b1, b2, b3 = st.columns(3)
    b1.metric("Total Listings (filtered)", f"{total:,}")
    b2.metric("Tiki Share", f"{len(df_t)/max(total,1)*100:.1f}%", f"{len(df_t):,} products")
    b3.metric("eBay Share",  f"{len(df_e)/max(total,1)*100:.1f}%", f"{len(df_e):,} products")

    col_donut, col_cats = st.columns([4, 6])

    with col_donut:
        with st.container(border=True):
            fig = go.Figure(go.Pie(
                labels=["Tiki", "eBay"],
                values=[len(df_t), len(df_e)],
                hole=0.65,
                marker=dict(colors=[_TEAL, _ORANGE], line=dict(color="#fff", width=2)),
                textinfo="label+percent",
                textfont=dict(size=12, family="Inter"),
                direction="clockwise",
                hovertemplate="%{label}: %{value:,} listings (%{percent})<extra></extra>",
            ))
            fig.update_layout(
                title=dict(text="Listing Share by Platform", font=dict(size=13, family="Inter", color=_DARK)),
                showlegend=True,
                legend=dict(orientation="h", y=-0.08, font=dict(family="Inter")),
                margin=dict(t=50, b=30, l=10, r=10),
                height=310,
                paper_bgcolor="rgba(0,0,0,0)",
                annotations=[dict(
                    text=f"<b>{total:,}</b><br><span style='font-size:10px'>total</span>",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=14, color=_DARK, family="Inter"),
                )],
            )
            st.plotly_chart(fig, width='stretch')

    merged_t = pd.DataFrame()
    top = pd.Series(dtype=int)
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
                top = (
                    merged_t[merged_t["category"] != "Unknown"]["category"]
                    .value_counts()
                    .head(8)
                )
                if not top.empty:
                    colors_bar = [_TEAL] + [f"rgba(13,148,136,{0.85-i*0.09:.2f})" for i in range(1, 8)]
                    fig2 = go.Figure(go.Bar(
                        y=top.index.tolist(),
                        x=top.values,
                        orientation="h",
                        marker=dict(color=colors_bar[:len(top)]),
                        text=top.values,
                        textposition="outside",
                        textfont=dict(size=11, family="Inter"),
                        hovertemplate="%{y}: %{x:,} listings<extra></extra>",
                    ))
                    fig2.update_layout(
                        title=dict(text="Top 8 Tiki Categories — Listing Count",
                                   font=dict(size=13, family="Inter", color=_DARK)),
                        template="plotly_white",
                        xaxis=dict(title="Number of Listings", showgrid=True, gridcolor="#f1f5f9"),
                        yaxis=dict(title="Category", autorange="reversed", showgrid=False),
                        margin=dict(t=50, b=30, l=10, r=60),
                        height=310,
                        paper_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig2, width='stretch')

    with st.expander("Chart Insights & Actionable Recommendations"):
        if not top.empty:
            top_names  = top.index.tolist()
            top3_share = top.values[:3].sum() / max(len(df_t), 1) * 100
            st.write(f"""
**Chart Analysis:**
* The three most-listed Tiki categories are **{top_names[0]}**, **{top_names[1] if len(top_names) > 1 else "—"}**, and **{top_names[2] if len(top_names) > 2 else "—"}**, collectively accounting for **{top3_share:.1f}%** of all categorised Tiki listings.
* High listing concentration in **{top_names[0]}** signals strong consumer demand — but also intense price competition forcing sellers to differentiate on service quality or product features.
* eBay has a more distributed structure across technology sub-categories, while Tiki concentrates on everyday consumer goods.

**Recommended Next Steps:**
* For sellers in the top categories: invest in differentiation (bundles, fast shipping) rather than price cuts.
* Lower-volume categories may offer higher margin opportunities with less saturation — worth exploring in Tab: Pricing & Promotions.
            """)
            st.markdown(
                '<i class="fa-solid fa-arrow-right-long" style="color:#0d9488;margin-right:0.4rem;"></i>'
                '<em>For deep-dive category and discount analysis — navigate to <strong>Tab: Pricing &amp; Promotions</strong></em>',
                unsafe_allow_html=True,
            )
        else:
            st.info("No category data available for the current filter selection.")

    st.divider()


# Section 3 - Price Landscape
def _render_price_landscape(df_t: pd.DataFrame, df_e: pd.DataFrame) -> None:
    _pal = _get_palette()
    _TEAL = _pal["teal"]; _ORANGE = _pal["orange"]; _BLUE = _pal["blue"]
    _PURPLE = _pal["purple"]; _SLATE = _pal["slate"]; _AMBER = _pal["amber"]
    _RED = _pal["red"]; _GREEN = _pal["green"]

    _icon_header("fa-solid fa-scale-balanced", "3. Price Landscape", color=_ORANGE)

    tiki_p = pd.to_numeric(df_t["price"], errors="coerce").dropna().values if not df_t.empty else np.array([])
    ebay_p = pd.to_numeric(df_e["Total_Cost_VND"], errors="coerce").dropna().values if not df_e.empty else np.array([])

    p1, p2, p3, p4 = st.columns(4)
    if len(tiki_p):
        p1.metric("Tiki Median Price", f"{np.median(tiki_p)/1e6:.2f}M VND",
                  f"IQR: {(np.percentile(tiki_p,75)-np.percentile(tiki_p,25))/1e6:.2f}M")
        p2.metric("Tiki Mean Price", f"{np.mean(tiki_p)/1e6:.2f}M VND",
                  f"std: {np.std(tiki_p)/1e6:.2f}M")
    else:
        p1.metric("Tiki Median Price", "N/A")
        p2.metric("Tiki Mean Price", "N/A")

    if len(ebay_p):
        p3.metric("eBay Median Price", f"{np.median(ebay_p)/1e6:.2f}M VND",
                  f"IQR: {(np.percentile(ebay_p,75)-np.percentile(ebay_p,25))/1e6:.2f}M")
        if len(tiki_p):
            gap = (np.median(ebay_p) - np.median(tiki_p)) / 1e6
            p4.metric("Median Price Gap", f"{abs(gap):.2f}M VND",
                      "eBay higher" if gap > 0 else "Tiki higher")
        else:
            p4.metric("eBay Mean Price", f"{np.mean(ebay_p)/1e6:.2f}M VND")
    else:
        p3.metric("eBay Median Price", "N/A")
        p4.metric("Median Price Gap", "N/A")

    col_box, col_hist = st.columns(2)

    with col_box:
        with st.container(border=True):
            rng = np.random.default_rng(42)
            tiki_s = rng.choice(tiki_p, min(3000, len(tiki_p)), replace=False) if len(tiki_p) else np.array([])
            ebay_s = rng.choice(ebay_p, min(3000, len(ebay_p)), replace=False) if len(ebay_p) else np.array([])

            fig_box = go.Figure()
            if len(tiki_s):
                fig_box.add_trace(go.Box(
                    y=tiki_s / 1e6, name="Tiki",
                    marker_color=_TEAL, line_color=_TEAL,
                    boxmean=True, boxpoints="outliers",
                    fillcolor="rgba(13,148,136,0.12)",
                    hovertemplate="Tiki — %{y:.2f}M VND<extra></extra>",
                ))
            if len(ebay_s):
                fig_box.add_trace(go.Box(
                    y=ebay_s / 1e6, name="eBay",
                    marker_color=_ORANGE, line_color=_ORANGE,
                    boxmean=True, boxpoints="outliers",
                    fillcolor="rgba(249,115,22,0.12)",
                    hovertemplate="eBay — %{y:.2f}M VND<extra></extra>",
                ))
            fig_box.update_layout(
                title=dict(text="Price Distribution — Box Plot (M VND)",
                           font=dict(size=13, family="Inter", color=_DARK)),
                template="plotly_white",
                yaxis=dict(title="Price (Million VND)", showgrid=True, gridcolor="#f1f5f9"),
                xaxis=dict(title="Platform", showgrid=False),
                legend=dict(orientation="h", y=1.05, font=dict(family="Inter", size=11)),
                margin=dict(t=55, b=30, l=20, r=20),
                height=380,
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_box, width='stretch')

    with col_hist:
        with st.container(border=True):
            fig_hist = go.Figure()
            if len(tiki_p):
                cap_t = np.percentile(tiki_p, 99)
                fig_hist.add_trace(go.Histogram(
                    x=tiki_p[tiki_p <= cap_t] / 1e6, name="Tiki",
                    marker_color=_TEAL, opacity=0.6, nbinsx=40,
                    hovertemplate="Price: %{x:.1f}M VND<br>Count: %{y}<extra>Tiki</extra>",
                ))
            if len(ebay_p):
                cap_e = np.percentile(ebay_p, 99)
                fig_hist.add_trace(go.Histogram(
                    x=ebay_p[ebay_p <= cap_e] / 1e6, name="eBay",
                    marker_color=_ORANGE, opacity=0.6, nbinsx=40,
                    hovertemplate="Price: %{x:.1f}M VND<br>Count: %{y}<extra>eBay</extra>",
                ))
            fig_hist.update_layout(
                barmode="overlay",
                title=dict(text="Price Frequency Distribution (capped at P99)",
                           font=dict(size=13, family="Inter", color=_DARK)),
                template="plotly_white",
                xaxis=dict(title="Price (Million VND)", showgrid=True, gridcolor="#f1f5f9"),
                yaxis=dict(title="Number of Listings", showgrid=True, gridcolor="#f1f5f9"),
                legend=dict(orientation="h", y=1.05, font=dict(family="Inter", size=11)),
                margin=dict(t=55, b=30, l=20, r=20),
                height=380,
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_hist, width='stretch')

    with st.expander("Chart Insights & Actionable Recommendations"):
        if len(tiki_p) and len(ebay_p):
            t_med = np.median(tiki_p) / 1e6
            e_med = np.median(ebay_p) / 1e6
            t_iqr = (np.percentile(tiki_p, 75) - np.percentile(tiki_p, 25)) / 1e6
            e_iqr = (np.percentile(ebay_p, 75) - np.percentile(ebay_p, 25)) / 1e6
            premium = "eBay" if e_med > t_med else "Tiki"
            diverse = "eBay" if e_iqr > t_iqr else "Tiki"
            st.write(f"""
**Chart Analysis:**
* Tiki median = **{t_med:.2f}M VND** (IQR {t_iqr:.2f}M) vs eBay median = **{e_med:.2f}M VND** (IQR {e_iqr:.2f}M).
* **{premium}** commands a price premium on median — reflecting its market positioning.
* **{diverse}** shows wider pricing diversity (larger IQR) — indicating a more heterogeneous product mix across new, used, and refurbished conditions.
* The histogram overlay confirms Tiki pricing is left-skewed with a concentration in the low-to-mid range, while eBay exhibits a longer right tail.

**Recommended Pricing Strategy:**
* Use the IQR band as the target anchor for new listings — products priced beyond Q3 risk poor conversion without strong brand equity.
* Outliers above the upper fence should be audited for pricing errors or legitimate premium positioning.
* Cross-platform price gaps signal possible arbitrage opportunities in high-value electronics categories.
            """)
            st.markdown(
                '<i class="fa-solid fa-arrow-right-long" style="color:#f97316;margin-right:0.4rem;"></i>'
                '<em>For category-level price breakdown and discount impact — navigate to <strong>Tab: Pricing &amp; Promotions</strong></em>',
                unsafe_allow_html=True,
            )
        else:
            st.info("Insufficient data to compute price insights for the current filter selection.")

    st.divider()


# Section 4 - Product Profile
def _render_product_profile(
    df_t: pd.DataFrame,
    df_e: pd.DataFrame,
    df_p: pd.DataFrame,
    df_c: pd.DataFrame,
) -> None:
    _pal = _get_palette()
    _TEAL = _pal["teal"]; _ORANGE = _pal["orange"]; _BLUE = _pal["blue"]
    _PURPLE = _pal["purple"]; _SLATE = _pal["slate"]; _AMBER = _pal["amber"]
    _RED = _pal["red"]; _GREEN = _pal["green"]

    _icon_header("fa-solid fa-boxes-stacked", "4. Product Profile", color=_BLUE)

    col_cond, col_tree = st.columns(2)

    cond_counts = pd.DataFrame()
    with col_cond:
        with st.container(border=True):
            if not df_e.empty:
                cond_map = {"New": _BLUE, "Used": _SLATE, "Refurbished": _PURPLE}
                df_e_c = df_e.copy()
                df_e_c["_cond"] = df_e_c["condition"].apply(_simplify_condition)
                cond_counts = df_e_c["_cond"].dropna().value_counts().reset_index()
                cond_counts.columns = ["Condition", "Count"]
                cond_counts["Pct"] = (cond_counts["Count"] / cond_counts["Count"].sum() * 100).round(1)

                fig_cond = px.bar(
                    cond_counts, x="Condition", y="Count",
                    color="Condition", color_discrete_map=cond_map,
                    text=cond_counts.apply(lambda r: f"{r['Count']:,}<br>({r['Pct']}%)", axis=1),
                    custom_data=["Pct"],
                )
                fig_cond.update_traces(
                    textposition="outside",
                    textfont=dict(size=11, family="Inter"),
                    marker_line_width=0,
                    hovertemplate="<b>%{x}</b><br>Count: %{y:,}<br>Share: %{customdata[0]:.1f}%<extra></extra>",
                )
                fig_cond.update_layout(
                    title=dict(text="eBay Listings by Item Condition",
                               font=dict(size=13, family="Inter", color=_DARK)),
                    template="plotly_white",
                    xaxis=dict(title="Item Condition", showgrid=False),
                    yaxis=dict(title="Number of Listings", showgrid=True, gridcolor="#f1f5f9"),
                    showlegend=False,
                    margin=dict(t=55, b=30, l=20, r=20),
                    height=340,
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_cond, width='stretch')

                d1, d2, d3 = st.columns(3)
                for i, (_, row) in enumerate(cond_counts.iterrows()):
                    [d1, d2, d3][i].metric(row["Condition"], f"{row['Count']:,}", f"{row['Pct']}%")
            else:
                st.info("No eBay data available in the current filter range.")

    with col_tree:
        with st.container(border=True):
            if not df_t.empty and "Discount_Segment" in df_t.columns:
                merged_t = (
                    df_t
                    .merge(df_p[["product_id", "category_id"]], on="product_id", how="left")
                    .merge(df_c, on="category_id", how="left")
                )
                merged_t["category"] = merged_t["category"].fillna("Unknown")
                merged_t["Discount_Segment"] = merged_t["Discount_Segment"].fillna("No Discount")

                # Keep top 8 categories by volume
                top8 = (
                    merged_t[merged_t["category"] != "Unknown"]["category"]
                    .value_counts()
                    .head(8)
                    .index.tolist()
                )
                seg_df = (
                    merged_t[
                        merged_t["category"].isin(top8)
                    ]
                    .groupby(["category", "Discount_Segment"])
                    .size()
                    .reset_index(name="Count")
                )

                seg_order = ["No Discount", "Low (1-20%)", "Medium (21-40%)", "High (40%+)"]
                seg_color = {
                    "No Discount":    _SLATE,
                    "Low (1-20%)":    "#6ee7b7",
                    "Medium (21-40%)": _TEAL,
                    "High (40%+)":    _ORANGE,
                }
                # Sort categories by total volume
                cat_order = (
                    seg_df.groupby("category")["Count"].sum()
                    .reindex(top8)
                    .sort_values(ascending=True)
                    .index.tolist()
                )

                fig_seg = px.bar(
                    seg_df,
                    y="category",
                    x="Count",
                    color="Discount_Segment",
                    orientation="h",
                    category_orders={
                        "category": cat_order,
                        "Discount_Segment": seg_order,
                    },
                    color_discrete_map=seg_color,
                    barmode="stack",
                    custom_data=["Discount_Segment"],
                )
                fig_seg.update_traces(
                    hovertemplate="<b>%{y}</b><br>%{customdata[0]}: %{x:,}<extra></extra>",
                    textfont=dict(size=10, family="Inter"),
                )
                fig_seg.update_layout(
                    title=dict(
                        text="Tiki Top 8 Categories — Discount Segment Distribution",
                        font=dict(size=13, family="Inter", color=_DARK),
                    ),
                    template="plotly_white",
                    xaxis=dict(title="Number of Listings", showgrid=True, gridcolor="#f1f5f9"),
                    yaxis=dict(title="Category", showgrid=False),
                    legend=dict(
                        title="Discount Segment",
                        orientation="h",
                        y=-0.22,
                        font=dict(family="Inter", size=10),
                    ),
                    margin=dict(t=55, b=10, l=10, r=10),
                    height=390,
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_seg, width='stretch')
            else:
                st.info("No Tiki data or Discount_Segment column not available.")

    with st.expander("Chart Insights & Actionable Recommendations"):
        dominant = cond_counts.iloc[0]["Condition"] if not cond_counts.empty else "N/A"
        dom_pct  = cond_counts.iloc[0]["Pct"] if not cond_counts.empty else 0.0
        st.write(f"""
**Chart Analysis:**
* Tiki operates as a **B2C marketplace** — all listings are new products sold by verified brands/retailers, concentrated in consumer electronics, grocery, and home goods.
* eBay introduces a **condition dimension**: the dominant condition is **{dominant}** at **{dom_pct:.1f}%** of classified listings. Used and Refurbished listings represent a distinct value-seeking segment entirely absent from Tiki.
* The stacked bar (right) reveals which Tiki categories compete primarily on **price discounts** (High segment in orange) vs. which maintain full-price positioning (grey = No Discount). Categories with heavy discounting may indicate saturation or demand-side pressure.

**Recommended Next Steps:**
* A **Refurbished** listing often carries the best margin potential if certification quality is assured — consider cross-referencing with seller feedback scores before bulk procurement.
* Categories with a high share of **High (40%+)** discount listings warrant a margin sustainability audit — deep discounting without volume growth is a profitability red flag.
        """)
        st.markdown(
            '<i class="fa-solid fa-arrow-right-long" style="color:#3b82f6;margin-right:0.4rem;"></i>'
            '<em>For condition-level price analysis and trust signals — navigate to <strong>Tab: Trust &amp; Reputation</strong></em>',
            unsafe_allow_html=True,
        )

    st.divider()


# Section 5 - Market Health Signals
def _render_market_health(
    df_t: pd.DataFrame,
    df_e: pd.DataFrame,
    df_p: pd.DataFrame,
    df_c: pd.DataFrame,
) -> None:
    _pal = _get_palette()
    _TEAL = _pal["teal"]; _ORANGE = _pal["orange"]; _BLUE = _pal["blue"]
    _PURPLE = _pal["purple"]; _SLATE = _pal["slate"]; _AMBER = _pal["amber"]
    _RED = _pal["red"]; _GREEN = _pal["green"]

    _icon_header("fa-solid fa-heart-pulse", "5. Market Health Signals", color=_PURPLE)

    stag = 0.0
    merged = pd.DataFrame()
    if not df_t.empty and "quantity_sold" in df_t.columns:
        merged = (
            df_t
            .merge(df_p[["product_id", "category_id"]], on="product_id", how="left")
            .merge(df_c, on="category_id", how="left")
        )
        merged["category"] = merged["category"].fillna("Unknown")
        valid = merged[merged["category"] != "Unknown"]
        cold  = valid[(valid["quantity_sold"] == 0) & (valid["review_count"] == 0)]
        stag  = len(cold) / max(len(valid), 1) * 100

    disc_pct = 0.0
    if not df_t.empty:
        disc = pd.to_numeric(df_t.get("discount_rate", pd.Series(dtype=float)), errors="coerce")
        disc_pct = (disc > 0).mean() * 100

    new_pct = 0.0
    if not df_e.empty:
        conds   = df_e["condition"].apply(_simplify_condition)
        valid_e = conds.dropna()
        new_pct = (valid_e == "New").mean() * 100

    stag_by_cat = pd.DataFrame()
    if not merged.empty:
        cat_stag = (
            merged[merged["category"] != "Unknown"]
            .assign(is_cold=lambda x: (x["quantity_sold"] == 0) & (x["review_count"] == 0))
            .groupby("category")["is_cold"]
            .agg(["sum", "count"])
        )
        cat_stag["stag_rate"] = cat_stag["sum"] / cat_stag["count"] * 100
        # Filter categories with at least 10 products to avoid micro-category noise
        cat_stag = cat_stag[cat_stag["count"] >= 10]
        stag_by_cat = (
            cat_stag.nlargest(5, "stag_rate")[["stag_rate", "count"]]
            .reset_index()
            .rename(columns={"category": "Category", "stag_rate": "Stagnation Rate (%)", "count": "Total Products"})
        )


    stag_status = "HIGH RISK" if stag > 30 else ("WARNING" if stag > 15 else "HEALTHY")
    disc_status = "OVER-DISCOUNTED" if disc_pct > 60 else ("HIGH PRESSURE" if disc_pct > 40 else "NORMAL")
    new_status  = "NEW-DOMINANT" if new_pct > 50 else "MIXED MARKET"

    e1, e2, e3 = st.columns(3)

    with e1:
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="text-align:center;padding:1rem 0.5rem;">
                  <div style="font-size:0.68rem;font-weight:700;color:{_SLATE};
                              text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.3rem;"
                  >Tiki Stagnation Risk</div>
                  <div style="font-size:2.4rem;font-weight:800;color:{_DARK};
                              line-height:1.1;margin:0.4rem 0;">{stag:.1f}%</div>
                  <div style="font-size:0.75rem;font-weight:600;color:{_SLATE};
                              margin-bottom:0.3rem;">{stag_status}</div>
                  <div style="font-size:0.72rem;color:{_SLATE};line-height:1.4;">
                    Products with zero sales <em>and</em> zero reviews — inactive inventory
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with e2:
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="text-align:center;padding:1rem 0.5rem;">
                  <div style="font-size:0.68rem;font-weight:700;color:{_SLATE};
                              text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.3rem;"
                  >Tiki Discount Rate</div>
                  <div style="font-size:2.4rem;font-weight:800;color:{_DARK};
                              line-height:1.1;margin:0.4rem 0;">{disc_pct:.1f}%</div>
                  <div style="font-size:0.75rem;font-weight:600;color:{_SLATE};
                              margin-bottom:0.3rem;">{disc_status}</div>
                  <div style="font-size:0.72rem;color:{_SLATE};line-height:1.4;">
                    Share of listings running a promotional price discount
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with e3:
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="text-align:center;padding:1rem 0.5rem;">
                  <div style="font-size:0.68rem;font-weight:700;color:{_SLATE};
                              text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.3rem;"
                  >eBay New Condition</div>
                  <div style="font-size:2.4rem;font-weight:800;color:{_DARK};
                              line-height:1.1;margin:0.4rem 0;">{new_pct:.1f}%</div>
                  <div style="font-size:0.75rem;font-weight:600;color:{_SLATE};
                              margin-bottom:0.3rem;">{new_status}</div>
                  <div style="font-size:0.72rem;color:{_SLATE};line-height:1.4;">
                    Share of eBay listings classified as brand-new condition
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("")

    # Stagnation by category bar chart
    if not stag_by_cat.empty:
        with st.container(border=True):
            colors_stag = [
                _RED if v > 30 else (_AMBER if v > 15 else _GREEN)
                for v in stag_by_cat["Stagnation Rate (%)"]
            ]
            # Label: rate + product count for context
            labels = stag_by_cat.apply(
                lambda r: f"{r['Stagnation Rate (%)']:.1f}%  ({int(r['Total Products'])} products)",
                axis=1,
            )
            fig_stag = go.Figure(go.Bar(
                y=stag_by_cat["Category"],
                x=stag_by_cat["Stagnation Rate (%)"],
                orientation="h",
                marker=dict(color=colors_stag),
                text=labels,
                textposition="outside",
                textfont=dict(size=11, family="Inter"),
                customdata=stag_by_cat["Total Products"],
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Stagnation Rate: %{x:.1f}%<br>"
                    "Products with no sales/reviews: %{customdata:.0f} products"
                    "<extra></extra>"
                ),
            ))
            fig_stag.add_vline(
                x=30, line_dash="dash", line_color=_RED,
                annotation_text="Alert (30%)", annotation_position="top right",
                annotation_font=dict(size=10, color=_RED),
            )
            fig_stag.add_vline(
                x=15, line_dash="dot", line_color=_AMBER,
                annotation_text="Warning (15%)", annotation_position="bottom right",
                annotation_font=dict(size=10, color=_AMBER),
            )
            fig_stag.update_layout(
                title=dict(
                    text="Top 5 Tiki Categories by Stagnation Risk",
                    font=dict(size=13, family="Inter", color=_DARK),
                ),
                template="plotly_white",
                xaxis=dict(title="Stagnation Rate (%) — products with 0 sales AND 0 reviews",
                           showgrid=True, gridcolor="#f1f5f9", range=[0, 135]),
                yaxis=dict(title="Category", autorange="reversed", showgrid=False),
                margin=dict(t=55, b=30, l=10, r=10),
                height=300,
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_stag, width='stretch')

    with st.expander("Chart Insights & Actionable Recommendations"):
        stag_label = "HIGH RISK" if stag > 30 else ("WARNING" if stag > 15 else "HEALTHY")
        disc_label = "over-discounted" if disc_pct > 60 else ("under high pressure" if disc_pct > 40 else "at a normal level")
        new_label  = "new-condition dominant" if new_pct > 50 else "a mixed-condition market"
        st.write(f"""
**Market Health Analysis:**
* **Stagnation Risk ({stag:.1f}% — {stag_label}):** {"Over a third of categorised Tiki listings have never generated a sale or review — indicating serious demand-supply misalignment." if stag > 30 else ("A meaningful share of Tiki inventory is inactive — worth monitoring closely." if stag > 15 else "Tiki's stagnation level is within acceptable bounds — the market is relatively healthy.")}
* **Discount Pressure ({disc_pct:.1f}%):** Tiki's discount rate is {disc_label}. {"High discount rates can signal over-supply or unsustainable competitive pressure." if disc_pct > 40 else "This suggests a balanced promotional environment."}
* **eBay Condition Mix ({new_pct:.1f}% New):** eBay is {new_label} in the current price range. When New listings dominate, eBay competes more directly with Tiki's core offering.

**Recommended Actions:**
* {"Activate targeted promotions in the highest-risk stagnation categories identified in the bar chart above." if stag > 30 else "Monitor stagnation categories quarterly and act before they exceed the 30% threshold."}
* {"Review pricing strategy and margin sustainability — over-discounting erodes long-term brand value." if disc_pct > 60 else "Maintain current discount discipline and track conversion rates by discount segment in Tab: Pricing."}
* Use the category-level stagnation chart to prioritise which product lines need inventory reduction or demand stimulation first.
        """)
        st.markdown(
            '<i class="fa-solid fa-arrow-right-long" style="color:#7c3aed;margin-right:0.4rem;"></i>'
            '<em>For stagnation analysis by category — navigate to <strong>Tab: Characteristics &amp; Trends</strong></em>',
            unsafe_allow_html=True,
        )


# Main render entry point
def render(filters: Dict[str, Any]) -> None:
    """
    Overview tab — renders all five analytical sections in sequence.
    Each section answers one focused research question about the Tiki x eBay market.
    """
    # ── Lazy imports (Streamlit Cloud: internal packages only safe at call time) ─
    from data.loaders import load_4_tables                                  # noqa: E402
    # ─────────────────────────────────────────────────────────────────────────

    _icon_header("fa-solid fa-gauge-high", "Market Overview Dashboard", level=2, color=_TEAL)
    with st.expander("About this dashboard"):
        st.markdown(
            "A structured analytical overview of the **Tiki x eBay** e-commerce ecosystem. "
            "Each section below answers a specific research question — read top-to-bottom "
            "to follow the analytical narrative from data structure through to market health."
        )

    try:
        df_t_raw, df_e_raw, df_p, df_c = load_4_tables()
    except Exception as exc:
        st.error(f"Failed to load datasets: {exc}")
        return

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

    st.divider()

    _render_dataset_snapshot(df_t, df_e, df_p, df_c, df_t_raw, df_e_raw)
    _render_platform_scale(df_t, df_e, df_p, df_c)
    _render_price_landscape(df_t, df_e)
    _render_product_profile(df_t, df_e, df_p, df_c)
    _render_market_health(df_t, df_e, df_p, df_c)
