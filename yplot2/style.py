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
    # Tick settings (shared)
    axis_tick_width: Optional[float] = None,
    axis_tick_length: Optional[float] = None,
    axis_tick_direction: Optional[str] = None,
    # X-axis tick settings
    x_axis_tick_pad: Optional[float] = None,
    x_axis_tick_fontsize: Optional[float] = None,
    # Y-axis tick settings
    y_axis_tick_pad: Optional[float] = None,
    y_axis_tick_fontsize: Optional[float] = None,
    # X-axis label settings
    x_axis_label_fontsize: Optional[float] = None,
    x_axis_label_pad: Optional[float] = None,
    # Y-axis label settings
    y_axis_label_fontsize: Optional[float] = None,
    y_axis_label_pad: Optional[float] = None,
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
        axis_tick_direction: Tick direction ("in", "out", "inout")
        x_axis_tick_pad: X-axis tick padding
        x_axis_tick_fontsize: X-axis tick label font size
        y_axis_tick_pad: Y-axis tick padding
        y_axis_tick_fontsize: Y-axis tick label font size
        x_axis_label_fontsize: X-axis label font size
        x_axis_label_pad: X-axis label padding
        y_axis_label_fontsize: Y-axis label font size
        y_axis_label_pad: Y-axis label padding
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

        # Different font sizes for x and y labels
        yp.apply_style(ax, x_axis_label_fontsize=10, y_axis_label_fontsize=8)

        # Preserve specific fonts (e.g., Arial Unicode MS for special chars)
        yp.apply_style(ax, preserve_font_families=("Arial Unicode MS",))

        # Skip all font changes
        yp.apply_style(ax, apply_fonts=False)
    """
    cfg = get_config()

    # Get values from config if not specified
    axis_linewidth = axis_linewidth if axis_linewidth is not None else cfg.axis_linewidth
    axis_tick_width = axis_tick_width if axis_tick_width is not None else cfg.axis_tick_width
    axis_tick_length = axis_tick_length if axis_tick_length is not None else cfg.axis_tick_length
    axis_tick_direction = axis_tick_direction if axis_tick_direction is not None else cfg.axis_tick_direction

    # X-axis settings
    x_axis_tick_pad = x_axis_tick_pad if x_axis_tick_pad is not None else cfg.x_axis_tick_pad
    x_axis_tick_fontsize = x_axis_tick_fontsize if x_axis_tick_fontsize is not None else cfg.x_axis_tick_fontsize
    x_axis_label_fontsize = x_axis_label_fontsize if x_axis_label_fontsize is not None else cfg.x_axis_label_fontsize
    x_axis_label_pad = x_axis_label_pad if x_axis_label_pad is not None else cfg.x_axis_label_pad

    # Y-axis settings
    y_axis_tick_pad = y_axis_tick_pad if y_axis_tick_pad is not None else cfg.y_axis_tick_pad
    y_axis_tick_fontsize = y_axis_tick_fontsize if y_axis_tick_fontsize is not None else cfg.y_axis_tick_fontsize
    y_axis_label_fontsize = y_axis_label_fontsize if y_axis_label_fontsize is not None else cfg.y_axis_label_fontsize
    y_axis_label_pad = y_axis_label_pad if y_axis_label_pad is not None else cfg.y_axis_label_pad

    # Title settings
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

    # Set tick parameters separately for x and y
    ax.tick_params(
        axis='x',
        width=axis_tick_width,
        length=axis_tick_length,
        pad=x_axis_tick_pad,
        direction=axis_tick_direction,
    )
    ax.tick_params(
        axis='y',
        width=axis_tick_width,
        length=axis_tick_length,
        pad=y_axis_tick_pad,
        direction=axis_tick_direction,
    )

    # Set axis label properties
    if apply_fontsizes:
        ax.xaxis.label.set_fontsize(x_axis_label_fontsize)
        ax.yaxis.label.set_fontsize(y_axis_label_fontsize)
    if apply_fonts:
        if not _should_preserve_font(ax.xaxis.label.get_fontname(), preserve_fonts):
            ax.xaxis.label.set_fontname(font_family)
        if not _should_preserve_font(ax.yaxis.label.get_fontname(), preserve_fonts):
            ax.yaxis.label.set_fontname(font_family)
    ax.xaxis.labelpad = x_axis_label_pad
    ax.yaxis.labelpad = y_axis_label_pad

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
            label.set_fontsize(x_axis_tick_fontsize)

    for label in ax.get_yticklabels():
        if apply_fonts and not _should_preserve_font(label.get_fontname(), preserve_fonts):
            label.set_fontname(font_family)
        if apply_fontsizes:
            label.set_fontsize(y_axis_tick_fontsize)


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


def add_legend_above(
    ax: Axes,
    labels: List[str],
    colors: Optional[List[str]] = None,
    # Position (in inches - absolute positioning)
    x_offset: float = 0.0,
    y_offset: float = 0.080,
    anchor: str = "upper right",
    # Layout
    ncol: Optional[int] = None,
    columnspacing: float = 0.8,
    # Styling (override config)
    legend_fontsize: Optional[float] = None,
    legend_frameon: Optional[bool] = None,
    legend_handlelength: Optional[float] = None,
    legend_labelspacing: Optional[float] = None,
    handletextpad: float = 0.4,
    font_family: Optional[str] = None,
    linewidth: Optional[float] = None,
    # Marker settings - can be single value or list per label
    marker: Optional[Union[str, List[str]]] = None,
    markersize: Optional[Union[float, List[float]]] = None,
    markerfacecolor: Optional[Union[str, List[str]]] = None,
    markeredgecolor: Optional[Union[str, List[str]]] = None,
    markeredgewidth: Optional[Union[float, List[float]]] = None,
    linestyle: Union[str, List[str]] = "-",
    **kwargs,
):
    """
    Add a legend above the subplot.

    Places the legend outside the axes, above the plot area.
    Highly customizable positioning and styling.

    Args:
        ax: Axes object
        labels: List of label strings
        colors: List of colors (default: use color cycle)

        Position args:
            x_offset: Horizontal offset in inches (absolute positioning)
            y_offset: Vertical offset above axes top in inches (absolute positioning)
            anchor: Legend anchor point. Options:
                - "upper right" (default): legend expands left
                - "upper left": legend expands right
                - "upper center": legend expands both directions

        Layout args:
            ncol: Number of columns (default: len(labels) for horizontal)
            columnspacing: Gap between columns

        Styling args (default from config):
            legend_fontsize: Font size
            legend_frameon: Show frame
            legend_handlelength: Handle length
            legend_labelspacing: Vertical spacing between entries
            handletextpad: Gap between handle and text
            font_family: Font family
            linewidth: Line width for handles

        Marker args (single value or list per label):
            marker: Marker style (e.g., 'o', 's', ['o', 'o'])
            markersize: Marker size
            markerfacecolor: Fill color (e.g., 'red', 'white', ['red', 'white'])
            markeredgecolor: Edge color (defaults to colors if not set)
            markeredgewidth: Edge line width
            linestyle: Line style (default: '-', use '' or 'none' for no line)

        **kwargs: Additional args passed to ax.legend()

    Returns:
        Legend object

    Examples:
        # Simple horizontal legend above plot
        yp.add_legend_above(ax, ["WT", "Mutant"], ["blue", "red"])

        # Filled and unfilled markers (red sphere, white sphere with red edge)
        yp.add_legend_above(
            ax, ["WT", "UUCG"], ["red", "red"],
            marker="o",
            markerfacecolor=["red", "white"],
            linestyle="none"
        )

        # Different markers per label
        yp.add_legend_above(
            ax, ["Data", "Fit"], ["blue", "red"],
            marker=["o", "none"],
            linestyle=["none", "-"]
        )

        # Centered above plot
        yp.add_legend_above(ax, labels, colors, anchor="upper center")

        # With markers and lines
        yp.add_legend_above(ax, labels, colors, marker="o", markersize=4)
    """
    cfg = get_config()

    # Get values from config
    legend_fontsize = legend_fontsize if legend_fontsize is not None else cfg.legend_fontsize
    legend_frameon = legend_frameon if legend_frameon is not None else cfg.legend_frameon
    legend_handlelength = legend_handlelength if legend_handlelength is not None else cfg.legend_handlelength
    legend_labelspacing = legend_labelspacing if legend_labelspacing is not None else cfg.legend_labelspacing
    font_family = font_family if font_family is not None else cfg.font_family
    linewidth = linewidth if linewidth is not None else cfg.axis_linewidth

    # Default to horizontal layout
    if ncol is None:
        ncol = len(labels)

    # Default colors from color cycle
    if colors is None:
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    n_labels = len(labels)

    # Helper to expand single value to list
    def expand(val, default=None):
        if val is None:
            return [default] * n_labels
        if isinstance(val, list):
            return val
        return [val] * n_labels

    # Expand all marker properties to lists
    markers = expand(marker)
    markersizes = expand(markersize)
    markerfacecolors = expand(markerfacecolor)
    markeredgecolors = expand(markeredgecolor)
    markeredgewidths = expand(markeredgewidth)
    linestyles = expand(linestyle, "-")

    # Build handles
    handles = []
    for i, (label, color) in enumerate(zip(labels, colors)):
        # Default edge color to the main color if not specified
        mec = markeredgecolors[i] if markeredgecolors[i] is not None else color
        # Default face color to the main color if not specified
        mfc = markerfacecolors[i] if markerfacecolors[i] is not None else color

        handle = mlines.Line2D(
            [], [],
            color=color,
            lw=linewidth,
            linestyle=linestyles[i],
            marker=markers[i],
            markersize=markersizes[i],
            markerfacecolor=mfc,
            markeredgecolor=mec,
            markeredgewidth=markeredgewidths[i],
            label=label,
        )
        handles.append(handle)

    # Font properties
    font_props = {"family": font_family, "size": legend_fontsize}

    # Convert inches to axes coordinates for absolute positioning
    fig = ax.get_figure()
    bbox = ax.get_position()
    fig_width, fig_height = fig.get_size_inches()
    ax_width_inches = bbox.width * fig_width
    ax_height_inches = bbox.height * fig_height

    # Convert inch offsets to axes fraction
    x_offset_axes = x_offset / ax_width_inches if ax_width_inches > 0 else 0
    y_offset_axes = y_offset / ax_height_inches if ax_height_inches > 0 else 0

    # Calculate position based on anchor
    if anchor == "upper right":
        x_position = 1.0 + x_offset_axes
    elif anchor == "upper left":
        x_position = 0.0 + x_offset_axes
    elif anchor == "upper center":
        x_position = 0.5 + x_offset_axes
    else:
        # Custom anchor - use x_offset directly as axes fraction
        x_position = x_offset_axes

    y_position = 1.0 + y_offset_axes

    legend = ax.legend(
        handles=handles,
        frameon=legend_frameon,
        loc=anchor,
        bbox_to_anchor=(x_position, y_position),
        bbox_transform=ax.transAxes,
        borderaxespad=0,
        borderpad=0,
        handlelength=legend_handlelength,
        handletextpad=handletextpad,
        labelspacing=legend_labelspacing,
        columnspacing=columnspacing,
        ncol=ncol,
        prop=font_props,
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
