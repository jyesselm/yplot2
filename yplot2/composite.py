"""Composite annotation helpers for image and plot panels.

annotate(), line_annotation(), and distance_label() place text and arrows on
axes in axes-fraction OR data coordinates — never pixels.  All offsets are
expressed in points (via the basic.text() anchor system) or in the native
coordinate space of the axes.
"""

from typing import Optional, Tuple, Union

from matplotlib.axes import Axes
from matplotlib.patches import FancyArrowPatch
from matplotlib.text import Text
from matplotlib.transforms import Transform

from .config import get_config
from .style import _resolve_font_family
from .plots.basic import text as _anchor_text

Coords2D = Tuple[float, float]


def _transform_for(ax: Axes, coords: str) -> Transform:
    """Return the matplotlib transform for the given coordinate system name.

    Args:
        ax: Target axes.
        coords: "axes" (fraction 0–1) or "data" (data coordinates).

    Returns:
        ax.transAxes or ax.transData.

    Raises:
        ValueError: If coords is not "axes" or "data".
    """
    if coords == "axes":
        return ax.transAxes
    if coords == "data":
        return ax.transData
    raise ValueError(f"coords must be 'axes' or 'data', got {coords!r}")


def annotate(
    ax: Axes,
    label: str,
    xy: Union[str, Coords2D] = "top left",
    *,
    coords: str = "axes",
    fontsize: Optional[float] = None,
    **kwargs,
) -> Text:
    """Place a text label on an image or plot panel.

    - ``coords="axes"`` + ``xy`` a named anchor string → delegates to
      ``basic.text()`` which uses the ``TEXT_POSITIONS`` point-offset system.
    - ``coords="axes"`` + ``xy`` a ``(fx, fy)`` tuple → places at axes fraction
      via ``basic.text(ax, label, pos=(fx, fy), ...)``.
    - ``coords="data"`` + ``xy`` a ``(x, y)`` tuple → places at data coordinates
      via ``ax.text(transform=ax.transData, ...)``.  No pixel offsets anywhere.

    Args:
        ax: Target axes.
        label: Text string to display.
        xy: Named anchor (e.g. "top left", "tr") or ``(x, y)`` tuple.
        coords: Coordinate system — "axes" (default) or "data".
        fontsize: Font size in points.  Defaults to config.text_fontsize.
        **kwargs: Extra keyword args forwarded to the underlying text call.

    Returns:
        The matplotlib Text object (in ax.texts).

    Raises:
        ValueError: If coords is unknown, or if coords="data" and xy is not a tuple.
    """
    cfg = get_config()
    fs = fontsize if fontsize is not None else cfg.text_fontsize
    if coords == "axes":
        return _anchor_text(ax, label, pos=xy, fontsize=fs, **kwargs)
    if coords == "data":
        if not isinstance(xy, tuple):
            raise ValueError(
                f"coords='data' requires xy to be a (x, y) tuple, got {xy!r}"
            )
        x, y = xy
        font_family = _resolve_font_family(cfg.font_family)
        return ax.text(
            x,
            y,
            label,
            transform=ax.transData,
            fontsize=fs,
            fontfamily=font_family,
            **kwargs,
        )
    raise ValueError(f"coords must be 'axes' or 'data', got {coords!r}")


def line_annotation(
    ax: Axes,
    xy0: Coords2D,
    xy1: Coords2D,
    *,
    coords: str = "axes",
    arrow: bool = False,
    label: Optional[str] = None,
    linewidth: Optional[float] = None,
    color: str = "black",
    **kwargs,
) -> FancyArrowPatch:
    """Draw a line or arrow between two points in axes-fraction or data coords.

    The patch is added to ``ax`` via ``ax.add_patch()``.  An optional centered
    label is placed at the segment midpoint — no manual pixel math.

    Args:
        ax: Target axes.
        xy0: Start point ``(x0, y0)`` in the chosen coordinate system.
        xy1: End point ``(x1, y1)``.
        coords: "axes" (default) or "data".
        arrow: When True, draw arrow-heads on both ends (``<->`` style).
            When False, draw a plain line segment.
        label: Optional text label placed at the segment midpoint.
        linewidth: Stroke width in points.  Defaults to cfg.axis_linewidth so
            the line matches house chrome.
        color: Line/arrow color (default "black").
        **kwargs: Extra keyword args forwarded to FancyArrowPatch.

    Returns:
        The FancyArrowPatch (already added to ax.patches).
    """
    cfg = get_config()
    lw = linewidth if linewidth is not None else cfg.axis_linewidth
    transform = _transform_for(ax, coords)
    arrowstyle = "<->" if arrow else "-"
    patch = FancyArrowPatch(
        posA=xy0,
        posB=xy1,
        arrowstyle=arrowstyle,
        linewidth=lw,
        color=color,
        transform=transform,
        **kwargs,
    )
    ax.add_patch(patch)
    if label is not None:
        mid_x = (xy0[0] + xy1[0]) / 2
        mid_y = (xy0[1] + xy1[1]) / 2
        _place_label(ax, label, (mid_x, mid_y), coords, cfg.text_fontsize)
    return patch


def _place_label(
    ax: Axes,
    label: str,
    pos: Coords2D,
    coords: str,
    fontsize: float,
) -> Text:
    """Place a text label at pos in the given coordinate system.

    Args:
        ax: Target axes.
        label: Text to display.
        pos: (x, y) position in the coordinate system given by coords.
        coords: "axes" or "data".
        fontsize: Font size in points.

    Returns:
        The matplotlib Text object.
    """
    if coords == "axes":
        return _anchor_text(ax, label, pos=pos, fontsize=fontsize)
    cfg = get_config()
    font_family = _resolve_font_family(cfg.font_family)
    return ax.text(
        pos[0],
        pos[1],
        label,
        transform=ax.transData,
        fontsize=fontsize,
        fontfamily=font_family,
        ha="center",
        va="center",
    )


def distance_label(
    ax: Axes,
    xy0: Coords2D,
    xy1: Coords2D,
    label: str,
    *,
    coords: str = "axes",
    **kwargs,
) -> FancyArrowPatch:
    """Draw a double-headed arrow with a distance label at the midpoint.

    Convenience wrapper for the common "N Å" distance overlay on structure
    image panels.  Delegates to ``line_annotation(..., arrow=True, label=label)``.

    Args:
        ax: Target axes.
        xy0: Start point.
        xy1: End point.
        label: Distance label text (e.g. "8 Å").
        coords: "axes" (default) or "data".
        **kwargs: Forwarded to line_annotation().

    Returns:
        The FancyArrowPatch (already added to ax.patches).
    """
    return line_annotation(
        ax,
        xy0,
        xy1,
        coords=coords,
        arrow=True,
        label=label,
        **kwargs,
    )
