"""
Strip-overlay helpers for statistical capsules.

``cap_strip_groups`` prevents the large-N footgun where a strip overlay of
hundreds-of-thousands of points visually swamps the underlying distribution
(the dms_vs_tmo Fig1D rebuild exposed this with 236k points).

All seaborn and pandas imports are lazy so this module is safe to import
without the [stats] extra.
"""

from typing import Any


def cap_strip_groups(
    data: Any,
    group_keys: list[str],
    max_points: int | None,
    seed: int,
) -> Any:
    """Return *data* with each group subsampled to at most *max_points* rows.

    Uses a list-comprehension + ``pd.concat`` idiom instead of
    ``groupby(...).apply(...)`` so that no ``FutureWarning`` about grouping
    columns being dropped is emitted and all columns are guaranteed to be
    preserved (the pandas 2.x ``apply`` behaviour that kept grouping columns
    is scheduled for removal).

    When ``max_points`` is ``None``, returns *data* unchanged (all points
    drawn). ``max_points=0`` is valid and returns empty groups. Negative
    values raise ``ValueError``.

    Rationale: the dms_vs_tmo Fig1D rebuild overlaid 236k strip points and
    swamped the violins.  Capping per group (not total) keeps every category
    legible and the render deterministic.

    Args:
        data: DataFrame with at least the columns named in *group_keys*.
        group_keys: Columns to group by (pass ``[x]`` or ``[x, hue]``).
        max_points: Maximum rows kept per group; ``None`` disables the cap.
            ``0`` is valid (returns an empty DataFrame); negative raises.
        seed: RNG seed forwarded to ``DataFrame.sample(random_state=seed)``.

    Returns:
        A (possibly smaller) DataFrame with the same columns as *data*.

    Raises:
        ValueError: If *max_points* is a negative integer.
    """
    if max_points is None:
        return data
    if max_points < 0:
        raise ValueError(
            f"max_points must be None or a non-negative integer, got {max_points}"
        )

    import pandas as pd

    parts = [
        g.sample(min(len(g), max_points), random_state=seed)
        for _, g in data.groupby(group_keys, sort=False)
    ]
    return pd.concat(parts) if parts else data


def _require_seaborn(caller: str) -> Any:
    """Lazily import seaborn; raise a helpful ``ImportError`` if absent.

    This is the single place where the lazy-import guard lives so that
    violin, box, and kde all give the same install hint instead of
    copy-pasting the same 7-line try/except.

    Args:
        caller: Name of the calling function (used in the error message).

    Returns:
        The seaborn module.

    Raises:
        ImportError: With a ``pip install 'yplot2[stats]'`` hint.
    """
    try:
        import seaborn as sns

        return sns
    except ImportError as exc:
        raise ImportError(
            f"seaborn is required for {caller}(). "
            "Install it with: pip install 'yplot2[stats]'"
        ) from exc


def _draw_strip(
    ax: Any,
    data: Any,
    *,
    x: str,
    y: str,
    hue: str | None,
    pal: dict,
    hue_ord: list | None,
    max_strip_points: int | None,
    seed: int,
) -> None:
    """Draw a seeded, subsampled strip overlay on *ax*.

    Extracts the ~12-line block that was duplicated byte-for-byte in
    violin.py and box.py.  Responsibilities: deduplicate group keys when
    ``hue == x``, subsample via ``cap_strip_groups``, and call
    ``sns.stripplot`` with the no-hue fix applied.

    No-hue fix: when *hue* is ``None``, seaborn is called with ``hue=x``
    and ``legend=False`` instead of passing ``palette`` without a hue
    variable (which triggers a seaborn FutureWarning, hard-break at 0.14).

    Args:
        ax: Target Axes.
        data: Full DataFrame (capping is applied inside this function).
        x: Categorical column name.
        y: Numeric column name.
        hue: Original hue column (``None`` → color by *x*).
        pal: Palette dict mapping category keys to colors.
        hue_ord: Hue order (``None`` → seaborn infers from data).
        max_strip_points: Per-group row cap (``None`` → no cap).
        seed: RNG seed for subsample determinism and jitter.
    """
    sns = _require_seaborn("strip overlay")

    # Deduplicate group keys when hue == x (avoids groupby on two identical cols)
    keys = [x] if (hue is None or hue == x) else [x, hue]
    strip_df = cap_strip_groups(data, keys, max_strip_points, seed)

    # When hue is None, color by x to avoid "palette without hue" FutureWarning
    effective_hue = hue if hue is not None else x
    dodge = bool(hue and hue != x)

    sns.stripplot(
        ax=ax,
        data=strip_df,
        x=x,
        y=y,
        hue=effective_hue,
        palette=pal,
        hue_order=hue_ord,
        size=2,
        jitter=True,
        dodge=dodge,
        legend=False,
    )
