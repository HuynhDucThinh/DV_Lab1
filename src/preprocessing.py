# src/preprocessing.py

from typing import List, Tuple
import pandas as pd
import numpy as np

def impute_categorical_mode(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Impute missing values in categorical columns using the Mode (most frequent value).
    This prevents creating false ordinal relationships that algorithms like MICE might introduce
    when converting categories to numeric formats.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    
    df_imputed = df.copy()
    for col in columns:
        if col in df_imputed.columns and df_imputed[col].isnull().any():
            mode_val = df_imputed[col].mode()[0]
            df_imputed[col].fillna(mode_val, inplace=True)
    return df_imputed

def impute_tiki_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values specifically for the Tiki dataset.
    - Fills categorical missing values with 'Unknown'.
    - Fills numerical missing values (counts/rates) with 0.
    """
    df = df.copy()
    
    # Fill categorical columns
    df['brand'] = df['brand'].fillna("Unknown")
    df['category'] = df['category'].fillna("Unknown")

    # Fill numerical features
    num_cols = ['discount_rate', 'rating_average', 'review_count', 'quantity_sold']
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)
            
    return df

def impute_ebay_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values specifically for the eBay dataset.
    - Drops columns with >90% missing data.
    - Uses Mode imputation for categories and Median/Zero for numericals.
    """
    df = df.copy()
    
    # Drop high missing value columns
    cols_to_drop = ['subtitle', 'item_end_date'] 
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

    # Mode Imputation
    cat_cols = ['shipping_currency', 'item_location_postal', 'item_location_country', 'condition_id']
    for col in cat_cols:
        if col in df.columns:
            mode_val = df[col].mode().iloc[0]
            df[col] = df[col].fillna(mode_val)

    # Explicit 'Unknown' filling
    for col in ['seller_username', 'category_path', 'condition']:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')

    # Zero / Median Imputation
    if 'shipping_cost' in df.columns:
        df['shipping_cost'] = df['shipping_cost'].fillna(0)
        
    for col in ['seller_feedback_score', 'seller_feedback_percent']:
        if col in df.columns:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)

    # Placeholder Imputation for Image URLs
    for col in ['image_url', 'thumbnail_url']:
        if col in df.columns:
            df[col] = df[col].fillna("Not Available")
            
    return df

def cap_outliers_percentile(df: pd.DataFrame, columns: List[str], upper_percentile: float = 0.99) -> pd.DataFrame:
    """
    Cap extreme high outliers at a specific percentile.

    This function applies Winsorization to the specified columns, limiting
    extreme upper values to the value at the given percentile. It prevents
    outliers from distorting aggregations and ML models without deleting records.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    columns : List[str]
        List of numerical column names to apply capping.
    upper_percentile : float, optional (default=0.99)
        The percentile threshold for capping (e.g., 0.99 means 99th percentile).

    Returns
    -------
    pd.DataFrame
        A new DataFrame with capped values.
    """
    df_cleaned = df.copy()
    for col in columns:
        if col in df_cleaned.columns:
            upper_limit = df_cleaned[col].quantile(upper_percentile)
            # Clip upper limits using np.clip, leave lower limits intact (a_min=None)
            df_cleaned[col] = np.clip(df_cleaned[col], a_min=None, a_max=upper_limit)
    return df_cleaned

def engineer_tiki_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate new business features for the Tiki dataset.
    """
    df_feat = df.copy()
    
    # 1. Discount_Segment
    if 'discount_rate' in df_feat.columns:
        # Use np.select to define clear business logic for discount segmentation
        conditions = [
            (df_feat['discount_rate'] == 0),
            (df_feat['discount_rate'] > 0) & (df_feat['discount_rate'] < 20),
            (df_feat['discount_rate'] >= 20) & (df_feat['discount_rate'] <= 50),
            (df_feat['discount_rate'] > 50)
        ]
        choices = ['0%', '< 20%', '20-50%', '> 50%']
        
        # default='Unknow' helps to catch any unexpected NaN values that might have been missed during imputation
        df_feat['Discount_Segment'] = np.select(conditions, choices, default='Unknown')
        
    # 2. Is_Best_Seller
    if 'quantity_sold' in df_feat.columns:
        df_feat['Is_Best_Seller'] = (df_feat['quantity_sold'] > 100).astype(int)
        
    return df_feat

def engineer_ebay_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate new business features for the eBay dataset.
    """
    df_feat = df.copy()
    
    # 1. Total_Cost_VND (Assuming USD to VND rate = 26,000)
    if 'price' in df_feat.columns and 'shipping_cost' in df_feat.columns:
        total_usd = df_feat['price'].fillna(0) + df_feat['shipping_cost'].fillna(0)
        df_feat['Total_Cost_VND'] = total_usd * 25000
        
    # 2. Listing_Duration_Days
    if 'item_end_date' in df_feat.columns and 'item_creation_date' in df_feat.columns:
        end_date = pd.to_datetime(df_feat['item_end_date'], errors='coerce')
        start_date = pd.to_datetime(df_feat['item_creation_date'], errors='coerce')
        df_feat['Listing_Duration_Days'] = (end_date - start_date).dt.days
        
    # 3. Trust_Level
    if 'seller_feedback_percent' in df_feat.columns:
        conditions = [
            df_feat['seller_feedback_percent'].isnull(),
            df_feat['seller_feedback_percent'] > 98.0
        ]
        choices = ['Unknown', 'High Trust']
        
        df_feat['Trust_Level'] = np.select(conditions, choices, default='Normal/Low Trust')
        
    return df_feat

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