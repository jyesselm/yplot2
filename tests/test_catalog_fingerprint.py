"""
Tests for yplot2/catalog_build/fingerprint.py — style-fingerprint gate.

Verifies that:
- Real styled demos pass the gate (violations empty)
- A deliberately unstyled demo is flagged
- Thumbnail failure is non-blocking
- Demo crash is blocking
- Missing seaborn is a skip, not a fail
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest
from unittest.mock import patch

from yplot2.catalog_build.fingerprint import (
    FingerprintResult,
    StyleViolation,
    _check_label_list,
    _is_colorbar_axes,
    check_house_style,
    fingerprint_capsule,
    render_thumbnail,
)
from yplot2.catalog_build.collect import collect_records


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_unstyled_fig() -> plt.Figure:
    """Return a bare plt.subplots() figure with default matplotlib styling."""
    fig, ax = plt.subplots(figsize=(3, 2))
    ax.plot([0, 1], [1, 0])
    return fig


# ---------------------------------------------------------------------------
# check_house_style
# ---------------------------------------------------------------------------


class TestCheckHouseStyle:
    """check_house_style detects house-style violations on rendered figures."""

    def test_unstyled_demo_flagged(self):
        """A bare plt.subplots() figure is flagged for spine_linewidth and/or font."""
        fig = _make_unstyled_fig()
        try:
            violations = check_house_style(fig)
            assert len(violations) > 0, "Expected violations on an unstyled figure"
            prop_names = {v.prop for v in violations}
            # Default spine lw is 0.8 ≠ 0.75, and font is DejaVu ≠ Arimo
            assert "spine_linewidth" in prop_names or "tick_font_family" in prop_names
        finally:
            plt.close(fig)

    def test_styled_demo_passes(self):
        """A figure styled via finish() returns no violations."""
        pytest.importorskip("seaborn")
        from yplot2.plots.statistical.violin import demo_violin

        fig = demo_violin()
        try:
            violations = check_house_style(fig)
            assert violations == [], f"Unexpected violations: {violations}"
        finally:
            plt.close(fig)

    def test_returns_list(self):
        """check_house_style always returns a list."""
        fig = _make_unstyled_fig()
        try:
            result = check_house_style(fig)
            assert isinstance(result, list)
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# _check_label_list
# ---------------------------------------------------------------------------


class TestCheckLabelList:
    """_check_label_list uses exact font match and checks font size."""

    def _make_label(self, fontname: str, fontsize: float) -> object:
        """Return a mock Text-like object with get_fontname/get_fontsize."""
        from unittest.mock import MagicMock

        label = MagicMock()
        label.get_fontname.return_value = fontname
        label.get_fontsize.return_value = fontsize
        return label

    def test_exact_match_passes(self):
        """When fontname matches exactly, no violation is raised."""
        label = self._make_label("Arimo", 9.0)
        violations = _check_label_list([label], 0, "Arimo", 9.0, "x_tick_fontsize")
        assert violations == []

    def test_substring_not_sufficient(self):
        """A font name that contains the expected name is an exact-match violation."""
        # "Arimo Bold" contains "Arimo" but is not an exact match
        label = self._make_label("Arimo Bold", 9.0)
        violations = _check_label_list([label], 0, "Arimo", 9.0, "x_tick_fontsize")
        font_violations = [v for v in violations if v.prop == "tick_font_family"]
        assert len(font_violations) == 1
        assert font_violations[0].actual == "Arimo Bold"
        assert font_violations[0].expected == "Arimo"

    def test_wrong_fontname_flagged(self):
        """A mismatched fontname produces a tick_font_family violation."""
        label = self._make_label("DejaVu Sans", 9.0)
        violations = _check_label_list([label], 0, "Arimo", 9.0, "x_tick_fontsize")
        assert any(v.prop == "tick_font_family" for v in violations)

    def test_wrong_fontsize_flagged(self):
        """A mismatched fontsize produces a size violation with the given prop name."""
        label = self._make_label("Arimo", 12.0)
        violations = _check_label_list([label], 0, "Arimo", 9.0, "y_tick_fontsize")
        assert any(v.prop == "y_tick_fontsize" for v in violations)

    def test_empty_labels_returns_empty(self):
        """Empty label list returns no violations."""
        assert _check_label_list([], 0, "Arimo", 9.0, "x_tick_fontsize") == []

    def test_axes_index_propagated(self):
        """Violation carries the axes_index passed in."""
        label = self._make_label("DejaVu", 9.0)
        violations = _check_label_list([label], 3, "Arimo", 9.0, "x_tick_fontsize")
        assert all(v.axes_index == 3 for v in violations)


# ---------------------------------------------------------------------------
# _is_colorbar_axes
# ---------------------------------------------------------------------------


class TestIsColorbarAxes:
    """_is_colorbar_axes detects colorbar axes by spine key."""

    def test_plain_axes_is_not_colorbar(self):
        """A standard subplots axes is not detected as a colorbar axes."""
        fig, ax = plt.subplots()
        try:
            assert _is_colorbar_axes(ax) is False
        finally:
            plt.close(fig)

    def test_colorbar_axes_detected(self):
        """A colorbar axes (from fig.colorbar) is detected correctly."""
        import numpy as np

        fig, ax = plt.subplots()
        im = ax.imshow(np.eye(3), cmap="magma")
        cbar = fig.colorbar(im, ax=ax)
        try:
            assert _is_colorbar_axes(cbar.ax) is True
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# render_thumbnail
# ---------------------------------------------------------------------------


class TestRenderThumbnail:
    """render_thumbnail is non-blocking and returns bool."""

    def test_success_returns_true(self, tmp_path):
        """render_thumbnail returns True when savefig succeeds."""
        fig = _make_unstyled_fig()
        path = str(tmp_path / "thumb.png")
        result = render_thumbnail(fig, path)
        plt.close(fig)
        assert result is True

    def test_failure_returns_false(self):
        """render_thumbnail returns False when savefig raises."""
        fig = _make_unstyled_fig()
        with patch.object(fig, "savefig", side_effect=RuntimeError("disk full")):
            result = render_thumbnail(fig, "/nowhere/thumb.png")
        plt.close(fig)
        assert result is False

    def test_never_raises(self):
        """render_thumbnail absorbs exceptions and never propagates them."""
        fig = _make_unstyled_fig()
        with patch.object(fig, "savefig", side_effect=OSError("permission denied")):
            try:
                render_thumbnail(fig, "/nowhere/thumb.png")
            except Exception as exc:
                pytest.fail(f"render_thumbnail raised: {exc}")
        plt.close(fig)


# ---------------------------------------------------------------------------
# FingerprintResult.blocking_failed
# ---------------------------------------------------------------------------


class TestBlockingFailed:
    """FingerprintResult.blocking_failed property."""

    def test_no_violations_no_error_not_blocking(self):
        """A clean result is not blocking."""
        res = FingerprintResult(
            name="test", violations=(), thumbnail_ok=True, error="", skipped=False
        )
        assert res.blocking_failed is False

    def test_violations_are_blocking(self):
        """A result with violations is blocking."""
        v = StyleViolation(
            axes_index=0, prop="spine_linewidth", expected="0.75", actual="0.8"
        )
        res = FingerprintResult(
            name="test", violations=(v,), thumbnail_ok=False, error="", skipped=False
        )
        assert res.blocking_failed is True

    def test_error_is_blocking(self):
        """A result with an error string is blocking."""
        res = FingerprintResult(
            name="test", violations=(), thumbnail_ok=False, error="crash", skipped=False
        )
        assert res.blocking_failed is True

    def test_skipped_is_not_blocking(self):
        """A skipped result is never blocking, even with errors."""
        res = FingerprintResult(
            name="test",
            violations=(),
            thumbnail_ok=False,
            error="seaborn missing",
            skipped=True,
        )
        assert res.blocking_failed is False

    def test_failed_thumbnail_alone_not_blocking(self):
        """A failed thumbnail with no violations is not blocking."""
        res = FingerprintResult(
            name="test", violations=(), thumbnail_ok=False, error="", skipped=False
        )
        assert res.blocking_failed is False


# ---------------------------------------------------------------------------
# fingerprint_capsule
# ---------------------------------------------------------------------------


class TestFingerprintCapsule:
    """fingerprint_capsule integration tests."""

    def test_styled_capsules_pass(self):
        """All five real statistical capsules produce no violations."""
        pytest.importorskip("seaborn")
        records, _ = collect_records()
        stat_records = [r for r in records if r.name in {"violin", "box", "kde"}]
        assert stat_records, "Expected at least violin/box/kde records"
        for rec in stat_records:
            result = fingerprint_capsule(rec)
            assert result.violations == (), (
                f"{rec.name}: unexpected violations: {result.violations}"
            )
            assert result.error == "", f"{rec.name}: demo raised: {result.error}"

    def test_heatmap_hexbin_pass(self):
        """heatmap2d and hexbin capsules pass (colorbar axes handled correctly)."""
        records, _ = collect_records()
        cb_records = [r for r in records if r.name in {"heatmap2d", "hexbin"}]
        for rec in cb_records:
            result = fingerprint_capsule(rec)
            assert result.violations == (), (
                f"{rec.name}: unexpected violations: {result.violations}"
            )
            assert result.error == "", f"{rec.name}: demo raised: {result.error}"

    def test_demo_crash_is_blocking(self):
        """A demo that raises yields blocking_failed=True."""
        from yplot2.catalog_build.records import CapsuleRecord

        rec = CapsuleRecord(
            name="crashing",
            category="test",
            tags=(),
            data_shape="xy",
            kind="panel",
            signature="(ax)",
            inputs=(),
            summary="",
            source_path="",
            import_path="yplot2.catalog_build.fingerprint.crashing",
            has_demo=True,
        )
        # The import_path module doesn't exist → ImportError → blocking error
        result = fingerprint_capsule(rec)
        assert result.blocking_failed is True

    def test_missing_seaborn_is_skip_not_fail(self):
        """An ImportError mentioning seaborn yields skipped=True, not blocking."""
        from yplot2.catalog_build.records import CapsuleRecord

        rec = CapsuleRecord(
            name="fake",
            category="statistical",
            tags=("seaborn",),
            data_shape="long-df",
            kind="panel",
            signature="(ax)",
            inputs=(),
            summary="",
            source_path="",
            import_path="yplot2.plots.statistical.violin.violin",
            has_demo=True,
        )

        def demo_raises_seaborn():
            raise ImportError("No module named 'seaborn'")

        import importlib

        real_import = importlib.import_module

        def fake_import(name, *args, **kwargs):
            m = real_import(name, *args, **kwargs)
            m.demo_fake = demo_raises_seaborn
            return m

        with patch(
            "yplot2.catalog_build.fingerprint.importlib.import_module",
            side_effect=fake_import,
        ):
            result = fingerprint_capsule(rec)

        assert result.skipped is True
        assert result.blocking_failed is False
