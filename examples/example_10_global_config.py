"""
Example 10: Global configuration system

Shows how to set global defaults once and have them apply everywhere.
"""
import numpy as np
import matplotlib.pyplot as plt
import yplot2 as yp

# Set global config at the start - everything uses Arial, consistent sizes
yp.set_config(
    fontname="Arial",
    fontsize=8,
    tick_fontsize=6,
    linewidth=0.75,
    tick_width=0.75,
    markersize=4,
    plot_linewidth=1.5,
)

fig_size = (7.0, 3.0)

# Simple row of 3 plots
a = yp.Coord(left=0.6, bottom=0.5, width=1.8, height=2.0)
b = yp.right_of(a, spacing=0.5)
c = yp.right_of(b, spacing=0.5)

coords = [a, b, c]
fig, axes = yp.create_figure(fig_size, coords)

# Plot data
np.random.seed(42)
x = np.linspace(0, 10, 30)

# Panel A - line plot
axes[0].plot(x, np.sin(x), 'o-', markersize=yp.get_config().markersize,
             lw=yp.get_config().plot_linewidth)
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('Amplitude')
axes[0].set_title('Sine Wave')

# Panel B - scatter
axes[1].scatter(np.random.rand(20), np.random.rand(20), s=20)
axes[1].set_xlabel('X value')
axes[1].set_ylabel('Y value')
axes[1].set_title('Random Scatter')

# Panel C - bar
axes[2].bar([1, 2, 3, 4], [3, 5, 2, 4], color='steelblue')
axes[2].set_xlabel('Category')
axes[2].set_ylabel('Count')
axes[2].set_title('Bar Chart')

# Apply styling - uses global config automatically!
yp.apply_style_to_all(axes)

# Add labels - also uses global config for font
yp.add_labels(fig, coords, fig_size, start="A")

fig.savefig("example_10_default.png", dpi=150, bbox_inches="tight", facecolor='white')
print("Saved example_10_default.png (publication style)")

# Now switch to poster preset and regenerate
plt.close(fig)
yp.use_preset("poster")

fig, axes = yp.create_figure(fig_size, coords)

# Same plots
axes[0].plot(x, np.sin(x), 'o-', markersize=yp.get_config().markersize,
             lw=yp.get_config().plot_linewidth)
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('Amplitude')
axes[0].set_title('Sine Wave')

axes[1].scatter(np.random.rand(20), np.random.rand(20), s=40)
axes[1].set_xlabel('X value')
axes[1].set_ylabel('Y value')
axes[1].set_title('Random Scatter')

axes[2].bar([1, 2, 3, 4], [3, 5, 2, 4], color='steelblue')
axes[2].set_xlabel('Category')
axes[2].set_ylabel('Count')
axes[2].set_title('Bar Chart')

# Same call - but now uses poster config!
yp.apply_style_to_all(axes)
yp.add_labels(fig, coords, fig_size, start="A")

fig.savefig("example_10_poster.png", dpi=150, bbox_inches="tight", facecolor='white')
print("Saved example_10_poster.png (poster style)")

# Reset for other examples
yp.reset_config()
