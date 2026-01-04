"""
Example 2: Using relative positioning (right_of, below)
"""
import numpy as np
import yplot2 as yp

fig_size = (7.5, 5.0)

# Start with panel A
a = yp.Coord(left=0.6, bottom=2.8, width=2.0, height=1.8)

# B is to the right of A (same size by default)
b = yp.right_of(a, spacing=0.4)

# C is to the right of B
c = yp.right_of(b, spacing=0.4)

# D is below A
d = yp.below(a, spacing=0.4)

# E is below B (same size as B)
e = yp.below(b, spacing=0.4)

# F is below C
f = yp.below(c, spacing=0.4)

coords = [a, b, c, d, e, f]
fig, axes = yp.create_figure(fig_size, coords)

# Add some sample data to each
np.random.seed(42)
for i, ax in enumerate(axes):
    ax.bar([1, 2, 3], np.random.rand(3) * 10)
    ax.set_xlabel("Category")
    ax.set_ylabel("Value")

yp.apply_style_to_all(axes)
yp.add_labels(fig, coords, fig_size, start="A")

# Show debug boxes
yp.draw_debug_boxes(fig, coords, fig_size)

fig.savefig("example_02_output.png", dpi=150, bbox_inches="tight")
print("Saved example_02_output.png")
