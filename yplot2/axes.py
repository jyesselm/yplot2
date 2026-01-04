"""
Axes grouping and shared axis utilities.

Functions for linking axes that share common x or y axes.
"""

from typing import List, Optional, Tuple, Union
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .coordinates import Coord


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
