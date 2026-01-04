"""
Example 11: Plot functions with global config

Shows yp.scatter(), yp.line(), yp.bar(), etc. that automatically
use global config but allow per-plot overrides.
"""
import numpy as np
import yplot2 as yp

# Set global config
yp.set_config(
    fontname="Arial",
    fontsize=8,
    tick_fontsize=6,
    linewidth=0.75,
    markersize=4,
    plot_linewidth=1.5,
)

fig_size = (7.5, 5.0)

# 2x3 grid
a = yp.Coord(left=0.6, bottom=3.0, width=2.0, height=1.7)
b = yp.right_of(a, spacing=0.4)
c = yp.right_of(b, spacing=0.4)
d = yp.below(a, spacing=0.4)
e = yp.below(b, spacing=0.4)
f = yp.below(c, spacing=0.4)

coords = [a, b, c, d, e, f]
fig, axes = yp.create_figure(fig_size, coords)

np.random.seed(42)

# Panel A: yp.line() - uses config.plot_linewidth, config.markersize
x = np.linspace(0, 10, 20)
yp.line(axes[0], x, np.sin(x), marker='o', color='#1565c0')
axes[0].set_title('yp.line()')

# Panel B: yp.scatter() - uses config.markersize
yp.scatter(axes[1], np.random.rand(30), np.random.rand(30), c='#e65100')
axes[1].set_title('yp.scatter()')

# Panel C: yp.bar() - uses config.linewidth for edges
yp.bar(axes[2], [1, 2, 3, 4], [3, 5, 2, 4], color='#2e7d32', edgecolor='black')
axes[2].set_title('yp.bar()')

# Panel D: yp.errorbar() - uses config for caps, line widths
x = np.array([1, 2, 3, 4, 5])
y = np.array([2.1, 3.5, 2.8, 4.2, 3.9])
yerr = np.array([0.3, 0.4, 0.2, 0.5, 0.3])
yp.errorbar(axes[3], x, y, yerr=yerr, color='#c62828')
axes[3].set_title('yp.errorbar()')

# Panel E: yp.hist() - uses config.linewidth for edges
data = np.random.randn(200)
yp.hist(axes[4], data, bins=15, color='#7b1fa2')
axes[4].set_title('yp.hist()')

# Panel F: yp.line() with OVERRIDE - larger markers for this plot only
x = np.linspace(0, 10, 15)
yp.line(axes[5], x, np.cos(x), marker='s', color='#00838f',
        markersize=8, linewidth=2.5)  # Override defaults
axes[5].set_title('yp.line(markersize=8)')

# Apply styling
yp.apply_style_to_all(axes)
yp.add_labels(fig, coords, fig_size, start="A")

fig.savefig("example_11_output.png", dpi=150, bbox_inches="tight", facecolor='white')
print("Saved example_11_output.png")
