"""
Global configuration for yplot2.

Set defaults once, apply everywhere.

Naming conventions:
- axis_*    : Axis spines, ticks, labels
- plot_*    : Data lines and markers
- legend_*  : Legend styling
- panel_*   : Panel labels (A, B, C)
- font_*    : Global font settings
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple, List
import copy


@dataclass
class Config:
    """Global style configuration."""

    # =========================================================================
    # Global font settings
    # =========================================================================
    font_family: str = "Arial"
    # Whether to apply font family changes in apply_style
    apply_fonts: bool = True
    # Whether to apply font size changes in apply_style
    apply_fontsizes: bool = True
    # Fonts to preserve - don't override these when apply_style is called
    preserve_font_families: Tuple[str, ...] = ("Arial Unicode MS",)

    # =========================================================================
    # Axis settings (spines, ticks, labels)
    # =========================================================================
    # Spine (axis lines)
    axis_linewidth: float = 0.75

    # Tick marks (shared settings)
    axis_tick_width: float = 0.75
    axis_tick_length: float = 2.0
    axis_tick_direction: str = "out"  # "in", "out", "inout"

    # X-axis tick settings
    x_axis_tick_pad: float = 1.0
    x_axis_tick_fontsize: float = 6

    # Y-axis tick settings
    y_axis_tick_pad: float = 1.0
    y_axis_tick_fontsize: float = 6

    # X-axis label settings
    x_axis_label_fontsize: float = 8
    x_axis_label_pad: float = 2.0

    # Y-axis label settings
    y_axis_label_fontsize: float = 8
    y_axis_label_pad: float = 2.0

    # Axis title
    axis_title_fontsize: float = 8
    axis_title_pad: float = 4.0

    # =========================================================================
    # Plot settings (data lines, markers)
    # =========================================================================
    plot_linewidth: float = 1.5
    plot_markersize: float = 4
    plot_capsize: float = 3.0         # Error bar caps
    plot_capthick: float = 0.75       # Error bar cap thickness

    # =========================================================================
    # Legend settings
    # =========================================================================
    legend_fontsize: float = 6
    legend_frameon: bool = False
    legend_handlelength: float = 1.0
    legend_labelspacing: float = 0.15

    # =========================================================================
    # Panel label settings (A, B, C, ...)
    # =========================================================================
    panel_label_fontsize: float = 12
    panel_label_fontweight: str = "bold"
    panel_label_offset: Tuple[float, float] = (-0.4, 0.15)  # (dx, dy) inches for plots
    panel_label_offset_image: Tuple[float, float] = (0.00, 0.00)  # (dx, dy) inches for images

    # =========================================================================
    # Colorbar settings
    # =========================================================================
    colorbar_width: float = 0.1       # inches
    colorbar_pad: float = 0.05        # inches
    colorbar_tick_fontsize: float = 6


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
        yp.set_config(font_family="Helvetica", axis_label_fontsize=10)
    """
    global _config
    for key, value in kwargs.items():
        if hasattr(_config, key):
            setattr(_config, key, value)
        else:
            raise ValueError(f"Unknown config option: {key}. "
                           f"Available: {list_config_options()}")


def get_config_value(key: str):
    """Get a single config value by name."""
    cfg = get_config()
    if hasattr(cfg, key):
        return getattr(cfg, key)
    raise ValueError(f"Unknown config option: {key}")


def list_config_options() -> list:
    """List all available config option names."""
    return [f.name for f in Config.__dataclass_fields__.values()]


def reset_config() -> None:
    """Reset configuration to defaults."""
    global _config
    _config = Config()


def print_config() -> None:
    """Print current configuration."""
    cfg = get_config()
    print("Current yplot2 configuration:")
    print("-" * 40)

    # Group by prefix (handle x_axis and y_axis as part of axis group)
    groups = {}
    for key in list_config_options():
        # Map x_axis_* and y_axis_* to 'axis' group
        if key.startswith('x_axis_') or key.startswith('y_axis_'):
            prefix = 'axis'
        else:
            prefix = key.split('_')[0]
        if prefix not in groups:
            groups[prefix] = []
        groups[prefix].append(key)

    for prefix in ['font', 'axis', 'plot', 'legend', 'panel', 'colorbar']:
        if prefix in groups:
            print(f"\n{prefix.upper()}:")
            for key in sorted(groups[prefix]):
                value = getattr(cfg, key)
                print(f"  {key}: {value}")


# =============================================================================
# Preset styles
# =============================================================================
_presets = {
    "publication": Config(
        font_family="Arial",
        axis_linewidth=0.75,
        axis_tick_width=0.75,
        axis_tick_length=2.0,
        x_axis_tick_fontsize=6,
        y_axis_tick_fontsize=6,
        x_axis_label_fontsize=8,
        y_axis_label_fontsize=8,
        axis_title_fontsize=8,
        plot_linewidth=1.5,
        plot_markersize=4,
        legend_fontsize=6,
        panel_label_fontsize=12,
    ),
    "poster": Config(
        font_family="Arial",
        axis_linewidth=1.5,
        axis_tick_width=1.5,
        axis_tick_length=4.0,
        x_axis_tick_fontsize=14,
        y_axis_tick_fontsize=14,
        x_axis_label_fontsize=16,
        y_axis_label_fontsize=16,
        axis_title_fontsize=16,
        plot_linewidth=2.5,
        plot_markersize=8,
        legend_fontsize=12,
        panel_label_fontsize=20,
    ),
    "presentation": Config(
        font_family="Arial",
        axis_linewidth=1.0,
        axis_tick_width=1.0,
        axis_tick_length=3.0,
        x_axis_tick_fontsize=10,
        y_axis_tick_fontsize=10,
        x_axis_label_fontsize=12,
        y_axis_label_fontsize=12,
        axis_title_fontsize=12,
        plot_linewidth=2.0,
        plot_markersize=6,
        legend_fontsize=10,
        panel_label_fontsize=16,
    ),
    "minimal": Config(
        font_family="Arial",
        axis_linewidth=0.5,
        axis_tick_width=0.5,
        axis_tick_length=1.5,
        x_axis_tick_fontsize=6,
        y_axis_tick_fontsize=6,
        x_axis_label_fontsize=7,
        y_axis_label_fontsize=7,
        axis_title_fontsize=7,
        plot_linewidth=1.0,
        plot_markersize=3,
        legend_fontsize=5,
        panel_label_fontsize=10,
    ),
    "nature": Config(
        font_family="Arial",
        axis_linewidth=0.5,
        axis_tick_width=0.5,
        axis_tick_length=2.0,
        x_axis_tick_fontsize=5,
        y_axis_tick_fontsize=5,
        x_axis_label_fontsize=6,
        y_axis_label_fontsize=6,
        axis_title_fontsize=6,
        plot_linewidth=1.0,
        plot_markersize=3,
        legend_fontsize=5,
        panel_label_fontsize=8,
        panel_label_fontweight="bold",
    ),
    # Journal-specific presets
    "cell": Config(
        font_family="Helvetica",
        axis_linewidth=0.5,
        axis_tick_width=0.5,
        axis_tick_length=2.0,
        x_axis_tick_fontsize=6,
        y_axis_tick_fontsize=6,
        x_axis_label_fontsize=7,
        y_axis_label_fontsize=7,
        axis_title_fontsize=7,
        plot_linewidth=1.0,
        plot_markersize=3,
        legend_fontsize=6,
        panel_label_fontsize=8,
        panel_label_fontweight="bold",
    ),
    "science": Config(
        font_family="Helvetica",
        axis_linewidth=0.35,
        axis_tick_width=0.35,
        axis_tick_length=1.5,
        x_axis_tick_fontsize=5,
        y_axis_tick_fontsize=5,
        x_axis_label_fontsize=6,
        y_axis_label_fontsize=6,
        axis_title_fontsize=6,
        plot_linewidth=0.75,
        plot_markersize=2.5,
        legend_fontsize=5,
        panel_label_fontsize=7,
        panel_label_fontweight="bold",
    ),
    "pnas": Config(
        font_family="Arial",
        axis_linewidth=0.5,
        axis_tick_width=0.5,
        axis_tick_length=2.0,
        x_axis_tick_fontsize=6,
        y_axis_tick_fontsize=6,
        x_axis_label_fontsize=8,
        y_axis_label_fontsize=8,
        axis_title_fontsize=8,
        plot_linewidth=1.0,
        plot_markersize=3,
        legend_fontsize=6,
        panel_label_fontsize=9,
        panel_label_fontweight="bold",
    ),
}


def use_preset(name: str) -> None:
    """
    Load a preset style configuration.

    Args:
        name: Preset name

    Available presets:
        General:
        - "publication": Standard publication (default)
        - "poster": Large fonts/lines for posters
        - "presentation": Medium for slides
        - "minimal": Thin lines, small fonts

        Journal-specific:
        - "nature": Nature journal style
        - "cell": Cell journal style (Helvetica)
        - "science": Science journal style (Helvetica, very thin)
        - "pnas": PNAS journal style

    Example:
        yp.use_preset("publication")
        yp.use_preset("cell")
    """
    global _config
    if name not in _presets:
        available = ", ".join(_presets.keys())
        raise ValueError(f"Unknown preset: {name}. Available: {available}")
    _config = copy.deepcopy(_presets[name])


def list_presets() -> list:
    """List available preset names."""
    return list(_presets.keys())
