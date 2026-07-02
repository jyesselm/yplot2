"""
Synthetic sample data for Phase 0 and Phase 2 spike tests.

NOT reachable from yplot2.__init__ — import only inside tests and demo fns.
Requires pandas/numpy (available via [stats] extra).
"""

import numpy as np
import pandas as pd

_NUCLEOTIDES = ["A", "C", "G", "U"]


def make_sample_df(seed: int = 42, n_per_nuc: int = 40) -> pd.DataFrame:
    """
    Build a deterministic synthetic dataframe that mimics RNA DMS reactivity.

    Columns: ``nuc`` (str), ``reactivity`` (float).

    Args:
        seed: RNG seed for reproducibility.
        n_per_nuc: Number of data points per nucleotide category.

    Returns:
        DataFrame with shape (n_per_nuc * 4, 2).
    """
    rng = np.random.default_rng(seed)
    rows = []
    means = {"A": 0.8, "C": 0.3, "G": 0.5, "U": 0.1}
    for nuc in _NUCLEOTIDES:
        values = rng.normal(loc=means[nuc], scale=0.15, size=n_per_nuc)
        values = np.clip(values, 0, 1.5)
        for v in values:
            rows.append({"nuc": nuc, "reactivity": float(v)})
    return pd.DataFrame(rows)


def make_xy_df(seed: int = 42, n: int = 2000) -> pd.DataFrame:
    """Build a deterministic bivariate-normal sample for 2-D density plots.

    Columns: ``x`` (float), ``y`` (float).

    Args:
        seed: RNG seed for reproducibility.
        n: Number of data points.

    Returns:
        DataFrame with shape (n, 2).
    """
    rng = np.random.default_rng(seed)
    x = rng.normal(loc=0.0, scale=1.0, size=n)
    y = rng.normal(loc=0.0, scale=1.0, size=n)
    return pd.DataFrame({"x": x, "y": y})
