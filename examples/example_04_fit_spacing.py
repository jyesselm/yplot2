"""
Example 4: Using fit_row_spacing to calculate ideal spacing
"""
import numpy as np
import yplot2 as yp

fig_size = (7.5, 5.5)

# Calculate spacing to evenly fit 4 plots of width 1.5" in a 7.5" figure
# with 0.5" margins on each side
spacing = yp.fit_row_spacing(
    fig_width=7.5,
    n=4,
    subplot_width=1.5,
    margins=(0.5, 0.5),
)
print(f"Calculated spacing for row 1: {spacing:.3f}\"")

# Row 1: 4 plots with calculated spacing
row1 = yp.row(
    n=4,
    size=(1.5, 1.5),
    spacing=spacing,
    left=0.5,
    bottom=3.5,
)

# Row 2: Different - fit 3 wider plots with same margins
spacing2 = yp.fit_row_spacing(
    fig_width=7.5,
    n=3,
    subplot_width=2.0,
    margins=(0.5, 0.5),
)
print(f"Calculated spacing for row 2: {spacing2:.3f}\"")

row2 = yp.row(
    n=3,
    size=(2.0, 1.5),
    spacing=spacing2,
    left=0.5,
    bottom=1.5,
)

coords = row1 + row2
fig, axes = yp.create_figure(fig_size, coords)

# Add data
np.random.seed(123)
for i, ax in enumerate(axes[:4]):
    ax.scatter(np.random.rand(20), np.random.rand(20), s=30)
    ax.set_title(f"Plot {i+1}", fontsize=8)

for i, ax in enumerate(axes[4:]):
    ax.hist(np.random.randn(100), bins=15, edgecolor="white")
    ax.set_title(f"Hist {i+1}", fontsize=8)

yp.apply_style_to_all(axes)
yp.add_labels(fig, coords, fig_size, start="A")

# Check if everything fits
result = yp.check_fit(fig_size, coords)
print(f"All coords fit: {result['fits']}")
if not result['fits']:
    for issue in result['issues']:
        print(f"  - {issue}")

fig.savefig("example_04_output.png", dpi=150, bbox_inches="tight")
print("Saved example_04_output.png")
