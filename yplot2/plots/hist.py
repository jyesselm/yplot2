"""Histogram plot utilities."""

from typing import Optional, Union, List
from matplotlib.axes import Axes

from ..config import get_config


def hist(
    ax: Axes,
    x,
    bins: Union[int, str, List] = 'auto',
    edgecolor: Optional[str] = 'white',
    linewidth: Optional[float] = None,
    **kwargs,
):
    """
    Histogram using global config defaults.

    Args:
        ax: Axes object
        x: Data
        bins: Number of bins or bin edges
        edgecolor: Edge color (default: 'white')
        linewidth: Edge line width
        **kwargs: Additional args to ax.hist()

    Returns:
        Tuple of (n, bins, patches)
    """
    cfg = get_config()

    if linewidth is None:
        linewidth = cfg.axis_linewidth * 0.5

    return ax.hist(x, bins=bins, edgecolor=edgecolor, linewidth=linewidth, **kwargs)
