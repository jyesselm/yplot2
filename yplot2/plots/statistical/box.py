"""
Seaborn-backed box plot wrapper with house-style enforcement.

Requires the [stats] extra: pip install yplot2[stats]
"""

from typing import Optional, Any
from matplotlib.axes import Axes

from ...catalog import catalog
from ._style import normalize_glyphs
from ._overlay import _require_seaborn, _draw_strip


@catalog(
    tags=["distribution", "categorical", "comparison", "seaborn"],
    data_shape="long-df",
    kind="panel",
)
def box(
    ax: Axes,
    data: Any,
    x: str,
    y: str,
    *,
    hue: Optional[str] = None,
    palette_name: str = "nucleotide",
    strip: bool = False,
    max_strip_points: int = 1000,
    seed: int = 0,
    **kw: Any,
) -> Axes:
    """
    Draw a house-styled box plot on *ax*.

    Applies ``saturation=1`` to seaborn to prevent the default 0.75 desaturation
    of palette colors, normalises seaborn glyph linewidths via
    ``normalize_glyphs()``, and calls ``finish(ax)`` for house chrome.

    When ``strip=True``, a jittered strip overlay is drawn with RNG seeded by
    *seed*. Large groups are capped at *max_strip_points* rows per group
    (``None`` = no cap). The global numpy RNG state is restored after drawing.

    No-hue coloring: when *hue* is ``None``, seaborn is called with
    ``hue=x, legend=False`` to avoid the "palette without hue" FutureWarning
    (hard-break at seaborn 0.14). When *hue* is explicitly set, the standard
    ``hue_order`` path is used instead.

    Args:
        ax: Target matplotlib Axes.
        data: DataFrame with at least *x* and *y* columns.
        x: Column name for the categorical axis.
        y: Column name for the numeric axis.
        hue: Optional column for color grouping.
        palette_name: Named palette in the yplot2 registry (default "nucleotide").
        strip: Draw a jittered strip overlay (opt-in; default False).
        max_strip_points: Max strip points per group; None disables the cap.
        seed: RNG seed for reproducible jitter (only meaningful when strip=True).
        **kw: Extra kwargs forwarded to ``sns.boxplot``.

    Returns:
        The same *ax*, after styling.

    Raises:
        ImportError: If seaborn is not installed (pip install yplot2[stats]).
    """
    sns = _require_seaborn("box")

    import numpy as np
    from ..colors import palette, hue_order as get_hue_order
    from ...style import finish
    from ...config import get_config

    cfg = get_config()
    pal = palette(palette_name)
    hue_ord = get_hue_order(palette_name) if hue is not None else None

    # Color by x when hue is None to avoid the seaborn "palette without hue"
    # FutureWarning (hard-break at seaborn 0.14, issue on the DEFAULT call path).
    effective_hue = hue if hue is not None else x
    no_hue_kw = {} if hue is not None else {"legend": False}
    merged_kw = {**no_hue_kw, **kw}

    rng_state = np.random.get_state()
    np.random.seed(seed)
    try:
        sns.boxplot(
            ax=ax,
            data=data,
            x=x,
            y=y,
            hue=effective_hue,
            palette=pal,
            hue_order=hue_ord,
            saturation=1,
            linewidth=cfg.axis_linewidth,
            **merged_kw,
        )
        if strip:
            _draw_strip(
                ax,
                data,
                x=x,
                y=y,
                hue=hue,
                pal=pal,
                hue_ord=hue_ord,
                max_strip_points=max_strip_points,
                seed=seed,
            )
    finally:
        np.random.set_state(rng_state)

    normalize_glyphs(ax, cfg.axis_linewidth)
    finish(ax)
    return ax


def demo_box():
    """Return a figure with a house-styled box plot from bundled sample data.

    Returns:
        matplotlib.figure.Figure with one axes showing a nucleotide box plot.
    """
    import matplotlib.pyplot as plt
    from ._sampledata import make_sample_df

    df = make_sample_df()
    fig, ax = plt.subplots(figsize=(4, 3))
    box(ax, df, x="nuc", y="reactivity", hue="nuc")
    return fig
