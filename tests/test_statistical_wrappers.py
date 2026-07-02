"""
Structural tests for the Phase 2 statistical wrappers:
box, kde, heatmap2d, hexbin.

Per-wrapper assertions:
- Return value is the input axes.
- House palette hex on seaborn categorical bodies (proves saturation=1 + palette dict).
- Spine lw == axis_linewidth (finish() applied).
- Tick label font contains "Arimo".
- __yp_catalog__ present.
- Seaborn-absent guard: importing the module succeeds; calling raises ImportError.
- heatmap2d/hexbin: work with seaborn absent; AxesImage / PolyCollection present.
"""

import sys
import warnings
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pytest

from yplot2.config import get_config
from yplot2.plots.colors import palette_hex


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _tick_font_ok(ax) -> bool:
    """Return True if any x-tick label contains 'Arimo'."""
    labels = ax.get_xticklabels()
    if not labels:
        return True  # no labels → pass
    return any("Arimo" in lbl.get_fontname() for lbl in labels)


def _spine_lw_ok(ax) -> bool:
    """Return True when all visible spines match axis_linewidth."""
    cfg = get_config()
    return all(
        abs(sp.get_linewidth() - cfg.axis_linewidth) < 1e-6
        for sp in ax.spines.values()
        if sp.get_visible()
    )


# ---------------------------------------------------------------------------
# box()
# ---------------------------------------------------------------------------


class TestBox:
    """Structural assertions for box()."""

    def setup_method(self):
        pytest.importorskip("seaborn")

    def _draw_box(self, strip=False):
        from yplot2.plots.statistical.box import box
        from yplot2.plots.statistical._sampledata import make_sample_df

        df = make_sample_df()
        fig, ax = plt.subplots(figsize=(4, 3))
        result = box(ax, df, x="nuc", y="reactivity", hue="nuc", strip=strip)
        return fig, ax, result

    def test_returns_ax(self):
        """box() returns the input axes."""
        fig, ax, result = self._draw_box()
        try:
            assert result is ax
        finally:
            plt.close(fig)

    def test_catalog_attrs(self):
        """box has __yp_catalog__ with expected keys."""
        from yplot2.plots.statistical.box import box

        meta = box.__yp_catalog__
        assert "tags" in meta
        assert "data_shape" in meta
        assert meta["category"] == "statistical"

    def test_house_palette_hex(self):
        """Box body facecolors match the undiluted house palette (saturation=1).

        Seaborn boxplot stores box bodies in ax.patches (FancyBboxPatch), not
        ax.collections. We collect facecolors from all patches to verify the
        undiluted palette hex colors are present.
        """
        fig, ax, _ = self._draw_box()
        try:
            patch_hexes = set()
            for patch in ax.patches:
                fc = patch.get_facecolor()
                patch_hexes.add(mcolors.to_hex(fc))

            for nuc in ["A", "C", "G", "U"]:
                expected = palette_hex("nucleotide", nuc)
                assert expected in patch_hexes, (
                    f"Expected {expected} for nuc={nuc!r}; got {patch_hexes}"
                )
        finally:
            plt.close(fig)

    def test_spine_linewidth(self):
        """box() applies finish(); spine lw == axis_linewidth."""
        fig, ax, _ = self._draw_box()
        try:
            assert _spine_lw_ok(ax), "Spine linewidth mismatch after box()"
        finally:
            plt.close(fig)

    def test_tick_font_arimo(self):
        """box() tick labels use Arimo after finish()."""
        fig, ax, _ = self._draw_box()
        try:
            assert _tick_font_ok(ax), "Tick label font is not Arimo after box()"
        finally:
            plt.close(fig)

    def test_strip_path_collections(self):
        """box(strip=True) produces PathCollections for the strip overlay."""
        from matplotlib.collections import PathCollection

        fig, ax, _ = self._draw_box(strip=True)
        try:
            strips = [c for c in ax.collections if isinstance(c, PathCollection)]
            assert strips, "Expected PathCollections when strip=True"
        finally:
            plt.close(fig)

    def test_demo_box_returns_figure(self):
        """demo_box() returns a Figure with at least one axes."""
        from yplot2.plots.statistical.box import demo_box

        fig = demo_box()
        try:
            assert hasattr(fig, "axes")
            assert len(fig.axes) >= 1
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# kde()
# ---------------------------------------------------------------------------


class TestKde:
    """Structural assertions for kde()."""

    def setup_method(self):
        pytest.importorskip("seaborn")

    def _draw_kde(self):
        from yplot2.plots.statistical.kde import kde
        from yplot2.plots.statistical._sampledata import make_sample_df

        df = make_sample_df()
        fig, ax = plt.subplots(figsize=(4, 3))
        result = kde(ax, df, x="reactivity", hue="nuc")
        return fig, ax, result

    def test_returns_ax(self):
        """kde() returns the input axes."""
        fig, ax, result = self._draw_kde()
        try:
            assert result is ax
        finally:
            plt.close(fig)

    def test_catalog_attrs(self):
        """kde has __yp_catalog__ with expected keys."""
        from yplot2.plots.statistical.kde import kde

        meta = kde.__yp_catalog__
        assert meta["category"] == "statistical"
        assert "density" in meta["tags"]

    def test_spine_linewidth(self):
        """kde() applies finish(); spine lw == axis_linewidth."""
        fig, ax, _ = self._draw_kde()
        try:
            assert _spine_lw_ok(ax), "Spine linewidth mismatch after kde()"
        finally:
            plt.close(fig)

    def test_tick_font_arimo(self):
        """kde() tick labels use Arimo after finish()."""
        fig, ax, _ = self._draw_kde()
        try:
            assert _tick_font_ok(ax), "Tick label font is not Arimo after kde()"
        finally:
            plt.close(fig)

    def test_demo_kde_returns_figure(self):
        """demo_kde() returns a Figure with at least one axes."""
        from yplot2.plots.statistical.kde import demo_kde

        fig = demo_kde()
        try:
            assert hasattr(fig, "axes")
            assert len(fig.axes) >= 1
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# heatmap2d()
# ---------------------------------------------------------------------------


class TestHeatmap2d:
    """heatmap2d is seaborn-free and produces an AxesImage + styled colorbar."""

    def _draw_heatmap2d(self, colorbar=True):
        import numpy as np
        from yplot2.plots.statistical.heatmap2d import heatmap2d

        rng = np.random.default_rng(0)
        x, y = rng.normal(size=500), rng.normal(size=500)
        fig, ax = plt.subplots(figsize=(4, 3))
        result = heatmap2d(ax, x, y, colorbar=colorbar)
        return fig, ax, result

    def test_returns_ax(self):
        """heatmap2d() returns the input axes."""
        fig, ax, result = self._draw_heatmap2d()
        try:
            assert result is ax
        finally:
            plt.close(fig)

    def test_axes_image_present(self):
        """heatmap2d() adds an AxesImage to the axes."""
        from matplotlib.image import AxesImage

        fig, ax, _ = self._draw_heatmap2d()
        try:
            images = [c for c in ax.get_children() if isinstance(c, AxesImage)]
            assert images, "No AxesImage found after heatmap2d()"
        finally:
            plt.close(fig)

    def test_colorbar_outline_lw(self):
        """heatmap2d colorbar outline matches axis_linewidth."""
        cfg = get_config()
        fig, ax, _ = self._draw_heatmap2d(colorbar=True)
        try:
            assert len(fig.axes) >= 2, "Expected colorbar axes"
            cbar_ax = fig.axes[-1]
            # colorbar frame spine
            for sp in cbar_ax.spines.values():
                if sp.get_visible():
                    assert abs(sp.get_linewidth() - cfg.axis_linewidth) < 1e-6
        finally:
            plt.close(fig)

    def test_no_colorbar(self):
        """heatmap2d(colorbar=False) does not add extra axes."""
        fig, ax, _ = self._draw_heatmap2d(colorbar=False)
        try:
            assert len(fig.axes) == 1, "Unexpected colorbar axes"
        finally:
            plt.close(fig)

    def test_catalog_attrs(self):
        """heatmap2d has __yp_catalog__."""
        from yplot2.plots.statistical.heatmap2d import heatmap2d

        meta = heatmap2d.__yp_catalog__
        assert meta["data_shape"] == "xy"
        assert "2d-histogram" in meta["tags"]

    def test_seaborn_absent_still_works(self):
        """heatmap2d works even when seaborn is not installed."""
        import numpy as np

        # Block seaborn in a copy of sys.modules
        saved = sys.modules.get("seaborn")
        sys.modules["seaborn"] = None  # type: ignore[assignment]
        try:
            # Force reimport of heatmap2d module
            import importlib
            import yplot2.plots.statistical.heatmap2d as _mod

            importlib.reload(_mod)

            x, y = np.linspace(0, 1, 100), np.linspace(0, 1, 100)
            fig, ax = plt.subplots()
            _mod.heatmap2d(ax, x, y, colorbar=False)
            plt.close(fig)
        finally:
            if saved is None:
                del sys.modules["seaborn"]
            else:
                sys.modules["seaborn"] = saved

    def test_demo_heatmap2d_returns_figure(self):
        """demo_heatmap2d() returns a Figure with at least one axes."""
        from yplot2.plots.statistical.heatmap2d import demo_heatmap2d

        fig = demo_heatmap2d()
        try:
            assert len(fig.axes) >= 1
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# hexbin()
# ---------------------------------------------------------------------------


class TestHexbin:
    """hexbin is seaborn-free and produces a PolyCollection + styled colorbar."""

    def _draw_hexbin(self, colorbar=True):
        import numpy as np
        from yplot2.plots.statistical.hexbin import hexbin

        rng = np.random.default_rng(0)
        x, y = rng.normal(size=300), rng.normal(size=300)
        fig, ax = plt.subplots(figsize=(4, 3))
        result = hexbin(ax, x, y, colorbar=colorbar)
        return fig, ax, result

    def test_returns_ax(self):
        """hexbin() returns the input axes."""
        fig, ax, result = self._draw_hexbin()
        try:
            assert result is ax
        finally:
            plt.close(fig)

    def test_poly_collection_present(self):
        """hexbin() adds a PolyCollection (the hexagons) to the axes."""
        from matplotlib.collections import PolyCollection

        fig, ax, _ = self._draw_hexbin()
        try:
            polys = [c for c in ax.collections if isinstance(c, PolyCollection)]
            assert polys, "No PolyCollection found after hexbin()"
        finally:
            plt.close(fig)

    def test_catalog_attrs(self):
        """hexbin has __yp_catalog__."""
        from yplot2.plots.statistical.hexbin import hexbin

        meta = hexbin.__yp_catalog__
        assert meta["data_shape"] == "xy"
        assert "hexbin" in meta["tags"]

    def test_seaborn_absent_still_works(self):
        """hexbin works even when seaborn is not installed."""
        import numpy as np

        saved = sys.modules.get("seaborn")
        sys.modules["seaborn"] = None  # type: ignore[assignment]
        try:
            import importlib
            import yplot2.plots.statistical.hexbin as _mod

            importlib.reload(_mod)

            x, y = np.linspace(0, 1, 100), np.linspace(0, 1, 100)
            fig, ax = plt.subplots()
            _mod.hexbin(ax, x, y, colorbar=False)
            plt.close(fig)
        finally:
            if saved is None:
                del sys.modules["seaborn"]
            else:
                sys.modules["seaborn"] = saved

    def test_no_colorbar(self):
        """hexbin(colorbar=False) does not add extra axes."""
        fig, ax, _ = self._draw_hexbin(colorbar=False)
        try:
            assert len(fig.axes) == 1
        finally:
            plt.close(fig)

    def test_demo_hexbin_returns_figure(self):
        """demo_hexbin() returns a Figure with at least one axes."""
        from yplot2.plots.statistical.hexbin import demo_hexbin

        fig = demo_hexbin()
        try:
            assert len(fig.axes) >= 1
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# FutureWarning regression — no seaborn or pandas FutureWarning on default calls
# ---------------------------------------------------------------------------


class TestNoFutureWarnings:
    """No seaborn 'palette without hue' or pandas groupby FutureWarning raised.

    These are the forward-compat trips that would become hard-breaks at
    seaborn 0.14 and a future pandas release respectively.  Turning them
    into errors in CI catches regressions immediately.
    """

    def _df(self):
        from yplot2.plots.statistical._sampledata import make_sample_df

        return make_sample_df()

    def test_violin_hue_none_no_futurewarning(self):
        """violin(hue=None) emits no FutureWarning."""
        pytest.importorskip("seaborn")
        from yplot2.plots.statistical.violin import violin

        fig, ax = plt.subplots()
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", FutureWarning)
                violin(ax, self._df(), x="nuc", y="reactivity")
        finally:
            plt.close(fig)

    def test_violin_strip_no_futurewarning(self):
        """violin(strip=True, hue=None) emits no FutureWarning."""
        pytest.importorskip("seaborn")
        from yplot2.plots.statistical.violin import violin

        fig, ax = plt.subplots()
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", FutureWarning)
                violin(ax, self._df(), x="nuc", y="reactivity", strip=True)
        finally:
            plt.close(fig)

    def test_box_hue_none_no_futurewarning(self):
        """box(hue=None) emits no FutureWarning."""
        pytest.importorskip("seaborn")
        from yplot2.plots.statistical.box import box

        fig, ax = plt.subplots()
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", FutureWarning)
                box(ax, self._df(), x="nuc", y="reactivity")
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# heatmap2d NaN/inf pre-check
# ---------------------------------------------------------------------------


class TestHeatmap2dFiniteCheck:
    """heatmap2d raises a clear ValueError on NaN/inf input."""

    def test_nan_x_raises(self):
        """NaN in x raises ValueError with a clear message."""
        import numpy as np
        from yplot2.plots.statistical.heatmap2d import heatmap2d

        x = np.array([0.0, float("nan"), 1.0])
        y = np.array([0.0, 1.0, 2.0])
        fig, ax = plt.subplots()
        try:
            with pytest.raises(ValueError, match="NaN or infinite"):
                heatmap2d(ax, x, y, colorbar=False)
        finally:
            plt.close(fig)

    def test_inf_y_raises(self):
        """Inf in y raises ValueError with a clear message."""
        import numpy as np
        from yplot2.plots.statistical.heatmap2d import heatmap2d

        x = np.array([0.0, 1.0, 2.0])
        y = np.array([0.0, float("inf"), 1.0])
        fig, ax = plt.subplots()
        try:
            with pytest.raises(ValueError, match="NaN or infinite"):
                heatmap2d(ax, x, y, colorbar=False)
        finally:
            plt.close(fig)

    def test_finite_data_passes(self):
        """Finite data does not raise."""
        import numpy as np
        from yplot2.plots.statistical.heatmap2d import heatmap2d

        rng = np.random.default_rng(0)
        x, y = rng.normal(size=100), rng.normal(size=100)
        fig, ax = plt.subplots()
        try:
            heatmap2d(ax, x, y, colorbar=False)  # must not raise
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# Seaborn-optional import safety for seaborn-backed wrappers
# ---------------------------------------------------------------------------


class TestSeabornOptionalImport:
    """Importing wrapper modules with seaborn absent must succeed; calling raises."""

    def _block_seaborn(self):
        """Return context that blocks seaborn and restores on exit."""
        return _BlockSeaborn()


class _BlockSeaborn:
    def __enter__(self):
        self._saved = sys.modules.get("seaborn")
        sys.modules["seaborn"] = None  # type: ignore[assignment]
        return self

    def __exit__(self, *_):
        if self._saved is None:
            sys.modules.pop("seaborn", None)
        else:
            sys.modules["seaborn"] = self._saved


def test_box_importerror_message_without_seaborn():
    """box() raises ImportError mentioning pip install when seaborn absent."""
    import importlib

    pytest.importorskip("pandas")
    from yplot2.plots.statistical._sampledata import make_sample_df

    df = make_sample_df()
    fig, ax = plt.subplots()
    try:
        with _BlockSeaborn():
            import yplot2.plots.statistical.box as _box_mod

            importlib.reload(_box_mod)
            with pytest.raises(ImportError, match="pip install"):
                _box_mod.box(ax, df, x="nuc", y="reactivity")
    finally:
        plt.close(fig)


def test_kde_importerror_message_without_seaborn():
    """kde() raises ImportError mentioning pip install when seaborn absent."""
    import importlib

    pytest.importorskip("pandas")
    from yplot2.plots.statistical._sampledata import make_sample_df

    df = make_sample_df()
    fig, ax = plt.subplots()
    try:
        with _BlockSeaborn():
            import yplot2.plots.statistical.kde as _kde_mod

            importlib.reload(_kde_mod)
            with pytest.raises(ImportError, match="pip install"):
                _kde_mod.kde(ax, df, x="reactivity")
    finally:
        plt.close(fig)
