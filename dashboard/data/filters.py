import pandas as pd
from typing import Dict, Any, List, Tuple


def clean_numeric(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """
    Coerce *cols* to numeric in-place and drop rows where coercion fails.
    Rows with NaN in any of the specified columns are removed.
    """
    out = df.copy()
    for col in cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out.dropna(subset=cols)


def apply_global_filters(
    df_tiki: pd.DataFrame,
    df_ebay: pd.DataFrame,
    filters: Dict[str, Any],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Apply sidebar platform and price-range filters to both datasets.

    Parameters
    df_tiki   : Tiki fact table (must have a ``price`` column).
    df_ebay   : eBay fact table (must have a ``Total_Cost_VND`` column).
    filters   : dict returned by render_sidebar() — keys: ``platform``, ``price_range``.

    Returns
    Filtered (df_tiki, df_ebay) copies.  Returns an empty Frame (iloc[0:0])
    for a platform that is not selected.
    """
    selected_platforms = filters.get("platform", ["Tiki", "eBay"])
    min_price, max_price = filters.get("price_range", (0, 50_000_000))

    if "Tiki" in selected_platforms:
        tiki_out = df_tiki[
            (df_tiki["price"] >= min_price) & (df_tiki["price"] <= max_price)
        ].copy()
    else:
        tiki_out = df_tiki.iloc[0:0].copy()

    if "eBay" in selected_platforms:
        ebay_out = df_ebay[
            (df_ebay["Total_Cost_VND"] >= min_price)
            & (df_ebay["Total_Cost_VND"] <= max_price)
        ].copy()
    else:
        ebay_out = df_ebay.iloc[0:0].copy()

    return tiki_out, ebay_out


def simplify_ebay_condition(cond: str) -> str | None:
    """
    Map a raw eBay condition string to one of three canonical groups.

    Returns None for 'For Parts' / unknown conditions (caller should exclude).
    Groups:
        'eBay — New'               : new / brand-new / new-with-tags
        'eBay — Used'              : used / usato
        'eBay — Refurb / Open Box' : refurbished, open box, certified, graded
    """
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
    return None


def simplify_condition_short(cond: str) -> str | None:
    """
    Map a raw eBay condition string to a short canonical group label.

    Returns None for 'For Parts' / unknown conditions (caller should exclude).
    Groups: 'New', 'Used', 'Refurbished'
    """
    c = str(cond).lower().strip()
    if c == "new" or any(k in c for k in ["brand new", "new with tags", "new other"]):
        return "New"
    if any(k in c for k in ["used", "usato"]):
        return "Used"
    if any(k in c for k in [
        "refurbished", "open box", "opened", "certified",
        "good -", "excellent -", "very good -",
    ]):
        return "Refurbished"
    return None
