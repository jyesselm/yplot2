"""Lollipop plot utilities.

This module provides functions for creating lollipop plots,
which display paired data points connected by vertical lines.
"""

from typing import Optional, Sequence

from matplotlib.axes import Axes

from ..config import get_config
from .basic import _merge_args


def lollipop(
    ax: Axes,
    x: Sequence,
    y1: Sequence,
    y2: Optional[Sequence] = None,
    line_args: Optional[dict] = None,
    marker_args: Optional[dict] = None,
) -> Axes:
    """
    Create a paired lollipop plot.

    Displays two sets of values at each x position connected by
    vertical lines.

    Args:
        ax: Matplotlib Axes to plot on.
        x: Categories or numeric positions for the lollipops.
        y1: First set of values.
        y2: Second set of values (required for paired plot).
        line_args: Dict of line styling options. Keys: color, linewidth,
            linestyle. Default color='gray'.
        marker_args: Dict of marker styling options. Keys: s (size), c (color),
            marker, alpha, edgecolors, etc. Passed to scatter().

    Returns:
        The matplotlib Axes containing the plot.

    Example:
        >>> lollipop(ax, x, y1, y2)
        >>> lollipop(ax, x, y1, y2, line_args={"color": "red", "linewidth": 2})
        >>> lollipop(ax, x, y1, y2, marker_args={"c": "blue", "s": 100})
    """
    cfg = get_config()

    if y2 is None:
        raise ValueError("y2 is required for paired lollipop plot")

    _line_args = _merge_args({
        "color": "gray",
        "linewidth": cfg.plot_linewidth,
    }, line_args)

    _marker_args = _merge_args({
        "s": cfg.plot_markersize ** 2,
        "zorder": 3,
    }, marker_args)

    # Draw connecting lines
    for xi, yi1, yi2 in zip(x, y1, y2):
        ax.vlines(
            xi, min(yi1, yi2), max(yi1, yi2),
            color=_line_args["color"],
            lw=_line_args["linewidth"],
        )

    # Draw markers
    ax.scatter(x, y1, **_marker_args)
    ax.scatter(x, y2, **_marker_args)

    ax.set_xticks(list(x))
    return ax
