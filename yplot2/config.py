"""
Global configuration for yplot2.

Set defaults once, apply everywhere.
"""

from dataclasses import dataclass, field
from typing import Optional
import copy


@dataclass
class Config:
    """Global style configuration."""

    # Fonts
    fontname: str = "Arial"
    fontsize: float = 8          # Labels, titles
    tick_fontsize: float = 6     # Tick labels
    label_fontsize: float = 8    # Axis labels
    title_fontsize: float = 8    # Titles
    legend_fontsize: float = 6   # Legend text
    panel_label_fontsize: float = 12  # A, B, C labels

    # Lines
    linewidth: float = 0.75      # Axis spines
    tick_width: float = 0.75     # Tick marks
    tick_size: float = 2.0       # Tick length
    tick_pad: float = 1.0        # Tick to label padding
    plot_linewidth: float = 1.5  # Data lines

    # Markers
    markersize: float = 4        # Data markers

    # Legend
    legend_frameon: bool = False
    legend_handlelength: float = 1.0
    legend_labelspacing: float = 0.15

    # Panel labels
    panel_label_weight: str = "bold"
    panel_label_offset: tuple = (-0.4, 0.15)  # (dx, dy) in inches


# Global instance
_config = Config()


def get_config() -> Config:
    """Get the current global configuration."""
    return _config


def set_config(**kwargs) -> None:
    """
    Set global configuration values.

    Args:
        **kwargs: Any Config field name and value

    Example:
        yp.set_config(fontname="Helvetica", fontsize=10)
    """
    global _config
    for key, value in kwargs.items():
        if hasattr(_config, key):
            setattr(_config, key, value)
        else:
            raise ValueError(f"Unknown config option: {key}")


def reset_config() -> None:
    """Reset configuration to defaults."""
    global _config
    _config = Config()


# Preset styles
_presets = {
    "publication": Config(
        fontname="Arial",
        fontsize=8,
        tick_fontsize=6,
        linewidth=0.75,
        tick_width=0.75,
        tick_size=2.0,
        markersize=4,
        plot_linewidth=1.5,
    ),
    "poster": Config(
        fontname="Arial",
        fontsize=14,
        tick_fontsize=12,
        linewidth=1.5,
        tick_width=1.5,
        tick_size=4.0,
        markersize=8,
        plot_linewidth=2.5,
    ),
    "presentation": Config(
        fontname="Arial",
        fontsize=12,
        tick_fontsize=10,
        linewidth=1.0,
        tick_width=1.0,
        tick_size=3.0,
        markersize=6,
        plot_linewidth=2.0,
    ),
    "minimal": Config(
        fontname="Arial",
        fontsize=8,
        tick_fontsize=6,
        linewidth=0.5,
        tick_width=0.5,
        tick_size=1.5,
        markersize=3,
        plot_linewidth=1.0,
    ),
}


def use_preset(name: str) -> None:
    """
    Load a preset style configuration.

    Args:
        name: Preset name ("publication", "poster", "presentation", "minimal")

    Example:
        yp.use_preset("publication")
    """
    global _config
    if name not in _presets:
        available = ", ".join(_presets.keys())
        raise ValueError(f"Unknown preset: {name}. Available: {available}")
    _config = copy.deepcopy(_presets[name])


def list_presets() -> list:
    """List available preset names."""
    return list(_presets.keys())
