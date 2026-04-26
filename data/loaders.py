import os
import streamlit as st
import pandas as pd

# dv_lab1/data/processed/ — đường dẫn tuyệt đối tính từ file này
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed")


@st.cache_data
def load_tiki_ebay() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (fact_tiki_listings, fact_ebay_listings) — used by tab1."""
    df_tiki = pd.read_csv(f"{DATA_DIR}/fact_tiki_listings.csv", dtype={"product_id": str})
    df_ebay = pd.read_csv(f"{DATA_DIR}/fact_ebay_listings.csv", dtype={"product_id": str})
    return df_tiki, df_ebay


@st.cache_data
def load_4_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return (fact_tiki, fact_ebay, dim_product, dim_category) — used by tab0 and tab3."""
    df_tiki     = pd.read_csv(f"{DATA_DIR}/fact_tiki_listings.csv", dtype={"product_id": str})
    df_ebay     = pd.read_csv(f"{DATA_DIR}/fact_ebay_listings.csv", dtype={"product_id": str})
    df_product  = pd.read_csv(f"{DATA_DIR}/dim_product.csv",        dtype={"product_id": str})
    df_category = pd.read_csv(f"{DATA_DIR}/dim_category.csv")
    return df_tiki, df_ebay, df_product, df_category


@st.cache_data
def load_5_tables() -> tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame
]:
    """Return (fact_tiki, fact_ebay, dim_product, dim_category, dim_seller) — used by tab2."""
    df_tiki     = pd.read_csv(f"{DATA_DIR}/fact_tiki_listings.csv", dtype={"product_id": str})
    df_ebay     = pd.read_csv(f"{DATA_DIR}/fact_ebay_listings.csv", dtype={"product_id": str})
    df_product  = pd.read_csv(f"{DATA_DIR}/dim_product.csv",        dtype={"product_id": str})
    df_category = pd.read_csv(f"{DATA_DIR}/dim_category.csv")
    df_seller   = pd.read_csv(f"{DATA_DIR}/dim_seller.csv")
    return df_tiki, df_ebay, df_product, df_category, df_seller


@st.cache_data
def load_kpi_data() -> dict:
    """Compute platform-level KPI metrics for the hero card row in app.py."""
    df_t = pd.read_csv(f"{DATA_DIR}/fact_tiki_listings.csv", dtype={"product_id": str})
    df_e = pd.read_csv(f"{DATA_DIR}/fact_ebay_listings.csv", dtype={"product_id": str})
    df_s = pd.read_csv(f"{DATA_DIR}/dim_seller.csv")

    tiki_p = pd.to_numeric(df_t["price"],          errors="coerce").dropna()
    ebay_p = pd.to_numeric(df_e["Total_Cost_VND"], errors="coerce").dropna()
    disc   = pd.to_numeric(df_t["discount_rate"],  errors="coerce")

    return {
        "total":        len(df_t) + len(df_e),
        "sellers":      len(df_s),
        "median_price": pd.concat([tiki_p, ebay_p]).median(),
        "disc_pct":     (disc > 0).mean() * 100,
    }
