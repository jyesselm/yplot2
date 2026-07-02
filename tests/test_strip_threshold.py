"""
Tests for cap_strip_groups and the violin/box strip-subsample integration.

Verifies:
- A group of 5000 rows capped at 1000 yields exactly 1000 rows.
- max_points=None returns all rows unchanged.
- Same seed → identical row indices (determinism).
- Different seeds → different row indices.
- violin(strip=True, max_strip_points=1000) subsamples when groups exceed cap.
- violin(strip=True, max_strip_points=None) draws all points.
- Seed determinism is preserved through violin().
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def large_df():
    """DataFrame with two groups: 'A' (5000 rows) and 'C' (200 rows).

    Both 'A' and 'C' are valid nucleotide palette keys so violin/box work
    without raising a ValueError about missing palette entries.
    """
    pd = pytest.importorskip("pandas")
    rng = np.random.default_rng(0)
    group_a = pd.DataFrame({"x": ["A"] * 5000, "y": rng.normal(size=5000)})
    group_c = pd.DataFrame({"x": ["C"] * 200, "y": rng.normal(size=200)})
    return pd.concat([group_a, group_c], ignore_index=True)


# ---------------------------------------------------------------------------
# cap_strip_groups unit tests
# ---------------------------------------------------------------------------


class TestCapStripGroups:
    """Unit tests for cap_strip_groups (list-comprehension form, no groupby.apply)."""

    def test_negative_max_points_raises(self, large_df):
        """Negative max_points raises ValueError with a clear message."""
        from yplot2.plots.statistical._overlay import cap_strip_groups

        with pytest.raises(ValueError, match="non-negative"):
            cap_strip_groups(large_df, ["x"], max_points=-1, seed=42)

    def test_zero_max_points_returns_empty(self, large_df):
        """max_points=0 returns an empty DataFrame (no points drawn)."""
        from yplot2.plots.statistical._overlay import cap_strip_groups

        result = cap_strip_groups(large_df, ["x"], max_points=0, seed=42)
        assert len(result) == 0

    def test_large_group_capped(self, large_df):
        """A group with 5000 rows capped at 1000 returns exactly 1000 rows."""
        from yplot2.plots.statistical._overlay import cap_strip_groups

        result = cap_strip_groups(large_df, ["x"], max_points=1000, seed=42)
        counts = result.groupby("x").size()
        assert counts["A"] == 1000

    def test_small_group_not_truncated(self, large_df):
        """A group smaller than max_points is returned in full (no ValueError)."""
        from yplot2.plots.statistical._overlay import cap_strip_groups

        result = cap_strip_groups(large_df, ["x"], max_points=1000, seed=42)
        counts = result.groupby("x").size()
        assert counts["C"] == 200

    def test_none_returns_all(self, large_df):
        """max_points=None returns data unchanged."""
        from yplot2.plots.statistical._overlay import cap_strip_groups

        result = cap_strip_groups(large_df, ["x"], max_points=None, seed=42)
        assert len(result) == len(large_df)

    def test_same_seed_deterministic(self, large_df):
        """Two calls with the same seed return identical row index sets."""
        from yplot2.plots.statistical._overlay import cap_strip_groups

        r1 = cap_strip_groups(large_df, ["x"], max_points=1000, seed=7)
        r2 = cap_strip_groups(large_df, ["x"], max_points=1000, seed=7)
        assert sorted(r1.index.tolist()) == sorted(r2.index.tolist())

    def test_different_seed_differs(self, large_df):
        """Two calls with different seeds return different row sets (with high probability)."""
        from yplot2.plots.statistical._overlay import cap_strip_groups

        r1 = cap_strip_groups(large_df, ["x"], max_points=1000, seed=0)
        r2 = cap_strip_groups(large_df, ["x"], max_points=1000, seed=99)
        assert sorted(r1.index.tolist()) != sorted(r2.index.tolist())


# ---------------------------------------------------------------------------
# violin() strip integration
# ---------------------------------------------------------------------------


def _count_strip_offsets(ax):
    """Count total offsets across all PathCollections on *ax*."""
    from matplotlib.collections import PathCollection

    return sum(
        len(c.get_offsets()) for c in ax.collections if isinstance(c, PathCollection)
    )


class TestViolinStripCap:
    """violin(strip=True) routes data through cap_strip_groups."""

    def test_strip_subsamples_large_group(self, large_df):
        """Strip overlay respects max_strip_points; total offsets <= n_groups * cap."""
        seaborn = pytest.importorskip("seaborn")  # noqa: F841
        from yplot2.plots.statistical.violin import violin

        fig, ax = plt.subplots(figsize=(4, 3))
        try:
            violin(
                ax,
                large_df,
                x="x",
                y="y",
                strip=True,
                max_strip_points=1000,
                seed=0,
            )
            n_offsets = _count_strip_offsets(ax)
            # 2 groups × 1000 cap = max 2000
            assert n_offsets <= 2000, f"Expected ≤2000 strip offsets, got {n_offsets}"
        finally:
            plt.close(fig)

    def test_strip_none_draws_all(self, large_df):
        """max_strip_points=None draws all points (no capping)."""
        seaborn = pytest.importorskip("seaborn")  # noqa: F841
        from yplot2.plots.statistical.violin import violin

        fig, ax = plt.subplots(figsize=(4, 3))
        try:
            violin(
                ax,
                large_df,
                x="x",
                y="y",
                strip=True,
                max_strip_points=None,
                seed=0,
            )
            n_offsets = _count_strip_offsets(ax)
            assert n_offsets == len(large_df), (
                f"Expected {len(large_df)} offsets with no cap, got {n_offsets}"
            )
        finally:
            plt.close(fig)

    def test_strip_seed_determinism(self, large_df):
        """Two violin(strip=True, seed=X) calls produce the same PathCollection offsets."""
        seaborn = pytest.importorskip("seaborn")  # noqa: F841
        from yplot2.plots.statistical.violin import violin

        def get_offsets(seed):
            fig, ax = plt.subplots(figsize=(4, 3))
            violin(
                ax, large_df, x="x", y="y", strip=True, max_strip_points=500, seed=seed
            )
            from matplotlib.collections import PathCollection

            offsets = np.concatenate(
                [
                    c.get_offsets().data
                    for c in ax.collections
                    if isinstance(c, PathCollection)
                ]
            )
            plt.close(fig)
            return offsets

        offs0a = get_offsets(0)
        offs0b = get_offsets(0)
        offs1 = get_offsets(1)

        np.testing.assert_array_equal(offs0a, offs0b)
        assert not np.array_equal(offs0a, offs1), (
            "Different seeds produced identical offsets"
        )

    def test_strip_false_default_no_path_collections(self):
        """violin() default strip=False draws no strip PathCollections."""
        seaborn = pytest.importorskip("seaborn")  # noqa: F841
        pytest.importorskip("pandas")
        from yplot2.plots.statistical.violin import violin
        from yplot2.plots.statistical._sampledata import make_sample_df
        from matplotlib.collections import PathCollection

        df = make_sample_df()
        fig, ax = plt.subplots(figsize=(4, 3))
        try:
            violin(ax, df, x="nuc", y="reactivity", hue="nuc")
            strips = [c for c in ax.collections if isinstance(c, PathCollection)]
            assert not strips, (
                f"Expected no strip PathCollections with strip=False (default), got {len(strips)}"
            )
        finally:
            plt.close(fig)
