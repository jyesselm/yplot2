"""
Axes grouping and shared axis utilities.

Functions for linking axes, log scales with zero handling,
and sequence/structure axis formatting.
"""

from typing import List, Optional, Tuple, Union, Sequence

import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import FixedLocator, FuncFormatter

from .coordinates import Coord
from .config import get_config


def share_x(
    axes_list: List[Axes],
    label: Optional[str] = None,
    keep_labels: str = "bottom",
) -> None:
    """
    Link axes to share x-axis. Hides redundant tick labels.

    Args:
        axes_list: List of Axes that share x-axis (should be in a column)
        label: Optional shared x-axis label (added to bottom axes only)
        keep_labels: Which axes keeps tick labels: "bottom", "top", "all", "none"
    """
    if not axes_list:
        return

    # Find the bottom-most axes (lowest position)
    bottom_ax = min(axes_list, key=lambda ax: ax.get_position().y0)
    top_ax = max(axes_list, key=lambda ax: ax.get_position().y0)

    for ax in axes_list:
        if keep_labels == "bottom" and ax != bottom_ax:
            ax.tick_params(labelbottom=False)
            ax.set_xlabel("")
        elif keep_labels == "top" and ax != top_ax:
            ax.tick_params(labelbottom=False)
            ax.set_xlabel("")
        elif keep_labels == "none":
            ax.tick_params(labelbottom=False)
            ax.set_xlabel("")

    if label:
        if keep_labels == "top":
            top_ax.set_xlabel(label)
        else:
            bottom_ax.set_xlabel(label)


def share_y(
    axes_list: List[Axes],
    label: Optional[str] = None,
    keep_labels: str = "left",
) -> None:
    """
    Link axes to share y-axis. Hides redundant tick labels.

    Args:
        axes_list: List of Axes that share y-axis (should be in a row)
        label: Optional shared y-axis label (added to leftmost axes only)
        keep_labels: Which axes keeps tick labels: "left", "right", "all", "none"
    """
    if not axes_list:
        return

    # Find the leftmost axes
    left_ax = min(axes_list, key=lambda ax: ax.get_position().x0)
    right_ax = max(axes_list, key=lambda ax: ax.get_position().x0)

    for ax in axes_list:
        if keep_labels == "left" and ax != left_ax:
            ax.tick_params(labelleft=False)
            ax.set_ylabel("")
        elif keep_labels == "right" and ax != right_ax:
            ax.tick_params(labelleft=False)
            ax.set_ylabel("")
        elif keep_labels == "none":
            ax.tick_params(labelleft=False)
            ax.set_ylabel("")

    if label:
        if keep_labels == "right":
            right_ax.set_ylabel(label)
        else:
            left_ax.set_ylabel(label)


def sync_limits(
    axes_list: List[Axes],
    axis: str = "both",
) -> None:
    """
    Synchronize axis limits across multiple axes.

    Args:
        axes_list: List of Axes to synchronize
        axis: Which axis to sync: "x", "y", or "both"
    """
    if not axes_list:
        return

    if axis in ("x", "both"):
        xlims = [ax.get_xlim() for ax in axes_list]
        xmin = min(lim[0] for lim in xlims)
        xmax = max(lim[1] for lim in xlims)
        for ax in axes_list:
            ax.set_xlim(xmin, xmax)

    if axis in ("y", "both"):
        ylims = [ax.get_ylim() for ax in axes_list]
        ymin = min(lim[0] for lim in ylims)
        ymax = max(lim[1] for lim in ylims)
        for ax in axes_list:
            ax.set_ylim(ymin, ymax)


def add_shared_xlabel(
    fig: Figure,
    coords: List[Coord],
    fig_size: Tuple[float, float],
    label: str,
    fontsize: int = 8,
    fontname: str = "Arial",
    offset: float = 0.35,
) -> None:
    """
    Add a shared x-axis label below a group of panels.

    Args:
        fig: Figure object
        coords: List of Coord objects in the group
        fig_size: (width, height) of figure in inches
        label: The label text
        fontsize: Font size
        fontname: Font family
        offset: Distance below the lowest panel in inches
    """
    fig_width, fig_height = fig_size

    # Find extent of the group
    left = min(c.left for c in coords)
    right = max(c.right for c in coords)
    bottom = min(c.bottom for c in coords)

    # Center x position
    center_x = (left + right) / 2 / fig_width
    y_pos = (bottom - offset) / fig_height

    fig.text(
        center_x, y_pos, label,
        fontsize=fontsize,
        fontname=fontname,
        ha="center",
        va="top",
    )


def add_shared_ylabel(
    fig: Figure,
    coords: List[Coord],
    fig_size: Tuple[float, float],
    label: str,
    fontsize: int = 8,
    fontname: str = "Arial",
    offset: float = 0.35,
) -> None:
    """
    Add a shared y-axis label to the left of a group of panels.

    Args:
        fig: Figure object
        coords: List of Coord objects in the group
        fig_size: (width, height) of figure in inches
        label: The label text
        fontsize: Font size
        fontname: Font family
        offset: Distance to the left of the leftmost panel in inches
    """
    fig_width, fig_height = fig_size

    # Find extent of the group
    left = min(c.left for c in coords)
    bottom = min(c.bottom for c in coords)
    top = max(c.top for c in coords)

    # Center y position
    x_pos = (left - offset) / fig_width
    center_y = (bottom + top) / 2 / fig_height

    fig.text(
        x_pos, center_y, label,
        fontsize=fontsize,
        fontname=fontname,
        ha="center",
        va="center",
        rotation=90,
    )


def group_grid(
    axes_grid: List[List[Axes]],
    share_x: bool = True,
    share_y: bool = True,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
) -> None:
    """
    Configure a grid of axes to share x and/or y axes.

    Args:
        axes_grid: 2D list of Axes, axes_grid[row][col]
        share_x: If True, columns share x-axis (hide labels except bottom)
        share_y: If True, rows share y-axis (hide labels except left)
        x_label: Optional shared x-label for bottom row
        y_label: Optional shared y-label for left column
    """
    if not axes_grid or not axes_grid[0]:
        return

    n_rows = len(axes_grid)
    n_cols = len(axes_grid[0])

    if share_x:
        # For each column, share x among all rows
        for col in range(n_cols):
            column_axes = [axes_grid[row][col] for row in range(n_rows)]
            for row, ax in enumerate(column_axes):
                if row < n_rows - 1:  # Not bottom row
                    ax.tick_params(labelbottom=False)
                    ax.set_xlabel("")

        # Add x_label to bottom row center (if provided)
        if x_label:
            bottom_row = axes_grid[-1]
            # Add to middle axes of bottom row
            mid_ax = bottom_row[n_cols // 2]
            mid_ax.set_xlabel(x_label)

    if share_y:
        # For each row, share y among all columns
        for row in range(n_rows):
            row_axes = axes_grid[row]
            for col, ax in enumerate(row_axes):
                if col > 0:  # Not leftmost column
                    ax.tick_params(labelleft=False)
                    ax.set_ylabel("")

        # Add y_label to left column center (if provided)
        if y_label:
            left_col = [axes_grid[row][0] for row in range(n_rows)]
            mid_ax = left_col[n_rows // 2]
            mid_ax.set_ylabel(y_label)


# =============================================================================
# Logarithmic axis utilities with zero handling
# =============================================================================

def compute_eps_and_transform(
    x: np.ndarray,
    epsilon_factor: float = 0.1,
) -> Tuple[float, np.ndarray, np.ndarray]:
    """
    Compute epsilon value and transform data for log scale with zeros.

    Args:
        x: Input array that may contain zeros.
        epsilon_factor: Factor to multiply minimum positive value (default: 0.1).

    Returns:
        Tuple of (epsilon, positive_values, transformed_x) where:
            - epsilon: Small value representing zero on log scale
            - positive_values: Array of positive values from x
            - transformed_x: x with zeros replaced by epsilon

    Raises:
        ValueError: If all x values are zero.

    Example:
        >>> x = np.array([0, 0.1, 1, 10])
        >>> eps, pos, x_plot = compute_eps_and_transform(x)
    """
    positive = x[x > 0]
    if positive.size == 0:
        raise ValueError("All x values are zero; cannot use log scale.")

    eps = epsilon_factor * float(np.min(positive))
    x_transformed = x.copy()
    x_transformed[x_transformed <= 0] = eps

    return eps, positive, x_transformed


def log_axis_with_zero(
    ax: Axes,
    eps: float,
    positive_values: np.ndarray,
    decade_ticks: Optional[Sequence[float]] = None,
    left_pad: float = 1.5,
    right_pad: float = 1.5,
) -> None:
    """
    Configure log scale x-axis with zero represented at epsilon.

    Args:
        ax: The matplotlib Axes object to modify.
        eps: Epsilon value representing zero.
        positive_values: Array of positive data values.
        decade_ticks: Optional list of decade tick positions.
        left_pad: Left padding factor for x-limits.
        right_pad: Right padding factor for x-limits.

    Example:
        >>> eps, pos, x_plot = compute_eps_and_transform(data)
        >>> ax.scatter(x_plot, y)
        >>> log_axis_with_zero(ax, eps, pos)
    """
    ax.set_xscale("log")

    tick_positions = _compute_tick_positions(eps, positive_values, decade_ticks)
    ax.xaxis.set_major_locator(FixedLocator(tick_positions))

    ax.xaxis.set_major_formatter(FuncFormatter(lambda val, _: _format_tick(val, eps)))
    ax.set_xlim(eps / left_pad, float(np.max(positive_values)) * right_pad)


def _compute_tick_positions(
    eps: float,
    positive_values: np.ndarray,
    decade_ticks: Optional[Sequence[float]],
) -> list:
    """Compute tick positions for log axis."""
    if decade_ticks is None:
        lo_pow = int(np.floor(np.log10(max(eps, float(np.min(positive_values)) * 0.8))))
        hi_pow = int(np.ceil(np.log10(float(np.max(positive_values)) * 1.2)))
        decade_ticks = [10.0**p for p in range(lo_pow, hi_pow + 1)]

    max_val = float(np.max(positive_values)) * 1.05
    filtered = [t for t in decade_ticks if eps <= t <= max_val]
    return [eps] + filtered


def _format_tick(val: float, eps: float) -> str:
    """Format tick label, showing '0' for epsilon value."""
    if np.isclose(val, eps):
        return "0"
    return f"{val:g}"


# =============================================================================
# Sequence and structure axis formatting
# =============================================================================

def sequence_x_axis(
    ax: Axes,
    sequence: str,
    x_delta: int = 1,
) -> Axes:
    """
    Set x-axis to display nucleotide sequence.

    Args:
        ax: The matplotlib Axes object to modify.
        sequence: The RNA or DNA sequence string.
        x_delta: Padding around sequence bounds (default: 1).

    Returns:
        The modified matplotlib Axes object.

    Example:
        >>> fig, ax = plt.subplots()
        >>> sequence_x_axis(ax, "ACGU")
    """
    cfg = get_config()
    ax.set_xticks(range(len(sequence)))
    ax.set_xticklabels(list(sequence), fontsize=cfg.x_axis_tick_fontsize,
                       fontname=cfg.font_family)
    ax.set_xlim(-x_delta, len(sequence) - 1 + x_delta)
    return ax


def structure_x_axis(
    ax: Axes,
    structure: str,
    x_delta: int = 1,
) -> Axes:
    """
    Set x-axis to display secondary structure notation.

    Args:
        ax: The matplotlib Axes object to modify.
        structure: The secondary structure string (dot-bracket notation).
        x_delta: Padding around structure bounds (default: 1).

    Returns:
        The modified matplotlib Axes object.

    Example:
        >>> fig, ax = plt.subplots()
        >>> structure_x_axis(ax, "(((.)))")
    """
    cfg = get_config()
    ax.set_xticks(range(len(structure)))
    ax.set_xticklabels(list(structure), fontsize=cfg.x_axis_tick_fontsize,
                       fontname=cfg.font_family)
    ax.set_xlim(-x_delta, len(structure) - 1 + x_delta)
    return ax


def sequence_structure_x_axis(
    ax: Axes,
    sequence: str,
    structure: str,
    x_delta: int = 1,
) -> Axes:
    """
    Set x-axis to display both sequence and structure.

    Each tick label shows the nucleotide with structure character below.

    Args:
        ax: The matplotlib Axes object to modify.
        sequence: The RNA or DNA sequence string.
        structure: The secondary structure string (same length as sequence).
        x_delta: Padding around bounds (default: 1).

    Returns:
        The modified matplotlib Axes object.

    Example:
        >>> fig, ax = plt.subplots()
        >>> sequence_structure_x_axis(ax, "ACGU", "(((.")
    """
    cfg = get_config()
    labels = [f"{seq}\n{struct}" for seq, struct in zip(sequence, structure)]
    ax.set_xticks(range(len(sequence)))
    ax.set_xticklabels(labels, fontsize=cfg.x_axis_tick_fontsize,
                       fontname=cfg.font_family)
    ax.set_xlim(-x_delta, len(sequence) - 1 + x_delta)
    return ax


def apply_x_axis_format(
    ax: Axes,
    sequence: str,
    structure: str,
    axis_type: str,
) -> Axes:
    """
    Apply x-axis labeling strategy by name.

    Args:
        ax: The matplotlib Axes to modify.
        sequence: Sequence string.
        structure: Structure string.
        axis_type: One of "sequence_structure", "sequence", "structure".

    Returns:
        The modified matplotlib Axes.

    Raises:
        ValueError: If axis_type is not recognized.

    Example:
        >>> apply_x_axis_format(ax, "ACGU", "(..)", "sequence_structure")
    """
    if axis_type == "sequence_structure":
        return sequence_structure_x_axis(ax, sequence, structure)
    elif axis_type == "sequence":
        return sequence_x_axis(ax, sequence)
    elif axis_type == "structure":
        return structure_x_axis(ax, structure)
    else:
        raise ValueError(
            f"Unknown axis_type: {axis_type}. "
            f"Use 'sequence_structure', 'sequence', or 'structure'."
        )
