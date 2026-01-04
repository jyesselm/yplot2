"""Reference line utilities (hline, vline)."""

from typing import Optional
from matplotlib.axes import Axes

from ..config import get_config


def hline(
    ax: Axes,
    y: float,
    linewidth: Optional[float] = None,
    linestyle: str = '--',
    color: str = 'gray',
    **kwargs,
):
    """
    Horizontal line using global config defaults.

    Args:
        ax: Axes object
        y: Y position
        linewidth: Line width
        linestyle: Line style (default: '--')
        color: Line color (default: 'gray')
        **kwargs: Additional args to ax.axhline()

    Returns:
        Line2D
    """
    cfg = get_config()

    if linewidth is None:
        linewidth = cfg.plot_linewidth

    return ax.axhline(y, linewidth=linewidth, linestyle=linestyle,
                      color=color, **kwargs)


def vline(
    ax: Axes,
    x: float,
    linewidth: Optional[float] = None,
    linestyle: str = '--',
    color: str = 'gray',
    **kwargs,
):
    """
    Vertical line using global config defaults.

    Args:
        ax: Axes object
        x: X position
        linewidth: Line width
        linestyle: Line style (default: '--')
        color: Line color (default: 'gray')
        **kwargs: Additional args to ax.axvline()

    Returns:
        Line2D
    """
    cfg = get_config()

    if linewidth is None:
        linewidth = cfg.plot_linewidth

    return ax.axvline(x, linewidth=linewidth, linestyle=linestyle,
                      color=color, **kwargs)
