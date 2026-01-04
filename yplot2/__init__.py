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

# Core coordinate type
from .coordinates import Coord

# Coordinate generators
from .coordinates import row, column, grid, flatten_grid

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
    load_image,
    add_labels,
    draw_debug_boxes,
    add_colorbar,
)

# Styling
from .style import (
    publication_style,
    apply_style_to_all,
    remove_spines,
    add_legend,
    scatter,
    line,
)

__all__ = [
    # Version
    "__version__",
    # Core type
    "Coord",
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
    "load_image",
    "add_labels",
    "draw_debug_boxes",
    "add_colorbar",
    # Style
    "publication_style",
    "apply_style_to_all",
    "remove_spines",
    "add_legend",
    "scatter",
    "line",
]
