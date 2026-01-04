"""Lollipop plot utilities.

This module provides functions for creating lollipop plots,
which display paired data points connected by vertical lines.
"""

from typing import Optional, Sequence

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from ..config import get_config


def lollipop(
    ax: Axes,
    x: Sequence,
    y1: Sequence,
    y2: Optional[Sequence] = None,
    line_color: Optional[str] = None,
    marker_size: Optional[float] = None,
    line_width: Optional[float] = None,
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
        line_color: Color of connecting lines (default: 'gray').
        marker_size: Size of scatter markers.
        line_width: Width of connecting lines.

    Returns:
        The matplotlib Axes containing the plot.

    Example:
        >>> x = [1, 2, 3, 4]
        >>> y1 = [0.1, 0.2, 0.3, 0.4]
        >>> y2 = [0.15, 0.25, 0.35, 0.45]
        >>> lollipop(ax, x, y1, y2)
    """
    cfg = get_config()

    if y2 is None:
        raise ValueError("y2 is required for paired lollipop plot")

    if line_color is None:
        line_color = 'gray'
    if marker_size is None:
        marker_size = cfg.plot_markersize ** 2  # scatter uses area
    if line_width is None:
        line_width = cfg.plot_linewidth

    # Draw connecting lines
    for xi, yi1, yi2 in zip(x, y1, y2):
        ax.vlines(xi, min(yi1, yi2), max(yi1, yi2), color=line_color, lw=line_width)

    # Draw markers
    ax.scatter(x, y1, s=marker_size, zorder=3)
    ax.scatter(x, y2, s=marker_size, zorder=3)

    ax.set_xticks(list(x))
    return ax
