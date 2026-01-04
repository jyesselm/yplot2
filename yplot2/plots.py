"""
Plot functions that use global config defaults.

All functions allow overriding any parameter via kwargs.
"""

from typing import Optional, List, Union, Any
import numpy as np
from matplotlib.axes import Axes

from .config import get_config


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


def hist(
    ax: Axes,
    x,
    bins: Union[int, str, list] = 'auto',
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


def boxplot(
    ax: Axes,
    x,
    linewidth: Optional[float] = None,
    fliersize: Optional[float] = None,
    **kwargs,
):
    """
    Box plot using global config defaults.

    Args:
        ax: Axes object
        x: Data (list of arrays for multiple boxes)
        linewidth: Line width for box edges
        fliersize: Outlier marker size
        **kwargs: Additional args to ax.boxplot()

    Returns:
        Dict of box plot components
    """
    cfg = get_config()

    if linewidth is None:
        linewidth = cfg.axis_linewidth
    if fliersize is None:
        fliersize = cfg.plot_markersize

    # Set box properties
    boxprops = kwargs.pop('boxprops', {})
    boxprops.setdefault('linewidth', linewidth)

    whiskerprops = kwargs.pop('whiskerprops', {})
    whiskerprops.setdefault('linewidth', linewidth)

    capprops = kwargs.pop('capprops', {})
    capprops.setdefault('linewidth', linewidth)

    medianprops = kwargs.pop('medianprops', {})
    medianprops.setdefault('linewidth', linewidth)

    flierprops = kwargs.pop('flierprops', {})
    flierprops.setdefault('markersize', fliersize)

    return ax.boxplot(x, boxprops=boxprops, whiskerprops=whiskerprops,
                      capprops=capprops, medianprops=medianprops,
                      flierprops=flierprops, **kwargs)


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


def text(
    ax: Axes,
    x: float,
    y: float,
    s: str,
    fontsize: Optional[float] = None,
    fontname: Optional[str] = None,
    **kwargs,
):
    """
    Text annotation using global config defaults.

    Args:
        ax: Axes object
        x, y: Text position
        s: Text string
        fontsize: Font size
        fontname: Font family
        **kwargs: Additional args to ax.text()

    Returns:
        Text object
    """
    cfg = get_config()

    if fontsize is None:
        fontsize = cfg.axis_label_fontsize
    if fontname is None:
        fontname = cfg.font_family

    return ax.text(x, y, s, fontsize=fontsize, fontname=fontname, **kwargs)
