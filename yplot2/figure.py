"""
Figure creation and rendering utilities.
"""

from typing import List, Optional, Tuple, Union
import warnings
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from .coordinates import Coord
from .config import get_config


def get_image_size(image_path: str, dpi: float = 300) -> Tuple[float, float]:
    """
    Get image dimensions in inches.

    Args:
        image_path: Path to image file
        dpi: DPI to use for conversion (default: 300)

    Returns:
        (width, height) in inches
    """
    try:
        img = mpimg.imread(image_path)
    except Exception as e:
        raise ValueError(f"Could not load image from {image_path}: {e}")

    # img.shape is (height, width) or (height, width, channels)
    pixel_height, pixel_width = img.shape[:2]
    width_inches = pixel_width / dpi
    height_inches = pixel_height / dpi

    return width_inches, height_inches


def coord_from_image(
    image_path: str,
    left: float,
    bottom: float,
    dpi: float = 300,
    scale: float = 1.0,
) -> Coord:
    """
    Create a Coord matching an image's exact dimensions.

    Args:
        image_path: Path to image file
        left: Left position in inches
        bottom: Bottom position in inches
        dpi: DPI to use for pixel-to-inch conversion (default: 300)
        scale: Scale factor for the image size (default: 1.0)

    Returns:
        Coord with dimensions matching the image

    Example:
        # Create panel exactly matching image size
        a = yp.coord_from_image("structure.png", left=0.5, bottom=3.0)

        # Scale to 50% of original size
        b = yp.coord_from_image("structure.png", left=0.5, bottom=1.0, scale=0.5)
    """
    width, height = get_image_size(image_path, dpi=dpi)
    return Coord(
        left=left,
        bottom=bottom,
        width=width * scale,
        height=height * scale,
    )


def create_figure(
    size: Tuple[float, float],
    coords: List[Coord],
    dpi: int = 100,
) -> Tuple[Figure, List[Axes]]:
    """
    Create a matplotlib figure with subplots at specified coordinates.

    Args:
        size: (width, height) of figure in inches
        coords: List of Coord objects defining subplot positions
        dpi: Figure resolution (dots per inch)

    Returns:
        Tuple of (Figure, list of Axes)
    """
    fig_width, fig_height = size
    fig = plt.figure(figsize=size, dpi=dpi)

    axes = []
    for coord in coords:
        # Convert from inches to figure-relative coordinates (0-1)
        rel_coords = coord.to_relative(fig_width, fig_height)
        ax = fig.add_axes(rel_coords)
        axes.append(ax)

    return fig, axes


def load_image(
    ax: Axes,
    image_path: str,
    coord: Optional[Coord] = None,
    warn_distortion: bool = True,
    distortion_threshold: float = 0.05,
) -> None:
    """
    Load an image into a subplot, stretching to fill the entire panel.

    The image will fill edge-to-edge with no white space or margins.
    If the panel aspect ratio differs from the image, a warning is issued.

    Args:
        ax: Axes object to load image into
        image_path: Path to image file
        coord: Optional Coord of the panel (for aspect ratio check)
        warn_distortion: Whether to warn if aspect ratios don't match (default: True)
        distortion_threshold: Tolerance for aspect ratio difference (default: 0.05 = 5%)

    Example:
        # With aspect ratio warning
        a = yp.Coord(left=0.5, bottom=2.0, width=3.0, height=2.0)
        yp.load_image(axes[0], "image.png", coord=a)

        # Or create panel from image to avoid distortion
        a = yp.coord_from_image("image.png", left=0.5, bottom=2.0)
        yp.load_image(axes[0], "image.png")
    """
    try:
        img = mpimg.imread(image_path)
    except Exception as e:
        raise ValueError(f"Could not load image from {image_path}: {e}")

    # Check aspect ratio if coord provided
    if coord is not None and warn_distortion:
        pixel_height, pixel_width = img.shape[:2]
        image_aspect = pixel_width / pixel_height
        panel_aspect = coord.width / coord.height

        aspect_diff = abs(image_aspect - panel_aspect) / image_aspect
        if aspect_diff > distortion_threshold:
            warnings.warn(
                f"Image aspect ratio ({image_aspect:.3f}) differs from panel "
                f"aspect ratio ({panel_aspect:.3f}) by {aspect_diff*100:.1f}%. "
                f"Image will be stretched. Use coord_from_image() to create a "
                f"panel matching the image dimensions.",
                UserWarning,
                stacklevel=2,
            )

    ax.clear()
    # aspect='auto' stretches image to fill the axes completely
    ax.imshow(img, aspect='auto')

    # Remove all axes decorations
    ax.axis('off')


def make_image_panel(ax: Axes) -> None:
    """
    Prepare an axes to be used as an image panel (no borders, ticks, etc.).

    Use this when you want to draw custom content that fills edge-to-edge.

    Args:
        ax: Axes object to prepare
    """
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


def add_labels(
    fig: Figure,
    coords: List[Coord],
    fig_size: Tuple[float, float],
    start: str = "A",
    fontsize: Optional[float] = None,
    fontweight: Optional[str] = None,
    fontname: Optional[str] = None,
    offset: Optional[Tuple[float, float]] = None,
) -> None:
    """
    Add panel labels (A, B, C, ...) to subplots.

    Uses global config defaults for any unspecified parameters.

    Args:
        fig: Figure object
        coords: List of Coord objects to label
        fig_size: (width, height) of figure in inches
        start: Starting letter
        fontsize: Font size for labels
        fontweight: Font weight ('normal', 'bold', etc.)
        fontname: Font family name
        offset: (dx, dy) offset from top-left corner in inches
    """
    cfg = get_config()

    fontsize = fontsize if fontsize is not None else cfg.panel_label_fontsize
    fontweight = fontweight if fontweight is not None else cfg.panel_label_fontweight
    fontname = fontname if fontname is not None else cfg.font_family
    offset = offset if offset is not None else cfg.panel_label_offset

    fig_width, fig_height = fig_size
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if start.upper() in letters:
        start_idx = letters.index(start.upper())
    else:
        start_idx = 0

    dx, dy = offset

    for i, coord in enumerate(coords):
        letter = letters[(start_idx + i) % 26]
        if start.islower():
            letter = letter.lower()

        # Position in figure-relative coordinates
        x = (coord.left + dx) / fig_width
        y = (coord.top + dy) / fig_height

        fig.text(
            x, y, letter,
            fontsize=fontsize,
            fontweight=fontweight,
            fontname=fontname,
            va="top",
            ha="left",
        )


def draw_debug_boxes(
    fig: Figure,
    coords: List[Coord],
    fig_size: Tuple[float, float],
    linewidth: float = 2,
    colors: Optional[List[str]] = None,
) -> None:
    """
    Draw colored boxes around each subplot for debugging layout.

    Args:
        fig: Figure object
        coords: List of Coord objects
        fig_size: (width, height) of figure in inches
        linewidth: Width of box outlines
        colors: List of colors to use (cycles if fewer than coords)
    """
    if colors is None:
        colors = plt.rcParams["axes.prop_cycle"].by_key().get(
            "color",
            ["red", "blue", "green", "orange", "purple", "brown", "pink", "gray"]
        )

    fig_width, fig_height = fig_size

    for i, coord in enumerate(coords):
        color = colors[i % len(colors)]
        rel = coord.to_relative(fig_width, fig_height)

        rect = patches.Rectangle(
            (rel[0], rel[1]),
            rel[2],
            rel[3],
            linewidth=linewidth,
            edgecolor=color,
            facecolor="none",
            transform=fig.transFigure,
        )
        fig.patches.append(rect)


def add_colorbar(
    fig: Figure,
    ax: Axes,
    mappable,
    coord: Coord,
    fig_size: Tuple[float, float],
    position: str = "right",
    width: float = 0.1,
    spacing: float = 0.05,
    **kwargs,
):
    """
    Add a colorbar adjacent to a subplot.

    Args:
        fig: Figure object
        ax: Axes the colorbar is associated with
        mappable: The mappable (e.g., from imshow, scatter with c=)
        coord: Coord of the subplot
        fig_size: (width, height) of figure in inches
        position: Where to place colorbar ('right', 'left', 'top', 'bottom')
        width: Width/height of colorbar in inches
        spacing: Gap between subplot and colorbar in inches
        **kwargs: Additional arguments passed to fig.colorbar()

    Returns:
        Colorbar object
    """
    fig_width, fig_height = fig_size

    if position == "right":
        cbar_coord = Coord(
            left=coord.right + spacing,
            bottom=coord.bottom,
            width=width,
            height=coord.height,
        )
        orientation = "vertical"
    elif position == "left":
        cbar_coord = Coord(
            left=coord.left - spacing - width,
            bottom=coord.bottom,
            width=width,
            height=coord.height,
        )
        orientation = "vertical"
    elif position == "top":
        cbar_coord = Coord(
            left=coord.left,
            bottom=coord.top + spacing,
            width=coord.width,
            height=width,
        )
        orientation = "horizontal"
    elif position == "bottom":
        cbar_coord = Coord(
            left=coord.left,
            bottom=coord.bottom - spacing - width,
            width=coord.width,
            height=width,
        )
        orientation = "horizontal"
    else:
        raise ValueError(f"Unknown position: {position}")

    rel = cbar_coord.to_relative(fig_width, fig_height)
    cax = fig.add_axes(rel)

    return fig.colorbar(mappable, cax=cax, orientation=orientation, **kwargs)
