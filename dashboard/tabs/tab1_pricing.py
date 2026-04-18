import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Tuple, Dict, Any


@st.cache_data
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
	"""Load and cache processed pricing datasets for Tiki and eBay."""
	data_dir = "../data/processed"
	df_fact_tiki = pd.read_csv(f"{data_dir}/fact_tiki_listings.csv", dtype={"product_id": str})
	df_fact_ebay = pd.read_csv(f"{data_dir}/fact_ebay_listings.csv", dtype={"product_id": str})
	return df_fact_tiki, df_fact_ebay


def _clean_numeric_columns(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
	"""Convert selected columns to numeric and drop null values in those columns."""
	cleaned = df.copy()
	for col in cols:
		cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
	return cleaned.dropna(subset=cols)


def _apply_global_filters(df_tiki: pd.DataFrame, df_ebay: pd.DataFrame, filters: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
	"""Apply global filters from the sidebar to both platform datasets."""
	selected_platforms = filters.get("platform", ["Tiki", "eBay"])
	min_price, max_price = filters.get("price_range", (0, 50_000_000))

	if "Tiki" in selected_platforms:
		tiki_filtered = df_tiki[(df_tiki["price"] >= min_price) & (df_tiki["price"] <= max_price)].copy()
	else:
		tiki_filtered = df_tiki.iloc[0:0].copy()

	if "eBay" in selected_platforms:
		ebay_filtered = df_ebay[(df_ebay["Total_Cost_VND"] >= min_price) & (df_ebay["Total_Cost_VND"] <= max_price)].copy()
	else:
		ebay_filtered = df_ebay.iloc[0:0].copy()

	return tiki_filtered, ebay_filtered

def render_ebay_violin_box(df_ebay: pd.DataFrame) -> None:
	"""Render combined violin + box traces to show eBay price volatility."""
	st.subheader("3. eBay Focus: Price Volatility (Violin + Box)")

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
	st.subheader("4. eBay Focus: Listing Price vs Shipping Fee Boundary")

	if df_ebay.empty:
		st.info("No eBay data available under current global filters.")
		return

	max_points = st.slider("Scatter sample size", min_value=300, max_value=5000, value=1800, step=100)

	df_vis = df_ebay[["price", "shipping_cost", "condition"]].copy()
	df_vis = _clean_numeric_columns(df_vis, ["price", "shipping_cost"])
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


def render(filters: Dict[str, Any]) -> None:
	"""Main rendering entrypoint for Tab 1: Pricing & Promotions."""
	st.header("📊 Pricing & Promotions")
	st.markdown("Price architecture and promotion effects across Tiki and eBay listings.")

	try:
		df_tiki, df_ebay = load_data()
	except Exception as exc:
		st.error(f"Error loading pricing datasets: {exc}. Check folder ../data/processed.")
		return

	df_tiki = _clean_numeric_columns(df_tiki, ["price"])
	df_ebay = _clean_numeric_columns(df_ebay, ["price", "shipping_cost", "Total_Cost_VND"])

	df_tiki_filtered, df_ebay_filtered = _apply_global_filters(df_tiki, df_ebay, filters)

	st.divider()

	with st.container():
		render_ebay_violin_box(df_ebay_filtered)

	st.divider()

	with st.container():
		render_ebay_price_shipping_boundary(df_ebay_filtered)
