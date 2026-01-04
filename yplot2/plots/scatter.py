"""Scatter plot utilities."""

from typing import Optional
from matplotlib.axes import Axes

from ..config import get_config


def scatter(
    ax: Axes,
    x,
    y,
    s: Optional[float] = None,
    c=None,
    marker: Optional[str] = None,
    edgecolors: Optional[str] = None,
    linewidths: Optional[float] = None,
    **kwargs,
):
    """
    Scatter plot using global config defaults.

    Args:
        ax: Axes object
        x, y: Data coordinates
        s: Marker size (default: config.plot_markersize ** 2)
        c: Color
        marker: Marker style
        edgecolors: Edge color
        linewidths: Edge line width
        **kwargs: Additional args to ax.scatter()

    Returns:
        PathCollection
    """
    cfg = get_config()

    if s is None:
        s = cfg.plot_markersize ** 2  # scatter uses area
    if linewidths is None:
        linewidths = cfg.axis_linewidth * 0.5

    return ax.scatter(x, y, s=s, c=c, marker=marker,
                      edgecolors=edgecolors, linewidths=linewidths, **kwargs)
