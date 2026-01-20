"""Regression plot utilities."""

from typing import Optional, Union

import numpy as np
from matplotlib.axes import Axes

from ..config import get_config
from .basic import scatter, line, text, _merge_args


def _compute_linear_regression(
    x: np.ndarray,
    y: np.ndarray,
) -> tuple[float, float, float]:
    """Compute linear regression.

    Args:
        x: X values.
        y: Y values.

    Returns:
        Tuple of (slope, intercept, r_squared).
    """
    coeffs = np.polyfit(x, y, 1)
    slope, intercept = coeffs[0], coeffs[1]
    r = np.corrcoef(x, y)[0, 1]
    r_squared = r**2
    return slope, intercept, r_squared


def regplot(
    ax: Axes,
    x,
    y,
    method: str = "linear",
    show_scatter: bool = True,
    show_r2: bool = True,
    line_args: Optional[dict] = None,
    scatter_args: Optional[dict] = None,
    r2_args: Optional[dict] = None,
) -> dict:
    """Create scatter plot with regression line and R-squared annotation.

    Args:
        ax: Axes to plot on.
        x: X data values.
        y: Y data values.
        method: Regression method ('linear'). Default 'linear'.
        show_scatter: Whether to show scatter points. Default True.
        show_r2: Whether to show R-squared annotation. Default True.
        line_args: Dict of line styling options. Keys: color, linewidth,
            linestyle. Passed to line().
        scatter_args: Dict of scatter styling options. Keys: c (color), s (size),
            marker, alpha, etc. Passed to scatter().
        r2_args: Dict of R-squared text options. Keys: pos, prefix, precision,
            fontsize, box. Defaults: pos='top left', prefix='R² = ',
            precision=3.

    Returns:
        Dict with 'slope', 'intercept', 'r_squared', 'line', 'scatter', 'text'.

    Raises:
        ValueError: If method is not 'linear' or data has fewer than 2 points.

    Example:
        >>> regplot(ax, x, y)  # Basic usage
        >>> regplot(ax, x, y, line_args={"color": "red", "linestyle": "--"})
        >>> regplot(ax, x, y, r2_args={"pos": "top right", "precision": 2})
        >>> regplot(ax, x, y, scatter_args={"c": "blue", "alpha": 0.5})
    """
    x = np.asarray(x)
    y = np.asarray(y)

    if len(x) < 2:
        raise ValueError("Need at least 2 data points for regression")
    if method != "linear":
        raise ValueError(f"Unknown method '{method}'. Only 'linear' is supported.")

    cfg = get_config()

    # Compute regression
    slope, intercept, r_squared = _compute_linear_regression(x, y)

    # Build args with defaults
    _line_args = _merge_args(
        {
            "color": "black",
            "linewidth": cfg.plot_linewidth,
            "linestyle": "--",
        },
        line_args,
    )

    _scatter_args = _merge_args(
        {},
        scatter_args,
    )

    _r2_args = _merge_args(
        {
            "pos": "top left",
            "prefix": "R² = ",
            "precision": 3,
            "fontsize": None,
            "box": False,
        },
        r2_args,
    )

    # Plot scatter first (so line appears on top)
    scatter_obj = None
    if show_scatter:
        scatter_obj = scatter(ax, x, y, **_scatter_args)

    # Plot regression line (after scatter so it's on top)
    x_line = np.array([x.min(), x.max()])
    y_line = slope * x_line + intercept
    line_obj = line(ax, x_line, y_line, **_line_args)

    # Add R-squared text
    text_obj = None
    if show_r2:
        precision = _r2_args.pop("precision")
        prefix = _r2_args.pop("prefix")
        r2_str = f"{prefix}{r_squared:.{precision}f}"
        text_obj = text(ax, r2_str, **_r2_args)

    return {
        "slope": slope,
        "intercept": intercept,
        "r_squared": r_squared,
        "line": line_obj,
        "scatter": scatter_obj,
        "text": text_obj,
    }


def _truncate_colormap(cmap, minval: float = 0.2, maxval: float = 1.0, n: int = 256):
    """Truncate a colormap to avoid near-white colors at low end."""
    import matplotlib.colors as mcolors

    colors = cmap(np.linspace(minval, maxval, n))
    return mcolors.ListedColormap(colors)


def regplot_density(
    ax: Axes,
    x,
    y,
    method: str = "linear",
    bins: int = 400,
    show_r2: bool = True,
    show_cbar: bool = True,
    scatter_args: Optional[dict] = None,
    line_args: Optional[dict] = None,
    r2_args: Optional[dict] = None,
    cbar_args: Optional[dict] = None,
) -> dict:
    """Create scatter plot with density-colored points and regression line.

    Each point is colored by the local density (number of nearby points),
    computed via 2D histogram binning. High-density points are drawn on top.

    Args:
        ax: Axes to plot on.
        x: X data values.
        y: Y data values.
        method: Regression method ('linear'). Default 'linear'.
        bins: Number of bins for density calculation. Default 400.
        show_r2: Whether to show R-squared annotation. Default True.
        show_cbar: Whether to show colorbar. Default True.
        scatter_args: Dict of scatter styling options. Keys: s (size), cmap,
            cmap_min (truncate colormap low end, default 0.2), alpha, marker.
        line_args: Dict of line styling options. Keys: color, linewidth, linestyle.
        r2_args: Dict of R-squared text options. Keys: pos, prefix, precision,
            fontsize, box. Defaults: pos='top left'.
        cbar_args: Dict of colorbar options. Keys: label, width (inches),
            pad (inches). Uses config defaults for width/pad.

    Returns:
        Dict with 'slope', 'intercept', 'r_squared', 'scatter', 'line', 'text', 'cbar'.

    Raises:
        ValueError: If method is not 'linear' or data has fewer than 2 points.

    Example:
        >>> regplot_density(ax, x, y)  # Density-colored scatter with colorbar
        >>> regplot_density(ax, x, y, bins=200, scatter_args={"s": 5})
        >>> regplot_density(ax, x, y, scatter_args={"cmap": "viridis"})
        >>> regplot_density(ax, x, y, cbar_args={"label": "Points"})
    """
    import matplotlib as mpl

    x = np.asarray(x)
    y = np.asarray(y)

    if len(x) < 2:
        raise ValueError("Need at least 2 data points for regression")
    if method != "linear":
        raise ValueError(f"Unknown method '{method}'. Only 'linear' is supported.")

    cfg = get_config()

    # Compute regression
    slope, intercept, r_squared = _compute_linear_regression(x, y)

    # Build args with defaults
    _scatter_args = _merge_args(
        {
            "s": 3,
            "cmap": "Blues",
            "cmap_min": 0.2,
        },
        scatter_args,
    )

    _line_args = _merge_args(
        {
            "color": "black",
            "linewidth": cfg.plot_linewidth,
            "linestyle": "--",
        },
        line_args,
    )

    _r2_args = _merge_args(
        {
            "pos": "top left",
            "prefix": "R² = ",
            "precision": 3,
            "fontsize": None,
            "box": False,
        },
        r2_args,
    )

    _cbar_args = _merge_args(
        {
            "label": "Count",
        },
        cbar_args,
    )

    # Compute density for each point using 2D histogram
    hh, locx, locy = np.histogram2d(x, y, bins=[bins, bins])

    # Assign density value to each point (count in its bin)
    z = np.array([
        hh[min(np.searchsorted(locx[1:], xi), bins - 1),
           min(np.searchsorted(locy[1:], yi), bins - 1)]
        for xi, yi in zip(x, y)
    ])

    # Sort by density so high-density points are drawn on top
    idx = z.argsort()
    x_sorted, y_sorted, z_sorted = x[idx], y[idx], z[idx]

    # Get colormap and truncate to avoid near-white colors
    cmap_name = _scatter_args.pop("cmap")
    cmap_min = _scatter_args.pop("cmap_min")
    base_cmap = mpl.colormaps[cmap_name]
    trunc_cmap = _truncate_colormap(base_cmap, minval=cmap_min, maxval=1.0)

    # Plot scatter with density coloring
    scatter_obj = ax.scatter(x_sorted, y_sorted, c=z_sorted, cmap=trunc_cmap, **_scatter_args)

    # Plot regression line (on top of scatter)
    x_line = np.array([x.min(), x.max()])
    y_line = slope * x_line + intercept
    line_obj = line(ax, x_line, y_line, **_line_args)

    # Add R-squared text
    text_obj = None
    if show_r2:
        precision = _r2_args.pop("precision")
        prefix = _r2_args.pop("prefix")
        r2_str = f"{prefix}{r_squared:.{precision}f}"
        text_obj = text(ax, r2_str, **_r2_args)

    # Add colorbar (positioned to the right without stealing axes space)
    cbar_obj = None
    if show_cbar:
        fig = ax.get_figure()
        cbar_label = _cbar_args.pop("label")
        cbar_width = _cbar_args.pop("width", cfg.colorbar_width)
        cbar_pad = _cbar_args.pop("pad", cfg.colorbar_pad)

        # Get axes position and create colorbar axes to the right
        pos = ax.get_position()
        fig_width, fig_height = fig.get_size_inches()
        # Convert width/pad from inches to figure fraction
        cbar_width_frac = cbar_width / fig_width
        cbar_pad_frac = cbar_pad / fig_width
        cbar_ax = fig.add_axes([
            pos.x1 + cbar_pad_frac,  # left
            pos.y0,                   # bottom (same as main axes)
            cbar_width_frac,          # width
            pos.height,               # height (same as main axes)
        ])
        cbar_obj = fig.colorbar(scatter_obj, cax=cbar_ax, **_cbar_args)
        cbar_obj.set_label(cbar_label, fontsize=cfg.x_axis_label_fontsize)
        cbar_obj.ax.tick_params(labelsize=cfg.colorbar_tick_fontsize)

    return {
        "slope": slope,
        "intercept": intercept,
        "r_squared": r_squared,
        "scatter": scatter_obj,
        "line": line_obj,
        "text": text_obj,
        "cbar": cbar_obj,
    }
