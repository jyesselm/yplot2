"""Box plot utilities."""

from typing import Optional
from matplotlib.axes import Axes

from ..config import get_config


def boxplot(
    ax: Axes,
    x,
    linewidth: Optional[float] = None,
    fliersize: Optional[float] = None,
    **kwargs,
):
    """
    Box plot using global config defaults.

    Args:
        ax: Axes object
        x: Data (list of arrays for multiple boxes)
        linewidth: Line width for box edges
        fliersize: Outlier marker size
        **kwargs: Additional args to ax.boxplot()

    Returns:
        Dict of box plot components
    """
    cfg = get_config()

    if linewidth is None:
        linewidth = cfg.axis_linewidth
    if fliersize is None:
        fliersize = cfg.plot_markersize

    # Set box properties
    boxprops = kwargs.pop('boxprops', {})
    boxprops.setdefault('linewidth', linewidth)

    whiskerprops = kwargs.pop('whiskerprops', {})
    whiskerprops.setdefault('linewidth', linewidth)

    capprops = kwargs.pop('capprops', {})
    capprops.setdefault('linewidth', linewidth)

    medianprops = kwargs.pop('medianprops', {})
    medianprops.setdefault('linewidth', linewidth)

    flierprops = kwargs.pop('flierprops', {})
    flierprops.setdefault('markersize', fliersize)

    return ax.boxplot(x, boxprops=boxprops, whiskerprops=whiskerprops,
                      capprops=capprops, medianprops=medianprops,
                      flierprops=flierprops, **kwargs)
