"""
2-D histogram heatmap using numpy + imshow (no seaborn required).

Computes a 2-D histogram with ``numpy.histogram2d`` and renders it as an
``imshow`` image with an optional house-styled colorbar.
"""

from typing import Any
from matplotlib.axes import Axes

from ...catalog import catalog
from ._style import style_colorbar


def _check_finite(arr: Any, name: str) -> None:
    """Raise a clear ValueError when *arr* contains NaN or infinite values.

    ``numpy.histogram2d`` raises a cryptic "autodetected range ... not finite"
    error in this case. Pre-checking here gives the caller an actionable message.

    Args:
        arr: Array-like to inspect.
        name: Human-readable variable name for the error message.

    Raises:
        ValueError: If *arr* contains any NaN or infinite values.
    """
    import numpy as np

    a = np.asarray(arr, dtype=float)
    if not np.all(np.isfinite(a)):
        raise ValueError(
            f"heatmap2d: '{name}' contains NaN or infinite values. "
            "Filter or impute them before plotting."
        )


def _hist2d_image(
    ax: Axes,
    x: Any,
    y: Any,
    bins: int,
    cmap: str,
    **kw: Any,
) -> Any:
    """Compute 2-D histogram and render it on *ax* via imshow.

    Args:
        ax: Target axes.
        x: 1-D array-like of x values (must be finite).
        y: 1-D array-like of y values (must be finite).
        bins: Number of bins in each dimension.
        cmap: Colormap name.
        **kw: Forwarded to ``ax.imshow``.

    Returns:
        The AxesImage returned by ``ax.imshow``.
    """
    import numpy as np

    _check_finite(x, "x")
    _check_finite(y, "y")
    counts, xedges, yedges = np.histogram2d(x, y, bins=bins)
    extent = (float(xedges[0]), float(xedges[-1]), float(yedges[0]), float(yedges[-1]))
    return ax.imshow(
        counts.T,
        origin="lower",
        extent=extent,
        aspect="auto",
        cmap=cmap,
        **kw,
    )


@catalog(
    tags=["2d-histogram", "density"],
    data_shape="xy",
    kind="panel",
)
def heatmap2d(
    ax: Axes,
    x: Any,
    y: Any,
    *,
    bins: int = 50,
    cmap: str = "magma",
    colorbar: bool = True,
    **kw: Any,
) -> Axes:
    """
    Draw a 2-D histogram heatmap on *ax* using numpy + imshow.

    No seaborn import is required: this capsule uses only numpy and matplotlib.
    An optional house-styled colorbar is added via ``style_colorbar()``.

    Args:
        ax: Target matplotlib Axes.
        x: 1-D array-like of x values.
        y: 1-D array-like of y values (same length as *x*).
        bins: Number of histogram bins per dimension (default 50).
        cmap: Colormap name (default ``"magma"``).
        colorbar: Attach and house-style a colorbar (default True).
        **kw: Extra kwargs forwarded to ``ax.imshow``.

    Returns:
        The same *ax*, after styling.
    """
    from ...style import finish

    im = _hist2d_image(ax, x, y, bins, cmap, **kw)

    if colorbar:
        cbar = ax.figure.colorbar(im, ax=ax)  # type: ignore[union-attr]
        style_colorbar(cbar)

    finish(ax)
    return ax


def demo_heatmap2d():
    """Return a figure with a house-styled 2-D histogram from bundled sample data.

    Returns:
        matplotlib.figure.Figure with one axes showing a bivariate heatmap.
    """
    import matplotlib.pyplot as plt
    from ._sampledata import make_xy_df

    df = make_xy_df()
    fig, ax = plt.subplots(figsize=(4, 3))
    heatmap2d(ax, df["x"].to_numpy(), df["y"].to_numpy())
    return fig
