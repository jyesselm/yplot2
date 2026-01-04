"""Text annotation utilities."""

from typing import Optional
from matplotlib.axes import Axes

from ..config import get_config


def text(
    ax: Axes,
    x: float,
    y: float,
    s: str,
    fontsize: Optional[float] = None,
    fontname: Optional[str] = None,
    **kwargs,
):
    """
    Text annotation using global config defaults.

    Args:
        ax: Axes object
        x, y: Text position
        s: Text string
        fontsize: Font size
        fontname: Font family
        **kwargs: Additional args to ax.text()

    Returns:
        Text object
    """
    cfg = get_config()

    if fontsize is None:
        fontsize = cfg.axis_label_fontsize
    if fontname is None:
        fontname = cfg.font_family

    return ax.text(x, y, s, fontsize=fontsize, fontname=fontname, **kwargs)
