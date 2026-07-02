"""Canvas: GridSpec7, figure(), and figure7() — declarative grid layout.

All panel geometry is derived arithmetically from a GridSpec7; no solver,
no pixel fudges.  Width is fixed; height is derived from row_heights (or
square-cell default) and margins/gutters.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .coordinates import Coord
from .figure import create_figure

# House defaults — (left, right, top, bottom) in inches.
DEFAULT_MARGINS: Tuple[float, float, float, float] = (0.6, 0.2, 0.2, 0.5)
# (hspace, vspace) in inches between panels.
DEFAULT_GUTTERS: Tuple[float, float] = (0.5, 0.5)

_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


@dataclass(frozen=True)
class GridSpec7:
    """Declarative grid spec resolved to Coords at a fixed figure width.

    Panel width/height are DERIVED, never passed in.  Given the figure width,
    margins, gutters and (rows, cols), each cell width is
    ``(width - left - right - (cols-1)*hspace) / cols``.  Cell height is taken
    from ``row_heights`` (one per row, inches) or, when None, set equal to
    ``cell_width`` (square cells) and figure height is derived to fit.

    Args:
        rows: Number of rows.
        cols: Number of columns.
        names: Optional panel names in row-major order; len must equal rows*cols.
            Defaults to "A", "B", "C", … .
        margins: (left, right, top, bottom) margins in inches.
        gutters: (hspace, vspace) between panels in inches.
        row_heights: Height per row in inches (len must equal rows).  When None,
            each row height equals cell_width (square cells).
    """

    rows: int
    cols: int
    names: Optional[Sequence[str]] = None
    margins: Tuple[float, float, float, float] = DEFAULT_MARGINS
    gutters: Tuple[float, float] = DEFAULT_GUTTERS
    row_heights: Optional[Sequence[float]] = None


def _resolve_names(names: Optional[Sequence[str]], n: int) -> List[str]:
    """Return validated list of n panel names, defaulting to A–Z.

    Args:
        names: Caller-supplied names (or None for default A–Z).
        n: Expected number of names (rows × cols).

    Returns:
        List of n panel name strings.

    Raises:
        ValueError: If n > 26 and no explicit names are supplied (would wrap
            and silently collapse the returned dict).
        ValueError: If names is supplied but has the wrong length.
        ValueError: If names contains duplicate strings (each duplicate would
            overwrite the earlier entry, orphaning the earlier Axes).
    """
    if names is None:
        if n > 26:
            raise ValueError(
                f"{n} panels requested but default names only cover A–Z (26). "
                f"Pass explicit names= to figure() or figure7()."
            )
        return list(_LETTERS[:n])
    if len(names) != n:
        raise ValueError(
            f"names has {len(names)} element(s), expected {n} (rows × cols)"
        )
    seen: set = set()
    dupes: List[str] = []
    for nm in names:
        if nm in seen:
            dupes.append(nm)
        else:
            seen.add(nm)
    if dupes:
        raise ValueError(
            f"names contains duplicate entries: {sorted(set(dupes))!r}. "
            f"Panel names must be unique — duplicates silently orphan axes."
        )
    return list(names)


def _cell_dims(
    spec: GridSpec7,
    width: float,
) -> Tuple[float, List[float], float]:
    """Return (cell_w, row_heights_list, fig_height) for a spec at `width`.

    Args:
        spec: GridSpec7 to resolve.
        width: Figure width in inches.

    Returns:
        Tuple of (cell_width, per-row height list, figure height) in inches.

    Raises:
        ValueError: If the computed cell width is non-positive (margins + gutters
            exceed the figure width).
        ValueError: If row_heights length does not match spec.rows.
    """
    left_m, right_m, top_m, bottom_m = spec.margins
    hspace, vspace = spec.gutters
    cell_w = (width - left_m - right_m - (spec.cols - 1) * hspace) / spec.cols
    if cell_w <= 0:
        raise ValueError(
            f"width {width}\" is too small for {spec.cols} column(s) with the "
            f"given margins and gutters (computed cell_width = {cell_w:.4f}\")."
        )
    if spec.row_heights is not None:
        if len(spec.row_heights) != spec.rows:
            raise ValueError(
                f"row_heights has {len(spec.row_heights)} element(s), "
                f"expected {spec.rows}"
            )
        row_heights_list = list(spec.row_heights)
    else:
        row_heights_list = [cell_w] * spec.rows
    fig_height = top_m + sum(row_heights_list) + (spec.rows - 1) * vspace + bottom_m
    return cell_w, row_heights_list, fig_height


def _resolve_grid(
    spec: GridSpec7,
    width: float,
) -> Tuple[Tuple[float, float], List[Coord], List[str]]:
    """Return (fig_size, coords, names) for a spec at `width`.

    Builds panel Coords ROW-BY-ROW so each row can have a different height.
    Does NOT use coordinates.grid() which forces a uniform cell height.

    Args:
        spec: GridSpec7 to resolve.
        width: Figure width in inches.

    Returns:
        Tuple of (fig_size_inches, list_of_Coords_row_major, list_of_names).
    """
    left_m, _, top_m, _ = spec.margins
    hspace, vspace = spec.gutters
    cell_w, row_heights_list, fig_height = _cell_dims(spec, width)
    n_panels = spec.rows * spec.cols
    names = _resolve_names(spec.names, n_panels)

    coords: List[Coord] = []
    for r in range(spec.rows):
        row_top = fig_height - top_m - sum(row_heights_list[:r]) - r * vspace
        cell_h = row_heights_list[r]
        for c in range(spec.cols):
            left = left_m + c * (cell_w + hspace)
            coords.append(Coord(left, row_top - cell_h, cell_w, cell_h))

    return (width, fig_height), coords, names


def figure(
    width: float,
    rows: int = 1,
    cols: int = 1,
    *,
    names: Optional[Sequence[str]] = None,
    margins: Tuple[float, float, float, float] = DEFAULT_MARGINS,
    gutters: Tuple[float, float] = DEFAULT_GUTTERS,
    row_heights: Optional[Sequence[float]] = None,
    dpi: int = 100,
) -> Tuple[Figure, Dict[str, Axes]]:
    """General fixed-width canvas: build a grid, return (fig, panels).

    Derives panel geometry arithmetically from the spec — no solver, no pixel
    fudges.  Returns an insertion-ordered dict so ``list(panels.values())``
    gives the flat row-major list for callers who want it.

    The figure is returned un-styled; call ``yp.apply_style_to_all`` and/or
    ``yp.finish`` on the axes when ready.

    Args:
        width: Figure width in inches (exact).
        rows: Number of panel rows (default 1).
        cols: Number of panel columns (default 1).
        names: Panel names in row-major order.  Defaults to "A", "B", "C", … .
            Raises ValueError if len(names) != rows * cols.
        margins: (left, right, top, bottom) margins in inches.
        gutters: (hspace, vspace) between panels in inches.
        row_heights: Height per row in inches.  None → square cells (height =
            cell_width).  Raises ValueError if len != rows.
        dpi: Figure DPI (default 100).

    Returns:
        (fig, panels) where panels is an ordered dict name → Axes.

    Raises:
        ValueError: Wrong names or row_heights count.

    Example::

        fig, panels = yp.figure(7.0, 2, 3)
        ax_a = panels["A"]   # top-left
        yp.apply_style_to_all(list(panels.values()))
    """
    spec = GridSpec7(
        rows=rows,
        cols=cols,
        names=names,
        margins=margins,
        gutters=gutters,
        row_heights=row_heights,
    )
    fig_size, coords, panel_names = _resolve_grid(spec, width)
    fig, axes_list = create_figure(fig_size, coords, dpi=dpi)
    panels: Dict[str, Axes] = {name: ax for name, ax in zip(panel_names, axes_list)}
    return fig, panels


def figure7(
    rows: int = 1,
    cols: int = 1,
    **kwargs,
) -> Tuple[Figure, Dict[str, Axes]]:
    """7-inch-wide headline preset.

    Thin wrapper: ``figure(7.0, rows, cols, **kwargs)``.  All keyword args from
    ``figure()`` are accepted (names, margins, gutters, row_heights, dpi).

    Args:
        rows: Number of panel rows (default 1).
        cols: Number of panel columns (default 1).
        **kwargs: Forwarded to figure().

    Returns:
        (fig, panels) — see figure() for details.

    Example::

        fig, panels = yp.figure7(2, 3)
        # panels["A"] … panels["F"] in row-major order
        for ax in panels.values():
            yp.apply_style(ax)
    """
    return figure(7.0, rows, cols, **kwargs)
