"""
Controlled vocabulary for the yplot2 catalog decorator.

Governance rule: an agent adding a new token MUST append it here (in the
appropriate frozenset) with a one-line justification in the same change.
Unknown tokens are rejected at decoration time so vocabulary drift cannot
start silently.

No heavy imports — this module stays pure so ``import yplot2`` stays fast
and seaborn/pandas-free.
"""

from collections.abc import Sequence

# ---------------------------------------------------------------------------
# Controlled token sets
# ---------------------------------------------------------------------------

TAGS: frozenset[str] = frozenset(
    {
        "distribution",  # plots showing the spread of a variable
        "categorical",  # x-axis is a category
        "density",  # kernel density or 2-D density estimate
        "comparison",  # emphasises differences between groups
        "points",  # raw data points are a primary feature
        "2d-histogram",  # 2-D binned count / heatmap
        "hexbin",  # hexagonal-bin density
        "nucleotide",  # data are nucleotide-labelled (RNA/DNA)
        "seaborn",  # backed by seaborn under the hood
    }
)

DATA_SHAPES: frozenset[str] = frozenset(
    {
        "long-df",  # tidy long-form DataFrame (one row per observation)
        "xy",  # two parallel array-likes (x, y)
        "matrix",  # 2-D array / DataFrame used as a grid
    }
)

KINDS: frozenset[str] = frozenset(
    {
        "panel",  # single axes-level capsule
        "figure",  # multi-axes figure-level layout
    }
)


# ---------------------------------------------------------------------------
# Validators — each raises ValueError on an unknown token
# ---------------------------------------------------------------------------


def validate_tags(tags: Sequence[str]) -> None:
    """Raise ValueError if any tag is not in TAGS.

    Args:
        tags: Sequence of tag strings to validate.

    Raises:
        ValueError: Names the offending token and lists the allowed set.
    """
    for tag in tags:
        if tag not in TAGS:
            raise ValueError(f"Unknown tag {tag!r}. Allowed tags: {sorted(TAGS)}")


def validate_shape(shape: str) -> None:
    """Raise ValueError if *shape* is not in DATA_SHAPES.

    Args:
        shape: Data shape token to validate.

    Raises:
        ValueError: Names the offending token and lists the allowed set.
    """
    if shape not in DATA_SHAPES:
        raise ValueError(
            f"Unknown data_shape {shape!r}. Allowed shapes: {sorted(DATA_SHAPES)}"
        )


def validate_kind(kind: str) -> None:
    """Raise ValueError if *kind* is not in KINDS.

    Args:
        kind: Kind token to validate.

    Raises:
        ValueError: Names the offending token and lists the allowed set.
    """
    if kind not in KINDS:
        raise ValueError(f"Unknown kind {kind!r}. Allowed kinds: {sorted(KINDS)}")
