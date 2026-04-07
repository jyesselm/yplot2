"""Population average plot utilities for RNA reactivity data.

This module provides functions for visualizing RNA chemical probing
data, with nucleotides colored by identity.
"""

from typing import Optional, Union, List, Tuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ..config import get_config
from ..coordinates import Coord, column
from ..figure import create_figure
from ..axes import sequence_structure_x_axis, sequence_x_axis, structure_x_axis
from ..style import apply_style_to_all, clear_axes_all
from .colors import colors_for_sequence
from .basic import text, _merge_args


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
    ax.set_xticklabels(labels, fontsize=cfg.x_axis_tick_fontsize,
                       fontname=cfg.font_family)


def pop_avg(
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
        >>> pop_avg(ax, "ACGU", "(..)", [0.1, 0.2, 0.3, 0.4])
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


def pop_avg_from_row(
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
        **kwargs: Additional arguments passed to pop_avg().

    Returns:
        The matplotlib Axes containing the bar plot.
    """
    return pop_avg(
        ax,
        row["sequence"],
        row["structure"],
        row[data_col],
        **kwargs,
    )


def pop_avg_diff(
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

    pop_avg_from_row(axes[0], row1, data_col=data_col)
    pop_avg_from_row(axes[1], row2, data_col=data_col)

    diff_row = {
        "sequence": row1["sequence"],
        "structure": row1["structure"],
        data_col: np.array(row1[data_col]) - np.array(row2[data_col]),
    }
    pop_avg_from_row(axes[2], diff_row, data_col=data_col)

    return fig


def pop_avg_all(
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
        pop_avg_from_row(axes[j], row, data_col=data_col)
        if "rna_name" in row:
            axes[j].set_title(row["rna_name"])

    return fig


def pop_avg_traces(
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


def stacked_pop_avg(
    df,
    data_col: str = "data",
    height: float = 0.50,
    width: float = 6.6,
    spacing: float = 0.0,
    margins: Tuple[float, float, float, float] = (0.5, 0.5, 0.1, 0.1),
    dpi: int = 200,
    x_delta: int = 1,
    axis: str = "sequence_structure",
    ylim: Optional[Tuple[float, float]] = None,
    yticks: Optional[str] = "max",
    label_col: Optional[str] = None,
    label_suffix: str = "",
    label_args: Optional[dict] = None,
    bar_args: Optional[dict] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    xlabel_args: Optional[dict] = None,
    ylabel_args: Optional[dict] = None,
) -> Tuple[Figure, List[Axes]]:
    """Create stacked population average plots for multiple rows.

    Vertically stacks one pop_avg bar plot per DataFrame row with shared
    x-limits and y-limits.  Only the bottom panel shows x-axis labels.

    Args:
        df: DataFrame with 'sequence', 'structure', and data columns.
        data_col: Column name containing reactivity data. Default 'data'.
        height: Height of each panel in inches. Default 0.50.
        width: Width of each panel in inches. Default 6.6.
        spacing: Vertical spacing between panels in inches. Default 0.0.
        margins: (left, bottom, right, top) margins in inches.
            Default (0.5, 0.5, 0.1, 0.1).
        dpi: Figure resolution. Default 200.
        x_delta: X-axis padding beyond sequence length. Default 1.
        axis: X-axis label type for bottom panel: 'sequence_structure',
            'sequence', or 'structure'. Default 'sequence_structure'.
        ylim: Manual (ymin, ymax). Default None (auto from data).
        yticks: Y-tick display mode. 'max' shows only the max tick
            (default), 'auto' uses matplotlib defaults, None hides ticks.
        label_col: Column name for per-panel text labels (e.g. 'rna_name').
            Default None (no labels).
        label_suffix: String appended to each label (e.g. ' µM', ' nM').
            Default '' (no suffix).
        label_args: Dict of label text options. Keys: pos, fontsize, box,
            box_args, and any kwargs accepted by yp.text(). Default
            pos='top right'.
        bar_args: Dict of bar styling options passed to pop_avg().
        xlabel: Shared x-axis label below the bottom panel (e.g. 'Nucleotides').
            Default None (no label).
        ylabel: Shared y-axis label centered vertically across all panels
            (e.g. 'Mutation Fraction'). Default None (no label).
        xlabel_args: Dict of x-label styling options. Keys: offset (distance
            below bottom panel in inches, default 0.15), fontsize, fontname.
        ylabel_args: Dict of y-label styling options. Keys: offset (distance
            left of panels in inches, default 0.15), fontsize, fontname.

    Returns:
        Tuple of (Figure, list of Axes).

    Example:
        >>> fig, axes = stacked_pop_avg(df)
        >>> fig, axes = stacked_pop_avg(df, height=0.6, width=5.0)
        >>> fig, axes = stacked_pop_avg(df, ylim=(0, 2.0), axis="sequence")
        >>> fig, axes = stacked_pop_avg(df, label_col="rna_name")
        >>> fig, axes = stacked_pop_avg(
        ...     df, xlabel="Nucleotides", ylabel="Mutation Fraction",
        ...     ylabel_args={"offset": 0.25},
        ... )
    """
    n = len(df)
    left, bottom, right, top = margins

    # Build layout
    coords = column(
        n=n,
        size=(width, height),
        spacing=spacing,
        top=top + n * height + (n - 1) * spacing,
        left=left,
    )
    fig_width = left + width + right
    fig_height = bottom + n * height + (n - 1) * spacing + top
    fig, axes = create_figure((fig_width, fig_height), coords, dpi=dpi)

    # Compute shared y-limits
    if ylim is None:
        all_y = np.concatenate(df[data_col].values)
        ymin = 0
        ymax = np.max(all_y) * 1.05
    else:
        ymin, ymax = ylim

    # Clear all axes first (ticks, labels removed)
    clear_axes_all(axes)

    # Resolve bar_args
    _bar_args = _merge_args({}, bar_args)

    # Resolve label_args
    _label_args = _merge_args({"pos": "top right"}, label_args)

    # Plot each row
    for j, (_, row) in enumerate(df.iterrows()):
        pop_avg_from_row(axes[j], row, data_col=data_col, **_bar_args)

        seq = row["sequence"]
        axes[j].set_xlim(-x_delta, len(seq) - 1 + x_delta)
        axes[j].set_ylim(ymin, ymax)

        # Y-ticks
        if yticks == "max":
            label_y = np.round(ymax, 2)
            axes[j].set_yticks([0, ymax], ["", label_y])
        elif yticks is None:
            axes[j].set_yticks([])

        # Per-panel label
        if label_col is not None and label_col in row:
            text(axes[j], f"{row[label_col]}{label_suffix}", **_label_args)

    # Bottom panel gets x-axis labels
    last_row = df.iloc[-1]
    if axis == "sequence_structure":
        sequence_structure_x_axis(axes[-1], last_row["sequence"], last_row["structure"])
    elif axis == "sequence":
        sequence_x_axis(axes[-1], last_row["sequence"])
    elif axis == "structure":
        structure_x_axis(axes[-1], last_row["structure"])

    apply_style_to_all(axes)

    cfg = get_config()

    # Shared y-label: centered vertically across all panels, to the left
    if ylabel is not None:
        _ylabel_args = _merge_args({
            "offset": 0.15,
            "fontsize": cfg.y_axis_label_fontsize,
            "fontname": cfg.font_family,
        }, ylabel_args)
        ylabel_offset = _ylabel_args.pop("offset")

        panels_bottom = coords[-1].bottom / fig_height
        panels_top = coords[0].top / fig_height
        center_y = (panels_bottom + panels_top) / 2
        x_pos = (left - ylabel_offset) / fig_width
        fig.text(
            x_pos, center_y, ylabel,
            ha="center",
            va="center",
            rotation=90,
            **_ylabel_args,
        )

    # Shared x-label: centered below the bottom panel
    if xlabel is not None:
        _xlabel_args = _merge_args({
            "offset": 0.15,
            "fontsize": cfg.x_axis_label_fontsize,
            "fontname": cfg.font_family,
        }, xlabel_args)
        xlabel_offset = _xlabel_args.pop("offset")

        bottom_coord = coords[-1]
        center_x = (bottom_coord.left + bottom_coord.right) / 2 / fig_width
        y_pos = (bottom_coord.bottom - xlabel_offset) / fig_height
        fig.text(
            center_x, y_pos, xlabel,
            ha="center",
            va="top",
            **_xlabel_args,
        )

    return fig, axes
