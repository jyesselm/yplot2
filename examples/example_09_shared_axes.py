"""
Example 9: Shared axes for grouped panels

Demonstrates:
- share_x(): Hide x-tick labels except on bottom panel
- share_y(): Hide y-tick labels except on left panel
- add_shared_xlabel/ylabel(): Single label for a group of panels
"""
import numpy as np
import matplotlib.pyplot as plt
import yplot2 as yp

fig_size = (7.0, 6.0)

# Create a 2x2 grid of plots
# Left column (C, E) shares y-axis
# Right column (D, F) shares y-axis
# Bottom row (E, F) shows x-labels
# Top row (C, D) hides x-labels

c = yp.Coord(left=0.7, bottom=3.5, width=2.5, height=2.0)
d = yp.right_of(c, spacing=0.3)
e = yp.below(c, spacing=0.2)
f = yp.below(d, spacing=0.2)

coords = [c, d, e, f]
fig, axes = yp.create_figure(fig_size, coords)

# Generate data
np.random.seed(42)
x = np.linspace(0, 40, 25)

# Panel C (red)
y1 = 0.025 * np.exp(-x/5) + 0.002
y2 = 0.028 - 0.002 * (1 - np.exp(-x/8))
axes[0].plot(x, y1, 'o-', color='#c62828', markersize=4, lw=1.5)
axes[0].plot(x, y2, 'o--', color='#c62828', markersize=4, lw=1.5, markerfacecolor='white')
axes[0].set_ylim(0, 0.035)
axes[0].legend(['Wild-Type', 'Knockout'], fontsize=6, frameon=False)

# Panel D (green)
y3 = 0.003 + 0.002 * np.random.randn(25)
y4 = 0.020 * (1 - np.exp(-x/6)) + 0.002
axes[1].plot(x, y3, 'o-', color='#2e7d32', markersize=4, lw=1.5)
axes[1].plot(x, y4, 'o--', color='#2e7d32', markersize=4, lw=1.5, markerfacecolor='white')
axes[1].set_ylim(0, 0.035)
axes[1].legend(['Wild-Type', 'Knockout'], fontsize=6, frameon=False)

# Panel E (orange)
y5 = 0.018 + 0.005 * np.random.randn(25)
y6 = 0.030 - 0.005 * (1 - np.exp(-x/15))
axes[2].plot(x, y5, 'o-', color='#ef6c00', markersize=4, lw=1.5)
axes[2].plot(x, y6, 'o--', color='#ef6c00', markersize=4, lw=1.5, markerfacecolor='white')
axes[2].set_ylim(0, 0.035)
axes[2].legend(['Wild-Type', 'Knockout'], fontsize=6, frameon=False)

# Panel F (blue)
y7 = 0.008 + 0.003 * np.random.randn(25)
y8 = 0.028 * np.exp(-x/20) + 0.005
axes[3].plot(x, y7, 'o-', color='#1565c0', markersize=4, lw=1.5)
axes[3].plot(x, y8, 'o--', color='#1565c0', markersize=4, lw=1.5, markerfacecolor='white')
axes[3].set_ylim(0, 0.035)
axes[3].legend(['Wild-Type', 'Knockout'], fontsize=6, frameon=False)

# Apply styling
yp.apply_style_to_all(axes)

# Share x-axis for each column (hide top row x-labels)
yp.share_x([axes[0], axes[2]])  # Left column: C, E
yp.share_x([axes[1], axes[3]])  # Right column: D, F

# Share y-axis for each row (hide right column y-labels)
yp.share_y([axes[0], axes[1]])  # Top row: C, D
yp.share_y([axes[2], axes[3]])  # Bottom row: E, F

# Add shared axis labels
yp.add_shared_xlabel(fig, [e, f], fig_size, r'Mg$^{2+}$ concentration (mM)', fontsize=10)
yp.add_shared_ylabel(fig, [c, e], fig_size, 'Mut. Frac.', fontsize=10, offset=0.5)

# Add panel labels
yp.add_labels(fig, coords, fig_size, start="C")

fig.savefig("example_09_output.png", dpi=150, bbox_inches="tight", facecolor='white')
print("Saved example_09_output.png")
