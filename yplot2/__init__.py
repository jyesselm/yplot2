"""
yplot2 - Matplotlib subplot layout with absolute positioning and helper tools.

All dimensions are in inches.

Example usage:

    import yplot2 as yp

    # Define panel a
    a = yp.Coord(left=0.5, bottom=7.2, width=2.8, height=1.5)

    # Panel b: same size as a, 0.5" to the right
    b = yp.right_of(a, spacing=0.5)

    # Panel c: below a
    c = yp.below(a, spacing=0.5)

    # Create figure with all panels
    fig_size = (7.5, 9.0)
    fig, axes = yp.create_figure(fig_size, [a, b, c])

    # Apply publication styling
    yp.apply_style_to_all(axes)

    # Add panel labels
    yp.add_labels(fig, [a, b, c], fig_size, start="a")
"""

__version__ = "0.1.0"

# Configuration
from .config import (
    Config,
    get_config,
    set_config,
    get_config_value,
    list_config_options,
    reset_config,
    print_config,
    use_preset,
    list_presets,
)

# Core coordinate type
from .coordinates import Coord

# Coordinate generators
from .coordinates import row, column, grid, flatten_grid

# Layout management
from .layout import Layout, Panel

# Relative positioning helpers
from .position import (
    right_of,
    left_of,
    below,
    above,
    copy,
    same_size,
    resize,
    shift,
)

# Spacing calculations
from .spacing import (
    fit_row_spacing,
    fit_column_spacing,
    fit_subplot_width,
    fit_subplot_height,
    check_fit,
    suggest_figure_size,
)

# Figure creation and utilities
from .figure import (
    create_figure,
    get_image_size,
    coord_from_image,
    load_image,
    make_image_panel,
    add_labels,
    draw_debug_boxes,
    draw_figure_border,
    add_colorbar,
)

# Axes grouping and shared axes
from .axes import (
    share_x,
    share_y,
    sync_limits,
    add_shared_xlabel,
    add_shared_ylabel,
    group_grid,
    # Log axis with zero handling
    compute_eps_and_transform,
    log_axis_with_zero,
    # Sequence/structure axis formatting
    sequence_x_axis,
    structure_x_axis,
    sequence_structure_x_axis,
    apply_x_axis_format,
)

# Styling
from .style import (
    apply_style,
    apply_style_to_all,
    publication_style,  # alias for apply_style
    remove_spines,
    add_legend,
    add_legend_above,
    set_xlabel,
    set_ylabel,
    set_title,
    set_background,
    set_background_all,
)

# Plot functions (use global config)
from .plots import (
    # Basic plots
    scatter,
    line,
    bar,
    barh,
    errorbar,
    fill_between,
    hist,
    boxplot,
    hline,
    vline,
    text,
    # Specialized plots
    lollipop,
    pop_avg,
    pop_avg_from_row,
    pop_avg_diff,
    pop_avg_all,
    pop_avg_traces,
    # Color utilities
    colors_for_sequence,
    NUCLEOTIDE_COLORS,
)

__all__ = [
    # Version
    "__version__",
    # Config
    "Config",
    "get_config",
    "set_config",
    "get_config_value",
    "list_config_options",
    "reset_config",
    "print_config",
    "use_preset",
    "list_presets",
    # Core type
    "Coord",
    # Layout
    "Layout",
    "Panel",
    # Generators
    "row",
    "column",
    "grid",
    "flatten_grid",
    # Positioning
    "right_of",
    "left_of",
    "below",
    "above",
    "copy",
    "same_size",
    "resize",
    "shift",
    # Spacing
    "fit_row_spacing",
    "fit_column_spacing",
    "fit_subplot_width",
    "fit_subplot_height",
    "check_fit",
    "suggest_figure_size",
    # Figure
    "create_figure",
    "get_image_size",
    "coord_from_image",
    "load_image",
    "make_image_panel",
    "add_labels",
    "draw_debug_boxes",
    "draw_figure_border",
    "add_colorbar",
    # Axes grouping
    "share_x",
    "share_y",
    "sync_limits",
    "add_shared_xlabel",
    "add_shared_ylabel",
    "group_grid",
    # Log axis with zero handling
    "compute_eps_and_transform",
    "log_axis_with_zero",
    # Sequence/structure axis formatting
    "sequence_x_axis",
    "structure_x_axis",
    "sequence_structure_x_axis",
    "apply_x_axis_format",
    # Style
    "apply_style",
    "apply_style_to_all",
    "publication_style",
    "remove_spines",
    "add_legend",
    "add_legend_above",
    "set_xlabel",
    "set_ylabel",
    "set_title",
    "set_background",
    "set_background_all",
    # Basic plot functions
    "scatter",
    "line",
    "bar",
    "barh",
    "errorbar",
    "fill_between",
    "hist",
    "boxplot",
    "hline",
    "vline",
    "text",
    # Specialized plots
    "lollipop",
    "pop_avg",
    "pop_avg_from_row",
    "pop_avg_diff",
    "pop_avg_all",
    "pop_avg_traces",
    # Color utilities
    "colors_for_sequence",
    "NUCLEOTIDE_COLORS",
]
