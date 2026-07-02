"""
Seaborn-backed KDE plot wrapper with house-style enforcement.

Requires the [stats] extra: pip install yplot2[stats]
"""

from typing import Optional, Any
from matplotlib.axes import Axes

from ...catalog import catalog
from ._style import normalize_glyphs
from ._overlay import _require_seaborn


@catalog(
    tags=["density", "distribution", "seaborn"],
    data_shape="long-df",
    kind="panel",
)
def kde(
    ax: Axes,
    data: Any,
    x: str,
    *,
    hue: Optional[str] = None,
    palette_name: str = "nucleotide",
    fill: bool = True,
    **kw: Any,
) -> Axes:
    """
    Draw a house-styled kernel density estimate on *ax*.

    Normalises seaborn glyph linewidths via ``normalize_glyphs()`` and calls
    ``finish(ax)`` for house chrome (spines, ticks, tick-label fonts).

    When *hue* is given, ``hue_order`` is set explicitly from the palette
    registry so color mapping is deterministic regardless of DataFrame row order.

    Note: ``kdeplot`` accepts no ``saturation`` argument; it is not passed.

    Args:
        ax: Target matplotlib Axes.
        data: DataFrame with at least the *x* column.
        x: Column name for the continuous variable.
        hue: Optional column for color grouping.
        palette_name: Named palette in the yplot2 registry (default "nucleotide").
        fill: Fill under the density curve (default True).
        **kw: Extra kwargs forwarded to ``sns.kdeplot``.

    Returns:
        The same *ax*, after styling.

    Raises:
        ImportError: If seaborn is not installed (pip install yplot2[stats]).
    """
    sns = _require_seaborn("kde")

    from ..colors import palette, hue_order as get_hue_order
    from ...style import finish
    from ...config import get_config

    cfg = get_config()
    pal = palette(palette_name)
    hue_ord = get_hue_order(palette_name) if hue is not None else None

    sns.kdeplot(
        ax=ax,
        data=data,
        x=x,
        hue=hue,
        palette=pal,
        hue_order=hue_ord,
        fill=fill,
        linewidth=cfg.axis_linewidth,
        **kw,
    )

    normalize_glyphs(ax, cfg.axis_linewidth)
    finish(ax)
    return ax


def demo_kde():
    """Return a figure with a house-styled KDE plot from bundled sample data.

    Returns:
        matplotlib.figure.Figure with one axes showing nucleotide KDE curves.
    """
    import matplotlib.pyplot as plt
    from ._sampledata import make_sample_df

    df = make_sample_df()
    fig, ax = plt.subplots(figsize=(4, 3))
    kde(ax, df, x="reactivity", hue="nuc")
    return fig
