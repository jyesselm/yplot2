"""
Seaborn-backed violin plot wrapper with house-style enforcement.

Requires the [stats] extra: pip install yplot2[stats]
"""

from typing import Optional, Any
from matplotlib.axes import Axes


def _normalize_seaborn_glyphs(ax: Axes, lw: float) -> None:
    """
    Coerce seaborn violin glyph linewidths to *lw* and suppress strip edgecolors.

    Called only from violin(), NOT from the general finish() helper, so that
    finish() is safe to call on plain line/scatter axes without corrupting
    user-set linewidths or edgecolors.

    - FillBetweenPolyCollection (violin bodies) → set_linewidth(lw)
    - Line2D in ax.lines (inner box/whisker/median) → set_linewidth(lw)
    - PathCollection (strip/scatter dots) → set_edgecolor("none")
    """
    from matplotlib.collections import PathCollection

    for coll in ax.collections:
        if isinstance(coll, PathCollection):
            coll.set_edgecolor("none")
        else:
            coll.set_linewidth(lw)

    for line in ax.lines:
        line.set_linewidth(lw)


def violin(
    ax: Axes,
    data: Any,
    x: str,
    y: str,
    *,
    hue: Optional[str] = None,
    palette_name: str = "nucleotide",
    strip: bool = True,
    seed: int = 0,
    **kw: Any,
) -> Axes:
    """
    Draw a house-styled violin plot on *ax*.

    Applies ``saturation=1`` to seaborn to prevent the default 0.75 desaturation
    of palette colors, normalises seaborn glyph linewidths via
    ``_normalize_seaborn_glyphs()``, and calls ``finish(ax)`` for house chrome
    (spines, ticks, tick-label fonts, axis-label fonts).

    When ``strip=True`` (default), a jittered strip overlay is drawn with RNG
    seeded by *seed* for deterministic renders.  The global numpy RNG state is
    restored after drawing so caller state is unchanged.

    When *hue* is given the ``hue_order`` is set explicitly from the palette
    registry so color mapping is deterministic regardless of DataFrame row order.

    Args:
        ax: Target matplotlib Axes.
        data: DataFrame with at least *x* and *y* columns.
        x: Column name for the categorical axis.
        y: Column name for the numeric axis.
        hue: Optional column for color grouping (must match *x* when present).
        palette_name: Named palette in the yplot2 registry (default "nucleotide").
        strip: Draw a jittered strip overlay for individual data points.
        seed: RNG seed for reproducible jitter (only meaningful when strip=True).
        **kw: Extra kwargs forwarded to ``sns.violinplot``.

    Returns:
        The same *ax*, after styling.

    Raises:
        ImportError: If seaborn is not installed (pip install yplot2[stats]).
    """
    try:
        import seaborn as sns
    except ImportError as exc:
        raise ImportError(
            "seaborn is required for violin(). "
            "Install it with: pip install 'yplot2[stats]'"
        ) from exc

    import numpy as np
    from ..colors import palette, hue_order as get_hue_order
    from ...style import finish
    from ...config import get_config

    cfg = get_config()
    pal = palette(palette_name)
    hue_ord = get_hue_order(palette_name) if hue is not None else None

    rng_state = np.random.get_state()
    np.random.seed(seed)
    try:
        sns.violinplot(
            ax=ax,
            data=data,
            x=x,
            y=y,
            hue=hue,
            palette=pal,
            hue_order=hue_ord,
            saturation=1,  # prevent 0.75 desaturation
            linewidth=cfg.axis_linewidth,
            **kw,
        )
        if strip:
            sns.stripplot(
                ax=ax,
                data=data,
                x=x,
                y=y,
                hue=hue,
                palette=pal,
                hue_order=hue_ord,
                size=2,
                jitter=True,
                dodge=bool(hue),
                legend=False,
            )
    finally:
        np.random.set_state(rng_state)

    _normalize_seaborn_glyphs(ax, cfg.axis_linewidth)
    finish(ax)
    return ax
