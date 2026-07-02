"""
Style-fingerprint gate for yplot2 @catalog capsules.

Runs each capsule's ``demo_<name>()`` and asserts house chrome using
artist-property checks only (never a pixel hash). BLOCKING: a style
violation fails the catalog build. Missing seaborn is a SKIP (non-blocking).
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.figure import Figure

from .records import CapsuleRecord


@dataclass(frozen=True)
class StyleViolation:
    """One artist-property mismatch found on a demo figure."""

    axes_index: int
    prop: str
    expected: str
    actual: str


@dataclass(frozen=True)
class FingerprintResult:
    """Summary of a single capsule fingerprint run."""

    name: str
    violations: tuple[StyleViolation, ...]
    thumbnail_ok: bool
    error: str
    skipped: bool

    @property
    def blocking_failed(self) -> bool:
        """True when the result is a hard failure (error or violations, not skipped)."""
        return (bool(self.error) or bool(self.violations)) and not self.skipped


def _is_colorbar_axes(ax: object) -> bool:
    """Return True when *ax* is a colorbar axes (has an 'outline' spine).

    Args:
        ax: Axes-like object to test.

    Returns:
        True if the axes was created by matplotlib's colorbar machinery.
    """
    spines = getattr(ax, "spines", {})
    return "outline" in spines


def _check_spine_lw(
    ax: object,
    ax_idx: int,
    expected_lw: float,
) -> list[StyleViolation]:
    """Check visible spine linewidths on *ax* against *expected_lw*.

    Args:
        ax: The axes to inspect.
        ax_idx: Index of this axes in fig.axes (for violation reporting).
        expected_lw: House linewidth from cfg.axis_linewidth.

    Returns:
        List of StyleViolation (may be empty).
    """
    violations = []
    spines = getattr(ax, "spines", {})
    for spine in spines.values():
        if not spine.get_visible():
            continue
        lw = spine.get_linewidth()
        if abs(lw - expected_lw) > 1e-6:
            violations.append(
                StyleViolation(
                    axes_index=ax_idx,
                    prop="spine_linewidth",
                    expected=str(expected_lw),
                    actual=str(lw),
                )
            )
    return violations


def _check_label_list(
    labels: list,
    ax_idx: int,
    expected_font: str,
    expected_size: float,
    size_prop: str,
) -> list[StyleViolation]:
    """Check font family and size on a list of tick-label Text objects.

    Uses exact match on font name (not substring) so that a font whose name
    merely contains the expected name cannot false-pass.

    Args:
        labels: Tick label Text objects to check.
        ax_idx: Axes index for violation reporting.
        expected_font: Expected font family name (exact match).
        expected_size: Expected font size in points.
        size_prop: Violation prop name for size mismatch.

    Returns:
        List of StyleViolation (may be empty).
    """
    violations = []
    for label in labels:
        fontname = label.get_fontname()
        if fontname != expected_font:
            violations.append(
                StyleViolation(
                    axes_index=ax_idx,
                    prop="tick_font_family",
                    expected=expected_font,
                    actual=fontname,
                )
            )
        size = label.get_fontsize()
        if abs(size - expected_size) > 1e-6:
            violations.append(
                StyleViolation(
                    axes_index=ax_idx,
                    prop=size_prop,
                    expected=str(expected_size),
                    actual=str(size),
                )
            )
    return violations


def _check_tick_labels(
    ax: object,
    ax_idx: int,
    resolved_font: str,
    x_fontsize: float,
    y_fontsize: float,
) -> list[StyleViolation]:
    """Check tick-label font family and size on *ax*.

    Args:
        ax: The axes to inspect.
        ax_idx: Index of this axes in fig.axes.
        resolved_font: Expected font family (resolved via _resolve_font_family).
        x_fontsize: Expected x-axis tick label font size.
        y_fontsize: Expected y-axis tick label font size.

    Returns:
        List of StyleViolation (may be empty).
    """
    x_labels = ax.get_xticklabels()  # type: ignore[attr-defined]
    y_labels = ax.get_yticklabels()  # type: ignore[attr-defined]
    return _check_label_list(
        x_labels, ax_idx, resolved_font, x_fontsize, "x_tick_fontsize"
    ) + _check_label_list(
        y_labels, ax_idx, resolved_font, y_fontsize, "y_tick_fontsize"
    )


def check_house_style(fig: "Figure") -> list[StyleViolation]:
    """Assert house chrome on every axes of a rendered demo figure.

    Artist-property checks ONLY (never a pixel hash): each visible spine's
    linewidth == cfg.axis_linewidth; every tick label's font family == the
    resolved house font (Arimo, exact match); tick-label fontsize == cfg
    tick fontsize. Colorbar axes are spine-checked but tick-font/size is
    skipped (see plan Q7 / fingerprint correctness).

    Returns an empty list when the figure is house-styled.

    Args:
        fig: A rendered matplotlib Figure to inspect.

    Returns:
        List of StyleViolation; empty means the figure passed the gate.
    """
    from yplot2.config import get_config
    from yplot2.style import _resolve_font_family

    cfg = get_config()
    expected_lw = cfg.axis_linewidth
    resolved_font = _resolve_font_family(cfg.font_family)
    x_fontsize = cfg.x_axis_tick_fontsize
    y_fontsize = cfg.y_axis_tick_fontsize

    violations: list[StyleViolation] = []
    for ax_idx, ax in enumerate(fig.axes):
        violations.extend(_check_spine_lw(ax, ax_idx, expected_lw))
        if _is_colorbar_axes(ax):
            continue
        violations.extend(
            _check_tick_labels(ax, ax_idx, resolved_font, x_fontsize, y_fontsize)
        )
    return violations


def render_thumbnail(fig: "Figure", path: str) -> bool:
    """Best-effort thumbnail PNG. Returns True on success, False on any failure.

    Never raises — a failed thumbnail is cosmetic, not a gate.

    Args:
        fig: Figure to save as a thumbnail.
        path: Output path for the thumbnail PNG.

    Returns:
        True if the file was written, False on any error.
    """
    try:
        fig.savefig(path, dpi=72)
        return True
    except Exception:
        return False


def _run_demo(rec: CapsuleRecord) -> tuple[Any, str, bool]:
    """Import rec's module, call demo_<name>(), and return (fig, error, skipped).

    Args:
        rec: The capsule whose demo to run.

    Returns:
        Tuple of (fig_or_None, error_string, skipped_flag).
        skipped=True means seaborn was absent (not a hard failure).
    """
    module_name, _ = rec.import_path.rsplit(".", 1)
    try:
        module = importlib.import_module(module_name)
        demo_fn = getattr(module, f"demo_{rec.name}")
        fig = demo_fn()
        return fig, "", False
    except ImportError as exc:
        if "seaborn" in str(exc).lower():
            return None, "", True
        return None, repr(exc), False
    except Exception as exc:
        return None, repr(exc), False


def fingerprint_capsule(
    rec: CapsuleRecord,
    *,
    thumb_path: str | None = None,
) -> FingerprintResult:
    """Import rec's module, run its demo, style-check it, and save a thumbnail.

    Returns a result carrying violations + thumbnail status.
    A demo that raises yields a result with a populated ``error`` (blocking).
    Missing seaborn yields ``skipped=True`` (non-blocking).

    Args:
        rec: The capsule record to fingerprint.
        thumb_path: Optional output path for the thumbnail PNG. When None,
            no thumbnail is attempted (thumbnail_ok=False in result).

    Returns:
        FingerprintResult summarising style violations, thumbnail, and errors.
    """
    import matplotlib

    matplotlib.use("Agg")

    fig, error, skipped = _run_demo(rec)

    if skipped or error or fig is None:
        return FingerprintResult(
            name=rec.name,
            violations=(),
            thumbnail_ok=False,
            error=error,
            skipped=skipped,
        )

    violations = tuple(check_house_style(fig))  # type: ignore[arg-type]
    thumbnail_ok = render_thumbnail(fig, thumb_path) if thumb_path else False

    try:
        import matplotlib.pyplot as plt

        plt.close(fig)  # type: ignore[arg-type]
    except Exception:
        pass

    return FingerprintResult(
        name=rec.name,
        violations=violations,
        thumbnail_ok=thumbnail_ok,
        error="",
        skipped=False,
    )
