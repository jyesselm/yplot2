"""
Example 5: Complex multi-panel figure like a publication
(Similar to the figure the user showed)
"""
import numpy as np
import yplot2 as yp

fig_size = (7.5, 9.0)

# Row 1: a (narrow) and b (wide with two subplots inside)
a = yp.Coord(left=0.6, bottom=7.0, width=2.5, height=1.5)
b = yp.right_of(a, spacing=0.5, width=3.5)

# Row 2: c and d (similar to row 1)
c = yp.below(a, spacing=0.4)
d = yp.below(b, spacing=0.4)

# Row 3: e - full width line plot
e = yp.below(c, spacing=0.4, width=6.5, height=1.3)

# Row 4: f - two bar chart panels (labeled as one "f")
f1 = yp.below(e, spacing=0.4, width=3.0, height=1.4)
f2 = yp.right_of(f1, spacing=0.5)

# Row 5: g - sequence logos (would be an image in real use)
g = yp.below(f1, spacing=0.4, width=6.5, height=0.9)

coords = [a, b, c, d, e, f1, f2, g]
fig, axes = yp.create_figure(fig_size, coords)

# Panel a: Horizontal bar chart
categories = ["Bulges", "Canonical", "Long loop", "Two-quartet",
              "G-quadruplex", "G4+40%", "G-triplex"]
values = np.random.rand(7) * 0.4
axes[0].barh(categories, values, color=["#E91E63", "#9C27B0", "#2196F3",
                                         "#4CAF50", "#FF9800", "#795548", "#607D8B"])
axes[0].set_xlabel("Proportion")
axes[0].set_xlim(0, 0.5)

# Panel b: Two grouped scatter/error bar plots
x = [1, 2, 3, 4, 5]
for offset, color in [(0, "steelblue"), (0.3, "coral")]:
    y = np.random.rand(5) * 0.5 - 0.3
    axes[1].errorbar([xi + offset for xi in x], y, yerr=0.1, fmt="o",
                     color=color, capsize=2, markersize=4)
axes[1].axhline(0, color="gray", linestyle="--", linewidth=0.5)
axes[1].set_ylabel("Delta Value")

# Panel c: Box/violin style plot
data = [np.random.randn(30) + i*0.5 for i in range(5)]
bp = axes[2].boxplot(data, patch_artist=True)
for patch, color in zip(bp['boxes'], ['#E91E63', '#9C27B0', '#2196F3', '#4CAF50', '#FF9800']):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

# Panel d: Grouped bars
x = np.arange(2)
width = 0.3
colors = ['#E91E63', '#FFC107']
axes[3].bar(x - width/2, [0.21, 1.96], width, color=colors[0], label="short")
axes[3].bar(x + width/2, [3.22, 2.1], width, color=colors[1], label="long")
axes[3].set_xticks(x)
axes[3].set_xticklabels(["5'UTR", "3'UTR"])
axes[3].legend(fontsize=6)

# Panel e: Line plot with colored regions
x = np.linspace(-25, 25, 100)
for i, color in enumerate(['#4CAF50', '#FF9800', '#2196F3', '#E91E63']):
    y = np.random.rand(100) * 0.3 + 0.1 * i
    axes[4].fill_between(x, 0, y, alpha=0.5, color=color)
axes[4].set_xlabel("Relative position (nt)")
axes[4].set_ylabel("Score")

# Panel f1 and f2: Bar charts
genes = ["Gene1", "Gene2", "Gene3", "Gene4", "Gene5"]
for ax in [axes[5], axes[6]]:
    values = np.random.rand(5) * 10
    ax.barh(genes, values, color="steelblue")
    ax.set_xlabel("Fold Enrichment")

# Panel g: Would be an image - here we just show placeholder
axes[7].text(0.5, 0.5, "[ Sequence Logo Image ]",
             ha="center", va="center", fontsize=10,
             transform=axes[7].transAxes)
axes[7].set_xlim(0, 1)
axes[7].set_ylim(0, 1)
for spine in axes[7].spines.values():
    spine.set_visible(False)
axes[7].set_xticks([])
axes[7].set_yticks([])

# Style all except image panel
yp.apply_style_to_all(axes[:7])

# Add labels - note f1 and f2 share label "f", and g follows
label_coords = [a, b, c, d, e, f1, g]
yp.add_labels(fig, label_coords, fig_size, start="a")

fig.savefig("example_05_output.png", dpi=150, bbox_inches="tight")
print("Saved example_05_output.png")
