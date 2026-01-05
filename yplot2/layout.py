"""
Layout management for yplot2 figures.

Provides Layout class to track figure size, panel coordinates, and metadata
(image vs plot) for smarter label positioning and panel management.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from .coordinates import Coord
from .config import get_config


@dataclass(frozen=True)
class Panel:
    """
    Metadata container for a single panel.

    Attributes:
        coord: Panel coordinates (position and size in inches)
        panel_type: Type of panel ("plot" or "image")
        name: Optional name for accessing panel by name
        label: Optional override for auto-generated label (A, B, C, etc.)
    """
    coord: Coord
    panel_type: str = "plot"
    name: Optional[str] = None
    label: Optional[str] = None

    def __post_init__(self):
        if self.panel_type not in ("plot", "image"):
            raise ValueError(f"panel_type must be 'plot' or 'image', got '{self.panel_type}'")


class Layout:
    """
    Central manager for figure layout with panel metadata.

    Tracks figure size, panel coordinates, and whether each panel is
    an image or plot. Enables type-aware label positioning.

    Example:
        layout = yp.Layout(fig_size=(7.0, 8.0))

        a = yp.Coord(left=0.4, bottom=5.5, width=2.9, height=2.5)
        b = yp.right_of(a, spacing=0.5)

        layout.add_image(a, name="structure")
        layout.add_plot(b, name="scatter")

        fig, axes = layout.create_figure()

        yp.load_image(axes[0], "image.png")
        yp.scatter(axes[1], x, y)

        layout.add_labels()  # Smart positioning per panel type
    """

    def __init__(self, fig_size: Tuple[float, float], dpi: int = 100):
        """
        Initialize layout with figure size.

        Args:
            fig_size: (width, height) of figure in inches
            dpi: Figure resolution (dots per inch)
        """
        self.fig_size = fig_size
        self.dpi = dpi
        self._panels: List[Panel] = []
        self._fig: Optional[Figure] = None
        self._axes: Optional[List[Axes]] = None
        self._names: dict = {}  # name -> index mapping

    def add(
        self,
        coord: Coord,
        panel_type: str = "plot",
        name: Optional[str] = None,
        label: Optional[str] = None,
    ) -> "Layout":
        """
        Add a panel to the layout.

        Args:
            coord: Panel coordinates
            panel_type: "plot" or "image"
            name: Optional name for accessing panel
            label: Optional override for auto label

        Returns:
            self (for method chaining)
        """
        if name is not None and name in self._names:
            raise ValueError(f"Panel name '{name}' already exists")

        panel = Panel(coord=coord, panel_type=panel_type, name=name, label=label)
        idx = len(self._panels)
        self._panels.append(panel)

        if name is not None:
            self._names[name] = idx

        return self

    def add_plot(
        self,
        coord: Coord,
        name: Optional[str] = None,
        label: Optional[str] = None,
    ) -> "Layout":
        """
        Add a plot panel.

        Args:
            coord: Panel coordinates
            name: Optional name for accessing panel
            label: Optional override for auto label

        Returns:
            self (for method chaining)
        """
        return self.add(coord, panel_type="plot", name=name, label=label)

    def add_image(
        self,
        coord: Coord,
        name: Optional[str] = None,
        label: Optional[str] = None,
    ) -> "Layout":
        """
        Add an image panel.

        Args:
            coord: Panel coordinates
            name: Optional name for accessing panel
            label: Optional override for auto label

        Returns:
            self (for method chaining)
        """
        return self.add(coord, panel_type="image", name=name, label=label)

    @property
    def panels(self) -> List[Panel]:
        """List of all panels."""
        return self._panels.copy()

    @property
    def coords(self) -> List[Coord]:
        """List of all panel coordinates."""
        return [p.coord for p in self._panels]

    @property
    def fig(self) -> Figure:
        """The matplotlib Figure (creates if not exists)."""
        if self._fig is None:
            self.create_figure()
        return self._fig

    @property
    def axes(self) -> List[Axes]:
        """List of all axes (creates figure if not exists)."""
        if self._axes is None:
            self.create_figure()
        return self._axes

    @property
    def plot_axes(self) -> List[Axes]:
        """List of axes for plot panels only."""
        if self._axes is None:
            self.create_figure()
        return [self._axes[i] for i, p in enumerate(self._panels) if p.panel_type == "plot"]

    @property
    def image_axes(self) -> List[Axes]:
        """List of axes for image panels only."""
        if self._axes is None:
            self.create_figure()
        return [self._axes[i] for i, p in enumerate(self._panels) if p.panel_type == "image"]

    def create_figure(self) -> Tuple[Figure, List[Axes]]:
        """
        Create the matplotlib figure and axes.

        Returns:
            Tuple of (Figure, list of Axes)

        Raises:
            RuntimeError: If figure already created (use reset() first)
        """
        if self._fig is not None:
            raise RuntimeError("Figure already created. Call reset() to recreate.")

        if not self._panels:
            raise ValueError("No panels added. Use add(), add_plot(), or add_image() first.")

        fig_width, fig_height = self.fig_size
        self._fig = plt.figure(figsize=self.fig_size, dpi=self.dpi)

        self._axes = []
        for panel in self._panels:
            rel_coords = panel.coord.to_relative(fig_width, fig_height)
            ax = self._fig.add_axes(rel_coords)
            self._axes.append(ax)

        return self._fig, self._axes

    def reset(self) -> "Layout":
        """
        Reset figure and axes (allows recreating).

        Returns:
            self (for method chaining)
        """
        if self._fig is not None:
            plt.close(self._fig)
        self._fig = None
        self._axes = None
        return self

    def get_ax(self, name: str) -> Axes:
        """
        Get axes by panel name.

        Args:
            name: Panel name

        Returns:
            The Axes object

        Raises:
            KeyError: If name not found
        """
        if name not in self._names:
            raise KeyError(f"No panel named '{name}'. Available: {list(self._names.keys())}")
        idx = self._names[name]
        return self.axes[idx]

    def get_panel(self, name: str) -> Panel:
        """
        Get panel by name.

        Args:
            name: Panel name

        Returns:
            The Panel object

        Raises:
            KeyError: If name not found
        """
        if name not in self._names:
            raise KeyError(f"No panel named '{name}'. Available: {list(self._names.keys())}")
        idx = self._names[name]
        return self._panels[idx]

    def add_labels(
        self,
        start: str = "A",
        fontsize: Optional[float] = None,
        fontweight: Optional[str] = None,
        fontname: Optional[str] = None,
    ) -> None:
        """
        Add panel labels (A, B, C, ...) with type-aware positioning.

        Plot panels use panel_label_offset (accounts for y-axis).
        Image panels use panel_label_offset_image (no y-axis).

        Args:
            start: Starting letter
            fontsize: Font size for labels
            fontweight: Font weight ('normal', 'bold', etc.)
            fontname: Font family name
        """
        if self._fig is None:
            self.create_figure()

        cfg = get_config()

        fontsize = fontsize if fontsize is not None else cfg.panel_label_fontsize
        fontweight = fontweight if fontweight is not None else cfg.panel_label_fontweight
        fontname = fontname if fontname is not None else cfg.font_family

        fig_width, fig_height = self.fig_size
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        if start.upper() in letters:
            start_idx = letters.index(start.upper())
        else:
            start_idx = 0

        for i, panel in enumerate(self._panels):
            # Use custom label or auto-generate
            if panel.label is not None:
                letter = panel.label
            else:
                letter = letters[(start_idx + i) % 26]
                if start.islower():
                    letter = letter.lower()

            # Get offset based on panel type
            if panel.panel_type == "image":
                dx, dy = cfg.panel_label_offset_image
            else:
                dx, dy = cfg.panel_label_offset

            # Position in figure-relative coordinates
            x = (panel.coord.left + dx) / fig_width
            y = (panel.coord.top + dy) / fig_height

            self._fig.text(
                x, y, letter,
                fontsize=fontsize,
                fontweight=fontweight,
                fontname=fontname,
                va="top",
                ha="left",
            )

    def draw_debug_boxes(
        self,
        linewidth: float = 2,
        colors: Optional[List[str]] = None,
    ) -> None:
        """
        Draw colored boxes around each panel for debugging layout.

        Args:
            linewidth: Width of box outlines
            colors: List of colors to use (cycles if fewer than panels)
        """
        import matplotlib.patches as patches

        if self._fig is None:
            self.create_figure()

        if colors is None:
            colors = plt.rcParams["axes.prop_cycle"].by_key().get(
                "color",
                ["red", "blue", "green", "orange", "purple", "brown", "pink", "gray"]
            )

        fig_width, fig_height = self.fig_size

        for i, panel in enumerate(self._panels):
            color = colors[i % len(colors)]
            rel = panel.coord.to_relative(fig_width, fig_height)

            rect = patches.Rectangle(
                (rel[0], rel[1]),
                rel[2],
                rel[3],
                linewidth=linewidth,
                edgecolor=color,
                facecolor="none",
                transform=self._fig.transFigure,
            )
            self._fig.patches.append(rect)

    def __len__(self) -> int:
        """Number of panels."""
        return len(self._panels)

    def __repr__(self) -> str:
        return f"Layout(fig_size={self.fig_size}, panels={len(self._panels)})"
