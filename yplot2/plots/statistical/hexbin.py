"""
Hexagonal-bin density plot using native matplotlib ax.hexbin (no seaborn required).

Renders with ``ax.hexbin`` and optionally attaches a house-styled colorbar.
"""

from typing import Any
from matplotlib.axes import Axes

from ...catalog import catalog
from ._style import style_colorbar


@catalog(
    tags=["hexbin", "density"],
    data_shape="xy",
    kind="panel",
)
def hexbin(
    ax: Axes,
    x: Any,
    y: Any,
    *,
    gridsize: int = 30,
    cmap: str = "magma",
    colorbar: bool = True,
    **kw: Any,
) -> Axes:
    """
    Draw a hexagonal-bin density plot on *ax* using native matplotlib hexbin.

    No seaborn import is required: this capsule uses only matplotlib.
    An optional house-styled colorbar is added via ``style_colorbar()``.

    Args:
        ax: Target matplotlib Axes.
        x: 1-D array-like of x values.
        y: 1-D array-like of y values (same length as *x*).
        gridsize: Number of hexagons across the x-axis (default 30).
        cmap: Colormap name (default ``"magma"``).
        colorbar: Attach and house-style a colorbar (default True).
        **kw: Extra kwargs forwarded to ``ax.hexbin``.

    Returns:
        The same *ax*, after styling.
    """
    from ...style import finish

    hb = ax.hexbin(x, y, gridsize=gridsize, cmap=cmap, **kw)

    if colorbar:
        cbar = ax.figure.colorbar(hb, ax=ax)  # type: ignore[union-attr]
        style_colorbar(cbar)

    finish(ax)
    return ax


def demo_hexbin():
    """Return a figure with a house-styled hexbin plot from bundled sample data.

    Returns:
        matplotlib.figure.Figure with one axes showing a bivariate hexbin.
    """
    import matplotlib.pyplot as plt
    from ._sampledata import make_xy_df

    df = make_xy_df()
    fig, ax = plt.subplots(figsize=(4, 3))
    hexbin(ax, df["x"].to_numpy(), df["y"].to_numpy())
    return fig
