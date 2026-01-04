"""
Example 1: Simple row of 3 plots
"""
import numpy as np
import yplot2 as yp

# Figure size
fig_size = (7.5, 3.0)

# Create a row of 3 equally-spaced plots
coords = yp.row(
    n=3,
    size=(2.0, 2.0),
    spacing=0.4,
    left=0.6,
    bottom=0.6,
)

# Create figure
fig, axes = yp.create_figure(fig_size, coords)

# Plot some data
x = np.linspace(0, 10, 50)
axes[0].plot(x, np.sin(x))
axes[0].set_title("sin(x)")

axes[1].plot(x, np.cos(x))
axes[1].set_title("cos(x)")

axes[2].plot(x, np.tan(x))
axes[2].set_ylim(-5, 5)
axes[2].set_title("tan(x)")

# Apply styling
yp.apply_style_to_all(axes)

# Add labels
yp.add_labels(fig, coords, fig_size, start="A")

fig.savefig("example_01_output.png", dpi=150, bbox_inches="tight")
print("Saved example_01_output.png")
