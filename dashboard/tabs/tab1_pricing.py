import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Tuple, Dict, Any

# ── Shared UI helpers ───────────────────────────────────────────────────────────────────
from components.ui_helpers import icon_header as _icon_header, fa_callout as _fa_callout
from data.loaders import load_5_tables
from data.filters import clean_numeric, apply_global_filters

# ── Palette (referenced by chart functions below) ───────────────────────────────
_TEAL   = "#0d9488"
_ORANGE = "#f97316"
_BLUE   = "#3b82f6"
_SLATE  = "#94a3b8"
_DARK   = "#0f172a"


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

	if df_tiki.empty:
		st.info("No Tiki data available under current global filters.")
		return

	bins = st.slider("Histogram bins (Tiki)", min_value=10, max_value=80, value=35, step=5)

	price_values = df_tiki["price"].to_numpy()
	hist_counts, hist_edges = np.histogram(price_values, bins=bins)
	max_bin_idx = int(np.argmax(hist_counts))
	popular_low = hist_edges[max_bin_idx]
	popular_high = hist_edges[max_bin_idx + 1]

	col1, col2 = st.columns(2)
	col1.metric("Tiki Listings", f"{len(df_tiki):,}")
	col2.metric("Most Popular Price Bin", f"{popular_low:,.0f} - {popular_high:,.0f} VND")

	chart_col1, chart_col2 = st.columns([3, 2])

	with chart_col1:
		fig_hist = px.histogram(
			df_tiki,
			x="price",
			nbins=bins,
			title="Histogram of Tiki Prices",
			labels={"price": "Price (VND)", "count": "Number of Listings"},
			color_discrete_sequence=["#14b8a6"],
		)
		fig_hist.add_vrect(
			x0=popular_low,
			x1=popular_high,
			fillcolor="#f59e0b",
			opacity=0.18,
			line_width=0,
			annotation_text="Most common segment",
			annotation_position="top left",
		)
		fig_hist.update_layout(template="plotly_white", bargap=0.05, margin=dict(t=60, l=20, r=20, b=20))
		st.plotly_chart(fig_hist, width="stretch")

	with chart_col2:
		fig_box = px.box(
			df_tiki,
			y="price",
			points="outliers",
			title="Boxplot of Tiki Prices",
			labels={"price": "Price (VND)"},
			color_discrete_sequence=["#0f766e"],
		)
		fig_box.update_layout(template="plotly_white", margin=dict(t=60, l=20, r=20, b=20), showlegend=False)
		st.plotly_chart(fig_box, width="stretch")


def render_tiki_discount_bestseller(df_tiki: pd.DataFrame) -> None:
	"""Render grouped bar chart by discount segment with best-seller ratio overlay."""
	_icon_header("fa-solid fa-percent", "2. Tiki Focus: Discount Segment vs Best Seller Ratio")

	if df_tiki.empty:
		st.info("No Tiki data available under current global filters.")
		return

	discount_options = sorted(df_tiki["Discount_Segment"].dropna().astype(str).unique().tolist())
	if not discount_options:
		st.warning("Discount segment data is missing in Tiki listings.")
		return

	selected_segments = st.multiselect(
		"Discount segment filter",
		options=discount_options,
		default=discount_options,
		help="Choose discount segments to inspect best seller behavior.",
	)
	min_group_size = st.slider("Minimum listings per segment", min_value=1, max_value=500, value=20, step=1)

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

	fig = go.Figure()
	fig.add_trace(
		go.Bar(
			x=summary["Discount_Segment"],
			y=summary["Best_Seller"],
			name="Best Seller",
			marker_color="#f97316",
		)
	)
	fig.add_trace(
		go.Bar(
			x=summary["Discount_Segment"],
			y=summary["Non_Best_Seller"],
			name="Non Best Seller",
			marker_color="#cbd5e1",
		)
	)
	fig.add_trace(
		go.Scatter(
			x=summary["Discount_Segment"],
			y=summary["Best_Seller_Rate"],
			name="Best Seller Rate (%)",
			yaxis="y2",
			mode="lines+markers+text",
			text=[f"{v:.1f}%" for v in summary["Best_Seller_Rate"]],
			textposition="top center",
			line=dict(color="#0f172a", width=2),
			marker=dict(size=7),
		)
	)
	fig.update_layout(
		template="plotly_white",
		barmode="group",
		title="Grouped Bar by Discount Segment with Best Seller Ratio",
		xaxis_title="Discount Segment",
		yaxis_title="Listing Count",
		yaxis2=dict(title="Best Seller Rate (%)", overlaying="y", side="right", range=[0, 100]),
		legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
		margin=dict(t=70, l=20, r=20, b=20),
	)
	st.plotly_chart(fig, width="stretch")


def render_ebay_violin_box(df_ebay: pd.DataFrame) -> None:
	"""Render combined violin + box traces to show eBay price volatility."""
	_icon_header("fa-solid fa-wave-square", "3. eBay Focus: Price Volatility (Violin + Box)", color=_ORANGE)

	if df_ebay.empty:
		st.info("No eBay data available under current global filters.")
		return

	condition_options = sorted(df_ebay["condition"].dropna().astype(str).unique().tolist())
	default_conditions = condition_options[:6] if len(condition_options) > 6 else condition_options

	selected_conditions = st.multiselect(
		"Condition filter (eBay)",
		options=condition_options,
		default=default_conditions,
		help="Choose condition groups to compare price spread.",
	)

	filtered = df_ebay[df_ebay["condition"].astype(str).isin(selected_conditions)].copy()
	if filtered.empty:
		st.info("No eBay records match the selected condition filter.")
		return

	fig = go.Figure()
	for cond in selected_conditions:
		cond_data = filtered[filtered["condition"].astype(str) == cond]["Total_Cost_VND"]
		if cond_data.empty:
			continue
		fig.add_trace(
			go.Violin(
				x=[cond] * len(cond_data),
				y=cond_data,
				name=cond,
				box_visible=True,
				meanline_visible=True,
				points="outliers",
				opacity=0.75,
			)
		)

	fig.update_layout(
		template="plotly_white",
		title="eBay Tech Listings: Distribution of Total Cost by Condition",
		xaxis_title="Condition",
		yaxis_title="Total Cost (VND)",
		margin=dict(t=70, l=20, r=20, b=20),
	)
	st.plotly_chart(fig, width="stretch")


def render_ebay_price_shipping_boundary(df_ebay: pd.DataFrame) -> None:
	"""Render stacked bar and scatter to compare listing price and shipping fee boundary."""
	_icon_header("fa-solid fa-truck", "4. eBay Focus: Listing Price vs Shipping Fee Boundary", color=_BLUE)

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
		st.plotly_chart(fig_stacked, width="stretch")

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
		st.plotly_chart(fig_scatter, width="stretch")

	dominance_ratio = (df_vis["shipping_cost"] > df_vis["price"]).mean() * 100
	st.caption(
		f"Shipping-dominant listings (shipping fee > listing price): {dominance_ratio:.2f}% of observed eBay records."
	)



def render_ebay_total_cost_box_by_condition(df_ebay: pd.DataFrame) -> None:
	"""Render interactive box plot for total cost by product condition."""
	_icon_header("fa-solid fa-chart-line", "5. eBay Focus: Total Cost Volatility by Condition", color=_BLUE)

	if df_ebay.empty:
		st.info("No eBay data available under current global filters.")
		return

	required_cols = {"condition", "Total_Cost_VND"}
	if not required_cols.issubset(df_ebay.columns):
		st.warning("Missing required columns for box plot: condition and/or Total_Cost_VND.")
		return

	df_box = df_ebay[["condition", "Total_Cost_VND"]].copy()
	df_box = clean_numeric(df_box, ["Total_Cost_VND"])
	df_box["condition"] = df_box["condition"].astype(str)
	df_box = df_box[df_box["condition"].str.strip() != ""]

	if df_box.empty:
		st.warning("Insufficient valid data to plot total cost by condition.")
		return

	condition_options = sorted(df_box["condition"].dropna().unique().tolist())
	selected_conditions = st.multiselect(
		"Condition filter (Total Cost Box Plot)",
		options=condition_options,
		default=condition_options[:10] if len(condition_options) > 10 else condition_options,
	)

	if not selected_conditions:
		st.info("Please select at least one condition.")
		return

	df_box = df_box[df_box["condition"].isin(selected_conditions)]
	if df_box.empty:
		st.info("No records match selected conditions.")
		return

	y_min = float(df_box["Total_Cost_VND"].min())
	y_max = float(df_box["Total_Cost_VND"].max())
	y_range = st.slider(
		"Y range - Total Cost (VND)",
		min_value=max(0.0, y_min),
		max_value=y_max,
		value=(max(0.0, y_min), y_max),
	)
	df_box = df_box[(df_box["Total_Cost_VND"] >= y_range[0]) & (df_box["Total_Cost_VND"] <= y_range[1])]

	if df_box.empty:
		st.info("No records remain after applying y-axis range.")
		return

	ordered_conditions = (
		df_box.groupby("condition", as_index=False)["Total_Cost_VND"]
		.median()
		.sort_values("Total_Cost_VND")
		["condition"]
		.tolist()
	)

	fig = px.box(
		df_box,
		x="condition",
		y="Total_Cost_VND",
		category_orders={"condition": ordered_conditions},
		points="suspectedoutliers",
		color="condition",
		title="Distribution of Total Cost (VND) by Product Condition",
		labels={"condition": "Condition", "Total_Cost_VND": "Total Cost (VND)"},
	)
	fig.update_layout(template="plotly_white", showlegend=False, margin=dict(t=70, l=20, r=20, b=20))
	fig.update_xaxes(type="category")
	st.plotly_chart(fig, width="stretch")


def render(filters: Dict[str, Any]) -> None:
	"""Main rendering entrypoint for Tab 1: Pricing & Promotions."""
	_icon_header("fa-solid fa-tags", "Pricing &amp; Promotions", level=2)
	_fa_callout(
		"fa-solid fa-circle-info", _TEAL,
		"Price architecture and promotion effects across Tiki and eBay listings."
	)

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

	st.divider()

	with st.container():
		render_ebay_total_cost_box_by_condition(df_ebay_filtered)