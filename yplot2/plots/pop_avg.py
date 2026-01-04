"""Population average plot utilities for RNA reactivity data.

This module provides functions for visualizing RNA chemical probing
data, with nucleotides colored by identity.
"""

from typing import Optional, Union, List

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ..config import get_config
from .colors import colors_for_sequence


def _apply_x_axis_by_name(
    ax: Axes,
    sequence: str,
    structure: str,
    axis: str = "sequence_structure",
) -> None:
    """
    Apply x-axis labels based on sequence and/or structure.

    Args:
        ax: Axes object.
        sequence: RNA sequence string.
        structure: Secondary structure string.
        axis: Label type - "sequence_structure", "sequence", or "structure".
    """
    cfg = get_config()
    n = len(sequence)

    if axis == "sequence_structure":
        # Two-line labels: sequence on top, structure below
        labels = [f"{sequence[i]}\n{structure[i]}" for i in range(n)]
    elif axis == "sequence":
        labels = list(sequence)
    elif axis == "structure":
        labels = list(structure)
    else:
        raise ValueError(f"Unknown axis type: {axis}. "
                        f"Use 'sequence_structure', 'sequence', or 'structure'.")

    ax.set_xticks(range(n))
    ax.set_xticklabels(labels, fontsize=cfg.axis_tick_fontsize,
                       fontname=cfg.font_family)


def plot_pop_avg(
    ax: Axes,
    sequence: str,
    structure: str,
    reactivities: List[float],
    axis: str = "sequence_structure",
    **kwargs,
) -> Axes:
    """
    Plot population average reactivities for an RNA sequence.

    Each nucleotide is colored by identity, with the x-axis showing
    sequence and/or structure information.

    Args:
        ax: Matplotlib Axes to plot on.
        sequence: The RNA sequence.
        structure: The secondary structure string.
        reactivities: Reactivity values for each nucleotide.
        axis: X-axis type: "sequence_structure", "sequence", or "structure".
        **kwargs: Additional arguments passed to ax.bar().

    Returns:
        The matplotlib Axes containing the bar plot.

    Example:
        >>> fig, ax = plt.subplots()
        >>> plot_pop_avg(ax, "ACGU", "(..)", [0.1, 0.2, 0.3, 0.4])
    """
    cfg = get_config()

    sequence = sequence.replace("U", "T")
    colors = colors_for_sequence(sequence)

    # Set defaults from config
    linewidth = kwargs.pop('linewidth', cfg.axis_linewidth)

    ax.bar(range(len(reactivities)), reactivities, color=colors,
           linewidth=linewidth, **kwargs)
    _apply_x_axis_by_name(ax, sequence, structure, axis)

    return ax


def plot_pop_avg_from_row(
    ax: Axes,
    row: dict,
    data_col: str = "data",
    **kwargs,
) -> Axes:
    """
    Plot population average from a data row.

    Args:
        ax: Matplotlib Axes to plot on.
        row: Dictionary-like object with 'sequence', 'structure', and data.
        data_col: Column name containing reactivity data.
        **kwargs: Additional arguments passed to plot_pop_avg().

    Returns:
        The matplotlib Axes containing the bar plot.
    """
    return plot_pop_avg(
        ax,
        row["sequence"],
        row["structure"],
        row[data_col],
        **kwargs,
    )


def plot_pop_avg_diff_from_rows(
    row1: dict,
    row2: dict,
    data_col: str = "data",
    axes: Optional[Union[List[Axes], np.ndarray]] = None,
    **kwargs,
) -> Figure:
    """
    Plot population average difference between two conditions.

    Creates three panels: row1 data, row2 data, and their difference.

    Args:
        row1: First data row.
        row2: Second data row.
        data_col: Column name containing reactivity data.
        axes: Array of 3 axes to plot on.
        **kwargs: Additional arguments for plt.subplots().

    Returns:
        The matplotlib Figure containing the plots.
    """
    if axes is None:
        fig, axes = plt.subplots(3, 1, **kwargs)
    else:
        fig = axes[0].get_figure()

    plot_pop_avg_from_row(axes[0], row1, data_col=data_col)
    plot_pop_avg_from_row(axes[1], row2, data_col=data_col)

    diff_row = {
        "sequence": row1["sequence"],
        "structure": row1["structure"],
        data_col: np.array(row1[data_col]) - np.array(row2[data_col]),
    }
    plot_pop_avg_from_row(axes[2], diff_row, data_col=data_col)

    return fig


def plot_pop_avg_all(
    df,
    data_col: str = "data",
    axes: Optional[Union[List[Axes], np.ndarray]] = None,
    **kwargs,
) -> Figure:
    """
    Plot population average for each row in a DataFrame.

    Args:
        df: DataFrame with sequence, structure, and data columns.
        data_col: Column name containing reactivity data.
        axes: Array of axes to plot on (one per row).
        **kwargs: Additional arguments for plt.subplots().

    Returns:
        The matplotlib Figure containing all plots.
    """
    n = len(df)
    if axes is None:
        fig, axes = plt.subplots(n, 1, **kwargs)
    else:
        fig = axes[0].get_figure()

    if n == 1 and not isinstance(axes, (list, np.ndarray)):
        axes = [axes]

    for j, (_, row) in enumerate(df.iterrows()):
        plot_pop_avg_from_row(axes[j], row, data_col=data_col)
        if "rna_name" in row:
            axes[j].set_title(row["rna_name"])

    return fig


def plot_pop_avg_traces(
    ax: Axes,
    df,
    data_col: str = "data",
    label_col: str = "rna_name",
    **kwargs,
) -> Axes:
    """
    Plot overlaid population average traces for all rows.

    Args:
        ax: Matplotlib Axes to plot on.
        df: DataFrame with data and label columns.
        data_col: Column containing trace data.
        label_col: Column containing trace labels.
        **kwargs: Additional arguments passed to ax.plot().

    Returns:
        The matplotlib Axes containing the traces.
    """
    cfg = get_config()
    linewidth = kwargs.pop('linewidth', cfg.plot_linewidth)

    for _, row in df.iterrows():
        ax.plot(row[data_col], label=row[label_col], linewidth=linewidth, **kwargs)

    return ax
