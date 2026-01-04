"""
Publication-quality styling utilities for matplotlib axes.

All functions use global config defaults when parameters aren't specified.
Any parameter can be overridden per-panel.
"""

from typing import Optional, List
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .config import get_config


def apply_style(
    ax: Axes,
    # Axis line (spine) settings
    axis_linewidth: Optional[float] = None,
    # Tick settings
    axis_tick_width: Optional[float] = None,
    axis_tick_length: Optional[float] = None,
    axis_tick_pad: Optional[float] = None,
    axis_tick_fontsize: Optional[float] = None,
    axis_tick_direction: Optional[str] = None,
    # Axis label settings
    axis_label_fontsize: Optional[float] = None,
    axis_label_pad: Optional[float] = None,
    # Title settings
    axis_title_fontsize: Optional[float] = None,
    axis_title_pad: Optional[float] = None,
    # Font
    font_family: Optional[str] = None,
) -> None:
    """
    Apply styling to a single axes.

    Uses global config defaults for any unspecified parameters.
    Override any parameter for this specific panel.

    Args:
        ax: Axes object to style
        axis_linewidth: Spine line width
        axis_tick_width: Tick mark width
        axis_tick_length: Tick mark length
        axis_tick_pad: Padding between tick and label
        axis_tick_fontsize: Tick label font size
        axis_tick_direction: Tick direction ("in", "out", "inout")
        axis_label_fontsize: Axis label (xlabel/ylabel) font size
        axis_label_pad: Axis label padding
        axis_title_fontsize: Title font size
        axis_title_pad: Title padding
        font_family: Font family for all text

    Example:
        # Use global config
        yp.apply_style(ax)

        # Override label size for this panel only
        yp.apply_style(ax, axis_label_fontsize=10)
    """
    cfg = get_config()

    # Get values from config if not specified
    axis_linewidth = axis_linewidth if axis_linewidth is not None else cfg.axis_linewidth
    axis_tick_width = axis_tick_width if axis_tick_width is not None else cfg.axis_tick_width
    axis_tick_length = axis_tick_length if axis_tick_length is not None else cfg.axis_tick_length
    axis_tick_pad = axis_tick_pad if axis_tick_pad is not None else cfg.axis_tick_pad
    axis_tick_fontsize = axis_tick_fontsize if axis_tick_fontsize is not None else cfg.axis_tick_fontsize
    axis_tick_direction = axis_tick_direction if axis_tick_direction is not None else cfg.axis_tick_direction
    axis_label_fontsize = axis_label_fontsize if axis_label_fontsize is not None else cfg.axis_label_fontsize
    axis_label_pad = axis_label_pad if axis_label_pad is not None else cfg.axis_label_pad
    axis_title_fontsize = axis_title_fontsize if axis_title_fontsize is not None else cfg.axis_title_fontsize
    axis_title_pad = axis_title_pad if axis_title_pad is not None else cfg.axis_title_pad
    font_family = font_family if font_family is not None else cfg.font_family

    # Set spine line widths
    for spine in ax.spines.values():
        spine.set_linewidth(axis_linewidth)

    # Set tick parameters
    ax.tick_params(
        width=axis_tick_width,
        length=axis_tick_length,
        pad=axis_tick_pad,
        direction=axis_tick_direction,
    )

    # Set axis label properties
    ax.xaxis.label.set_fontsize(axis_label_fontsize)
    ax.yaxis.label.set_fontsize(axis_label_fontsize)
    ax.xaxis.label.set_fontname(font_family)
    ax.yaxis.label.set_fontname(font_family)
    ax.xaxis.labelpad = axis_label_pad
    ax.yaxis.labelpad = axis_label_pad

    # Set title properties
    ax.title.set_fontsize(axis_title_fontsize)
    ax.title.set_fontname(font_family)

    # Set tick label fonts
    for label in ax.get_xticklabels():
        label.set_fontname(font_family)
        label.set_fontsize(axis_tick_fontsize)

    for label in ax.get_yticklabels():
        label.set_fontname(font_family)
        label.set_fontsize(axis_tick_fontsize)


def apply_style_to_all(
    axes: List[Axes],
    **kwargs,
) -> None:
    """
    Apply styling to all axes in a list.

    Args:
        axes: List of Axes objects
        **kwargs: Arguments passed to apply_style()

    Example:
        yp.apply_style_to_all(axes)
        yp.apply_style_to_all(axes, axis_label_fontsize=10)
    """
    for ax in axes:
        apply_style(ax, **kwargs)


# Alias for backwards compatibility
publication_style = apply_style


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
    # Override config
    legend_fontsize: Optional[float] = None,
    legend_frameon: Optional[bool] = None,
    legend_handlelength: Optional[float] = None,
    legend_labelspacing: Optional[float] = None,
    font_family: Optional[str] = None,
    linewidth: Optional[float] = None,
    **kwargs,
):
    """
    Add a styled legend to an axes.

    Args:
        ax: Axes object
        labels: List of label strings
        colors: List of colors (default: use color cycle)
        loc: Legend location
        legend_fontsize: Font size for legend text
        legend_frameon: Whether to draw legend frame
        legend_handlelength: Length of legend handles
        legend_labelspacing: Spacing between legend entries
        font_family: Font family
        linewidth: Line width for handles
        **kwargs: Additional arguments passed to ax.legend()

    Returns:
        Legend object
    """
    cfg = get_config()

    legend_fontsize = legend_fontsize if legend_fontsize is not None else cfg.legend_fontsize
    legend_frameon = legend_frameon if legend_frameon is not None else cfg.legend_frameon
    legend_handlelength = legend_handlelength if legend_handlelength is not None else cfg.legend_handlelength
    legend_labelspacing = legend_labelspacing if legend_labelspacing is not None else cfg.legend_labelspacing
    font_family = font_family if font_family is not None else cfg.font_family
    linewidth = linewidth if linewidth is not None else cfg.axis_linewidth

    if colors is None:
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    handles = []
    for label, color in zip(labels, colors):
        handle = mlines.Line2D([], [], color=color, lw=linewidth, label=label)
        handles.append(handle)

    font_props = {"family": font_family, "size": legend_fontsize}

    legend = ax.legend(
        handles=handles,
        frameon=legend_frameon,
        loc=loc,
        handlelength=legend_handlelength,
        handleheight=0.5,
        handletextpad=0.30,
        borderaxespad=-0.10,
        prop=font_props,
        labelspacing=legend_labelspacing,
        **kwargs,
    )

    return legend


def set_xlabel(
    ax: Axes,
    label: str,
    fontsize: Optional[float] = None,
    fontname: Optional[str] = None,
    **kwargs,
) -> None:
    """
    Set x-axis label with config defaults.

    Args:
        ax: Axes object
        label: Label text
        fontsize: Font size (default: config.axis_label_fontsize)
        fontname: Font family (default: config.font_family)
        **kwargs: Additional args to ax.set_xlabel()
    """
    cfg = get_config()
    fontsize = fontsize if fontsize is not None else cfg.axis_label_fontsize
    fontname = fontname if fontname is not None else cfg.font_family
    ax.set_xlabel(label, fontsize=fontsize, fontname=fontname, **kwargs)


def set_ylabel(
    ax: Axes,
    label: str,
    fontsize: Optional[float] = None,
    fontname: Optional[str] = None,
    **kwargs,
) -> None:
    """
    Set y-axis label with config defaults.

    Args:
        ax: Axes object
        label: Label text
        fontsize: Font size (default: config.axis_label_fontsize)
        fontname: Font family (default: config.font_family)
        **kwargs: Additional args to ax.set_ylabel()
    """
    cfg = get_config()
    fontsize = fontsize if fontsize is not None else cfg.axis_label_fontsize
    fontname = fontname if fontname is not None else cfg.font_family
    ax.set_ylabel(label, fontsize=fontsize, fontname=fontname, **kwargs)


def set_title(
    ax: Axes,
    title: str,
    fontsize: Optional[float] = None,
    fontname: Optional[str] = None,
    **kwargs,
) -> None:
    """
    Set title with config defaults.

    Args:
        ax: Axes object
        title: Title text
        fontsize: Font size (default: config.axis_title_fontsize)
        fontname: Font family (default: config.font_family)
        **kwargs: Additional args to ax.set_title()
    """
    cfg = get_config()
    fontsize = fontsize if fontsize is not None else cfg.axis_title_fontsize
    fontname = fontname if fontname is not None else cfg.font_family
    ax.set_title(title, fontsize=fontsize, fontname=fontname, **kwargs)
