"""
Publication-quality styling utilities for matplotlib axes.
"""

from typing import Optional, List
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.axes import Axes
from matplotlib.figure import Figure


def publication_style(
    ax: Axes,
    fontsize: int = 8,
    xtick_fontsize: Optional[int] = None,
    ytick_fontsize: Optional[int] = None,
    fontname: str = "Arial",
    linewidth: float = 0.75,
    tick_width: float = 0.75,
    tick_size: float = 2.0,
    tick_pad: float = 1.0,
) -> None:
    """
    Apply publication-quality styling to an axes.

    Args:
        ax: Axes object to style
        fontsize: Font size for labels and title
        xtick_fontsize: Font size for x-tick labels (default: fontsize - 2)
        ytick_fontsize: Font size for y-tick labels (default: fontsize - 2)
        fontname: Font family name
        linewidth: Width of axis spines
        tick_width: Width of tick marks
        tick_size: Length of tick marks
        tick_pad: Padding between ticks and labels
    """
    if xtick_fontsize is None:
        xtick_fontsize = fontsize - 2
    if ytick_fontsize is None:
        ytick_fontsize = fontsize - 2

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
    fontsize: int = 6,
    fontname: str = "Arial",
    frameon: bool = False,
    linewidth: float = 0.75,
    **kwargs,
):
    """
    Add a styled legend to an axes.

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
        handlelength=1.0,
        handleheight=0.5,
        handletextpad=0.30,
        borderaxespad=-0.10,
        prop=font_props,
        labelspacing=0.15,
        **kwargs,
    )

    return legend


def scatter(
    ax: Axes,
    x,
    y,
    s: float = 150,
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
    return ax.scatter(x, y, s=s, **kwargs)


def line(
    ax: Axes,
    x,
    y,
    linewidth: float = 2,
    markersize: float = 10,
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
    return ax.plot(x, y, lw=linewidth, markersize=markersize, **kwargs)
