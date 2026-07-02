"""
Phase 0 live-figure reproduction — Task 0.6 stub.

TODO(user): wire real data
  - Point at (a) which figure to reproduce and (b) the path to its
    analysis-ready dataframe from the 2025_dms_vs_tmo_paper violin panel.
  - Replace ``df = make_sample_df()`` below with ``df = pd.read_csv(<path>)``
    or equivalent, and update the x/y/hue column names.

Until then, this script runs against the synthetic fixture as a smoke test.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import yplot2
from yplot2.plots.statistical.violin import violin
from yplot2.plots.statistical._sampledata import make_sample_df


def main() -> None:
    """Render a smoke-test violin using the synthetic fixture."""
    df = make_sample_df()
    # TODO(user): replace above with real dataframe, e.g.:
    #   import pandas as pd
    #   df = pd.read_csv("/path/to/analysis_ready.csv")

    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    violin(ax, df, x="nuc", y="reactivity", hue="nuc", seed=0)
    yplot2.set_xlabel(ax, "Nucleotide")
    yplot2.set_ylabel(ax, "Reactivity")
    yplot2.set_title(ax, "Phase 0 smoke test")

    out = "phase0_smoke_test.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)


if __name__ == "__main__":
    main()
