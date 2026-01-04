"""Error bar plot utilities."""

from typing import Optional
from matplotlib.axes import Axes

from ..config import get_config


def errorbar(
    ax: Axes,
    x,
    y,
    yerr=None,
    xerr=None,
    fmt: str = 'o',
    linewidth: Optional[float] = None,
    markersize: Optional[float] = None,
    capsize: Optional[float] = None,
    capthick: Optional[float] = None,
    elinewidth: Optional[float] = None,
    **kwargs,
):
    """
    Error bar plot using global config defaults.

    Args:
        ax: Axes object
        x, y: Data coordinates
        yerr: Y error values
        xerr: X error values
        fmt: Format string (default: 'o')
        linewidth: Line width
        markersize: Marker size
        capsize: Error bar cap size
        capthick: Cap line thickness
        elinewidth: Error line width
        **kwargs: Additional args to ax.errorbar()

    Returns:
        ErrorbarContainer
    """
    cfg = get_config()

    if linewidth is None:
        linewidth = cfg.plot_linewidth
    if markersize is None:
        markersize = cfg.plot_markersize
    if capsize is None:
        capsize = cfg.plot_capsize
    if capthick is None:
        capthick = cfg.plot_capthick
    if elinewidth is None:
        elinewidth = cfg.axis_linewidth

    return ax.errorbar(x, y, yerr=yerr, xerr=xerr, fmt=fmt,
                       linewidth=linewidth, markersize=markersize,
                       capsize=capsize, capthick=capthick,
                       elinewidth=elinewidth, **kwargs)
