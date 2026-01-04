"""
Plot functions that use global config defaults.

All functions allow overriding any parameter via kwargs.
"""

# Basic plot types
from .scatter import scatter
from .line import line
from .bar import bar, barh
from .errorbar import errorbar
from .fill import fill_between
from .hist import hist
from .boxplot import boxplot
from .reference import hline, vline
from .text import text

# Specialized plot types
from .lollipop import lollipop
from .pop_avg import (
    plot_pop_avg,
    plot_pop_avg_from_row,
    plot_pop_avg_diff_from_rows,
    plot_pop_avg_all,
    plot_pop_avg_traces,
)

# Color utilities
from .colors import colors_for_sequence, NUCLEOTIDE_COLORS

__all__ = [
    # Basic plots
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
    "plot_pop_avg",
    "plot_pop_avg_from_row",
    "plot_pop_avg_diff_from_rows",
    "plot_pop_avg_all",
    "plot_pop_avg_traces",
    # Colors
    "colors_for_sequence",
    "NUCLEOTIDE_COLORS",
]
