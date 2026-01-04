"""
Core coordinate types and generators for subplot layouts.

All dimensions are in inches.
"""

from typing import NamedTuple, List, Optional, Tuple, Union


class Coord(NamedTuple):
    """
    Subplot coordinate in inches.

    Attributes:
        left: Distance from left edge of figure (inches)
        bottom: Distance from bottom edge of figure (inches)
        width: Width of subplot (inches)
        height: Height of subplot (inches)
    """
    left: float
    bottom: float
    width: float
    height: float

    @property
    def right(self) -> float:
        """Right edge position (inches)."""
        return self.left + self.width

    @property
    def top(self) -> float:
        """Top edge position (inches)."""
        return self.bottom + self.height

    @property
    def center_x(self) -> float:
        """Horizontal center position (inches)."""
        return self.left + self.width / 2

    @property
    def center_y(self) -> float:
        """Vertical center position (inches)."""
        return self.bottom + self.height / 2

    def to_relative(self, fig_width: float, fig_height: float) -> Tuple[float, float, float, float]:
        """
        Convert to figure-relative coordinates (0-1).

        Args:
            fig_width: Figure width in inches
            fig_height: Figure height in inches

        Returns:
            Tuple of (left, bottom, width, height) in relative units (0-1)
        """
        return (
            self.left / fig_width,
            self.bottom / fig_height,
            self.width / fig_width,
            self.height / fig_height,
        )


def row(
    n: int,
    size: Tuple[float, float],
    spacing: float,
    left: float,
    bottom: float,
) -> List[Coord]:
    """
    Generate a row of equally-spaced subplots.

    Args:
        n: Number of subplots
        size: (width, height) of each subplot in inches
        spacing: Horizontal spacing between subplots in inches
        left: Left edge of first subplot in inches
        bottom: Bottom edge of all subplots in inches

    Returns:
        List of Coord objects for each subplot
    """
    width, height = size
    coords = []
    for i in range(n):
        coord = Coord(
            left=left + i * (width + spacing),
            bottom=bottom,
            width=width,
            height=height,
        )
        coords.append(coord)
    return coords


def column(
    n: int,
    size: Tuple[float, float],
    spacing: float,
    left: float,
    top: float,
) -> List[Coord]:
    """
    Generate a column of equally-spaced subplots (top to bottom).

    Args:
        n: Number of subplots
        size: (width, height) of each subplot in inches
        spacing: Vertical spacing between subplots in inches
        left: Left edge of all subplots in inches
        top: Top edge of first subplot in inches

    Returns:
        List of Coord objects for each subplot (top to bottom)
    """
    width, height = size
    coords = []
    for i in range(n):
        coord = Coord(
            left=left,
            bottom=top - height - i * (height + spacing),
            width=width,
            height=height,
        )
        coords.append(coord)
    return coords


def grid(
    rows: int,
    cols: int,
    size: Tuple[float, float],
    hspace: float,
    vspace: float,
    left: float,
    top: float,
) -> List[List[Coord]]:
    """
    Generate a grid of subplots.

    Args:
        rows: Number of rows
        cols: Number of columns
        size: (width, height) of each subplot in inches
        hspace: Horizontal spacing between subplots in inches
        vspace: Vertical spacing between subplots in inches
        left: Left edge of first column in inches
        top: Top edge of first row in inches

    Returns:
        List of lists, where grid[row][col] is the Coord for that position
    """
    width, height = size
    grid_coords = []
    for r in range(rows):
        row_coords = []
        for c in range(cols):
            coord = Coord(
                left=left + c * (width + hspace),
                bottom=top - height - r * (height + vspace),
                width=width,
                height=height,
            )
            row_coords.append(coord)
        grid_coords.append(row_coords)
    return grid_coords


def flatten_grid(grid_coords: List[List[Coord]]) -> List[Coord]:
    """
    Flatten a grid of coordinates to a single list (row by row).

    Args:
        grid_coords: Grid from grid() function

    Returns:
        Flat list of Coord objects
    """
    return [coord for row in grid_coords for coord in row]
