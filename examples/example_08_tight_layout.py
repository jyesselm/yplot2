"""
Example 8: Tight layout like publication figures

Replicates layout where:
- Image panels (A, B, G) fill completely edge-to-edge
- Minimal spacing between panels
- Plots touch image panels directly
"""
import numpy as np
import matplotlib.pyplot as plt
import yplot2 as yp

fig_size = (6.5, 8.5)

# Row 1: Two image panels (A and B) - NO extra space
a = yp.Coord(left=0.0, bottom=6.3, width=3.0, height=2.2)
b = yp.Coord(left=3.0, bottom=6.3, width=3.5, height=2.2)

# Row 2: Plots C and D - tight to images above
# Note: plots need left margin for y-axis label
c = yp.Coord(left=0.45, bottom=4.7, width=2.55, height=1.4)
d = yp.Coord(left=3.45, bottom=4.7, width=3.0, height=1.4)

# Row 3: Plots E and F
e = yp.Coord(left=0.45, bottom=3.1, width=2.55, height=1.4)
f = yp.Coord(left=3.45, bottom=3.1, width=3.0, height=1.4)

# Row 4: Wide image G - full width, no margins
g = yp.Coord(left=0.0, bottom=0.0, width=6.5, height=2.8)

coords = [a, b, c, d, e, f, g]
fig, axes = yp.create_figure(fig_size, coords)

# --- Panel A: 3D Structure (edge-to-edge) ---
yp.make_image_panel(axes[0])
axes[0].fill([0, 1, 1, 0], [0, 0, 1, 1], color='#1a1a1a')
axes[0].text(0.5, 0.5, "3D Structure", ha='center', va='center',
             fontsize=12, color='#888', transform=axes[0].transAxes)

# --- Panel B: Schematic (edge-to-edge) ---
yp.make_image_panel(axes[1])
axes[1].fill([0, 1, 1, 0], [0, 0, 1, 1], color='#f8f8f8')
axes[1].text(0.5, 0.5, "Schematic", ha='center', va='center',
             fontsize=12, color='#666', transform=axes[1].transAxes)

# --- Panels C-F: Line plots ---
x = np.linspace(0, 40, 25)

# Panel C (red)
y1 = 0.025 * np.exp(-x/5) + 0.002
y2 = 0.028 - 0.002 * (1 - np.exp(-x/8))
axes[2].plot(x, y1, 'o-', color='#c62828', markersize=3, lw=1, markerfacecolor='#c62828')
axes[2].plot(x, y2, 'o--', color='#c62828', markersize=3, lw=1, markerfacecolor='white', markeredgecolor='#c62828')
axes[2].set_ylabel('Mut. Frac.', fontsize=7)
axes[2].set_ylim(0, 0.035)
axes[2].legend(['Wild-Type', 'TLR-knockout'], fontsize=5, frameon=False, loc='upper right')

# Panel D (green)
y3 = 0.003 + 0.001 * np.random.randn(25)
y4 = 0.018 * (1 - np.exp(-x/6)) + 0.002
axes[3].plot(x, y3, 'o-', color='#2e7d32', markersize=3, lw=1, markerfacecolor='#2e7d32')
axes[3].plot(x, y4, 'o--', color='#2e7d32', markersize=3, lw=1, markerfacecolor='white', markeredgecolor='#2e7d32')
axes[3].set_ylim(0, 0.025)
axes[3].legend(['Wild-Type', 'TL-knockout'], fontsize=5, frameon=False, loc='upper right')

# Panel E (orange)
y5 = 0.022 + 0.004 * np.random.randn(25)
y6 = 0.032 - 0.002 * (1 - np.exp(-x/12))
axes[4].plot(x, y5, 'o-', color='#ef6c00', markersize=3, lw=1, markerfacecolor='#ef6c00')
axes[4].plot(x, y6, 'o--', color='#ef6c00', markersize=3, lw=1, markerfacecolor='white', markeredgecolor='#ef6c00')
axes[4].set_ylabel('Mut. Frac.', fontsize=7)
axes[4].set_ylim(0, 0.04)
axes[4].legend(['Wild-Type', 'TL-knockout'], fontsize=5, frameon=False, loc='upper right')

# Panel F (blue)
y7 = 0.005 + 0.003 * np.random.randn(25)
y8 = 0.12 * np.exp(-x/10) + 0.08
axes[5].plot(x, y7, 'o-', color='#1565c0', markersize=3, lw=1, markerfacecolor='#1565c0')
axes[5].plot(x, y8, 'o--', color='#1565c0', markersize=3, lw=1, markerfacecolor='white', markeredgecolor='#1565c0')
axes[5].set_ylim(0, 0.15)
axes[5].legend(['Wild-Type', 'TL-knockout'], fontsize=5, frameon=False, loc='upper right')

# Shared x-label for E and F
axes[4].set_xlabel('Mg$^{2+}$ concentration (mM)', fontsize=7)
axes[5].set_xlabel('Mg$^{2+}$ concentration (mM)', fontsize=7)

# --- Panel G: Structure comparison (edge-to-edge) ---
yp.make_image_panel(axes[6])
axes[6].fill([0, 1, 1, 0], [0, 0, 1, 1], color='#1a1a1a')
# Draw three "structure" placeholders
for cx in [0.18, 0.5, 0.82]:
    axes[6].add_patch(plt.Circle((cx, 0.5), 0.12, color='#444', transform=axes[6].transAxes))
axes[6].annotate('', xy=(0.35, 0.5), xytext=(0.28, 0.5),
                 arrowprops=dict(arrowstyle='->', color='white', lw=1.5),
                 transform=axes[6].transAxes)
axes[6].text(0.315, 0.65, 'Mg$^{2+}$', ha='center', fontsize=8, color='white', transform=axes[6].transAxes)
axes[6].annotate('', xy=(0.72, 0.5), xytext=(0.62, 0.5),
                 arrowprops=dict(arrowstyle='->', color='white', lw=1.5),
                 transform=axes[6].transAxes)
axes[6].text(0.67, 0.65, 'GAAA', ha='center', fontsize=8, color='white', transform=axes[6].transAxes)

# Apply styling to plot panels
plot_axes = [axes[2], axes[3], axes[4], axes[5]]
for ax in plot_axes:
    ax.tick_params(labelsize=6, width=0.5, length=2)
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)

# Add panel labels - positioned at top-left of each panel
labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
label_coords = [a, b, c, d, e, f, g]
for label, coord in zip(labels, label_coords):
    fig.text(coord.left / fig_size[0] + 0.01,
             (coord.bottom + coord.height) / fig_size[1] - 0.01,
             label, fontsize=14, fontweight='bold', va='top', ha='left')

fig.savefig("example_08_output.png", dpi=150, facecolor='white',
            pad_inches=0, bbox_inches='tight')
print("Saved example_08_output.png")
