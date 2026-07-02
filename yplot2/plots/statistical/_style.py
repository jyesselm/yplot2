"""
Shared post-draw styling helpers for seaborn/matplotlib statistical artists.

Kept in ``statistical/`` because the glyph normalizer is seaborn-specific
(it knows which collection types seaborn creates). The module itself imports
no seaborn — it only touches already-drawn matplotlib artists, so it is safe
to import at any time.
"""

from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar

from ...config import Config, get_config


def normalize_glyphs(ax: Axes, lw: float) -> None:
    """Flatten seaborn body/inner-line linewidths to *lw*; suppress strip edges.

    Called after every seaborn categorical draw (violin, box) so that glyph
    linewidths match the house spine width.  Must NOT be called from the general
    ``finish()`` helper — finish() is safe on plain axes and must not mutate
    user data artists.

    - PathCollection (strip/scatter dots) → set_edgecolor("none")
    - All other collections (violin bodies, box patches) → set_linewidth(lw)
    - Line2D in ax.lines (inner box/whisker/median) → set_linewidth(lw)

    HAZARD: this function wipes the edgecolor of ALL PathCollections on *ax*
    (sets alpha to 0) and forces the linewidth of ALL other collections and
    ALL Line2D artists to *lw*.  It is intentionally destructive because it is
    designed for a freshly-drawn seaborn violin/box/strip axes where those
    artists are owned by the wrapper.  NEVER call this on an axes that also
    carries user scatter plots, custom line artists, or any collection whose
    edgecolor or linewidth the user controls — it will silently overwrite them.

    Args:
        ax: Axes whose seaborn artists will be restyled.
        lw: Target linewidth (typically ``cfg.axis_linewidth``).
    """
    from matplotlib.collections import PathCollection

    for coll in ax.collections:
        if isinstance(coll, PathCollection):
            coll.set_edgecolor("none")
        else:
            coll.set_linewidth(lw)

    for line in ax.lines:
        line.set_linewidth(lw)


def style_colorbar(cbar: Colorbar, cfg: Config | None = None) -> None:
    """House-style a colorbar: outline lw, Arimo tick labels, tick mark width.

    Applies the same chrome discipline as ``finish(ax)`` but for the colorbar
    frame and its tick labels.

    Args:
        cbar: The colorbar to restyle (returned by ``fig.colorbar(...)``).
        cfg: Config to read settings from; defaults to the global config.
    """
    if cfg is None:
        cfg = get_config()

    lw = cfg.axis_linewidth
    fontsize = cfg.colorbar_tick_fontsize
    font_family = cfg.font_family

    # Outline (the frame around the colorbar swatch)
    cbar.outline.set_linewidth(lw)  # type: ignore[operator]

    # Tick marks on the colorbar axis
    cbar.ax.tick_params(width=lw)

    # Tick labels: font and size
    for label in cbar.ax.get_yticklabels():
        label.set_fontfamily(font_family)
        label.set_fontsize(fontsize)
    for label in cbar.ax.get_xticklabels():
        label.set_fontfamily(font_family)
        label.set_fontsize(fontsize)
