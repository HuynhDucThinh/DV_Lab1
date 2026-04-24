import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any

from components.ui_helpers import icon_header as _icon_header
from data.loaders import load_5_tables
from data.filters import clean_numeric, apply_global_filters
from config import (
	TEAL as _TEAL, ORANGE as _ORANGE, BLUE as _BLUE,
	SLATE as _SLATE, DARK as _DARK,
	get_chart_palette as _get_palette,
)


def _enrich_ebay_for_tab1(
	df_ebay: pd.DataFrame,
	df_product: pd.DataFrame,
	df_category: pd.DataFrame,
	df_seller: pd.DataFrame,
) -> pd.DataFrame:
	"""Attach seller trust and category labels to eBay listings for tab-1 charts."""
	out = df_ebay.copy()

	if "seller_username" in out.columns and "seller_username" in df_seller.columns:
		seller_lookup = df_seller.drop_duplicates(subset=["seller_username"]).set_index("seller_username")
		for col in ["seller_feedback_percent", "Trust_Level", "seller_feedback_score"]:
			if col in seller_lookup.columns and col not in out.columns:
				out[col] = out["seller_username"].map(seller_lookup[col])

	if "product_id" in out.columns and "product_id" in df_product.columns and "category_id" in df_product.columns:
		product_lookup = df_product.drop_duplicates(subset=["product_id"]).set_index("product_id")
		if "category_id" not in out.columns:
			out["category_id"] = out["product_id"].map(product_lookup["category_id"])

	if "category" not in out.columns and {"category_id", "category"}.issubset(df_category.columns):
		category_lookup = df_category.drop_duplicates(subset=["category_id"]).set_index("category_id")
		out["category"] = out.get("category_id", pd.Series(index=out.index)).map(category_lookup["category"])

	return out

def render_tiki_price_segments(df_tiki: pd.DataFrame) -> None:
	"""Render histogram and boxplot to show popular Tiki price segments."""
	_icon_header("fa-solid fa-chart-simple", "1. Tiki Focus: Price Segment Distribution")
	pal = _get_palette()

	if df_tiki.empty:
		st.info("No Tiki data available under current global filters.")
		return

	bins = st.slider("Histogram bins (Tiki)", min_value=10, max_value=80, value=35, step=5)

	price_values = df_tiki["price"].to_numpy()
	hist_counts, hist_edges = np.histogram(price_values, bins=bins)
	max_bin_idx = int(np.argmax(hist_counts))
	popular_low  = hist_edges[max_bin_idx]
	popular_high = hist_edges[max_bin_idx + 1]

	p_median = float(np.median(price_values))
	p_mean   = float(np.mean(price_values))
	p_q1     = float(np.percentile(price_values, 25))
	p_q3     = float(np.percentile(price_values, 75))
	p_iqr    = p_q3 - p_q1

	c1, c2, c3, c4 = st.columns(4)
	c1.metric("Tiki Listings", f"{len(df_tiki):,}")
	c2.metric("Median Price", f"{p_median:,.0f} VND")
	c3.metric("IQR (Q1–Q3)", f"{p_iqr:,.0f} VND")
	c4.metric("Most Popular Bin", f"{popular_low/1e6:.1f}M – {popular_high/1e6:.1f}M VND")

	chart_col1, chart_col2 = st.columns([3, 2])

	with chart_col1:
		fig_hist = px.histogram(
			df_tiki,
			x="price",
			nbins=bins,
			title="Histogram of Tiki Prices (VND)",
			labels={"price": "Price (VND)", "count": "Number of Listings"},
			color_discrete_sequence=[pal["teal"]],
		)
		fig_hist.add_vrect(
			x0=popular_low, x1=popular_high,
			fillcolor=pal["amber"], opacity=0.18, line_width=0,
			annotation_text="Most common segment",
			annotation_position="top left",
		)
		fig_hist.update_layout(template="plotly_white", bargap=0.05, margin=dict(t=60, l=20, r=20, b=20))
		st.plotly_chart(fig_hist, use_container_width=True)

	with chart_col2:
		fig_box = px.box(
			df_tiki,
			y="price",
			points="outliers",
			title="Boxplot of Tiki Prices (VND)",
			labels={"price": "Price (VND)"},
			color_discrete_sequence=[pal["teal"]],
		)
		fig_box.update_layout(template="plotly_white", margin=dict(t=60, l=20, r=20, b=20), showlegend=False)
		st.plotly_chart(fig_box, use_container_width=True)

	with st.expander("Chart 1A & 1B — Insights & Analytical Notes"):
		skew_dir = "right-skewed (positive)" if p_mean > p_median else "left-skewed (negative)"
		st.markdown(
			'<i class="fa-solid fa-circle-info" style="color:#0369a1;margin-right:0.4rem;"></i>'
			'**How to read:** The Histogram shows how many listings fall in each price range. '
			'The highlighted amber band is the single most-populated bin. '
			'The Boxplot summarises the full distribution: centre line = **median**, box = IQR, whiskers = 1.5×IQR.',
			unsafe_allow_html=True,
		)
		st.divider()
		st.markdown(
			'<i class="fa-solid fa-magnifying-glass" style="color:#0d9488;margin-right:0.4rem;"></i>'
			'**Chart Analysis**', unsafe_allow_html=True,
		)
		st.write(f"""
**Distribution shape:** The price distribution is **{skew_dir}** — mean ({p_mean:,.0f} VND) vs
median ({p_median:,.0f} VND) differ by **{abs(p_mean - p_median):,.0f} VND**, indicating
{"a long tail of expensive outlier listings" if p_mean > p_median else "a concentration of lower-priced listings"}.

**Price concentration:** 50% of all Tiki listings fall within the range
**{p_q1:,.0f} – {p_q3:,.0f} VND** (IQR = {p_iqr:,.0f} VND).
The most popular price bin **{popular_low:,.0f} – {popular_high:,.0f} VND** is where buyer
demand concentrates most densely.

**Difference Histogram vs Box:** The histogram reveals the *shape* and *mode* of the distribution
(where listings cluster). The boxplot adds precise quartile boundaries, enabling outlier detection
— products outside 1.5×IQR are plotted individually as dots.
""")
		st.markdown(
			'<i class="fa-solid fa-lightbulb" style="color:#f59e0b;margin-right:0.4rem;"></i>'
			'**Pricing Strategy**', unsafe_allow_html=True,
		)
		st.write(f"""
* **List within the most popular bin** ({popular_low:,.0f}–{popular_high:,.0f} VND) to maximise
  organic discovery — buyers browse this segment most.
* Use the **median ({p_median:,.0f} VND)** as the benchmark for competitive pricing,
  not the mean which is inflated by expensive outliers.
* Products priced above **{p_q3:,.0f} VND** (Q3) compete in the premium tier
  — differentiate with quality signals, not just price.
""")


def render_tiki_discount_bestseller(df_tiki: pd.DataFrame) -> None:
	"""Render grouped bar chart by discount segment with best-seller ratio overlay."""
	_icon_header("fa-solid fa-percent", "2. Tiki Focus: Discount Segment vs Best Seller Ratio")
	pal = _get_palette()

	if df_tiki.empty:
		st.info("No Tiki data available under current global filters.")
		return

	discount_options = sorted(df_tiki["Discount_Segment"].dropna().astype(str).unique().tolist())
	if not discount_options:
		st.warning("Discount segment data is missing in Tiki listings.")
		return

	with st.container(border=True):
		fc1, fc2 = st.columns([3, 1])
		with fc1:
			selected_segments = st.multiselect(
				"Discount segments",
				options=discount_options,
				default=discount_options,
			)
		with fc2:
			min_group_size = st.slider("Min listings / segment", min_value=1, max_value=500, value=20, step=1)

	filtered = df_tiki[df_tiki["Discount_Segment"].astype(str).isin(selected_segments)].copy()
	if filtered.empty:
		st.info("No records match the selected discount segments.")
		return

	filtered["Is_Best_Seller"] = pd.to_numeric(filtered["Is_Best_Seller"], errors="coerce").fillna(0).astype(int)

	summary = (
		filtered.groupby("Discount_Segment", as_index=False)
		.agg(
			Total_Listings=("product_id", "count"),
			Best_Seller=("Is_Best_Seller", "sum"),
		)
		.sort_values("Discount_Segment")
	)
	summary = summary[summary["Total_Listings"] >= min_group_size].copy()

	if summary.empty:
		st.info("No discount segment passes the minimum listing threshold.")
		return

	summary["Non_Best_Seller"] = summary["Total_Listings"] - summary["Best_Seller"]
	summary["Best_Seller_Rate"] = (summary["Best_Seller"] / summary["Total_Listings"]) * 100

	best_seg   = summary.loc[summary["Best_Seller_Rate"].idxmax(), "Discount_Segment"]
	best_rate  = summary["Best_Seller_Rate"].max()
	worst_seg  = summary.loc[summary["Best_Seller_Rate"].idxmin(), "Discount_Segment"]
	worst_rate = summary["Best_Seller_Rate"].min()

	k1, k2, k3 = st.columns(3)
	k1.metric("Segments Shown", f"{len(summary)}")
	k2.metric("Highest BS Rate", f"{best_seg} → {best_rate:.1f}%")
	k3.metric("Lowest BS Rate",  f"{worst_seg} → {worst_rate:.1f}%")

	fig = go.Figure()
	fig.add_trace(go.Bar(
		x=summary["Discount_Segment"], y=summary["Best_Seller"],
		name="Best Seller", marker_color=pal["orange"],
	))
	fig.add_trace(go.Bar(
		x=summary["Discount_Segment"], y=summary["Non_Best_Seller"],
		name="Non Best Seller", marker_color="#cbd5e1",
	))
	fig.add_trace(go.Scatter(
		x=summary["Discount_Segment"], y=summary["Best_Seller_Rate"],
		name="Best Seller Rate (%)", yaxis="y2",
		mode="lines+markers+text",
		text=[f"{v:.1f}%" for v in summary["Best_Seller_Rate"]],
		textposition="top center",
		line=dict(color="#0f172a", width=2),
		marker=dict(size=7),
	))
	fig.update_layout(
		template="plotly_white",
		barmode="group",
		title="Grouped Bar: Discount Segment × Best Seller Rate",
		xaxis_title="Discount Segment",
		yaxis_title="Listing Count",
		yaxis2=dict(title="Best Seller Rate (%)", overlaying="y", side="right", range=[0, 100]),
		legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
		margin=dict(t=70, l=20, r=20, b=20),
	)
	st.plotly_chart(fig, use_container_width=True)

	with st.expander("Chart 2 — Insights & Actionable Recommendations"):
		st.markdown(
			'<i class="fa-solid fa-circle-info" style="color:#0369a1;margin-right:0.4rem;"></i>'
			'**How to read:** Bars show the volume of Best Seller vs Non Best Seller listings per '
			'discount segment. The dark line (right axis) shows the **Best Seller Rate (%)** — '
			'the fraction of listings in each group that achieved best-seller status.',
			unsafe_allow_html=True,
		)
		st.divider()
		st.markdown(
			'<i class="fa-solid fa-magnifying-glass" style="color:#0d9488;margin-right:0.4rem;"></i>'
			'**Chart Analysis**', unsafe_allow_html=True,
		)
		rate_table = "\n".join(
			f"- **{row.Discount_Segment}**: {row.Total_Listings:,} listings → Best Seller Rate **{row.Best_Seller_Rate:.1f}%**"
			for _, row in summary.iterrows()
		)
		st.write(f"""
**Top performer:** Discount segment **"{best_seg}"** achieves the highest Best Seller Rate
at **{best_rate:.1f}%** — indicating that this level of discount most effectively converts
listings into top-selling products.

**Underperformer:** Segment **"{worst_seg}"** has the lowest rate at **{worst_rate:.1f}%**,
suggesting diminishing returns or that listings in this range are inherently less competitive.

**Full breakdown:**
{rate_table}

**Key insight:** A higher discount does not always yield a higher Best Seller Rate.
The optimal discount level is the one that balances margin loss against conversion gain.
""")
		st.markdown(
			'<i class="fa-solid fa-lightbulb" style="color:#f59e0b;margin-right:0.4rem;"></i>'
			'**Promotion Strategy**', unsafe_allow_html=True,
		)
		st.write(f"""
* **Focus promotional budget** on the **"{best_seg}"** discount tier — it yields the highest
  Best Seller conversion rate.
* Avoid deep discounting beyond this tier unless clearing stock — it does not improve
  best-seller status and reduces margins unnecessarily.
* Use this chart to set **campaign discount targets** based on data, not intuition.
""")



def render_ebay_violin_box(df_ebay: pd.DataFrame) -> None:
	"""Render combined violin + box traces to show eBay price volatility by condition,
	and a bar chart of median price by category to identify the top-3 highest-price categories."""
	_icon_header("fa-solid fa-wave-square", "3. eBay Focus: Price Volatility by Condition & Category", color=_ORANGE)
	pal = _get_palette()

	if df_ebay.empty:
		st.info("No eBay data available under current global filters.")
		return

	condition_options = sorted(df_ebay["condition"].dropna().astype(str).unique().tolist())
	default_conditions = condition_options[:10] if len(condition_options) > 10 else condition_options

	with st.container(border=True):
		vc1, vc2 = st.columns([3, 1])
		with vc1:
			selected_conditions = st.multiselect(
				"Item condition groups to compare",
				options=condition_options,
				default=default_conditions,
				help="Select eBay condition groups. Fewer groups = clearer violin shapes.",
			)
		with vc2:
			y_pct_trim = st.slider(
				"Trim top %",
				min_value=80, max_value=100, value=99, step=1,
				help="Remove the top N% of listings to suppress outliers from the violin shape.",
			)

	filtered = df_ebay[df_ebay["condition"].astype(str).isin(selected_conditions)].copy()
	if filtered.empty:
		st.info("No eBay records match the selected condition filter.")
		return

	# Apply trim to Total_Cost_VND
	y_max = float(filtered["Total_Cost_VND"].quantile(y_pct_trim / 100))
	filtered = filtered[filtered["Total_Cost_VND"] <= y_max]
	if filtered.empty:
		st.info("No records remain after applying trim threshold.")
		return

	violin_stats: dict = {}
	fig = go.Figure()
	for cond in selected_conditions:
		cond_data = filtered[filtered["condition"].astype(str) == cond]["Total_Cost_VND"].dropna()
		if cond_data.empty:
			continue
		fig.add_trace(go.Violin(
			x=[cond] * len(cond_data),
			y=cond_data,
			name=cond,
			box_visible=True,
			meanline_visible=True,
			points="outliers",
			opacity=0.75,
		))
		q1, q3 = float(cond_data.quantile(0.25)), float(cond_data.quantile(0.75))
		violin_stats[cond] = {
			"median": float(cond_data.median()),
			"mean":   float(cond_data.mean()),
			"iqr":    q3 - q1,
			"n":      len(cond_data),
		}

	fig.update_layout(
		template="plotly_white",
		title="eBay Tech Listings: Distribution of Total Cost by Condition (VND)",
		xaxis_title="Condition",
		yaxis_title="Total Cost (VND)",
		margin=dict(t=70, l=20, r=20, b=20),
	)
	st.plotly_chart(fig, use_container_width=True)

	with st.expander("Chart 3A — Insights & Actionable Recommendations"):
		if violin_stats:
			highest_med = max(violin_stats, key=lambda k: violin_stats[k]["median"])
			widest_iqr  = max(violin_stats, key=lambda k: violin_stats[k]["iqr"])
			hm = violin_stats[highest_med]
			wi = violin_stats[widest_iqr]
			st.markdown(
				'<i class="fa-solid fa-circle-info" style="color:#0369a1;margin-right:0.4rem;"></i>'
				'**How to read:** Each violin shows the **price density** for one condition group — '
				'wider = more listings at that price level. The embedded box shows Q1–Q3 (IQR). '
				'The dashed line = mean; solid line = median.',
				unsafe_allow_html=True,
			)
			st.divider()
			st.markdown(
				'<i class="fa-solid fa-magnifying-glass" style="color:#0d9488;margin-right:0.4rem;"></i>'
				'**Chart Analysis**', unsafe_allow_html=True,
			)
			stat_lines = "\n".join(
				f"- **{c}**: median = {s['median']:,.0f} VND | IQR = {s['iqr']:,.0f} VND | n = {s['n']:,}"
				for c, s in violin_stats.items()
			)
			st.write(f"""
**Price ranking:** **{highest_med}** commands the highest median at **{hm['median']:,.0f} VND**
(mean {hm['mean']:,.0f} VND). The mean-median gap signals how much outliers skew the average.

**Price volatility:** **{widest_iqr}** has the widest IQR (**{wi['iqr']:,.0f} VND**) —
heterogeneous pricing within this condition group. Buyers face more uncertainty on final cost.

**Full stats:**
{stat_lines}

**Violin vs Box:** The violin reveals the *density shape* — bimodal, skewed, or uniform.
The box alone would hide these nuances. A narrow violin at a price level = high listing concentration.
""")
			st.markdown(
				'<i class="fa-solid fa-lightbulb" style="color:#f59e0b;margin-right:0.4rem;"></i>'
				'**Sourcing Strategy**', unsafe_allow_html=True,
			)
			st.write(f"""
* Use **median** (not mean) as procurement benchmark — mean is distorted by premium outliers.
* **{widest_iqr}** has high price variance — inspect individually before bulk sourcing.
* A narrow violin with small IQR signals price predictability — lower procurement risk.
""")

	# --- Chart 3B: Top-3 categories by median price (Obj 3 requirement) ---
	st.markdown("#### Median Total Cost by Category (Top-3 Highlighted)")

	if "category" in df_ebay.columns:
		cat_stats = (
			df_ebay.dropna(subset=["category", "Total_Cost_VND"])
			.groupby("category")["Total_Cost_VND"]
			.agg(median="median", count="count")
			.query("count >= 10")
			.sort_values("median", ascending=False)
			.reset_index()
		)

		if not cat_stats.empty:
			max_cats = len(cat_stats)
			with st.container(border=True):
				show_n = st.slider(
					"Number of categories to display",
					min_value=3, max_value=max_cats, value=min(10, max_cats), step=1,
					key="cat_median_show_n",
					help="Show top N categories by median total cost.",
				)
			cat_stats = cat_stats.head(show_n).sort_values("median", ascending=True)

			top3 = set(cat_stats.nlargest(3, "median")["category"].tolist())
			cat_stats["color"] = cat_stats["category"].apply(
				lambda c: pal["orange"] if c in top3 else pal["slate"]
			)
			cat_stats["label"] = cat_stats["category"]

			k1, k2, k3 = st.columns(3)
			top3_sorted = cat_stats.nlargest(3, "median")[["category", "median"]].values.tolist()
			for i, (cat, med) in enumerate(top3_sorted):
				[k1, k2, k3][i].metric(f"#{i+1} Highest Median", cat, delta=f"{med:,.0f} VND")

			fig_cat = go.Figure(go.Bar(
				x=cat_stats["median"],
				y=cat_stats["label"],
				orientation="h",
				marker_color=cat_stats["color"].tolist(),
				text=[f"{v/1e6:.1f}M" for v in cat_stats["median"]],
				textposition="outside",
			))
			fig_cat.update_layout(
				template="plotly_white",
				title=f"Median Total Cost (VND) by Product Category — Top {show_n} shown",
				xaxis_title="Median Total Cost (VND)",
				yaxis_title="Category",
				margin=dict(t=60, l=20, r=60, b=20),
				height=max(300, len(cat_stats) * 38),
			)
			st.plotly_chart(fig_cat, use_container_width=True)

			with st.expander("Chart 3B — Top-3 Category Insights"):
				st.markdown(
					'<i class="fa-solid fa-circle-info" style="color:#0369a1;margin-right:0.4rem;"></i>'
					'**How to read:** Horizontal bars show median Total Cost (VND) per category. '
					'**Orange bars** = top-3 categories with highest median price. '
					'Only categories with ≥ 10 listings are included.',
					unsafe_allow_html=True,
				)
				st.divider()
				top3_lines = "\n".join(
					f"- **#{i+1} {cat}**: median {med:,.0f} VND"
					for i, (cat, med) in enumerate(top3_sorted)
				)
				st.write(f"""
**Top-3 highest-price categories:**
{top3_lines}

These categories command a price premium — likely due to higher product complexity,
brand positioning, or lower supply relative to demand.

Sellers in these categories can justify higher listing prices; buyers should expect
to pay above the platform average.
""")
	else:
		st.info("Category data not available — ensure eBay data includes product category mapping.")


def render_ebay_price_shipping_boundary(df_ebay: pd.DataFrame) -> None:
	"""Render stacked bar (price vs shipping) and scatter plot (price vs shipping cost boundary)."""
	_icon_header("fa-solid fa-truck", "4. eBay Focus: Listing Price vs Shipping Fee Boundary", color=_BLUE)
	pal = _get_palette()

	if df_ebay.empty:
		st.info("No eBay data available under current global filters.")
		return

	max_points = st.slider("Scatter sample size", min_value=300, max_value=5000, value=1800, step=100)

	df_vis = df_ebay[["price", "shipping_cost", "condition"]].copy()
	df_vis = clean_numeric(df_vis, ["price", "shipping_cost"])
	if df_vis.empty:
		st.warning("Insufficient eBay price/shipping data for boundary analysis.")
		return

	quantile_bins = pd.qcut(df_vis["price"], q=6, duplicates="drop")
	df_vis["Price_Bin"] = quantile_bins.astype(str)

	stacked_data = (
		df_vis.groupby("Price_Bin", as_index=False)
		.agg(
			Avg_Listing_Price=("price", "mean"),
			Avg_Shipping_Fee=("shipping_cost", "mean"),
		)
		.sort_values("Avg_Listing_Price")
	)

	dominance_ratio = (df_vis["shipping_cost"] > df_vis["price"]).mean() * 100
	free_ship_ratio = (df_vis["shipping_cost"] == 0).mean() * 100
	avg_ship_pct    = (df_vis["shipping_cost"] / (df_vis["price"] + 1e-9)).median() * 100

	k1, k2, k3 = st.columns(3)
	k1.metric("Listings Analysed", f"{len(df_vis):,}")
	k2.metric("Free Shipping", f"{free_ship_ratio:.1f}%", delta="Dominant" if free_ship_ratio > 50 else "Minority")
	k3.metric("Shipping > Price", f"{dominance_ratio:.1f}%", delta="Anomaly" if dominance_ratio > 5 else "Normal", delta_color="inverse")

	left_col, right_col = st.columns(2)

	with left_col:
		fig_stacked = go.Figure()
		fig_stacked.add_trace(
			go.Bar(
				x=stacked_data["Price_Bin"],
				y=stacked_data["Avg_Listing_Price"],
				name="Avg Listing Price",
				marker_color="#0369a1",
			)
		)
		fig_stacked.add_trace(
			go.Bar(
				x=stacked_data["Price_Bin"],
				y=stacked_data["Avg_Shipping_Fee"],
				name="Avg Shipping Fee",
				marker_color="#f59e0b",
			)
		)
		fig_stacked.update_layout(
			template="plotly_white",
			barmode="stack",
			title="Stacked Average Cost Components by Listing Price Bin (USD)",
			xaxis_title="Listing Price Segment",
			yaxis_title="Average Cost (USD)",
			margin=dict(t=70, l=20, r=20, b=20),
		)
		st.plotly_chart(fig_stacked, use_container_width=True)

	with right_col:
		sampled = df_vis.sample(n=min(max_points, len(df_vis)), random_state=42)
		fig_scatter = px.scatter(
			sampled,
			x="price",
			y="shipping_cost",
			color="condition",
			opacity=0.55,
			title="Scatter Boundary: Shipping Fee vs Listing Price (USD)",
			labels={"price": "Listing Price (USD)", "shipping_cost": "Shipping Fee (USD)"},
		)

		max_axis = float(max(sampled["price"].max(), sampled["shipping_cost"].max()))
		fig_scatter.add_shape(
			type="line",
			x0=0,
			y0=0,
			x1=max_axis,
			y1=max_axis,
			line=dict(color="#111827", width=2, dash="dash"),
		)
		fig_scatter.add_annotation(
			x=max_axis * 0.72,
			y=max_axis * 0.75,
			text="Boundary y = x",
			showarrow=False,
			bgcolor="#ffffff",
		)
		fig_scatter.update_layout(template="plotly_white", margin=dict(t=70, l=20, r=20, b=20))
		st.plotly_chart(fig_scatter, use_container_width=True)


	with st.expander("Chart 4A & 4B - Insights & Actionable Recommendations"):
		highest_ship_bin = stacked_data.loc[stacked_data["Avg_Shipping_Fee"].idxmax(), "Price_Bin"]
		highest_ship_val = stacked_data["Avg_Shipping_Fee"].max()
		st.markdown(
			'<i class="fa-solid fa-circle-info" style="color:#0369a1;margin-right:0.4rem;"></i>'
			'**How to read:** The **Stacked Bar** decomposes each price tier into avg listing price + '
			'avg shipping fee — the amber segment shows the shipping overhead. '
			'The **Scatter** plots individual listings; points above the dashed y=x line '
			'have shipping fees exceeding the listing price itself.',
			unsafe_allow_html=True,
		)
		st.divider()
		st.markdown(
			'<i class="fa-solid fa-magnifying-glass" style="color:#0d9488;margin-right:0.4rem;"></i>'
			'**Chart Analysis**', unsafe_allow_html=True,
		)
		st.write(f"""
**Free shipping adoption:** **{free_ship_ratio:.1f}%** of eBay listings offer free shipping —
{"a majority, suggesting free shipping is the norm in this market" if free_ship_ratio > 50 else "a minority, meaning most buyers pay additional shipping costs"}.

**Shipping burden:** The median shipping fee represents approximately **{avg_ship_pct:.1f}%**
of the listing price — {"a significant cost overhead that materially affects the buyer's total spend" if avg_ship_pct > 10 else "a relatively minor addition to the final cost"}.

**Anomalous listings:** **{dominance_ratio:.1f}%** of listings have shipping fees exceeding the
listing price (points above y=x in the scatter). These are outliers — likely error entries or
specialty items where freight cost dominates.

**Price bin with highest shipping:** Bin **{highest_ship_bin}** carries the largest average
shipping fee at **${highest_ship_val:.2f} USD** — suggesting heavier or bulkier items in
that price segment.
""")
		st.markdown(
			'<i class="fa-solid fa-lightbulb" style="color:#f59e0b;margin-right:0.4rem;"></i>'
			'**Buyer & Seller Strategy**', unsafe_allow_html=True,
		)
		st.write(f"""
* **Buyers:** Always compare **total cost** (listing + shipping), not listing price alone —
  the stacked bar reveals the true cost structure per price tier.
* **Sellers:** Offering free shipping in price tiers where competitors charge fees
  provides a competitive advantage and increases conversion.
* Filter out listings with `shipping_cost > price` before any pricing benchmarking —
  they distort averages significantly.
""")

	# --- Chart 4C: Top-3 categories by avg shipping fee (Obj 4 requirement) ---
	st.markdown("#### Average Shipping Fee by Category (Top-3 Highlighted)")

	if "category" in df_ebay.columns:
		df_ship_cat = (
			df_ebay.dropna(subset=["category", "shipping_cost"])
			.assign(shipping_cost=lambda x: pd.to_numeric(x["shipping_cost"], errors="coerce"))
			.dropna(subset=["shipping_cost"])
		)
		df_ship_cat = df_ship_cat[df_ship_cat["shipping_cost"] > 0]

		if not df_ship_cat.empty:
			ship_by_cat = (
				df_ship_cat.groupby("category")["shipping_cost"]
				.agg(avg_ship="mean", count="count", free_pct=lambda x: (x == 0).mean() * 100)
				.query("count >= 10")
				.sort_values("avg_ship", ascending=True)
				.reset_index()
			)

			if not ship_by_cat.empty:
				max_ship_cats = len(ship_by_cat)
				with st.container(border=True):
					show_n_ship = st.slider(
						"Number of categories to display",
						min_value=3, max_value=max_ship_cats, value=min(10, max_ship_cats), step=1,
						key="cat_ship_show_n",
						help="Show top N categories by average shipping fee.",
					)
				ship_by_cat = ship_by_cat.nlargest(show_n_ship, "avg_ship").sort_values("avg_ship", ascending=True)

				top3_ship = set(ship_by_cat.nlargest(3, "avg_ship")["category"].tolist())
				ship_by_cat["color"] = ship_by_cat["category"].apply(
					lambda c: pal["amber"] if c in top3_ship else pal["slate"]
				)
				ship_by_cat["label"] = ship_by_cat["category"]

				top3_ship_sorted = ship_by_cat.nlargest(3, "avg_ship")[["category", "avg_ship"]].values.tolist()
				k1, k2, k3 = st.columns(3)
				for i, (cat, avg) in enumerate(top3_ship_sorted):
					[k1, k2, k3][i].metric(f"#{i+1} Highest Shipping", cat, delta=f"${avg:.2f} USD avg")

				fig_ship = go.Figure(go.Bar(
					x=ship_by_cat["avg_ship"],
					y=ship_by_cat["label"],
					orientation="h",
					marker_color=ship_by_cat["color"].tolist(),
					text=[f"${v:.2f}" for v in ship_by_cat["avg_ship"]],
					textposition="outside",
				))
				fig_ship.update_layout(
					template="plotly_white",
					title=f"Average Shipping Fee (USD) by Product Category — Top {show_n_ship} shown",
					xaxis_title="Average Shipping Fee (USD)",
					yaxis_title="Category",
					margin=dict(t=60, l=20, r=80, b=20),
					height=max(300, len(ship_by_cat) * 38),
				)
				st.plotly_chart(fig_ship, use_container_width=True)

				with st.expander("Chart 4C - Top-3 Shipping Category Insights"):
					st.markdown(
						'<i class="fa-solid fa-circle-info" style="color:#0369a1;margin-right:0.4rem;"></i>'
						'**How to read:** Horizontal bars show average shipping fee per category (paid listings only). '
						'**Amber bars** = top-3 categories with highest avg shipping cost. '
						'Only categories with ≥ 10 listings are included.',
						unsafe_allow_html=True,
					)
					st.divider()
					top3_lines = "\n".join(
						f"- **#{i+1} {cat}**: avg ${avg:.2f} USD"
						for i, (cat, avg) in enumerate(top3_ship_sorted)
					)
					st.write(f"""
**Top-3 categories with highest shipping overhead:**
{top3_lines}

These categories likely involve heavier or bulkier products requiring special handling.
Buyers should factor in this shipping premium when comparing total cost across categories.
Sellers in these categories could gain competitive advantage by offering free or subsidised shipping.
""")
	else:
		st.info("Category data not available — ensure eBay data includes product category mapping.")



def render(filters: Dict[str, Any]) -> None:
	"""Main rendering entrypoint for Tab 1: Pricing & Promotions."""
	_icon_header("fa-solid fa-tags", "Pricing &amp; Promotions", level=2)
	with st.expander("About this tab"):
		st.markdown("""
This tab analyses **price architecture and promotional dynamics** across Tiki and eBay,
covering four research objectives:

- **Section 1 (Tiki):** How are product prices distributed?
  Histogram reveals the most popular price segment; Boxplot provides median, IQR and outlier detection.
- **Section 2 (Tiki):** Which discount tier converts best-seller status most effectively?
  Grouped bar + dual-axis line compares listing volume vs best-seller rate per discount segment.
- **Section 3 (eBay):** How does price volatility differ across product conditions?
  Violin plot with embedded box reveals density shape, IQR, and mean-median divergence.
- **Section 4 (eBay):** What is the true buyer cost when shipping is included?
  Stacked bar quantifies the shipping overhead per price tier; scatter plot maps individual listings against the y = x boundary.

Read top-to-bottom to follow the analytical flow from **Tiki pricing structure**
through **promotion effectiveness** to **eBay cost composition**.
""")

	try:
		df_tiki, df_ebay, df_product, df_category, df_seller = load_5_tables()
	except Exception as exc:
		st.error(f"Error loading pricing datasets: {exc}. Check folder ../data/processed.")
		return

	df_ebay = _enrich_ebay_for_tab1(df_ebay, df_product, df_category, df_seller)

	df_tiki = clean_numeric(df_tiki, ["price"])
	df_ebay = clean_numeric(df_ebay, ["price", "shipping_cost", "Total_Cost_VND"])

	df_tiki_filtered, df_ebay_filtered = apply_global_filters(df_tiki, df_ebay, filters)

	with st.container():
		render_tiki_price_segments(df_tiki_filtered)

	st.divider()

	with st.container():
		render_tiki_discount_bestseller(df_tiki_filtered)

	st.divider()

	with st.container():
		render_ebay_violin_box(df_ebay_filtered)

	st.divider()

	with st.container():
		render_ebay_price_shipping_boundary(df_ebay_filtered)
