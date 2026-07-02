"""
Catalog decorator for yplot2 plot functions.

``@catalog(tags=..., data_shape=..., kind=...)`` attaches a validated
``__yp_catalog__`` metadata dict to a plot function.

SCOPE (Phase 2 SEED only):
- Attaches metadata; validates against ``yplot2.vocab``.
- There is NO global registry, collector, gallery, or catalog.json here —
  all of that is deferred to Phase 3.

Pure module: imports only ``yplot2.vocab`` — no seaborn, pandas, or mpl.
"""

from collections.abc import Callable, Sequence
from typing import Any

from .vocab import validate_tags, validate_shape, validate_kind


def _category_from_module(module: str) -> str:
    """Extract the category segment from a dotted module path.

    Returns the segment immediately after ``"plots"`` in the path, which
    gives the plot family (e.g. ``"statistical"``). Falls back to
    ``"uncategorized"`` when ``"plots"`` is absent or is the final segment.

    Args:
        module: Dotted module string (e.g. ``"yplot2.plots.statistical.violin"``).

    Returns:
        Category string such as ``"statistical"``.

    Examples:
        >>> _category_from_module("yplot2.plots.statistical.violin")
        'statistical'
        >>> _category_from_module("yplot2.other")
        'uncategorized'
    """
    parts = module.split(".")
    if "plots" not in parts:
        return "uncategorized"
    idx = parts.index("plots")
    if idx + 1 >= len(parts):
        return "uncategorized"
    return parts[idx + 1]


def catalog(
    *,
    tags: Sequence[str],
    data_shape: str,
    kind: str = "panel",
) -> Callable[[Any], Any]:
    """Attach validated catalog metadata to a plot function.

    Validates *tags*, *data_shape*, and *kind* against the controlled
    vocabulary in ``yplot2.vocab`` and raises ``ValueError`` on any unknown
    token (so vocabulary drift is caught at decoration time, not at query
    time in Phase 3).

    Attaches ``fn.__yp_catalog__`` with keys:
    ``tags``, ``data_shape``, ``kind``, ``category``.

    Args:
        tags: One or more controlled-vocabulary tag strings.
        data_shape: Data-shape token (e.g. ``"long-df"``, ``"xy"``).
        kind: Plot kind token (``"panel"`` or ``"figure"``). Default ``"panel"``.

    Returns:
        Decorator that attaches ``__yp_catalog__`` and returns the function unchanged.

    Raises:
        ValueError: If any tag, data_shape, or kind is not in the vocab.
    """
    validate_tags(tags)
    validate_shape(data_shape)
    validate_kind(kind)

    def decorator(fn: Any) -> Any:
        fn.__yp_catalog__ = {
            "tags": tuple(tags),
            "data_shape": data_shape,
            "kind": kind,
            "category": _category_from_module(fn.__module__),
        }
        return fn

    return decorator
