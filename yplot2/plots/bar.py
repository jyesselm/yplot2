"""Bar plot utilities."""

from typing import Optional
from matplotlib.axes import Axes

from ..config import get_config


def bar(
    ax: Axes,
    x,
    height,
    width: float = 0.8,
    edgecolor: Optional[str] = None,
    linewidth: Optional[float] = None,
    **kwargs,
):
    """
    Bar plot using global config defaults.

    Args:
        ax: Axes object
        x: Bar positions
        height: Bar heights
        width: Bar width
        edgecolor: Edge color (default: None)
        linewidth: Edge line width (default: config.axis_linewidth)
        **kwargs: Additional args to ax.bar()

    Returns:
        BarContainer
    """
    cfg = get_config()

    if linewidth is None:
        linewidth = cfg.axis_linewidth

    return ax.bar(x, height, width=width, edgecolor=edgecolor,
                  linewidth=linewidth, **kwargs)


def barh(
    ax: Axes,
    y,
    width,
    height: float = 0.8,
    edgecolor: Optional[str] = None,
    linewidth: Optional[float] = None,
    **kwargs,
):
    """
    Horizontal bar plot using global config defaults.

    Args:
        ax: Axes object
        y: Bar positions
        width: Bar widths (the data values)
        height: Bar height
        edgecolor: Edge color
        linewidth: Edge line width (default: config.axis_linewidth)
        **kwargs: Additional args to ax.barh()

    Returns:
        BarContainer
    """
    cfg = get_config()

    if linewidth is None:
        linewidth = cfg.axis_linewidth

    return ax.barh(y, width, height=height, edgecolor=edgecolor,
                   linewidth=linewidth, **kwargs)
