"""
Example 6: Mixed layout with images and plots

This demonstrates a common scientific figure layout where some panels
are images (e.g., molecular structures, microscopy) and others are
data plots.

Layout similar to:
- A, B: Images (top row)
- C, D: Line plots (middle row)
- E, F: Line plots (lower middle row)
- G: Wide image (bottom, spans width)
"""
import numpy as np
import matplotlib.pyplot as plt
import yplot2 as yp

fig_size = (7.0, 9.0)

# Row 1: Two images (A and B) - taller panels for structure images
a = yp.Coord(left=0.5, bottom=6.8, width=2.8, height=2.0)
b = yp.right_of(a, spacing=0.4, width=3.0)

# Row 2: Two plots (C and D)
c = yp.below(a, spacing=0.3, height=1.4)
d = yp.below(b, spacing=0.3, height=1.4)

# Row 3: Two plots (E and F)
e = yp.below(c, spacing=0.3)
f = yp.below(d, spacing=0.3)

# Row 4: Wide image spanning bottom (G)
g = yp.below(e, spacing=0.4, width=6.0, height=1.8)

coords = [a, b, c, d, e, f, g]
fig, axes = yp.create_figure(fig_size, coords)

# --- Panel A: Image placeholder (would be molecular structure) ---
yp.make_image_panel(axes[0])
axes[0].fill([0, 1, 1, 0], [0, 0, 1, 1], color='#2a2a2a')
axes[0].text(0.5, 0.5, "3D Structure\n(image)", ha='center', va='center',
             fontsize=10, color='white', transform=axes[0].transAxes)

# --- Panel B: Image placeholder (would be schematic/diagram) ---
yp.make_image_panel(axes[1])
axes[1].fill([0, 1, 1, 0], [0, 0, 1, 1], color='#f0f0f0')
axes[1].text(0.5, 0.5, "Schematic\n(image)", ha='center', va='center',
             fontsize=10, color='#333', transform=axes[1].transAxes)

# --- Panel C: Line plot with two conditions ---
x = np.linspace(0, 40, 30)
y1 = 0.025 * np.exp(-x/5) + 0.002
y2 = 0.028 - 0.003 * (1 - np.exp(-x/10))
axes[2].plot(x, y1, 'o-', color='#d32f2f', markersize=4, label='Wild-Type', markerfacecolor='#d32f2f')
axes[2].plot(x, y2, 'o--', color='#d32f2f', markersize=4, label='Knockout', markerfacecolor='white', markeredgecolor='#d32f2f')
axes[2].set_ylabel('Mut. Frac.')
axes[2].set_ylim(0, 0.035)
axes[2].legend(fontsize=6, frameon=False, loc='upper right')

# --- Panel D: Line plot ---
y3 = 0.002 + 0.001 * np.random.randn(30)
y4 = 0.018 * (1 - np.exp(-x/8)) + 0.002
axes[3].plot(x, y3, 'o-', color='#388e3c', markersize=4, markerfacecolor='#388e3c')
axes[3].plot(x, y4, 'o--', color='#388e3c', markersize=4, markerfacecolor='white', markeredgecolor='#388e3c')
axes[3].set_ylabel('Mut. Frac.')
axes[3].set_ylim(0, 0.025)

# --- Panel E: Line plot ---
y5 = 0.022 + 0.003 * np.sin(x/5) + 0.002 * np.random.randn(30)
y6 = 0.030 - 0.003 * (1 - np.exp(-x/15))
axes[4].plot(x, y5, 'o-', color='#f57c00', markersize=4, markerfacecolor='#f57c00')
axes[4].plot(x, y6, 'o--', color='#f57c00', markersize=4, markerfacecolor='white', markeredgecolor='#f57c00')
axes[4].set_ylabel('Mut. Frac.')
axes[4].set_xlabel('Mg$^{2+}$ concentration (mM)')

# --- Panel F: Line plot ---
y7 = 0.005 + 0.002 * np.random.randn(30)
y8 = 0.12 * np.exp(-x/15) + 0.08
axes[5].plot(x, y7, 'o-', color='#1976d2', markersize=4, markerfacecolor='#1976d2')
axes[5].plot(x, y8, 'o--', color='#1976d2', markersize=4, markerfacecolor='white', markeredgecolor='#1976d2')
axes[5].set_ylabel('Mut. Frac.')
axes[5].set_xlabel('Mg$^{2+}$ concentration (mM)')

# --- Panel G: Wide image (would be multiple structures with arrows) ---
yp.make_image_panel(axes[6])
axes[6].fill([0, 1, 1, 0], [0, 0, 1, 1], color='#2a2a2a')
axes[6].text(0.5, 0.5, "Structure comparison panels (image)\n← Mg²⁺ →    ← GAAA →",
             ha='center', va='center', fontsize=10, color='white',
             transform=axes[6].transAxes)

# Apply styling to plot panels only (not image panels)
plot_axes = [axes[2], axes[3], axes[4], axes[5]]
yp.apply_style_to_all(plot_axes)

# Add panel labels
yp.add_labels(fig, coords, fig_size, start="A")

fig.savefig("example_06_output.png", dpi=150, bbox_inches="tight", facecolor='white')
print("Saved example_06_output.png")
