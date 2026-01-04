"""
Relative positioning helpers for subplot coordinates.

All functions take a reference Coord and return a new Coord positioned
relative to it. By default, the new Coord has the same size as the reference.
"""

from typing import Optional, Tuple, Union
from .coordinates import Coord


def right_of(
    ref: Coord,
    spacing: float,
    width: Optional[float] = None,
    height: Optional[float] = None,
    size: Optional[Tuple[float, float]] = None,
) -> Coord:
    """
    Create a Coord to the right of the reference.

    Args:
        ref: Reference coordinate
        spacing: Horizontal gap between ref and new coord (inches)
        width: Width of new coord (default: same as ref)
        height: Height of new coord (default: same as ref)
        size: (width, height) tuple, overrides individual width/height

    Returns:
        New Coord positioned to the right of ref
    """
    if size is not None:
        width, height = size
    if width is None:
        width = ref.width
    if height is None:
        height = ref.height

    return Coord(
        left=ref.right + spacing,
        bottom=ref.bottom,
        width=width,
        height=height,
    )


def left_of(
    ref: Coord,
    spacing: float,
    width: Optional[float] = None,
    height: Optional[float] = None,
    size: Optional[Tuple[float, float]] = None,
) -> Coord:
    """
    Create a Coord to the left of the reference.

    Args:
        ref: Reference coordinate
        spacing: Horizontal gap between ref and new coord (inches)
        width: Width of new coord (default: same as ref)
        height: Height of new coord (default: same as ref)
        size: (width, height) tuple, overrides individual width/height

    Returns:
        New Coord positioned to the left of ref
    """
    if size is not None:
        width, height = size
    if width is None:
        width = ref.width
    if height is None:
        height = ref.height

    return Coord(
        left=ref.left - spacing - width,
        bottom=ref.bottom,
        width=width,
        height=height,
    )


def below(
    ref: Coord,
    spacing: float,
    width: Optional[float] = None,
    height: Optional[float] = None,
    size: Optional[Tuple[float, float]] = None,
) -> Coord:
    """
    Create a Coord below the reference.

    Args:
        ref: Reference coordinate
        spacing: Vertical gap between ref and new coord (inches)
        width: Width of new coord (default: same as ref)
        height: Height of new coord (default: same as ref)
        size: (width, height) tuple, overrides individual width/height

    Returns:
        New Coord positioned below ref
    """
    if size is not None:
        width, height = size
    if width is None:
        width = ref.width
    if height is None:
        height = ref.height

    return Coord(
        left=ref.left,
        bottom=ref.bottom - spacing - height,
        width=width,
        height=height,
    )


def above(
    ref: Coord,
    spacing: float,
    width: Optional[float] = None,
    height: Optional[float] = None,
    size: Optional[Tuple[float, float]] = None,
) -> Coord:
    """
    Create a Coord above the reference.

    Args:
        ref: Reference coordinate
        spacing: Vertical gap between ref and new coord (inches)
        width: Width of new coord (default: same as ref)
        height: Height of new coord (default: same as ref)
        size: (width, height) tuple, overrides individual width/height

    Returns:
        New Coord positioned above ref
    """
    if size is not None:
        width, height = size
    if width is None:
        width = ref.width
    if height is None:
        height = ref.height

    return Coord(
        left=ref.left,
        bottom=ref.top + spacing,
        width=width,
        height=height,
    )


def copy(
    ref: Coord,
    dx: float = 0.0,
    dy: float = 0.0,
    width: Optional[float] = None,
    height: Optional[float] = None,
) -> Coord:
    """
    Copy a Coord with optional offset and size changes.

    Args:
        ref: Reference coordinate
        dx: Horizontal offset (inches, positive = right)
        dy: Vertical offset (inches, positive = up)
        width: Width of new coord (default: same as ref)
        height: Height of new coord (default: same as ref)

    Returns:
        New Coord with applied offset
    """
    if width is None:
        width = ref.width
    if height is None:
        height = ref.height

    return Coord(
        left=ref.left + dx,
        bottom=ref.bottom + dy,
        width=width,
        height=height,
    )


def same_size(
    ref: Coord,
    left: float,
    bottom: float,
) -> Coord:
    """
    Create a Coord with the same size as ref at a new position.

    Args:
        ref: Reference coordinate (for size)
        left: Left edge of new coord (inches)
        bottom: Bottom edge of new coord (inches)

    Returns:
        New Coord with same size as ref at specified position
    """
    return Coord(
        left=left,
        bottom=bottom,
        width=ref.width,
        height=ref.height,
    )


def resize(
    ref: Coord,
    width: Optional[float] = None,
    height: Optional[float] = None,
    anchor: str = "bottom_left",
) -> Coord:
    """
    Resize a Coord, keeping a specified anchor point fixed.

    Args:
        ref: Reference coordinate
        width: New width (default: keep same)
        height: New height (default: keep same)
        anchor: Which point to keep fixed. Options:
            - "bottom_left", "bottom_right", "top_left", "top_right"
            - "center", "bottom_center", "top_center", "left_center", "right_center"

    Returns:
        Resized Coord
    """
    if width is None:
        width = ref.width
    if height is None:
        height = ref.height

    dw = width - ref.width
    dh = height - ref.height

    # Calculate new position based on anchor
    if anchor == "bottom_left":
        left, bottom = ref.left, ref.bottom
    elif anchor == "bottom_right":
        left, bottom = ref.left - dw, ref.bottom
    elif anchor == "top_left":
        left, bottom = ref.left, ref.bottom - dh
    elif anchor == "top_right":
        left, bottom = ref.left - dw, ref.bottom - dh
    elif anchor == "center":
        left, bottom = ref.left - dw / 2, ref.bottom - dh / 2
    elif anchor == "bottom_center":
        left, bottom = ref.left - dw / 2, ref.bottom
    elif anchor == "top_center":
        left, bottom = ref.left - dw / 2, ref.bottom - dh
    elif anchor == "left_center":
        left, bottom = ref.left, ref.bottom - dh / 2
    elif anchor == "right_center":
        left, bottom = ref.left - dw, ref.bottom - dh / 2
    else:
        raise ValueError(f"Unknown anchor: {anchor}")

    return Coord(left=left, bottom=bottom, width=width, height=height)


def shift(
    ref: Coord,
    dx: float = 0.0,
    dy: float = 0.0,
) -> Coord:
    """
    Shift a Coord by an offset (alias for copy with no size change).

    Args:
        ref: Reference coordinate
        dx: Horizontal offset (inches, positive = right)
        dy: Vertical offset (inches, positive = up)

    Returns:
        Shifted Coord
    """
    return copy(ref, dx=dx, dy=dy)
