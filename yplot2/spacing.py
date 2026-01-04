"""
Spacing calculation utilities.

Functions to calculate ideal spacing or subplot sizes given constraints.
"""

from typing import Optional, Tuple, Union


def fit_row_spacing(
    fig_width: float,
    n: int,
    subplot_width: float,
    margins: Tuple[float, float],
) -> float:
    """
    Calculate the spacing needed to evenly distribute N subplots across a figure width.

    Args:
        fig_width: Total figure width in inches
        n: Number of subplots
        subplot_width: Width of each subplot in inches
        margins: (left_margin, right_margin) in inches

    Returns:
        Spacing between subplots in inches

    Raises:
        ValueError: If subplots cannot fit even with zero spacing
    """
    left_margin, right_margin = margins
    available_width = fig_width - left_margin - right_margin
    total_subplot_width = n * subplot_width

    if total_subplot_width > available_width:
        raise ValueError(
            f"Subplots ({total_subplot_width:.2f}\") don't fit in available "
            f"width ({available_width:.2f}\"). Reduce subplot_width or margins."
        )

    if n <= 1:
        return 0.0

    remaining_space = available_width - total_subplot_width
    spacing = remaining_space / (n - 1)
    return spacing


def fit_column_spacing(
    fig_height: float,
    n: int,
    subplot_height: float,
    margins: Tuple[float, float],
) -> float:
    """
    Calculate the spacing needed to evenly distribute N subplots vertically.

    Args:
        fig_height: Total figure height in inches
        n: Number of subplots
        subplot_height: Height of each subplot in inches
        margins: (bottom_margin, top_margin) in inches

    Returns:
        Spacing between subplots in inches

    Raises:
        ValueError: If subplots cannot fit even with zero spacing
    """
    bottom_margin, top_margin = margins
    available_height = fig_height - bottom_margin - top_margin
    total_subplot_height = n * subplot_height

    if total_subplot_height > available_height:
        raise ValueError(
            f"Subplots ({total_subplot_height:.2f}\") don't fit in available "
            f"height ({available_height:.2f}\"). Reduce subplot_height or margins."
        )

    if n <= 1:
        return 0.0

    remaining_space = available_height - total_subplot_height
    spacing = remaining_space / (n - 1)
    return spacing


def fit_subplot_width(
    fig_width: float,
    n: int,
    spacing: float,
    margins: Tuple[float, float],
) -> float:
    """
    Calculate subplot width to fit N subplots with given spacing.

    Args:
        fig_width: Total figure width in inches
        n: Number of subplots
        spacing: Desired spacing between subplots in inches
        margins: (left_margin, right_margin) in inches

    Returns:
        Width for each subplot in inches

    Raises:
        ValueError: If no positive width is possible
    """
    left_margin, right_margin = margins
    available_width = fig_width - left_margin - right_margin
    total_spacing = (n - 1) * spacing if n > 1 else 0

    remaining_for_subplots = available_width - total_spacing
    if remaining_for_subplots <= 0:
        raise ValueError(
            f"No room for subplots. Available: {available_width:.2f}\", "
            f"spacing requires: {total_spacing:.2f}\""
        )

    subplot_width = remaining_for_subplots / n
    return subplot_width


def fit_subplot_height(
    fig_height: float,
    n: int,
    spacing: float,
    margins: Tuple[float, float],
) -> float:
    """
    Calculate subplot height to fit N subplots vertically with given spacing.

    Args:
        fig_height: Total figure height in inches
        n: Number of subplots
        spacing: Desired spacing between subplots in inches
        margins: (bottom_margin, top_margin) in inches

    Returns:
        Height for each subplot in inches

    Raises:
        ValueError: If no positive height is possible
    """
    bottom_margin, top_margin = margins
    available_height = fig_height - bottom_margin - top_margin
    total_spacing = (n - 1) * spacing if n > 1 else 0

    remaining_for_subplots = available_height - total_spacing
    if remaining_for_subplots <= 0:
        raise ValueError(
            f"No room for subplots. Available: {available_height:.2f}\", "
            f"spacing requires: {total_spacing:.2f}\""
        )

    subplot_height = remaining_for_subplots / n
    return subplot_height


def check_fit(
    fig_size: Tuple[float, float],
    coords_list: list,
) -> dict:
    """
    Check if coordinates fit within figure bounds.

    Args:
        fig_size: (width, height) of figure in inches
        coords_list: List of Coord objects

    Returns:
        Dictionary with:
            - 'fits': bool, True if all coords fit
            - 'issues': list of strings describing any fit problems
    """
    fig_width, fig_height = fig_size
    issues = []

    for i, coord in enumerate(coords_list):
        if coord.left < 0:
            issues.append(f"Coord {i}: left edge ({coord.left:.2f}\") is negative")
        if coord.bottom < 0:
            issues.append(f"Coord {i}: bottom edge ({coord.bottom:.2f}\") is negative")
        if coord.right > fig_width:
            issues.append(
                f"Coord {i}: right edge ({coord.right:.2f}\") exceeds "
                f"figure width ({fig_width:.2f}\")"
            )
        if coord.top > fig_height:
            issues.append(
                f"Coord {i}: top edge ({coord.top:.2f}\") exceeds "
                f"figure height ({fig_height:.2f}\")"
            )

    return {
        'fits': len(issues) == 0,
        'issues': issues,
    }


def suggest_figure_size(
    coords_list: list,
    margins: Tuple[float, float, float, float] = (0.5, 0.5, 0.5, 0.5),
) -> Tuple[float, float]:
    """
    Suggest minimum figure size to fit all coordinates.

    Args:
        coords_list: List of Coord objects
        margins: (left, right, bottom, top) margins in inches

    Returns:
        (width, height) of minimum figure size in inches
    """
    if not coords_list:
        left_m, right_m, bottom_m, top_m = margins
        return (left_m + right_m, bottom_m + top_m)

    left_m, right_m, bottom_m, top_m = margins

    max_right = max(c.right for c in coords_list)
    max_top = max(c.top for c in coords_list)

    # Account for any coords that might have negative positions
    min_left = min(c.left for c in coords_list)
    min_bottom = min(c.bottom for c in coords_list)

    width = max_right + right_m - min(0, min_left - left_m)
    height = max_top + top_m - min(0, min_bottom - bottom_m)

    return (width, height)
