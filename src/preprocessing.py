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

def engineer_tiki_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate new business features for Tiki dataset.
    """
    df_feat = df.copy()
    
    # 1. Discount_Segment
    if 'discount_rate' in df_feat.columns:
        bins = [-np.inf, 0, 20, 50, np.inf]
        labels = ['0%', '< 20%', '20-50%', '> 50%']
        df_feat['Discount_Segment'] = pd.cut(df_feat['discount_rate'], bins=bins, labels=labels, right=True)
        # Fix exact 0% mapping if needed, as pd.cut includes right edge
        df_feat.loc[df_feat['discount_rate'] == 0, 'Discount_Segment'] = '0%'
        
    # 2. Is_Best_Seller
    if 'quantity_sold' in df_feat.columns:
        df_feat['Is_Best_Seller'] = (df_feat['quantity_sold'] > 100).astype(int)
        
    return df_feat

def engineer_ebay_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate new business features for eBay dataset.
    """
    df_feat = df.copy()
    
    # 1. Total_Cost_VND (assuming USD to VND rate = 25000)
    if 'price' in df_feat.columns and 'shipping_cost' in df_feat.columns:
        df_feat['Total_Cost_VND'] = (df_feat['price'].fillna(0) + df_feat['shipping_cost'].fillna(0)) * 25000
        
    # 2. Listing_Duration_Days
    if 'item_end_date' in df_feat.columns and 'item_creation_date' in df_feat.columns:
        duration = (pd.to_datetime(df_feat['item_end_date']) - pd.to_datetime(df_feat['item_creation_date'])).dt.days
        df_feat['Listing_Duration_Days'] = duration.fillna(-1) # -1 for missing
        
    # 3. Trust_Level
    if 'seller_feedback_percent' in df_feat.columns:
        df_feat['Trust_Level'] = np.where(df_feat['seller_feedback_percent'] > 98, 'High Trust', 'Normal/Low Trust')
        # Handle cases where percent was missing originally if needed
        mask_missing = df_feat['seller_feedback_percent'].isnull()
        df_feat.loc[mask_missing, 'Trust_Level'] = 'Unknown'
        
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