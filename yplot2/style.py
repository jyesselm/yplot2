"""
Publication-quality styling utilities for matplotlib axes.

All functions use global config defaults when parameters aren't specified.
Any parameter can be overridden per-panel.
"""

import dataclasses
from contextlib import contextmanager
from typing import Generator, List, Optional, Tuple, Union
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.font_manager as fm
from matplotlib.axes import Axes
from matplotlib.text import Text

from .config import Config, get_config


def _should_preserve_font(current_font: str, preserve_list: Tuple[str, ...]) -> bool:
    """Check if a font should be preserved (not overwritten)."""
    if not preserve_list:
        return False
    # Case-insensitive comparison
    current_lower = current_font.lower()
    return any(
        font.lower() in current_lower or current_lower in font.lower()
        for font in preserve_list
    )


def _is_arial(name: str) -> bool:
    """Return True only for the bare "Arial" family (not Arial Narrow/Black/etc.)."""
    return name.strip().lower() == "arial"


def _resolve_font_family(font_family: Union[str, Tuple[str, ...]]) -> str:
    """
    Resolve a font family, supporting fallback chains and Arial→Arimo mapping.

    When the requested font is exactly "Arial" (case-insensitive, not Arial
    Narrow or Arial Black) and Arial is absent from the host system, this
    returns "Arimo" if the bundled Arimo is registered — providing a
    deterministic metric-compatible substitute.  "Arial Narrow" and similar
    variants are passed through unchanged (they are distinct faces with
    different metrics).

    Args:
        font_family: Single font name, or tuple of fonts to try in order.
            None or non-str/tuple inputs fall back to "Arimo".

    Returns:
        The resolved font name (str).
    """
    if font_family is None or not isinstance(font_family, (str, tuple)):
        return "Arimo"

    available_fonts = set(f.name for f in fm.fontManager.ttflist)

    if isinstance(font_family, str):
        if font_family in available_fonts:
            return font_family
        # Exact "Arial" → Arimo when Arial absent; Arial Narrow/Black pass through
        if _is_arial(font_family) and "Arimo" in available_fonts:
            return "Arimo"
        return font_family

    # Tuple: try each font in order (apply Arial→Arimo in each slot)
    for font in font_family:
        if font in available_fonts:
            return font
        if _is_arial(font) and "Arimo" in available_fonts:
            return "Arimo"

    # Return first font as fallback (matplotlib will handle missing fonts)
    return font_family[0] if font_family else "Arimo"


def _set_fontname_if_needed(
    label: Text,
    font_family: str,
    *,
    check_preserve: bool,
    preserve_fonts: Tuple[str, ...],
) -> None:
    """Set fontname on a tick label unless the preserve-check blocks it.

    Args:
        label: Tick label Text object to modify.
        font_family: Target font family name.
        check_preserve: When True, skip labels whose current font is in preserve_fonts.
            When False (finish path), overwrite unconditionally — matching current finish
            behavior which ignores preserve_font_families on tick labels.
        preserve_fonts: Fonts that should not be overwritten when check_preserve is True.
    """
    if check_preserve and _should_preserve_font(label.get_fontname(), preserve_fonts):
        return
    label.set_fontname(font_family)


def _apply_tick_fonts(
    labels: List[Text],
    font_family: str,
    fontsize: float,
    *,
    apply_fonts: bool,
    apply_fontsizes: bool,
    check_preserve: bool,
    preserve_fonts: Tuple[str, ...],
) -> None:
    """Apply font family and size to a list of tick label Text objects.

    Args:
        labels: Tick label Text objects (from ax.get_xticklabels() / get_yticklabels()).
        font_family: Target font family name (already resolved).
        fontsize: Target font size in points.
        apply_fonts: Whether to change the font family at all.
        apply_fontsizes: Whether to change the font size.
        check_preserve: Passed through to _set_fontname_if_needed.
        preserve_fonts: Fonts to skip when check_preserve is True.
    """
    for label in labels:
        if apply_fonts:
            _set_fontname_if_needed(
                label,
                font_family,
                check_preserve=check_preserve,
                preserve_fonts=preserve_fonts,
            )
        if apply_fontsizes:
            label.set_fontsize(fontsize)


def _enforce_spines_ticks(
    ax: Axes,
    cfg: Config,
    *,
    set_tick_direction: bool,
) -> None:
    """Set spine linewidths and tick mark parameters from cfg.

    Args:
        ax: Target axes.
        cfg: Config instance whose numeric chrome values are applied.
        set_tick_direction: When True, also applies cfg.axis_tick_direction.
            apply_style sets this True; finish sets it False to leave direction alone.
    """
    for spine in ax.spines.values():
        spine.set_linewidth(cfg.axis_linewidth)
    tick_x: dict = {
        "width": cfg.axis_tick_width,
        "length": cfg.axis_tick_length,
        "pad": cfg.x_axis_tick_pad,
    }
    tick_y: dict = {
        "width": cfg.axis_tick_width,
        "length": cfg.axis_tick_length,
        "pad": cfg.y_axis_tick_pad,
    }
    if set_tick_direction:
        tick_x["direction"] = cfg.axis_tick_direction
        tick_y["direction"] = cfg.axis_tick_direction
    ax.tick_params(axis="x", **tick_x)
    ax.tick_params(axis="y", **tick_y)


def _enforce_text_fonts(
    ax: Axes,
    cfg: Config,
    font_family: str,
    *,
    set_label_fontsizes: bool,
    set_label_pads: bool,
    set_title_fontsize: bool,
    check_preserve_on_ticks: bool,
    apply_fonts: bool,
    apply_fontsizes: bool,
    preserve_fonts: Tuple[str, ...],
) -> None:
    """Set axis-label, title, and tick-label fonts and sizes from cfg.

    Args:
        ax: Target axes.
        cfg: Config instance whose numeric values are applied.
        font_family: Resolved font family name.
        set_label_fontsizes: Apply x/y axis-label fontsizes (apply_style path only).
        set_label_pads: Apply x/y labelpad values (apply_style path only).
        set_title_fontsize: Apply title fontsize (apply_style path only).
        check_preserve_on_ticks: apply_style honors preserve_fonts on tick labels;
            finish ignores it (overwrites unconditionally — current behavior pinned).
        apply_fonts: Whether to change font families at all.
        apply_fontsizes: Whether to change tick-label fontsizes.
        preserve_fonts: Fonts to leave unchanged on axis labels and title.
    """
    if set_label_fontsizes:
        ax.xaxis.label.set_fontsize(cfg.x_axis_label_fontsize)
        ax.yaxis.label.set_fontsize(cfg.y_axis_label_fontsize)
    if apply_fonts:
        if not _should_preserve_font(ax.xaxis.label.get_fontname(), preserve_fonts):
            ax.xaxis.label.set_fontname(font_family)
        if not _should_preserve_font(ax.yaxis.label.get_fontname(), preserve_fonts):
            ax.yaxis.label.set_fontname(font_family)
    if set_label_pads:
        ax.xaxis.labelpad = cfg.x_axis_label_pad
        ax.yaxis.labelpad = cfg.y_axis_label_pad
    if set_title_fontsize:
        ax.title.set_fontsize(cfg.axis_title_fontsize)
    if apply_fonts and not _should_preserve_font(
        ax.title.get_fontname(), preserve_fonts
    ):
        ax.title.set_fontname(font_family)
    _apply_tick_fonts(
        ax.get_xticklabels(),
        font_family,
        cfg.x_axis_tick_fontsize,
        apply_fonts=apply_fonts,
        apply_fontsizes=apply_fontsizes,
        check_preserve=check_preserve_on_ticks,
        preserve_fonts=preserve_fonts,
    )
    _apply_tick_fonts(
        ax.get_yticklabels(),
        font_family,
        cfg.y_axis_tick_fontsize,
        apply_fonts=apply_fonts,
        apply_fontsizes=apply_fontsizes,
        check_preserve=check_preserve_on_ticks,
        preserve_fonts=preserve_fonts,
    )


def _enforce_chrome(
    ax: Axes,
    cfg: Config,
    font_family: str,
    *,
    set_label_fontsizes: bool,
    set_label_pads: bool,
    set_tick_direction: bool,
    set_title_fontsize: bool,
    check_preserve_on_ticks: bool,
    apply_fonts: bool,
    apply_fontsizes: bool,
    preserve_fonts: Tuple[str, ...],
) -> None:
    """Single chrome enforcer: spines, ticks, tick-label and axis-label fonts/sizes.

    Reads all numeric chrome values from the cfg it is passed.  Both apply_style
    and finish delegate here; the flag matrix reproduces each caller's exact current
    behavior without duplicating rendering logic.

    Args:
        ax: Target axes.
        cfg: Config instance to read chrome values from.  apply_style passes a
            per-call copy with overrides folded in via dataclasses.replace; finish
            passes the global cfg unchanged.
        font_family: Resolved font family (already run through _resolve_font_family).
        set_label_fontsizes: Apply x/y axis-label fontsizes.
        set_label_pads: Apply x/y labelpad values.
        set_tick_direction: Apply tick direction from cfg.
        set_title_fontsize: Apply title fontsize.
        check_preserve_on_ticks: Honor preserve_fonts on tick labels (apply_style=True,
            finish=False — intentional divergence, see BLOCKER-1 in Phase 1 plan).
        apply_fonts: Whether to change font families.
        apply_fontsizes: Whether to change font sizes (tick labels and optionally labels).
        preserve_fonts: Fonts to leave unchanged (axis labels + title always checked;
            tick labels checked only when check_preserve_on_ticks=True).
    """
    _enforce_spines_ticks(ax, cfg, set_tick_direction=set_tick_direction)
    _enforce_text_fonts(
        ax,
        cfg,
        font_family,
        set_label_fontsizes=set_label_fontsizes,
        set_label_pads=set_label_pads,
        set_title_fontsize=set_title_fontsize,
        check_preserve_on_ticks=check_preserve_on_ticks,
        apply_fonts=apply_fonts,
        apply_fontsizes=apply_fontsizes,
        preserve_fonts=preserve_fonts,
    )


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
    axis_linewidth = (
        axis_linewidth if axis_linewidth is not None else cfg.axis_linewidth
    )
    axis_tick_width = (
        axis_tick_width if axis_tick_width is not None else cfg.axis_tick_width
    )
    axis_tick_length = (
        axis_tick_length if axis_tick_length is not None else cfg.axis_tick_length
    )
    axis_tick_direction = (
        axis_tick_direction
        if axis_tick_direction is not None
        else cfg.axis_tick_direction
    )

    # X-axis settings
    x_axis_tick_pad = (
        x_axis_tick_pad if x_axis_tick_pad is not None else cfg.x_axis_tick_pad
    )
    x_axis_tick_fontsize = (
        x_axis_tick_fontsize
        if x_axis_tick_fontsize is not None
        else cfg.x_axis_tick_fontsize
    )
    x_axis_label_fontsize = (
        x_axis_label_fontsize
        if x_axis_label_fontsize is not None
        else cfg.x_axis_label_fontsize
    )
    x_axis_label_pad = (
        x_axis_label_pad if x_axis_label_pad is not None else cfg.x_axis_label_pad
    )

    # Y-axis settings
    y_axis_tick_pad = (
        y_axis_tick_pad if y_axis_tick_pad is not None else cfg.y_axis_tick_pad
    )
    y_axis_tick_fontsize = (
        y_axis_tick_fontsize
        if y_axis_tick_fontsize is not None
        else cfg.y_axis_tick_fontsize
    )
    y_axis_label_fontsize = (
        y_axis_label_fontsize
        if y_axis_label_fontsize is not None
        else cfg.y_axis_label_fontsize
    )
    y_axis_label_pad = (
        y_axis_label_pad if y_axis_label_pad is not None else cfg.y_axis_label_pad
    )

    # Title settings
    axis_title_fontsize = (
        axis_title_fontsize
        if axis_title_fontsize is not None
        else cfg.axis_title_fontsize
    )

    # Font settings
    font_family_raw = font_family if font_family is not None else cfg.font_family
    font_family = _resolve_font_family(font_family_raw)
    apply_fonts = apply_fonts if apply_fonts is not None else cfg.apply_fonts
    preserve_fonts = (
        preserve_font_families
        if preserve_font_families is not None
        else cfg.preserve_font_families
    )
    apply_fontsizes = (
        apply_fontsizes if apply_fontsizes is not None else cfg.apply_fontsizes
    )

    # Fold all resolved overrides into a per-call Config so _enforce_chrome reads them.
    # Do NOT pass the global cfg here — that would silently drop per-call overrides.
    local_cfg = dataclasses.replace(
        cfg,
        axis_linewidth=axis_linewidth,
        axis_tick_width=axis_tick_width,
        axis_tick_length=axis_tick_length,
        axis_tick_direction=axis_tick_direction,
        x_axis_tick_pad=x_axis_tick_pad,
        y_axis_tick_pad=y_axis_tick_pad,
        x_axis_tick_fontsize=x_axis_tick_fontsize,
        y_axis_tick_fontsize=y_axis_tick_fontsize,
        x_axis_label_fontsize=x_axis_label_fontsize,
        y_axis_label_fontsize=y_axis_label_fontsize,
        x_axis_label_pad=x_axis_label_pad,
        y_axis_label_pad=y_axis_label_pad,
        axis_title_fontsize=axis_title_fontsize,
    )
    _enforce_chrome(
        ax,
        local_cfg,
        font_family,
        set_label_fontsizes=apply_fontsizes,
        set_label_pads=True,
        set_tick_direction=True,
        set_title_fontsize=apply_fontsizes,
        check_preserve_on_ticks=True,
        apply_fonts=apply_fonts,
        apply_fontsizes=apply_fontsizes,
        preserve_fonts=preserve_fonts,
    )


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
        yp.apply_style_to_all(axes, x_axis_label_fontsize=10)
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


def clear_axes(
    ax: Axes,
    x: bool = True,
    y: bool = True,
    spines: bool = False,
) -> None:
    """
    Remove axis elements (ticks, labels, optionally spines).

    Args:
        ax: Axes object
        x: Clear x-axis elements (default: True)
        y: Clear y-axis elements (default: True)
        spines: Also remove spines (default: False)

    Example:
        # Clear both axes
        yp.clear_axes(ax)

        # Clear only x-axis
        yp.clear_axes(ax, y=False)

        # Clear only y-axis
        yp.clear_axes(ax, x=False)

        # Clear everything including spines
        yp.clear_axes(ax, spines=True)
    """
    if x:
        ax.set_xticks([])
        ax.set_xticklabels([])
        ax.set_xlabel("")
        if spines:
            ax.spines["top"].set_visible(False)
            ax.spines["bottom"].set_visible(False)

    if y:
        ax.set_yticks([])
        ax.set_yticklabels([])
        ax.set_ylabel("")
        if spines:
            ax.spines["left"].set_visible(False)
            ax.spines["right"].set_visible(False)


def clear_axes_all(
    axes: List[Axes],
    x: bool = True,
    y: bool = True,
    spines: bool = False,
) -> None:
    """
    Remove axis elements from multiple axes.

    Args:
        axes: List of Axes objects
        x: Clear x-axis elements (default: True)
        y: Clear y-axis elements (default: True)
        spines: Also remove spines (default: False)

    Example:
        yp.clear_axes_all(image_axes)
        yp.clear_axes_all(axes, x=False)  # Clear only y-axes
    """
    for ax in axes:
        clear_axes(ax, x=x, y=y, spines=spines)


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

    legend_fontsize = (
        legend_fontsize if legend_fontsize is not None else cfg.legend_fontsize
    )
    legend_frameon = (
        legend_frameon if legend_frameon is not None else cfg.legend_frameon
    )
    legend_handlelength = (
        legend_handlelength
        if legend_handlelength is not None
        else cfg.legend_handlelength
    )
    legend_labelspacing = (
        legend_labelspacing
        if legend_labelspacing is not None
        else cfg.legend_labelspacing
    )
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
    legend_fontsize = (
        legend_fontsize if legend_fontsize is not None else cfg.legend_fontsize
    )
    legend_frameon = (
        legend_frameon if legend_frameon is not None else cfg.legend_frameon
    )
    legend_handlelength = (
        legend_handlelength
        if legend_handlelength is not None
        else cfg.legend_handlelength
    )
    legend_labelspacing = (
        legend_labelspacing
        if legend_labelspacing is not None
        else cfg.legend_labelspacing
    )
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
            [],
            [],
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
        fontsize: Font size (default: config.x_axis_label_fontsize)
        fontname: Font family (default: config.font_family)
        **kwargs: Additional args to ax.set_xlabel()
    """
    cfg = get_config()
    fontsize = fontsize if fontsize is not None else cfg.x_axis_label_fontsize
    fontname = _resolve_font_family(
        fontname if fontname is not None else cfg.font_family
    )
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
        fontsize: Font size (default: config.y_axis_label_fontsize)
        fontname: Font family (default: config.font_family)
        **kwargs: Additional args to ax.set_ylabel()
    """
    cfg = get_config()
    fontsize = fontsize if fontsize is not None else cfg.y_axis_label_fontsize
    fontname = _resolve_font_family(
        fontname if fontname is not None else cfg.font_family
    )
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
    fontname = _resolve_font_family(
        fontname if fontname is not None else cfg.font_family
    )
    ax.set_title(title, fontsize=fontsize, fontname=fontname, **kwargs)


def strip_labels(
    ax: Axes,
) -> None:
    """
    Remove axis labels, tick labels, and x tick lines from an axes.

    Keeps tick positions and spines intact, unlike clear_axes which
    removes ticks entirely.

    Args:
        ax: Axes object

    Example:
        yp.strip_labels(ax)
    """
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.tick_params(axis="x", length=0)


def strip_labels_all(
    axes: List[Axes],
) -> None:
    """
    Remove axis labels, tick labels, and x tick lines from multiple axes.

    Args:
        axes: List of Axes objects

    Example:
        yp.strip_labels_all(axes)
    """
    for ax in axes:
        strip_labels(ax)


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


def finish(ax: Axes) -> None:
    """
    Re-assert house CHROME style on an already-drawn axes.

    Applies spines, ticks, tick-label fonts/sizes, and axis-label + title
    fonts — exactly the same chrome that apply_style() sets.  Does NOT touch
    data artists (Line2D, PathCollections, patches), so a user's lw=3 line or
    explicitly coloured scatter edge is left intact.

    For seaborn violin glyphs (violin bodies, inner box/whisker/median, strip
    dots) use ``violin()`` from yplot2.plots.statistical.violin, which calls
    ``_normalize_seaborn_glyphs(ax)`` before ``finish(ax)``.

    Idempotent: calling finish() twice yields identical artist properties.

    Args:
        ax: Axes object to finalize.
    """
    cfg = get_config()
    font_family = _resolve_font_family(cfg.font_family)
    # finish passes the global cfg unchanged (no per-call overrides).
    # Flag matrix reproduces current finish behavior exactly:
    #   set_label_fontsizes=False  — finish never sets axis-label fontsizes
    #   set_label_pads=False       — finish never sets labelpads
    #   set_tick_direction=False   — finish never sets tick direction
    #   set_title_fontsize=False   — finish never sets title fontsize
    #   check_preserve_on_ticks=False — finish overwrites tick-label fonts unconditionally
    _enforce_chrome(
        ax,
        cfg,
        font_family,
        set_label_fontsizes=False,
        set_label_pads=False,
        set_tick_direction=False,
        set_title_fontsize=False,
        check_preserve_on_ticks=False,
        apply_fonts=True,
        apply_fontsizes=True,
        preserve_fonts=cfg.preserve_font_families,
    )


def use_style() -> None:
    """
    Push a subset of the house Config into matplotlib rcParams.

    This is the coarse global default for raw escape-hatch plots.  It is NOT
    the per-axes uniformity guarantee — use finish()/apply_style() for that.

    Imports house_palette_colors lazily to avoid a circular import via
    plots/__init__ -> pop_avg.py importing from a partially-initialized style
    module.
    """
    cfg = get_config()
    import matplotlib as mpl
    from matplotlib.rcsetup import cycler  # type: ignore[attr-defined]
    from .plots.colors import house_palette_colors  # lazy — avoids circular import

    mpl.rcParams.update(
        {
            "font.family": _resolve_font_family(cfg.font_family),
            "axes.linewidth": cfg.axis_linewidth,
            "xtick.labelsize": cfg.x_axis_tick_fontsize,
            "ytick.labelsize": cfg.y_axis_tick_fontsize,
            "savefig.dpi": 300,
            "axes.prop_cycle": cycler(color=house_palette_colors()),
        }
    )


@contextmanager
def style() -> Generator[None, None, None]:
    """
    Context manager that applies house rcParams for the duration of the block
    and restores the prior rcParams on exit.

    Example::

        with yp.style():
            fig, ax = plt.subplots()
            ax.plot(x, y)

    The context is coarse (same scope as use_style()) and is NOT a substitute
    for finish()/apply_style() per-axes enforcement.
    """
    import matplotlib as mpl

    saved = dict(mpl.rcParams)
    use_style()
    try:
        yield
    finally:
        mpl.rcParams.update(saved)
