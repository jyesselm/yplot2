"""
Example 7: Loading real images into panels (edge-to-edge)

Shows the workflow for loading actual image files (PNG, JPG, etc.)
into figure panels. Images fill the entire panel with NO white space.
"""
import numpy as np
import yplot2 as yp

fig_size = (7.0, 5.0)

# Create a 2x2 layout where top row is images, bottom row is plots
a = yp.Coord(left=0.5, bottom=2.8, width=2.8, height=2.0)
b = yp.right_of(a, spacing=0.4, width=3.0)
c = yp.below(a, spacing=0.3, height=1.8)
d = yp.below(b, spacing=0.3, height=1.8)

coords = [a, b, c, d]
fig, axes = yp.create_figure(fig_size, coords)

# --- Panels A and B: Image panels (edge-to-edge, no margins) ---
# In real use:
#   yp.load_image(axes[0], "structure_front.png")
#   yp.load_image(axes[1], "structure_side.png")

# For demo, use make_image_panel and fill with color
for i, (ax, color) in enumerate([(axes[0], '#2a2a2a'), (axes[1], '#3a3a3a')]):
    yp.make_image_panel(ax)
    # Fill entire panel with rectangle (edge-to-edge)
    ax.fill([0, 1, 1, 0], [0, 0, 1, 1], color=color)
    ax.text(0.5, 0.5, f"Image panel\n(edge-to-edge)\n\nyp.load_image(axes[{i}],\n'structure.png')",
            ha='center', va='center', fontsize=8, color='white',
            family='monospace', transform=ax.transAxes)

# --- Panels C and D: Regular plots (with normal axes margins) ---
x = np.linspace(0, 10, 50)

axes[2].plot(x, np.sin(x), 'b-', lw=2)
axes[2].fill_between(x, np.sin(x) - 0.2, np.sin(x) + 0.2, alpha=0.3)
axes[2].set_xlabel('Time (s)')
axes[2].set_ylabel('Signal')

axes[3].bar([1, 2, 3, 4], [3.2, 4.1, 2.8, 3.9], color=['#e74c3c', '#3498db', '#2ecc71', '#f39c12'])
axes[3].set_xlabel('Condition')
axes[3].set_ylabel('Response')

# Style only the plot panels
yp.apply_style_to_all([axes[2], axes[3]])

# Add labels
yp.add_labels(fig, coords, fig_size, start="A")

fig.savefig("example_07_output.png", dpi=150, bbox_inches="tight", facecolor='white')
print("Saved example_07_output.png")
