"""
Publication-quality styling utilities for matplotlib axes.

All functions use global config defaults when parameters aren't specified.
Any parameter can be overridden per-panel.
"""

from typing import Optional, List, Tuple, Union
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.font_manager as fm
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .config import get_config


def _should_preserve_font(current_font: str, preserve_list: Tuple[str, ...]) -> bool:
    """Check if a font should be preserved (not overwritten)."""
    if not preserve_list:
        return False
    # Case-insensitive comparison
    current_lower = current_font.lower()
    return any(font.lower() in current_lower or current_lower in font.lower()
               for font in preserve_list)


def _resolve_font_family(font_family: Union[str, Tuple[str, ...]]) -> str:
    """
    Resolve a font family, supporting fallback chains.

    Args:
        font_family: Single font name or tuple of fonts to try in order

    Returns:
        The first available font from the chain, or the first font if none found
    """
    if isinstance(font_family, str):
        return font_family

    # Get list of available fonts
    available_fonts = set(f.name for f in fm.fontManager.ttflist)

    # Try each font in the chain
    for font in font_family:
        if font in available_fonts:
            return font

    # Return first font as fallback (matplotlib will handle missing fonts)
    return font_family[0] if font_family else "Arial"


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
    # Font settings
    font_family: Optional[Union[str, Tuple[str, ...]]] = None,
    apply_fonts: Optional[bool] = None,
    preserve_font_families: Optional[Tuple[str, ...]] = None,
    apply_fontsizes: Optional[bool] = None,
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
        font_family: Font family for all text. Can be a string or tuple of
            fonts to try in order (fallback chain).
        apply_fonts: Whether to apply font family changes (default: True).
            Set to False to skip all font changes.
        preserve_font_families: Tuple of font names to preserve (not override).
            If a text element already uses one of these fonts, its font won't
            be changed. Set globally via config.preserve_font_families.
        apply_fontsizes: Whether to apply font size changes (default: True).
            Set to False to preserve existing font sizes.

    Example:
        # Use global config
        yp.apply_style(ax)

        # Override label size for this panel only
        yp.apply_style(ax, axis_label_fontsize=10)

        # Preserve specific fonts (e.g., Arial MS Unicode for special chars)
        yp.apply_style(ax, preserve_font_families=("Arial MS Unicode",))

        # Skip all font changes
        yp.apply_style(ax, apply_fonts=False)

        # Use font fallback chain
        yp.apply_style(ax, font_family=("Arial", "Helvetica", "sans-serif"))

        # Skip font size changes (preserve manually set sizes)
        yp.apply_style(ax, apply_fontsizes=False)
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

    # Font settings
    font_family_raw = font_family if font_family is not None else cfg.font_family
    font_family = _resolve_font_family(font_family_raw)
    apply_fonts = apply_fonts if apply_fonts is not None else cfg.apply_fonts
    preserve_fonts = preserve_font_families if preserve_font_families is not None else cfg.preserve_font_families
    apply_fontsizes = apply_fontsizes if apply_fontsizes is not None else cfg.apply_fontsizes

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
    if apply_fontsizes:
        ax.xaxis.label.set_fontsize(axis_label_fontsize)
        ax.yaxis.label.set_fontsize(axis_label_fontsize)
    if apply_fonts:
        if not _should_preserve_font(ax.xaxis.label.get_fontname(), preserve_fonts):
            ax.xaxis.label.set_fontname(font_family)
        if not _should_preserve_font(ax.yaxis.label.get_fontname(), preserve_fonts):
            ax.yaxis.label.set_fontname(font_family)
    ax.xaxis.labelpad = axis_label_pad
    ax.yaxis.labelpad = axis_label_pad

    # Set title properties
    if apply_fontsizes:
        ax.title.set_fontsize(axis_title_fontsize)
    if apply_fonts and not _should_preserve_font(ax.title.get_fontname(), preserve_fonts):
        ax.title.set_fontname(font_family)

    # Set tick label fonts
    for label in ax.get_xticklabels():
        if apply_fonts and not _should_preserve_font(label.get_fontname(), preserve_fonts):
            label.set_fontname(font_family)
        if apply_fontsizes:
            label.set_fontsize(axis_tick_fontsize)

    for label in ax.get_yticklabels():
        if apply_fonts and not _should_preserve_font(label.get_fontname(), preserve_fonts):
            label.set_fontname(font_family)
        if apply_fontsizes:
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


def set_background(
    ax: Axes,
    color: str = "lightgray",
) -> None:
    """
    Set background color of an axes to make it easy to see.

    Args:
        ax: Axes object
        color: Background color (default: "lightgray")

    Example:
        yp.set_background(ax)
        yp.set_background(ax, "lightyellow")
    """
    ax.set_facecolor(color)


def set_background_all(
    axes: List[Axes],
    color: str = "lightgray",
) -> None:
    """
    Set background color for multiple axes.

    Args:
        axes: List of Axes objects
        color: Background color (default: "lightgray")

    Example:
        yp.set_background_all(axes)
    """
    for ax in axes:
        set_background(ax, color)
