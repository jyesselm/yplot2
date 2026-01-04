"""
Example 3: Panels with different sizes (like a publication figure)
"""
import numpy as np
import yplot2 as yp

fig_size = (7.5, 6.5)

# Row 1: Two panels of different widths
a = yp.Coord(left=0.6, bottom=4.5, width=2.5, height=1.6)
b = yp.right_of(a, spacing=0.5, width=3.5)  # wider panel

# Row 2: Below row 1
c = yp.below(a, spacing=0.5)
d = yp.below(b, spacing=0.5)

# Row 3: Full-width panel
e = yp.below(c, spacing=0.5, width=6.5, height=1.4)

coords = [a, b, c, d, e]
fig, axes = yp.create_figure(fig_size, coords)

# Panel A: Horizontal bar chart
categories = ["Type A", "Type B", "Type C", "Type D"]
values = [0.3, 0.5, 0.2, 0.4]
axes[0].barh(categories, values, color="steelblue")
axes[0].set_xlabel("Proportion")

# Panel B: Scatter with error bars
x = np.array([1, 2, 3, 4])
y = np.array([2.3, 3.1, 2.8, 3.5])
yerr = np.array([0.3, 0.2, 0.4, 0.25])
axes[1].errorbar(x, y, yerr=yerr, fmt="o", capsize=3)
axes[1].set_xlabel("Condition")
axes[1].set_ylabel("Response")

# Panel C: Box plot
data = [np.random.normal(0, 1, 50) for _ in range(4)]
axes[2].boxplot(data)
axes[2].set_xlabel("Group")
axes[2].set_ylabel("Value")

# Panel D: Grouped bar chart
x = np.arange(3)
width = 0.35
axes[3].bar(x - width/2, [3, 5, 4], width, label="Control")
axes[3].bar(x + width/2, [4, 6, 5], width, label="Treatment")
axes[3].set_xticks(x)
axes[3].set_xticklabels(["A", "B", "C"])
axes[3].legend(fontsize=6)

# Panel E: Line plot (full width)
x = np.linspace(0, 20, 100)
axes[4].plot(x, np.sin(x) * np.exp(-x/10), label="Signal")
axes[4].fill_between(x, np.sin(x) * np.exp(-x/10) - 0.2,
                     np.sin(x) * np.exp(-x/10) + 0.2, alpha=0.3)
axes[4].set_xlabel("Position")
axes[4].set_ylabel("Score")

yp.apply_style_to_all(axes)
yp.add_labels(fig, coords, fig_size, start="a")

fig.savefig("example_03_output.png", dpi=150, bbox_inches="tight")
print("Saved example_03_output.png")
