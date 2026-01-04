"""
Plot functions that use global config defaults.

All functions allow overriding any parameter via kwargs.
"""

# Basic plot types
from .basic import (
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
)

# Specialized plot types
from .lollipop import lollipop
from .pop_avg import (
    pop_avg,
    pop_avg_from_row,
    pop_avg_diff,
    pop_avg_all,
    pop_avg_traces,
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
    "pop_avg",
    "pop_avg_from_row",
    "pop_avg_diff",
    "pop_avg_all",
    "pop_avg_traces",
    # Colors
    "colors_for_sequence",
    "NUCLEOTIDE_COLORS",
]
