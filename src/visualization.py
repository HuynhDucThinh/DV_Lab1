# src/visualization.py

from typing import List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_distribution_with_zoom(
    df: pd.DataFrame,
    columns: List[str],
    quantile_threshold: float = 0.95,
    bins: int = 50,
    figsize: tuple = (10, 5)
) -> None:
    """
    Plot distribution visualizations for skewed numerical features.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing the data.

    columns : List[str]
        List of numerical column names to visualize.

    quantile_threshold : float, optional (default=0.95)
        Upper quantile threshold used to filter extreme values (e.g., 0.95 = keep 95% of data).

    bins : int, optional (default=50)
        Number of bins used in the histogram.

    figsize : tuple, optional (default=(10, 5))
        Figure size for each plot.

    Returns
    -------
    None
        Displays plots directly.
    """

    # Validate input
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    for col in columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame")
        series = df[col].dropna()
        zoom_limit = series.quantile(quantile_threshold)
        plot_data = series[series <= zoom_limit]

        # Create subplots (boxplot + histogram)
        fig, (ax_box, ax_hist) = plt.subplots(
            nrows=2,
            ncols=1,
            sharex=True,
            gridspec_kw={"height_ratios": [0.25, 0.75]},
            figsize=figsize
        )

        # --- Boxplot ---
        sns.boxplot(
            x=plot_data,
            ax=ax_box,
            orient="h",
            width=0.4,
            color="lightblue",
            showfliers=True,
            flierprops={
                "marker": "o",
                "markerfacecolor": "black",
                "markersize": 3,
                "alpha": 0.3,
            },
        )

        ax_box.set(xlabel="")
        ax_box.set_title(
            f"Distribution of '{col}' (Zoomed to {int(quantile_threshold * 100)}% of data)",
            fontsize=12,
            fontweight="bold",
        )

        # --- Histogram ---
        sns.histplot(
            plot_data,
            ax=ax_hist,
            bins=bins,
            kde=True,
            color="steelblue",
            edgecolor="white",
        )
        ax_hist.set_xlabel(col)
        ax_hist.set_ylabel("Frequency")
        ax_hist.xaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: f"{x:,.0f}")
        )
        plt.tight_layout()
        plt.show()

