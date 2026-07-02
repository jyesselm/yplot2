"""Tests for yplot2.canvas: figure(), figure7(), GridSpec7 (Phase 1, Task 1).

All assertions are geometry-only (font-independent) and use the Agg backend.
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.axes
import matplotlib.pyplot as plt
import pytest

import yplot2 as yp

# Matching the canvas module defaults for explicit test formulas.
_M = (0.6, 0.2, 0.2, 0.5)  # (left, right, top, bottom)
_G = (0.5, 0.5)  # (hspace, vspace)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _inches_bbox(ax: matplotlib.axes.Axes, fig) -> tuple:
    """Return (left, bottom, right, top) of ax in inches."""
    pos = ax.get_position()
    fw, fh = fig.get_size_inches()
    return pos.x0 * fw, pos.y0 * fh, pos.x1 * fw, pos.y1 * fh


# ---------------------------------------------------------------------------
# figure7() basic geometry
# ---------------------------------------------------------------------------


class TestFigure7BasicGeometry:
    """figure7() produces the expected figure width and panel structure."""

    def test_width_exactly_7(self):
        """figure7() width is exactly 7.0 inches."""
        fig, panels = yp.figure7(2, 2)
        try:
            assert fig.get_size_inches()[0] == 7.0
        finally:
            plt.close(fig)

    def test_panel_keys_row_major(self):
        """2×2 figure7() has keys A, B, C, D in row-major order."""
        fig, panels = yp.figure7(2, 2)
        try:
            assert list(panels.keys()) == ["A", "B", "C", "D"]
        finally:
            plt.close(fig)

    def test_panels_are_axes(self):
        """Each panel value is a matplotlib Axes object."""
        fig, panels = yp.figure7(2, 2)
        try:
            for ax in panels.values():
                assert isinstance(ax, matplotlib.axes.Axes)
        finally:
            plt.close(fig)

    def test_cell_width_formula(self):
        """Panel widths match (7 - left - right - (cols-1)*hspace) / cols."""
        fig, panels = yp.figure7(1, 3, margins=_M, gutters=_G)
        try:
            expected_cw = (7.0 - _M[0] - _M[1] - 2 * _G[0]) / 3
            for ax in panels.values():
                left, _, right, _ = _inches_bbox(ax, fig)
                assert abs((right - left) - expected_cw) < 1e-6, (
                    f"Cell width {right - left:.6f}, expected {expected_cw:.6f}"
                )
        finally:
            plt.close(fig)

    def test_no_overlap(self):
        """No pair of panels has overlapping inch-space bounding boxes."""
        fig, panels = yp.figure7(2, 2)
        try:
            axs = list(panels.values())
            for i in range(len(axs)):
                for j in range(i + 1, len(axs)):
                    l1, b1, r1, t1 = _inches_bbox(axs[i], fig)
                    l2, b2, r2, t2 = _inches_bbox(axs[j], fig)
                    no_overlap = r1 <= l2 or r2 <= l1 or t1 <= b2 or t2 <= b1
                    assert no_overlap, (
                        f"Panels {i} and {j} overlap: "
                        f"[{l1:.3f},{r1:.3f}]×[{b1:.3f},{t1:.3f}] vs "
                        f"[{l2:.3f},{r2:.3f}]×[{b2:.3f},{t2:.3f}]"
                    )
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# figure() general (non-7-inch)
# ---------------------------------------------------------------------------


class TestFigureGeneral:
    """figure() works with arbitrary widths."""

    def test_custom_width(self):
        """figure(6.0) returns a 6.0-inch-wide figure."""
        fig, panels = yp.figure(6.0, 1, 1)
        try:
            assert fig.get_size_inches()[0] == 6.0
        finally:
            plt.close(fig)

    def test_single_panel_named_A(self):
        """figure(6.0, 1, 1) returns panels with key 'A'."""
        fig, panels = yp.figure(6.0, 1, 1)
        try:
            assert list(panels.keys()) == ["A"]
        finally:
            plt.close(fig)

    def test_wrong_names_count_raises(self):
        """Providing one name for a 1×2 grid raises ValueError."""
        with pytest.raises(ValueError):
            yp.figure7(1, 2, names=["x"])

    def test_custom_names_used(self):
        """Custom names are returned as panel keys in row-major order."""
        fig, panels = yp.figure7(1, 2, names=["left", "right"])
        try:
            assert list(panels.keys()) == ["left", "right"]
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# Variable row heights
# ---------------------------------------------------------------------------


class TestVariableRowHeights:
    """row_heights=[h0, h1] produces correctly sized rows and figure height."""

    def test_figure_height_formula(self):
        """fig_height == top_m + sum(row_heights) + (rows-1)*vspace + bottom_m."""
        fig, panels = yp.figure7(2, 1, row_heights=[1.0, 2.0], gutters=_G, margins=_M)
        try:
            _, fh = fig.get_size_inches()
            expected_h = _M[2] + 1.0 + 2.0 + _G[1] + _M[3]
            assert abs(fh - expected_h) < 1e-6, (
                f"Figure height {fh:.6f}, expected {expected_h:.6f}"
            )
        finally:
            plt.close(fig)

    def test_row_a_height(self):
        """Top-row panel (A) has height 1.0 inch."""
        fig, panels = yp.figure7(2, 1, row_heights=[1.0, 2.0], gutters=_G, margins=_M)
        try:
            _, b, _, t = _inches_bbox(panels["A"], fig)
            assert abs((t - b) - 1.0) < 1e-6, (
                f"Panel A height {t - b:.6f}, expected 1.0"
            )
        finally:
            plt.close(fig)

    def test_row_b_height(self):
        """Bottom-row panel (B) has height 2.0 inches."""
        fig, panels = yp.figure7(2, 1, row_heights=[1.0, 2.0], gutters=_G, margins=_M)
        try:
            _, b, _, t = _inches_bbox(panels["B"], fig)
            assert abs((t - b) - 2.0) < 1e-6, (
                f"Panel B height {t - b:.6f}, expected 2.0"
            )
        finally:
            plt.close(fig)

    def test_a_is_above_b(self):
        """Panel A (top row) is entirely above panel B (bottom row)."""
        fig, panels = yp.figure7(2, 1, row_heights=[1.0, 2.0], gutters=_G, margins=_M)
        try:
            _, bottom_a, _, _ = _inches_bbox(panels["A"], fig)
            _, _, _, top_b = _inches_bbox(panels["B"], fig)
            assert bottom_a > top_b, (
                f"Panel A bottom {bottom_a:.4f} should be above panel B top {top_b:.4f}"
            )
        finally:
            plt.close(fig)

    def test_wrong_row_heights_len_raises(self):
        """row_heights with wrong length raises ValueError."""
        with pytest.raises(ValueError):
            yp.figure7(2, 1, row_heights=[1.0])


# ---------------------------------------------------------------------------
# Edge-case guards (items 1 and 2 from coordinator review)
# ---------------------------------------------------------------------------


class TestNamingGuards:
    """_resolve_names never silently returns a dict shorter than rows*cols."""

    def test_default_names_over_26_raises(self):
        """Default names for >26 panels raises ValueError (wrapping would collapse dict)."""
        with pytest.raises(ValueError, match="26"):
            yp.figure(
                100.0, 1, 27, gutters=(0.0, 0.0), margins=(0.0, 0.0, 0.0, 0.0)
            )

    def test_default_names_exactly_26_works(self):
        """26 panels with default names A–Z succeeds without wrapping."""
        fig, panels = yp.figure(
            100.0, 1, 26, gutters=(0.0, 0.0), margins=(0.0, 0.0, 0.0, 0.0)
        )
        try:
            assert len(panels) == 26
            assert list(panels.keys())[0] == "A"
            assert list(panels.keys())[-1] == "Z"
        finally:
            plt.close(fig)

    def test_duplicate_user_names_raises(self):
        """User-supplied duplicate names raise ValueError mentioning 'duplicate'."""
        with pytest.raises(ValueError, match="duplicate"):
            yp.figure7(1, 2, names=["X", "X"])

    def test_unique_user_names_accepted(self):
        """Unique user-supplied names of any string are accepted."""
        fig, panels = yp.figure7(1, 2, names=["left", "right"])
        try:
            assert list(panels.keys()) == ["left", "right"]
            assert len(panels) == 2
        finally:
            plt.close(fig)


class TestNegativeCellWidthGuard:
    """_cell_dims raises a clear error before margins+gutters exceed figure width."""

    def test_too_many_columns_raises_clear_error(self):
        """Too many cols for the figure width raises ValueError, not a cryptic mpl error."""
        with pytest.raises(ValueError, match="too small"):
            # 14 cols with DEFAULT_GUTTERS on a 7" figure → negative cell_w
            yp.figure7(1, 14)
