"""Color utilities for sequence visualization and house palette registry."""

from typing import Dict, List

# Nucleotide color mapping
NUCLEOTIDE_COLORS = {
    "A": "red",
    "C": "blue",
    "G": "orange",
    "T": "green",
    "U": "green",
    "&": "gray",
}

# Named palettes — extend here as new paper conditions arise
_PALETTES: Dict[str, Dict[str, str]] = {
    "nucleotide": dict(NUCLEOTIDE_COLORS),
    "conditions": {
        "cond1": "#2e89c7",
        "cond2": "#ff8b26",
    },
}

# Order of colors for the default prop_cycle (A C G U in RNA order)
_HOUSE_CYCLE_ORDER = ["A", "C", "G", "U"]


def palette(name: str) -> Dict[str, str]:
    """
    Return the named palette dict.

    Args:
        name: Palette name (e.g. "nucleotide", "conditions").

    Returns:
        Dict mapping category key → color string/hex.

    Raises:
        KeyError: If the palette name is unknown.
    """
    if name not in _PALETTES:
        raise KeyError(f"Unknown palette '{name}'. Available: {list(_PALETTES)}")
    return dict(_PALETTES[name])


def palette_hex(name: str, key: str) -> str:
    """
    Return the exact hex color for a single palette entry.

    Both named matplotlib colors ("red") and hex strings are normalized to
    lowercase #rrggbb via matplotlib.colors.to_hex.

    Args:
        name: Palette name (e.g. "nucleotide").
        key: Category key (e.g. "A").

    Returns:
        Hex color string (e.g. "#ff0000").
    """
    import matplotlib.colors as mcolors

    pal = palette(name)
    if key not in pal:
        raise KeyError(f"Key '{key}' not in palette '{name}'. Available: {list(pal)}")
    return mcolors.to_hex(pal[key])


def house_palette_colors() -> List[str]:
    """
    Return an ordered list of hex colors for the default matplotlib prop_cycle.

    Uses ACGU order from the nucleotide palette, then any remaining entries.
    """
    import matplotlib.colors as mcolors

    pal = _PALETTES["nucleotide"]
    ordered = [mcolors.to_hex(pal[k]) for k in _HOUSE_CYCLE_ORDER if k in pal]
    remaining = [
        mcolors.to_hex(v) for k, v in pal.items() if k not in _HOUSE_CYCLE_ORDER
    ]
    return ordered + remaining


def hue_order(name: str) -> List[str]:
    """
    Return the canonical key order for a named palette (for seaborn hue_order).

    Args:
        name: Palette name.

    Returns:
        List of palette keys in insertion order.
    """
    return list(_PALETTES[name].keys())


def colors_for_sequence(seq: str) -> List[str]:
    """
    Get colors for each nucleotide in a sequence.

    Maps each nucleotide character to a specific color:
        - A: red
        - C: blue
        - G: orange
        - T/U: green
        - &: gray

    Args:
        seq: RNA or DNA sequence string.

    Returns:
        List of color strings corresponding to each nucleotide.

    Raises:
        ValueError: If sequence contains invalid characters.

    Example:
        >>> colors_for_sequence("ACGU")
        ['red', 'blue', 'orange', 'green']
    """
    colors = []
    for char in seq.upper():
        if char not in NUCLEOTIDE_COLORS:
            raise ValueError(
                f"Invalid character '{char}' in sequence. "
                f"Valid characters: {list(NUCLEOTIDE_COLORS.keys())}"
            )
        colors.append(NUCLEOTIDE_COLORS[char])

    return colors


def register_seaborn_palettes() -> None:
    """
    Register house palettes with seaborn as named palettes.

    No-op when seaborn is not installed (guarded import).  Safe to call
    multiple times — seaborn.register_colormap is idempotent.
    """
    try:
        import seaborn as sns
        import matplotlib.colors as mcolors
    except ImportError:
        return  # seaborn optional

    for pal_name, pal_dict in _PALETTES.items():
        hex_colors = [mcolors.to_hex(v) for v in pal_dict.values()]
        sns.set_palette(sns.color_palette(hex_colors), n_colors=len(hex_colors))
        # Register as a named seaborn palette for sns.color_palette(pal_name)
        sns.palettes.SEABORN_PALETTES[f"yplot2_{pal_name}"] = hex_colors
