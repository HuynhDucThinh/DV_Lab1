import numpy as np


def compute_kde(
    values: np.ndarray,
    n_points: int = 500,
    trim_pct: float = 99.0,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Vectorized Gaussian KDE using Scott's bandwidth rule.
    Subsamples up to 6,000 observations for performance.

    Parameters
    ----------
    values    : 1-D array of raw numeric values (e.g. prices in VND).
    n_points  : Number of grid points for the density estimate.
    trim_pct  : Upper percentile used to clip the evaluation range
                (removes extreme outliers from the x-grid).

    Returns
    -------
    x   : Evaluation grid (n_points,)
    kde : Probability density at each grid point (n_points,)
          Returns empty arrays when data is insufficient.
    """
    values = values[np.isfinite(values)]
    n = len(values)
    if n < 5:
        return np.array([]), np.array([])

    bw = 1.06 * np.std(values) * n ** (-0.2)
    if bw <= 0:
        return np.array([]), np.array([])

    x_lo = np.percentile(values, 100 - trim_pct)
    x_hi = np.percentile(values, trim_pct)
    if x_lo >= x_hi:
        return np.array([]), np.array([])

    x = np.linspace(x_lo, x_hi, n_points)

    rng    = np.random.default_rng(42)
    sample = values if n <= 6_000 else rng.choice(values, 6_000, replace=False)

    diff = (x[:, None] - sample[None, :]) / bw
    kde  = np.exp(-0.5 * diff ** 2).mean(axis=1) / (bw * np.sqrt(2 * np.pi))
    return x, kde


def age_to_color(norm_val: float) -> str:
    """
    Map a normalised listing-age value [0, 1] to an RGB colour string.

    0.0 → green  (fast turnover / new listing)
    1.0 → red    (slow turnover / stagnant listing)
    """
    r = int(34  + norm_val * (220 - 34))
    g = int(197 - norm_val * (197 - 50))
    b = int(94  - norm_val * 94)
    return f"rgb({r},{g},{b})"
