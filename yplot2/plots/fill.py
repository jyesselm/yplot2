"""Fill plot utilities."""

from typing import Optional
from matplotlib.axes import Axes

from ..config import get_config


def fill_between(
    ax: Axes,
    x,
    y1,
    y2=0,
    alpha: float = 0.3,
    linewidth: Optional[float] = None,
    **kwargs,
):
    """
    Filled region plot using global config defaults.

    Args:
        ax: Axes object
        x: X coordinates
        y1: Upper bound
        y2: Lower bound (default: 0)
        alpha: Fill transparency (default: 0.3)
        linewidth: Edge line width
        **kwargs: Additional args to ax.fill_between()

    Returns:
        PolyCollection
    """
    cfg = get_config()

    if linewidth is None:
        linewidth = 0  # Usually no edge for fill

    return ax.fill_between(x, y1, y2, alpha=alpha, linewidth=linewidth, **kwargs)
