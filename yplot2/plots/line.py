"""Line plot utilities."""

from typing import Optional
from matplotlib.axes import Axes

from ..config import get_config


def line(
    ax: Axes,
    x,
    y,
    linewidth: Optional[float] = None,
    markersize: Optional[float] = None,
    **kwargs,
):
    """
    Line plot using global config defaults.

    Args:
        ax: Axes object
        x, y: Data coordinates
        linewidth: Line width (default: config.plot_linewidth)
        markersize: Marker size (default: config.plot_markersize)
        **kwargs: Additional args to ax.plot()

    Returns:
        List of Line2D
    """
    cfg = get_config()

    if linewidth is None:
        linewidth = cfg.plot_linewidth
    if markersize is None:
        markersize = cfg.plot_markersize

    return ax.plot(x, y, linewidth=linewidth, markersize=markersize, **kwargs)
