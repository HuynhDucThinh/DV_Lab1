# src/preprocessing.py

from typing import List
import pandas as pd


def detect_outliers_iqr_summary(
    df: pd.DataFrame,
    columns: List[str]
) -> pd.DataFrame:
    """
    Compute outlier statistics for numerical features using the IQR method.
    This function calculates Q1, Q3, IQR, and outlier bounds for each specified column.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.

    columns : List[str]
        List of numerical column names to analyze.

    Returns
    -------
    pd.DataFrame
        A summary table containing:
        - Q1 (25th percentile)
        - Q3 (75th percentile)
        - IQR (Interquartile Range)
        - Lower Bound
        - Upper Bound
        - Outlier Count
        - Outlier Percentage
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if not isinstance(columns, list):
        raise TypeError("columns must be a list of column names")

    summary_data = []
    for col in columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame")
        series = df[col].dropna()
        if series.empty:
            continue

        # --- Compute quartiles and IQR ---
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        # --- Define outlier boundaries ---
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # --- Detect outliers ---
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        outlier_count = len(outliers)
        outlier_percentage = (outlier_count / len(series)) * 100

        # --- Store results ---
        summary_data.append({
            "feature": col,
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "outlier_count": outlier_count,
            "outlier_percentage": round(outlier_percentage, 2),
        })
    summary_df = pd.DataFrame(summary_data)
    return summary_df