"""
Publication-quality styling utilities for matplotlib axes.

All functions use global config defaults when parameters aren't specified.
"""

from typing import Optional, List
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .config import get_config


def publication_style(
    ax: Axes,
    fontsize: Optional[float] = None,
    xtick_fontsize: Optional[float] = None,
    ytick_fontsize: Optional[float] = None,
    fontname: Optional[str] = None,
    linewidth: Optional[float] = None,
    tick_width: Optional[float] = None,
    tick_size: Optional[float] = None,
    tick_pad: Optional[float] = None,
) -> None:
    """
    Apply publication-quality styling to an axes.

    Uses global config defaults for any unspecified parameters.

    Args:
        ax: Axes object to style
        fontsize: Font size for labels and title
        xtick_fontsize: Font size for x-tick labels
        ytick_fontsize: Font size for y-tick labels
        fontname: Font family name
        linewidth: Width of axis spines
        tick_width: Width of tick marks
        tick_size: Length of tick marks
        tick_pad: Padding between ticks and labels
    """
    cfg = get_config()

    # Use config defaults for unspecified values
    fontsize = fontsize if fontsize is not None else cfg.fontsize
    fontname = fontname if fontname is not None else cfg.fontname
    linewidth = linewidth if linewidth is not None else cfg.linewidth
    tick_width = tick_width if tick_width is not None else cfg.tick_width
    tick_size = tick_size if tick_size is not None else cfg.tick_size
    tick_pad = tick_pad if tick_pad is not None else cfg.tick_pad
    xtick_fontsize = xtick_fontsize if xtick_fontsize is not None else cfg.tick_fontsize
    ytick_fontsize = ytick_fontsize if ytick_fontsize is not None else cfg.tick_fontsize

    # Set spine line widths
    for spine in ax.spines.values():
        spine.set_linewidth(linewidth)

    # Set tick parameters
    ax.tick_params(width=tick_width, size=tick_size, pad=tick_pad)

    # Set label font sizes and names
    ax.xaxis.label.set_fontsize(fontsize)
    ax.yaxis.label.set_fontsize(fontsize)
    ax.title.set_fontsize(fontsize)

    ax.xaxis.label.set_fontname(fontname)
    ax.yaxis.label.set_fontname(fontname)
    ax.title.set_fontname(fontname)

    # Set tick label fonts
    for label in ax.get_xticklabels():
        label.set_fontname(fontname)
        label.set_fontsize(xtick_fontsize)

    for label in ax.get_yticklabels():
        label.set_fontname(fontname)
        label.set_fontsize(ytick_fontsize)


def apply_style_to_all(
    axes: List[Axes],
    **kwargs,
) -> None:
    """
    Apply publication styling to all axes in a list.

    Args:
        axes: List of Axes objects
        **kwargs: Arguments passed to publication_style()
    """
    for ax in axes:
        publication_style(ax, **kwargs)


def remove_spines(
    ax: Axes,
    spines: List[str] = ["top", "right"],
) -> None:
    """
    Remove specified spines from an axes.

    Args:
        ax: Axes object
        spines: List of spine names to remove ('top', 'bottom', 'left', 'right')
    """
    for spine in spines:
        ax.spines[spine].set_visible(False)


def add_legend(
    ax: Axes,
    labels: List[str],
    colors: Optional[List[str]] = None,
    loc: str = "upper right",
    fontsize: Optional[float] = None,
    fontname: Optional[str] = None,
    frameon: Optional[bool] = None,
    linewidth: Optional[float] = None,
    **kwargs,
):
    """
    Add a styled legend to an axes.

    Uses global config defaults for any unspecified parameters.

    Args:
        ax: Axes object
        labels: List of label strings
        colors: List of colors (default: use color cycle)
        loc: Legend location
        fontsize: Font size for legend text
        fontname: Font family name
        frameon: Whether to draw legend frame
        linewidth: Line width for legend handles
        **kwargs: Additional arguments passed to ax.legend()

    Returns:
        Legend object
    """
    cfg = get_config()

    fontsize = fontsize if fontsize is not None else cfg.legend_fontsize
    fontname = fontname if fontname is not None else cfg.fontname
    frameon = frameon if frameon is not None else cfg.legend_frameon
    linewidth = linewidth if linewidth is not None else cfg.linewidth

    if colors is None:
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    handles = []
    for label, color in zip(labels, colors):
        handle = mlines.Line2D([], [], color=color, lw=linewidth, label=label)
        handles.append(handle)

    font_props = {"family": fontname, "size": fontsize}

    legend = ax.legend(
        handles=handles,
        frameon=frameon,
        loc=loc,
        handlelength=cfg.legend_handlelength,
        handleheight=0.5,
        handletextpad=0.30,
        borderaxespad=-0.10,
        prop=font_props,
        labelspacing=cfg.legend_labelspacing,
        **kwargs,
    )

    return legend


def scatter(
    ax: Axes,
    x,
    y,
    s: Optional[float] = None,
    **kwargs,
):
    """
    Create a publication-style scatter plot.

    Args:
        ax: Axes object
        x: x-coordinates
        y: y-coordinates
        s: Marker size
        **kwargs: Additional arguments passed to ax.scatter()

    Returns:
        PathCollection from scatter
    """
    cfg = get_config()
    s = s if s is not None else cfg.markersize ** 2  # scatter uses area
    return ax.scatter(x, y, s=s, **kwargs)


def line(
    ax: Axes,
    x,
    y,
    linewidth: Optional[float] = None,
    markersize: Optional[float] = None,
    **kwargs,
):
    """
    Create a publication-style line plot.

    Args:
        ax: Axes object
        x: x-coordinates
        y: y-coordinates
        linewidth: Line width
        markersize: Size of markers (if using markers)
        **kwargs: Additional arguments passed to ax.plot()

    Returns:
        List of Line2D objects
    """
    cfg = get_config()
    linewidth = linewidth if linewidth is not None else cfg.plot_linewidth
    markersize = markersize if markersize is not None else cfg.markersize
    return ax.plot(x, y, lw=linewidth, markersize=markersize, **kwargs)
