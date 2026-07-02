"""Tests for the unified style engine refactor (Phase 1, Task 2).

Pins that:
- apply_style and finish share a single _enforce_chrome code path.
- Per-call overrides (e.g. axis_linewidth=2.0) are preserved through
  the dataclasses.replace local_cfg.
- finish NEVER sets axis-label fontsizes, labelpads, or title fontsize.
- apply_style PRESERVES tick-label fonts in preserve_font_families;
  finish OVERWRITES them unconditionally (the intentional divergence).
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from yplot2.config import get_config
from yplot2.style import _resolve_font_family, apply_style, finish


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _make_ax_with_ticks():
    """Return (fig, ax) with one x-tick labelled 'test'."""
    fig, ax = plt.subplots()
    ax.set_xticks([0.5])
    ax.set_xticklabels(["test"])
    return fig, ax


# ---------------------------------------------------------------------------
# Task 1: single path — finish produces correct chrome
# ---------------------------------------------------------------------------


class TestSinglePath:
    """After refactor finish(ax) still produces correct chrome values."""

    def test_spine_linewidth(self):
        """finish() sets all spine linewidths to cfg.axis_linewidth."""
        cfg = get_config()
        fig, ax = plt.subplots()
        try:
            finish(ax)
            for spine in ax.spines.values():
                assert abs(spine.get_linewidth() - cfg.axis_linewidth) < 1e-6
        finally:
            plt.close(fig)

    def test_tick_fontsize(self):
        """finish() sets x tick-label fontsize to cfg.x_axis_tick_fontsize."""
        cfg = get_config()
        fig, ax = _make_ax_with_ticks()
        try:
            finish(ax)
            for label in ax.get_xticklabels():
                assert abs(label.get_fontsize() - cfg.x_axis_tick_fontsize) < 1e-6
        finally:
            plt.close(fig)

    def test_tick_fontname(self):
        """finish() sets x tick-label fontname to the resolved house family."""
        fig, ax = _make_ax_with_ticks()
        try:
            finish(ax)
            expected = _resolve_font_family(get_config().font_family)
            for label in ax.get_xticklabels():
                assert label.get_fontname() == expected
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# Task 2: idempotency
# ---------------------------------------------------------------------------


class TestIdempotency:
    """Calling finish(ax) twice yields identical artist properties."""

    def test_double_finish_idempotent(self):
        """Spine lw, tick fontsize, and tick fontname are stable on second finish."""
        fig, ax = _make_ax_with_ticks()
        try:
            finish(ax)
            lw_1 = [s.get_linewidth() for s in ax.spines.values()]
            fs_1 = [lb.get_fontsize() for lb in ax.get_xticklabels()]
            fn_1 = [lb.get_fontname() for lb in ax.get_xticklabels()]

            finish(ax)
            lw_2 = [s.get_linewidth() for s in ax.spines.values()]
            fs_2 = [lb.get_fontsize() for lb in ax.get_xticklabels()]
            fn_2 = [lb.get_fontname() for lb in ax.get_xticklabels()]

            assert lw_1 == lw_2, "Spine lw changed on second finish"
            assert fs_1 == fs_2, "Tick fontsize changed on second finish"
            assert fn_1 == fn_2, "Tick fontname changed on second finish"
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# Task 3: apply_style overrides are preserved (BLOCKER fix)
# ---------------------------------------------------------------------------


class TestApplyStyleOverrides:
    """Per-call overrides thread through the dataclasses.replace local_cfg."""

    def test_fontsize_override(self):
        """apply_style(x_axis_label_fontsize=11) → label fontsize == 11."""
        fig, ax = plt.subplots()
        try:
            apply_style(ax, x_axis_label_fontsize=11)
            assert abs(ax.xaxis.label.get_fontsize() - 11) < 1e-6
        finally:
            plt.close(fig)

    def test_y_fontsize_independent(self):
        """Overriding x fontsize does not affect y fontsize."""
        cfg = get_config()
        fig, ax = plt.subplots()
        try:
            apply_style(ax, x_axis_label_fontsize=11)
            assert abs(ax.yaxis.label.get_fontsize() - cfg.y_axis_label_fontsize) < 1e-6
        finally:
            plt.close(fig)

    def test_linewidth_override(self):
        """apply_style(axis_linewidth=2.0) → all spine lw == 2.0."""
        fig, ax = plt.subplots()
        try:
            apply_style(ax, axis_linewidth=2.0)
            for spine in ax.spines.values():
                assert abs(spine.get_linewidth() - 2.0) < 1e-6
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# Task 4: finish does NOT set labelpad (set_label_pads=False divergence)
# ---------------------------------------------------------------------------


class TestLabelpadDivergence:
    """finish must not touch xaxis.labelpad — proves set_label_pads=False routes right."""

    def test_finish_preserves_labelpad(self):
        """An explicit labelpad survives a finish() call unchanged."""
        fig, ax = plt.subplots()
        ax.xaxis.labelpad = 42.0
        try:
            finish(ax)
            assert abs(ax.xaxis.labelpad - 42.0) < 1e-6
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# Task 5: tick-preserve divergence (BLOCKER-1 fix)
# ---------------------------------------------------------------------------


class TestTickPreserveDivergence:
    """Pin the intentional apply_style vs finish divergence on tick-label fonts."""

    def test_finish_overwrites_preserved_font_on_ticks(self):
        """finish() overwrites 'Arial Unicode MS' tick labels unconditionally."""
        fig, ax = _make_ax_with_ticks()
        for label in ax.get_xticklabels():
            label.set_fontname("Arial Unicode MS")
        try:
            finish(ax)
            house = _resolve_font_family(get_config().font_family)
            for label in ax.get_xticklabels():
                assert label.get_fontname() == house, (
                    f"finish should overwrite tick font, got {label.get_fontname()!r}"
                )
        finally:
            plt.close(fig)

    def test_apply_style_preserves_font_on_ticks(self):
        """apply_style() PRESERVES 'Arial Unicode MS' when it is in preserve_fonts."""
        fig, ax = _make_ax_with_ticks()
        for label in ax.get_xticklabels():
            label.set_fontname("Arial Unicode MS")
        try:
            apply_style(ax, preserve_font_families=("Arial Unicode MS",))
            for label in ax.get_xticklabels():
                assert label.get_fontname() == "Arial Unicode MS", (
                    f"apply_style should preserve tick font, got {label.get_fontname()!r}"
                )
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# Task 6: finish does NOT set title fontsize (CONCERN-2 fix)
# ---------------------------------------------------------------------------


class TestFinishNoTitleFontsize:
    """finish() must not alter a title fontsize set explicitly by the caller."""

    def test_finish_preserves_title_fontsize(self):
        """A title fontsize of 20 survives finish() unchanged."""
        fig, ax = plt.subplots()
        ax.set_title("Test", fontsize=20.0)
        try:
            finish(ax)
            assert abs(ax.title.get_fontsize() - 20.0) < 1e-6, (
                f"finish() changed title fontsize to {ax.title.get_fontsize()}"
            )
        finally:
            plt.close(fig)
