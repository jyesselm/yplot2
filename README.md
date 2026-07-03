# yplot2

Matplotlib subplot layout with absolute positioning and helper tools. All dimensions in inches for intuitive control over publication-quality figures.

## Installation

```bash
pip install -e .
```

## Quick Start

```python
import yplot2 as yp

# Define panel positions (all in inches)
a = yp.Coord(left=0.5, bottom=3.0, width=2.5, height=2.0)
b = yp.right_of(a, spacing=0.5)  # Same size, 0.5" to the right
c = yp.below(a, spacing=0.4)     # Same size, 0.4" below

# Create figure
fig_size = (7.5, 5.0)
fig, axes = yp.create_figure(fig_size, [a, b, c])

# Plot using wrapper functions (use global config)
yp.line(axes[0], x, y, marker='o')
yp.scatter(axes[1], x, y)
yp.bar(axes[2], categories, values)

# Apply styling and labels
yp.apply_style_to_all(axes)
yp.add_labels(fig, [a, b, c], fig_size, start="A")

fig.savefig("figure.png", dpi=300)
```

## Core Concepts

### Coordinates

All positions and sizes are in **inches**. A `Coord` defines a panel:

```python
coord = yp.Coord(left=0.5, bottom=2.0, width=3.0, height=2.0)

# Properties
coord.right    # left + width
coord.top      # bottom + height
coord.center_x # horizontal center
coord.center_y # vertical center
```

### Relative Positioning

Position panels relative to each other:

```python
a = yp.Coord(left=0.5, bottom=5.0, width=2.0, height=1.5)

# Same size as reference by default
b = yp.right_of(a, spacing=0.5)
c = yp.below(a, spacing=0.4)
d = yp.left_of(a, spacing=0.5)
e = yp.above(a, spacing=0.4)

# Override size
f = yp.right_of(a, spacing=0.5, width=3.0)
g = yp.below(a, spacing=0.4, height=2.0)
h = yp.below(a, spacing=0.4, size=(3.0, 2.0))

# Copy and shift
i = yp.copy(a, dx=3.0, dy=-2.0)
j = yp.shift(a, dx=0.5)
k = yp.same_size(a, left=4.0, bottom=1.0)

# Resize with anchor
l = yp.resize(a, width=3.0, anchor="center")
```

## Layout Class (Recommended)

For figures with mixed image and plot panels, use the `Layout` class for smarter label positioning:

```python
import yplot2 as yp

# Create layout with figure size
layout = yp.Layout(fig_size=(7.0, 5.0))

# Add panels with type information
a = yp.Coord(left=0.5, bottom=1.5, width=2.5, height=2.5)
b = yp.right_of(a, spacing=0.5)

layout.add_image(a, name="structure")   # Image panel
layout.add_plot(b, name="scatter")      # Plot panel

# Create figure
fig, axes = layout.create_figure()

# Use panels
yp.load_image(axes[0], "structure.png")
yp.scatter(axes[1], x, y)
yp.apply_style(axes[1])

# Smart labels - different offset for images vs plots
layout.add_labels()  # "A" closer to image edge, "B" offset for y-axis

fig.savefig("figure.png", dpi=300)
```

### Layout Features

```python
# Method chaining
layout = (yp.Layout(fig_size=(7.0, 5.0))
    .add_image(a, name="img1")
    .add_plot(b, name="plot1")
    .add_plot(c, name="plot2"))

# Access panels by name
ax = layout.get_ax("scatter")
panel = layout.get_panel("structure")

# Filter by type
layout.plot_axes   # List of plot axes only
layout.image_axes  # List of image axes only

# All coords/panels
layout.coords      # List of Coord objects
layout.panels      # List of Panel objects

# Debug helpers
layout.draw_debug_boxes()

# Reset to recreate figure
layout.reset()
fig, axes = layout.create_figure()
```

### Generators

Create rows, columns, or grids:

```python
# Row of 4 equally-spaced panels
row1 = yp.row(n=4, size=(1.5, 1.5), spacing=0.3, left=0.5, bottom=3.0)

# Column of 3 panels (top to bottom)
col1 = yp.column(n=3, size=(2.0, 1.5), spacing=0.3, left=0.5, top=6.0)

# 2x3 grid
grid1 = yp.grid(rows=2, cols=3, size=(1.5, 1.5),
                hspace=0.3, vspace=0.3, left=0.5, top=6.0)
coords = yp.flatten_grid(grid1)  # Convert to flat list
```

### Spacing Calculations

Calculate ideal spacing or sizes:

```python
# Calculate spacing to evenly fit 4 panels in 7.5" with 0.5" margins
spacing = yp.fit_row_spacing(
    fig_width=7.5,
    n=4,
    subplot_width=1.5,
    margins=(0.5, 0.5)  # left, right
)

# Calculate panel width given spacing
width = yp.fit_subplot_width(
    fig_width=7.5,
    n=4,
    spacing=0.3,
    margins=(0.5, 0.5)
)

# Check if coords fit in figure
result = yp.check_fit(fig_size, coords)
if not result['fits']:
    print(result['issues'])

# Suggest minimum figure size
suggested = yp.suggest_figure_size(coords, margins=(0.5, 0.5, 0.5, 0.5))
```

## Global Configuration

Set style defaults once, apply everywhere:

```python
# Set individual parameters
yp.set_config(
    font_family="Arial",
    axis_label_fontsize=8,
    axis_tick_fontsize=6,
    axis_linewidth=0.75,
    plot_markersize=4,
    plot_linewidth=1.5,
)

# Or use a preset
yp.use_preset("publication")  # Small fonts, thin lines
yp.use_preset("poster")       # Large fonts, thick lines
yp.use_preset("presentation") # Medium
yp.use_preset("minimal")      # Very thin lines

# View current config
cfg = yp.get_config()
print(cfg.font_family, cfg.axis_label_fontsize)

# Reset to defaults
yp.reset_config()
```

### All Config Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| **Font** | | |
| `font_family` | "Arial" | Font family for all text |
| **Axis** | | |
| `axis_linewidth` | 0.75 | Axis spine line width |
| `axis_tick_width` | 0.75 | Tick mark width |
| `axis_tick_length` | 2.0 | Tick mark length |
| `axis_tick_pad` | 1.0 | Tick to label padding |
| `axis_tick_fontsize` | 6 | Tick label font size |
| `axis_tick_direction` | "out" | Tick direction ("in", "out", "inout") |
| `axis_label_fontsize` | 8 | X/Y axis label font size |
| `axis_label_pad` | 2.0 | Axis label padding |
| `axis_title_fontsize` | 8 | Axis title font size |
| `axis_title_pad` | 4.0 | Axis title padding |
| **Plot** | | |
| `plot_linewidth` | 1.5 | Data line width |
| `plot_markersize` | 4 | Data marker size |
| `plot_capsize` | 3.0 | Error bar cap size |
| `plot_capthick` | 0.75 | Error bar cap thickness |
| **Legend** | | |
| `legend_fontsize` | 6 | Legend text size |
| `legend_frameon` | False | Draw legend frame |
| `legend_handlelength` | 1.0 | Legend handle length |
| `legend_labelspacing` | 0.15 | Legend entry spacing |
| **Panel Labels** | | |
| `panel_label_fontsize` | 12 | A, B, C label size |
| `panel_label_fontweight` | "bold" | A, B, C label weight |
| `panel_label_offset` | (-0.4, 0.15) | Label offset for plots (dx, dy) inches |
| `panel_label_offset_image` | (0.05, 0.15) | Label offset for images (dx, dy) inches |
| **Colorbar** | | |
| `colorbar_width` | 0.1 | Colorbar width (inches) |
| `colorbar_pad` | 0.05 | Colorbar padding (inches) |
| `colorbar_tick_fontsize` | 6 | Colorbar tick font size |

## Plot Functions

All plot functions use global config but allow overrides:

```python
# Line plot
yp.line(ax, x, y, marker='o', color='blue')
yp.line(ax, x, y, linewidth=3, markersize=8)  # Override

# Scatter plot
yp.scatter(ax, x, y, c='red')
yp.scatter(ax, x, y, s=100)  # Override marker size

# Bar plots
yp.bar(ax, x, height, color='steelblue')
yp.barh(ax, y, width, color='coral')

# Error bars
yp.errorbar(ax, x, y, yerr=errors, fmt='o', color='green')

# Histogram
yp.hist(ax, data, bins=20, color='purple')

# Box plot
yp.boxplot(ax, [data1, data2, data3])

# Fill between (for confidence intervals)
yp.fill_between(ax, x, y-err, y+err, alpha=0.3)

# Reference lines
yp.hline(ax, y=0, color='gray', linestyle='--')
yp.vline(ax, x=5, color='gray', linestyle='--')

# Text with named positions
yp.text(ax, "n = 100", pos="top left")
yp.text(ax, "p < 0.05", pos="tr")  # Alias for "top right"
yp.text(ax, "R² = 0.95", pos="bottom right", fontweight="bold")

# Text with box
yp.text(ax, "Important", pos="center", box=True)

# Styled box using box_args
yp.text(ax, "Styled", pos="center", box=True,
        box_args={"facecolor": "yellow", "edgecolor": "red", "alpha": 0.8})

# Custom position (x, y in axes coordinates 0-1)
yp.text(ax, "Custom", pos=(0.5, 0.8))

# Available positions:
# Corners: 'top left' (tl), 'top right' (tr), 'bottom left' (bl), 'bottom right' (br)
# Edges: 'top', 'bottom', 'left', 'right'
# Center: 'center'
# Outside: 'above', 'below'
```

## Argument Grouping Pattern

Composite plot functions use `*_args` dicts to group related styling options. This keeps function signatures clean while allowing full customization:

```python
# Instead of many individual parameters:
# regplot(ax, x, y, line_color="red", line_linewidth=2, line_linestyle="--", ...)

# Use grouped *_args dicts:
yp.regplot(ax, x, y,
           line_args={"color": "red", "linewidth": 2, "linestyle": "--"},
           scatter_args={"c": "blue", "s": 100, "alpha": 0.5},
           r2_args={"pos": "top right", "precision": 2})
```

Common `*_args` patterns:
- `line_args` - color, linewidth, linestyle (passed to `line()`)
- `scatter_args` - c, s, marker, alpha, edgecolors (passed to `scatter()`)
- `marker_args` - same as scatter_args
- `r2_args` - pos, prefix, precision, fontsize, box
- `cbar_args` - label, width, pad (colorbar options, width/pad in inches)
- `box_args` - facecolor, edgecolor, alpha, style

## Specialized Plots

### RNA Reactivity Plots

Plot population average reactivities with nucleotide-colored bars:

```python
# Plot RNA reactivity data
yp.pop_avg(ax, "ACGU", "(..)", [0.1, 0.2, 0.3, 0.4])

# Plot from DataFrame row
yp.pop_avg_from_row(ax, row, data_col="data")

# Plot all rows in DataFrame
yp.pop_avg_all(df, data_col="data")

# Overlay traces
yp.pop_avg_traces(ax, df, data_col="data", label_col="rna_name")

# Get colors for nucleotides
colors = yp.colors_for_sequence("ACGU")  # ['red', 'blue', 'orange', 'green']
```

### Lollipop Plots

Compare paired data points with connecting lines:

```python
x = [1, 2, 3, 4]
y1 = [0.1, 0.2, 0.3, 0.4]
y2 = [0.15, 0.25, 0.35, 0.45]

# Basic usage
yp.lollipop(ax, x, y1, y2)

# Custom styling with *_args
yp.lollipop(ax, x, y1, y2,
            line_args={"color": "red", "linewidth": 2},
            marker_args={"c": "blue", "s": 100})
```

### Regression Plots

Scatter plot with regression line and R² annotation:

```python
# Basic usage - dashed black fit line, R² shown in top-left by default
result = yp.regplot(ax, x, y)
print(f"Slope: {result['slope']}, R²: {result['r_squared']}")

# Custom styling
yp.regplot(ax, x, y,
           line_args={"color": "red", "linestyle": "-"},
           scatter_args={"c": "blue", "alpha": 0.5},
           r2_args={"pos": "top right", "precision": 2, "box": True})

# Hide scatter or R² text
yp.regplot(ax, x, y, show_scatter=False)
yp.regplot(ax, x, y, show_r2=False)
```

### Density Regression Plots

For large datasets, use `regplot_density` to show point density with color.
Each point is colored by local density (computed via 2D histogram), with
high-density points drawn on top:

```python
# Basic usage - density-colored scatter with colorbar
result = yp.regplot_density(ax, x, y)

# Custom styling
yp.regplot_density(ax, x, y,
                   bins=200,
                   scatter_args={"cmap": "viridis", "s": 5, "cmap_min": 0.3},
                   line_args={"color": "red"},
                   cbar_args={"label": "Points"})

# Hide colorbar or R²
yp.regplot_density(ax, x, y, show_cbar=False)
yp.regplot_density(ax, x, y, show_r2=False)
```

## Styling

```python
# Apply publication style to all axes
yp.apply_style_to_all(axes)

# Or individual axes with overrides
yp.apply_style(ax, axis_label_fontsize=10, axis_linewidth=1.0)

# Remove spines
yp.remove_spines(ax, ['top', 'right'])

# Add styled legend
yp.add_legend(ax, ['Label 1', 'Label 2'], loc='upper right')

# Set background color (useful for debugging layout)
yp.set_background(ax, "lightgray")
yp.set_background_all(axes, "lightyellow")

# Draw border around entire figure
yp.draw_figure_border(fig)
yp.draw_figure_border(fig, linewidth=2, color="gray")
```

## Axis Utilities

### Match Ticks Between Axes

Copy tick positions and limits from one axis to another (useful for square plots):

```python
# Copy y-axis ticks and limits to x-axis (default)
yp.match_ticks(ax, source="y", target="x")

# Copy only ticks, keep original limits
yp.match_ticks(ax, source="y", target="x", match_limits=False)
```

## Shared Axes

For grouped panels with shared labels:

```python
# Share x-axis (hide labels except bottom)
yp.share_x([axes[0], axes[2]])  # Column of panels

# Share y-axis (hide labels except left)
yp.share_y([axes[0], axes[1]])  # Row of panels

# Sync axis limits
yp.sync_limits([axes[0], axes[1]], axis="y")

# Add shared labels
yp.add_shared_xlabel(fig, [c, d], fig_size, "X Label")
yp.add_shared_ylabel(fig, [a, c], fig_size, "Y Label")

# Configure entire grid at once
yp.group_grid(
    [[ax_a, ax_b], [ax_c, ax_d]],
    share_x=True,
    share_y=True,
)
```

## Log Axis with Zero Handling

For log-scale plots that include zero values:

```python
import numpy as np

x = np.array([0, 0.1, 1, 10, 100])
y = np.array([1, 2, 3, 4, 5])

# Transform zeros to epsilon for log scale
eps, positive_vals, x_plot = yp.compute_eps_and_transform(x)

# Plot with transformed x values
ax.scatter(x_plot, y)

# Configure axis to show "0" at epsilon position
yp.log_axis_with_zero(ax, eps, positive_vals)
```

## Sequence/Structure Axis Formatting

For molecular data with sequence or structure labels:

```python
sequence = "ACGU"
structure = "(..)"

# Show just sequence on x-axis
yp.sequence_x_axis(ax, sequence)

# Show just structure on x-axis
yp.structure_x_axis(ax, structure)

# Show both (sequence on top, structure below)
yp.sequence_structure_x_axis(ax, sequence, structure)

# Or use by name
yp.apply_x_axis_format(ax, sequence, structure, "sequence_structure")
```

## Image Panels

For figures with molecular structures, schematics, etc:

```python
# Create panel matching exact image dimensions (no distortion)
a = yp.coord_from_image("structure.png", left=0.5, bottom=3.0, dpi=300)

# Scale image to 50% of original size
b = yp.coord_from_image("structure.png", left=0.5, bottom=1.0, scale=0.5)

# Get image size in inches
width, height = yp.get_image_size("structure.png", dpi=300)

# Load image (fills panel edge-to-edge)
yp.load_image(axes[0], "structure.png")

# Load with aspect ratio check (warns if panel doesn't match image)
yp.load_image(axes[0], "structure.png", coord=a)

# Prepare panel for custom edge-to-edge content
yp.make_image_panel(axes[1])
axes[1].fill([0, 1, 1, 0], [0, 0, 1, 1], color='#333')
```

### Tight Layouts (Publication Style)

For edge-to-edge image panels like publications:

```python
# Image panels start at edge (left=0)
a = yp.Coord(left=0.0, bottom=5.0, width=3.0, height=2.0)

# Plot panels have small margin for y-axis
c = yp.Coord(left=0.5, bottom=2.5, width=2.5, height=2.0)

# Full-width bottom image
g = yp.Coord(left=0.0, bottom=0.0, width=7.0, height=2.0)
```

## Panel Labels

```python
# Add A, B, C labels
yp.add_labels(fig, coords, fig_size, start="A")

# Lowercase
yp.add_labels(fig, coords, fig_size, start="a")

# Custom offset (dx, dy from top-left corner)
yp.add_labels(fig, coords, fig_size, start="A", offset=(-0.3, 0.1))
```

## Debugging

```python
# Draw colored boxes around each panel
yp.draw_debug_boxes(fig, coords, fig_size)
```

## Complete Example

```python
import numpy as np
import yplot2 as yp

# Configure global style
yp.use_preset("publication")

fig_size = (7.5, 6.0)

# Layout: 2 images on top, 4 plots below in 2x2
a = yp.Coord(left=0.0, bottom=4.0, width=3.5, height=2.0)
b = yp.right_of(a, spacing=0.3, width=3.7)

c = yp.Coord(left=0.6, bottom=2.0, width=2.8, height=1.6)
d = yp.right_of(c, spacing=0.4)
e = yp.below(c, spacing=0.3)
f = yp.below(d, spacing=0.3)

coords = [a, b, c, d, e, f]
fig, axes = yp.create_figure(fig_size, coords)

# Panels A, B: Images
yp.load_image(axes[0], "structure1.png")
yp.load_image(axes[1], "structure2.png")

# Panels C-F: Plots
x = np.linspace(0, 10, 30)
yp.line(axes[2], x, np.sin(x), marker='o', color='#c62828')
yp.line(axes[3], x, np.cos(x), marker='o', color='#2e7d32')
yp.scatter(axes[4], np.random.rand(30), np.random.rand(30))
yp.bar(axes[5], [1,2,3,4], [3,5,2,4])

# Style plots (not images)
yp.apply_style_to_all(axes[2:])

# Shared axes for bottom grid
yp.share_x([axes[2], axes[4]])
yp.share_x([axes[3], axes[5]])
yp.share_y([axes[2], axes[3]])
yp.share_y([axes[4], axes[5]])

# Labels
yp.add_labels(fig, coords, fig_size, start="A")

fig.savefig("figure.png", dpi=300, bbox_inches="tight")
```

## API Reference

### Coordinates
- `Coord(left, bottom, width, height)` - Panel position/size in inches
- `row(n, size, spacing, left, bottom)` - Generate row of panels
- `column(n, size, spacing, left, top)` - Generate column of panels
- `grid(rows, cols, size, hspace, vspace, left, top)` - Generate grid

### Layout
- `Layout(fig_size, dpi)` - Layout manager for mixed image/plot figures
- `Layout.add(coord, panel_type, name)` - Add panel ("plot" or "image")
- `Layout.add_plot(coord, name)` - Add plot panel
- `Layout.add_image(coord, name)` - Add image panel
- `Layout.create_figure()` - Create figure and axes
- `Layout.add_labels(start)` - Add type-aware panel labels
- `Layout.get_ax(name)` - Get axes by name
- `Layout.get_panel(name)` - Get Panel by name
- `Layout.plot_axes` - List of plot axes
- `Layout.image_axes` - List of image axes
- `Layout.draw_debug_boxes()` - Draw debug boxes
- `Layout.reset()` - Reset to recreate figure
- `Panel(coord, panel_type, name, label)` - Panel metadata container

### Positioning
- `right_of(ref, spacing, ...)` - Panel to the right
- `left_of(ref, spacing, ...)` - Panel to the left
- `below(ref, spacing, ...)` - Panel below
- `above(ref, spacing, ...)` - Panel above
- `copy(ref, dx, dy, ...)` - Copy with offset
- `shift(ref, dx, dy)` - Shift position
- `same_size(ref, left, bottom)` - Same size at new position
- `resize(ref, width, height, anchor)` - Resize with anchor

### Spacing
- `fit_row_spacing(fig_width, n, subplot_width, margins)` - Calculate spacing
- `fit_subplot_width(fig_width, n, spacing, margins)` - Calculate width
- `check_fit(fig_size, coords)` - Check if coords fit
- `suggest_figure_size(coords, margins)` - Suggest figure size

### Figure
- `create_figure(size, coords)` - Create figure with axes
- `get_image_size(path, dpi)` - Get image dimensions in inches
- `coord_from_image(path, left, bottom, dpi, scale)` - Create Coord matching image size
- `load_image(ax, path, coord)` - Load image into panel (warns if aspect ratio differs)
- `make_image_panel(ax)` - Prepare for edge-to-edge content
- `add_labels(fig, coords, fig_size, start)` - Add panel labels
- `draw_debug_boxes(fig, coords, fig_size)` - Debug visualization
- `draw_figure_border(fig, linewidth, color)` - Draw border around figure

### Config
- `set_config(**kwargs)` - Set config values
- `get_config()` - Get current config
- `reset_config()` - Reset to defaults
- `use_preset(name)` - Load preset ("publication", "poster", etc.)

### Plotting (Basic)
- `line(ax, x, y, ...)` - Line plot
- `scatter(ax, x, y, ...)` - Scatter plot
- `bar(ax, x, height, ...)` - Bar plot
- `barh(ax, y, width, ...)` - Horizontal bar plot
- `errorbar(ax, x, y, yerr, ...)` - Error bars
- `fill_between(ax, x, y1, y2, ...)` - Filled region
- `hist(ax, x, ...)` - Histogram
- `boxplot(ax, x, ...)` - Box plot
- `hline(ax, y, ...)` - Horizontal line
- `vline(ax, x, ...)` - Vertical line
- `text(ax, text, pos, box, box_args, ...)` - Text at named position ('top left', 'center', etc.)

### Plotting (Specialized)
- `regplot(ax, x, y, line_args, scatter_args, r2_args, ...)` - Regression plot with R² annotation
- `regplot_density(ax, x, y, bins, scatter_args, line_args, r2_args, cbar_args, ...)` - Density-colored scatter with colorbar
- `lollipop(ax, x, y1, y2, line_args, marker_args)` - Paired lollipop plot
- `pop_avg(ax, sequence, structure, reactivities, ...)` - RNA reactivity bar plot
- `pop_avg_from_row(ax, row, ...)` - Plot from DataFrame row
- `pop_avg_diff(row1, row2, ...)` - Difference plot
- `pop_avg_all(df, ...)` - Plot all rows in DataFrame
- `pop_avg_traces(ax, df, ...)` - Overlaid traces
- `colors_for_sequence(seq)` - Get nucleotide colors (A=red, C=blue, G=orange, T/U=green)

### Styling
- `apply_style(ax, ...)` - Apply style to one axes
- `apply_style_to_all(axes)` - Apply style to all axes
- `remove_spines(ax, spines)` - Remove axis spines
- `add_legend(ax, labels, ...)` - Add styled legend
- `set_background(ax, color)` - Set axes background color
- `set_background_all(axes, color)` - Set background for all axes

### Axis Utilities
- `match_ticks(ax, source, target)` - Copy tick positions from one axis to another

### Shared Axes
- `share_x(axes_list)` - Share x-axis (hide labels)
- `share_y(axes_list)` - Share y-axis (hide labels)
- `sync_limits(axes_list, axis)` - Sync axis limits
- `add_shared_xlabel(fig, coords, fig_size, label)` - Shared x label
- `add_shared_ylabel(fig, coords, fig_size, label)` - Shared y label
- `group_grid(axes_grid, ...)` - Configure grid of axes

### Log Axis with Zero Handling
- `compute_eps_and_transform(x)` - Transform data with zeros for log scale
- `log_axis_with_zero(ax, eps, positive_values)` - Configure log axis showing zero

### Sequence/Structure Axis Formatting
- `sequence_x_axis(ax, sequence)` - Show nucleotide sequence on x-axis
- `structure_x_axis(ax, structure)` - Show dot-bracket structure on x-axis
- `sequence_structure_x_axis(ax, sequence, structure)` - Show both (stacked)
- `apply_x_axis_format(ax, sequence, structure, axis_type)` - Apply by name

## Anti-fork lint

`python -m yplot2.lint` is a pure-stdlib AST lint for **paper repos** that use yplot2.
It flags patterns that re-invent what yplot2 already provides and points each finding at
the yplot2 replacement. It is intentionally **not** run against yplot2 itself.

The #1 design goal is **low false-positives** — a noisy lint gets disabled.

### Rules

| Code  | Level   | What it flags |
|-------|---------|---------------|
| YP001 | ERROR   | locally-defined house-style function (`publication_style_ax`, `format_small_plot`, `publication_style`, `publication_scatter`, `publication_line`) |
| YP002 | WARNING | inline `figsize=` tuple/list on `plt.subplots` / `plt.figure` |
| YP003 | WARNING | `plt.subplots_adjust(...)` — manual layout |
| YP004 | WARNING | raw `fig.savefig(...)` / `plt.savefig(...)` |
| YP005 | WARNING | dict literal with ≥2 hex-string values (hardcoded palette) |
| YP006 | WARNING | raw `sns.violinplot` / `sns.boxplot` / `sns.stripplot` (opt-in only) |

Only YP001 (ERROR) causes a nonzero exit by default, so it can be wired as a blocking
pre-commit or CI check without disrupting exploratory scripts that use `figsize=` or
`savefig`. YP006 (raw seaborn) is **opt-in only** — yplot2 supports raw seaborn drawn
into a panel followed by `yp.finish(ax)`, so it is not flagged by default.

### Usage

```bash
# Lint a directory tree
python -m yplot2.lint src/ figures/

# Only check specific rules
python -m yplot2.lint --select YP001,YP002 src/

# Suppress a rule
python -m yplot2.lint --ignore YP003 figures/

# Enable the opt-in raw-seaborn rule
python -m yplot2.lint --select YP001,YP002,YP003,YP004,YP005,YP006 src/
```

### Inline suppression

```python
def publication_style_ax(ax):  # yplot2: ignore
    ...

fig, ax = plt.subplots(figsize=(2, 1.5))  # yplot2: ignore=YP002
```

### Pre-commit hook (paper repo `.pre-commit-config.yaml`)

```yaml
-   repo: local
    hooks:
    -   id: yplot2-anti-fork
        name: yplot2 anti-fork lint
        entry: python -m yplot2.lint
        language: system
        types: [python]
        # optional: keep raw seaborn allowed (default)
        args: ["--ignore", "YP006"]
```

### GitHub Actions step

```yaml
      - name: yplot2 anti-fork lint
        run: python -m yplot2.lint src/ figures/
```

### Limitations

The callee-set rules (YP002 for `figsize=`, YP006 for seaborn plots) match
only the standard aliases `plt.`/`pyplot.` and `sns.`. Unusual import aliases
(e.g. `import matplotlib.pyplot as mpl`) are intentionally not matched — this
keeps false-positives near zero at the cost of missing the aliased form. If
your paper repo uses a non-standard alias, add an explicit `--select` / annotation
or rename the import to the conventional alias. Similarly, a bare `subplots()`
from a `from matplotlib.pyplot import subplots` is not flagged by YP002.
