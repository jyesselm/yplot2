"""Color utilities for sequence visualization."""

from typing import List

# Nucleotide color mapping
NUCLEOTIDE_COLORS = {
    "A": "red",
    "C": "blue",
    "G": "orange",
    "T": "green",
    "U": "green",
    "&": "gray",
}


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
