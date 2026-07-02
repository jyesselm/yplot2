"""
Unit tests for yplot2/plots/statistical/_style.py.

Verifies that normalize_glyphs correctly flattens linewidths and suppresses
strip edgecolors, and that style_colorbar applies house chrome to a colorbar.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from yplot2.config import get_config
from yplot2.plots.statistical._style import normalize_glyphs, style_colorbar


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_violin_ax(strip: bool = True, seed: int = 0):
    """Draw a nucleotide violin and return (fig, ax)."""
    seaborn = pytest.importorskip("seaborn")  # noqa: F841 — guard only
    from yplot2.plots.statistical.violin import violin
    from yplot2.plots.statistical._sampledata import make_sample_df

    df = make_sample_df()
    fig, ax = plt.subplots(figsize=(4, 3))
    violin(ax, df, x="nuc", y="reactivity", hue="nuc", seed=seed, strip=strip)
    return fig, ax


def _make_colorbar_fig():
    """Draw an imshow colorbar so we can test style_colorbar."""
    import numpy as np

    fig, ax = plt.subplots()
    data = np.arange(12).reshape(3, 4)
    im = ax.imshow(data, cmap="magma")
    cbar = fig.colorbar(im, ax=ax)
    return fig, cbar


# ---------------------------------------------------------------------------
# normalize_glyphs
# ---------------------------------------------------------------------------


class TestNormalizeGlyphs:
    """normalize_glyphs flattens body/inner lw and suppresses strip edges."""

    def test_body_linewidths_flattened(self):
        """Violin body collections have lw == axis_linewidth after normalize_glyphs."""
        from matplotlib.collections import PathCollection

        cfg = get_config()
        fig, ax = _make_violin_ax(strip=False)
        try:
            bodies = [c for c in ax.collections if not isinstance(c, PathCollection)]
            assert bodies, "No body collections on violin axes"
            for body in bodies:
                for lw in body.get_linewidth():
                    assert abs(lw - cfg.axis_linewidth) < 1e-6
        finally:
            plt.close(fig)

    def test_inner_line_linewidths_flattened(self):
        """Inner Line2D artists have lw == axis_linewidth after normalize_glyphs."""
        cfg = get_config()
        fig, ax = _make_violin_ax(strip=False)
        try:
            for line in ax.lines:
                assert abs(line.get_linewidth() - cfg.axis_linewidth) < 1e-6
        finally:
            plt.close(fig)

    def test_strip_edge_alpha_zero(self):
        """Strip PathCollections have edgecolor alpha == 0 after normalize_glyphs."""
        from matplotlib.collections import PathCollection

        fig, ax = _make_violin_ax(strip=True)
        try:
            strips = [c for c in ax.collections if isinstance(c, PathCollection)]
            assert strips, "Expected strip PathCollections when strip=True"
            for coll in strips:
                for rgba in coll.get_edgecolor():
                    assert rgba[3] == 0.0
        finally:
            plt.close(fig)

    def test_normalize_glyphs_direct(self):
        """Direct call to normalize_glyphs on a plain axes is a no-op (no error)."""
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])
        try:
            normalize_glyphs(ax, 0.75)  # must not raise
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# style_colorbar
# ---------------------------------------------------------------------------


class TestStyleColorbar:
    """style_colorbar applies house chrome to a matplotlib colorbar."""

    def test_outline_linewidth(self):
        """Colorbar outline lw matches cfg.axis_linewidth after style_colorbar."""
        cfg = get_config()
        fig, cbar = _make_colorbar_fig()
        try:
            style_colorbar(cbar)
            outline_lw = cbar.outline.get_linewidth()
            assert abs(outline_lw - cfg.axis_linewidth) < 1e-6
        finally:
            plt.close(fig)

    def test_tick_label_font_arimo(self):
        """Colorbar tick labels report Arimo family after style_colorbar."""
        fig, cbar = _make_colorbar_fig()
        try:
            style_colorbar(cbar)
            labels = cbar.ax.get_yticklabels()
            if not labels:
                pytest.skip("No colorbar tick labels to inspect")
            for label in labels:
                fontname = label.get_fontfamily()
                assert any("Arimo" in f for f in fontname), (
                    f"Expected Arimo in {fontname}"
                )
        finally:
            plt.close(fig)

    def test_tick_label_fontsize(self):
        """Colorbar tick labels use cfg.colorbar_tick_fontsize."""
        cfg = get_config()
        fig, cbar = _make_colorbar_fig()
        try:
            style_colorbar(cbar)
            labels = cbar.ax.get_yticklabels()
            if not labels:
                pytest.skip("No colorbar tick labels to inspect")
            for label in labels:
                assert abs(label.get_fontsize() - cfg.colorbar_tick_fontsize) < 1e-6
        finally:
            plt.close(fig)

    def test_accepts_explicit_cfg(self):
        """style_colorbar accepts an explicit Config object."""
        from yplot2.config import Config

        cfg = Config(axis_linewidth=1.5, colorbar_tick_fontsize=10)
        fig, cbar = _make_colorbar_fig()
        try:
            style_colorbar(cbar, cfg)
            assert abs(cbar.outline.get_linewidth() - 1.5) < 1e-6
        finally:
            plt.close(fig)
