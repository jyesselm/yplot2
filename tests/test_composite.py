"""Tests for yplot2.composite and the coord_from_image upgrade (Phase 1, Task 3).

Uses the Agg backend and a synthetic PNG with known pixel dimensions
(300 px wide × 150 px tall → aspect 2.0 at dpi=300).
"""

import matplotlib

matplotlib.use("Agg")

import numpy as np
import matplotlib.pyplot as plt
import pytest
from matplotlib.patches import FancyArrowPatch

import yplot2 as yp
from yplot2.config import get_config


# ---------------------------------------------------------------------------
# Fixture: synthetic PNG
# ---------------------------------------------------------------------------


def _make_png(tmp_path, width_px: int = 300, height_px: int = 150) -> str:
    """Save a solid-colour PNG with known pixel dimensions and return path."""
    img = np.full((height_px, width_px, 3), fill_value=128, dtype=np.uint8)
    path = str(tmp_path / "test_image.png")
    plt.imsave(path, img)
    return path


# ---------------------------------------------------------------------------
# 3a: coord_from_image — aspect-derived sizing
# ---------------------------------------------------------------------------


class TestCoordFromImage:
    """coord_from_image always preserves image aspect ratio."""

    def test_column_width_scale_1(self, tmp_path):
        """column_width=3.0, scale=1.0 → width==3.0, aspect==2.0."""
        png = _make_png(tmp_path)
        c = yp.coord_from_image(png, 0.5, 1.0, column_width=3.0, scale=1.0)
        assert c.width == 3.0
        assert abs(c.width / c.height - 2.0) < 1e-6

    def test_column_width_scale_half(self, tmp_path):
        """column_width=3.0, scale=0.5 → width==1.5, aspect==2.0."""
        png = _make_png(tmp_path)
        c = yp.coord_from_image(png, 0.5, 1.0, column_width=3.0, scale=0.5)
        assert abs(c.width - 1.5) < 1e-6
        assert abs(c.width / c.height - 2.0) < 1e-6

    def test_back_compat_no_column_width(self, tmp_path):
        """No column_width → native width (300px/300dpi=1.0") and aspect 2.0."""
        png = _make_png(tmp_path, width_px=300, height_px=150)
        c = yp.coord_from_image(png, 0, 0)
        assert abs(c.width - 1.0) < 1e-6, f'Native width should be 1.0", got {c.width}'
        assert abs(c.width / c.height - 2.0) < 1e-6

    def test_position_preserved(self, tmp_path):
        """left and bottom coordinates are passed through unchanged."""
        png = _make_png(tmp_path)
        c = yp.coord_from_image(png, 1.5, 2.3, column_width=3.0)
        assert c.left == 1.5
        assert c.bottom == 2.3

    def test_scale_zero_raises(self, tmp_path):
        """scale=0 raises ValueError before creating a zero-size Coord."""
        png = _make_png(tmp_path)
        with pytest.raises(ValueError, match="scale"):
            yp.coord_from_image(png, 0, 0, scale=0)

    def test_scale_negative_raises(self, tmp_path):
        """scale < 0 raises ValueError."""
        png = _make_png(tmp_path)
        with pytest.raises(ValueError, match="scale"):
            yp.coord_from_image(png, 0, 0, scale=-1.0)

    def test_column_width_zero_raises(self, tmp_path):
        """column_width=0 raises ValueError."""
        png = _make_png(tmp_path)
        with pytest.raises(ValueError, match="column_width"):
            yp.coord_from_image(png, 0, 0, column_width=0)

    def test_column_width_negative_raises(self, tmp_path):
        """column_width < 0 raises ValueError."""
        png = _make_png(tmp_path)
        with pytest.raises(ValueError, match="column_width"):
            yp.coord_from_image(png, 0, 0, column_width=-2.0)


# ---------------------------------------------------------------------------
# 3b: annotate()
# ---------------------------------------------------------------------------


class TestAnnotate:
    """annotate() places text with the correct transform and anchor."""

    def test_named_anchor_in_ax_texts(self):
        """annotate(ax, 'd', xy='top left') → Text in ax.texts with correct string."""
        fig, ax = plt.subplots()
        try:
            t = yp.annotate(ax, "d", xy="top left")
            assert t.get_text() == "d"
            assert t in ax.texts
        finally:
            plt.close(fig)

    def test_tuple_anchor_axes(self):
        """annotate with tuple xy in axes coords → text placed on axes fraction."""
        fig, ax = plt.subplots()
        try:
            t = yp.annotate(ax, "label", xy=(0.5, 0.5), coords="axes")
            assert t in ax.texts
        finally:
            plt.close(fig)

    def test_data_coords_transform(self):
        """annotate(coords='data') → transform is ax.transData."""
        fig, ax = plt.subplots()
        try:
            t = yp.annotate(ax, "d", xy=(0.5, 0.5), coords="data")
            assert t.get_transform() is ax.transData
        finally:
            plt.close(fig)

    def test_data_coords_position(self):
        """annotate(coords='data') → text stored at the given data position."""
        fig, ax = plt.subplots()
        try:
            t = yp.annotate(ax, "pt", xy=(3.0, 4.0), coords="data")
            x, y = t.get_position()
            assert abs(x - 3.0) < 1e-9 and abs(y - 4.0) < 1e-9
        finally:
            plt.close(fig)

    def test_invalid_coords_raises(self):
        """Unknown coords string raises ValueError."""
        fig, ax = plt.subplots()
        try:
            with pytest.raises(ValueError, match="coords"):
                yp.annotate(ax, "d", xy=(0.5, 0.5), coords="pixels")
        finally:
            plt.close(fig)

    def test_data_coords_requires_tuple(self):
        """coords='data' with a string xy raises ValueError."""
        fig, ax = plt.subplots()
        try:
            with pytest.raises(ValueError):
                yp.annotate(ax, "d", xy="top left", coords="data")
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# 3b: line_annotation()
# ---------------------------------------------------------------------------


class TestLineAnnotation:
    """line_annotation() adds a FancyArrowPatch to ax.patches."""

    def test_returns_fancy_arrow_patch(self):
        """Return type is FancyArrowPatch."""
        fig, ax = plt.subplots()
        try:
            patch = yp.line_annotation(ax, (0.1, 0.1), (0.9, 0.9))
            assert isinstance(patch, FancyArrowPatch)
        finally:
            plt.close(fig)

    def test_patch_in_ax_patches(self):
        """The patch is in ax.patches after the call."""
        fig, ax = plt.subplots()
        try:
            patch = yp.line_annotation(ax, (0.1, 0.1), (0.9, 0.9))
            assert patch in ax.patches
        finally:
            plt.close(fig)

    def test_linewidth_matches_cfg(self):
        """Default linewidth equals cfg.axis_linewidth."""
        cfg = get_config()
        fig, ax = plt.subplots()
        try:
            patch = yp.line_annotation(ax, (0.1, 0.1), (0.9, 0.9))
            assert abs(patch.get_linewidth() - cfg.axis_linewidth) < 1e-6
        finally:
            plt.close(fig)

    def test_custom_linewidth(self):
        """Explicit linewidth override is respected."""
        fig, ax = plt.subplots()
        try:
            patch = yp.line_annotation(ax, (0.1, 0.1), (0.9, 0.9), linewidth=2.0)
            assert abs(patch.get_linewidth() - 2.0) < 1e-6
        finally:
            plt.close(fig)

    def test_label_adds_text(self):
        """label kwarg adds a Text to ax.texts."""
        fig, ax = plt.subplots()
        n_before = len(ax.texts)
        try:
            yp.line_annotation(ax, (0.1, 0.5), (0.9, 0.5), label="8 Å")
            assert len(ax.texts) > n_before
        finally:
            plt.close(fig)

    def test_data_coords(self):
        """line_annotation with coords='data' uses data coordinate transform."""
        fig, ax = plt.subplots()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        try:
            patch = yp.line_annotation(ax, (1.0, 1.0), (9.0, 9.0), coords="data")
            assert isinstance(patch, FancyArrowPatch)
            assert patch in ax.patches
        finally:
            plt.close(fig)

    def test_data_coords_with_label(self):
        """line_annotation(coords='data', label=...) adds a Text in data coords."""
        fig, ax = plt.subplots()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        n_before = len(ax.texts)
        try:
            yp.line_annotation(ax, (1.0, 5.0), (9.0, 5.0), coords="data", label="dist")
            assert len(ax.texts) > n_before
        finally:
            plt.close(fig)

    def test_invalid_coords_raises(self):
        """Unknown coords string raises ValueError."""
        fig, ax = plt.subplots()
        try:
            with pytest.raises(ValueError, match="coords"):
                yp.line_annotation(ax, (0.1, 0.1), (0.9, 0.9), coords="pixels")
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# 3b: distance_label()
# ---------------------------------------------------------------------------


class TestDistanceLabel:
    """distance_label() is a convenience wrapper: arrow + label + patch."""

    def test_adds_patch_and_text(self):
        """distance_label adds both a FancyArrowPatch and a Text object."""
        fig, ax = plt.subplots()
        n_texts = len(ax.texts)
        n_patches = len(ax.patches)
        try:
            yp.distance_label(ax, (0.1, 0.5), (0.9, 0.5), "8 Å")
            assert len(ax.patches) > n_patches
            assert len(ax.texts) > n_texts
        finally:
            plt.close(fig)

    def test_returns_fancy_arrow_patch(self):
        """Return value is a FancyArrowPatch in ax.patches."""
        fig, ax = plt.subplots()
        try:
            patch = yp.distance_label(ax, (0.1, 0.5), (0.9, 0.5), "8 Å")
            assert isinstance(patch, FancyArrowPatch)
            assert patch in ax.patches
        finally:
            plt.close(fig)
