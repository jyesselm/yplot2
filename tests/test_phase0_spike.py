"""
Task 0.5 — Phase 0 spike acceptance tests.

All four primary assertions are the GO/NO-GO gate for Phase 0:
  (i)   Linewidth: violin() flattens seaborn glyph artists to cfg.axis_linewidth
  (ii)  Exact palette hex: violin bodies carry undiluted house palette colors
  (iii) Font: tick labels use Arimo after finish()
  (iv)  Determinism: seed=0 twice -> byte-identical PNG; seed=1 -> different PNG
"""

import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

import yplot2
from yplot2.config import get_config
from yplot2.plots.colors import palette_hex


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_violin_ax(seed: int = 0, strip: bool = True):
    """Create a figure + axes and draw a nucleotide violin with the given seed."""
    from yplot2.plots.statistical.violin import violin
    from yplot2.plots.statistical._sampledata import make_sample_df

    df = make_sample_df()
    fig, ax = plt.subplots(figsize=(4, 3))
    violin(ax, df, x="nuc", y="reactivity", hue="nuc", seed=seed, strip=strip)
    return fig, ax


def _render_to_bytes(fig) -> bytes:
    """Render figure to PNG bytes buffer."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    return buf.read()


def _violin_body_collections(ax):
    """Return only violin body collections (FillBetweenPolyCollection), not PathCollections."""
    from matplotlib.collections import PathCollection

    return [c for c in ax.collections if not isinstance(c, PathCollection)]


# ---------------------------------------------------------------------------
# Assertion (i): linewidth -- glyph normalization via violin() path
# ---------------------------------------------------------------------------


class TestFinishLinewidth:
    """Seaborn glyph artists are flattened to axis_linewidth by violin()."""

    def test_body_collection_linewidths(self):
        """Violin body (FillBetweenPolyCollection) linewidths == axis_linewidth."""
        cfg = get_config()
        fig, ax = _make_violin_ax()
        try:
            for coll in _violin_body_collections(ax):
                lws = coll.get_linewidth()
                # get_linewidth() returns an array -- compare elementwise
                for lw in lws:
                    assert abs(lw - cfg.axis_linewidth) < 1e-6, (
                        f"Body collection lw={lw}, expected {cfg.axis_linewidth}"
                    )
        finally:
            plt.close(fig)

    def test_line_artists_linewidths(self):
        """Inner Line2D (box/whisker/median) linewidths == axis_linewidth."""
        cfg = get_config()
        fig, ax = _make_violin_ax()
        try:
            for line in ax.lines:
                lw = line.get_linewidth()
                assert abs(lw - cfg.axis_linewidth) < 1e-6, (
                    f"Line2D lw={lw}, expected {cfg.axis_linewidth}"
                )
        finally:
            plt.close(fig)

    def test_strip_collections_excluded_from_linewidth(self):
        """Strip PathCollections have edgecolor='none' (not a gray ring)."""
        from matplotlib.collections import PathCollection

        fig, ax = _make_violin_ax(strip=True)
        try:
            strip_colls = [c for c in ax.collections if isinstance(c, PathCollection)]
            assert strip_colls, "Expected strip PathCollections when strip=True"
            for coll in strip_colls:
                ec = coll.get_edgecolor()
                for rgba in ec:
                    assert rgba[3] == 0.0, (
                        f"Strip collection edgecolor alpha={rgba[3]}, expected 0 (none)"
                    )
        finally:
            plt.close(fig)

    def test_finish_idempotent(self):
        """Calling finish() twice yields identical artist properties on violin axes."""
        from yplot2.style import finish

        cfg = get_config()
        fig, ax = _make_violin_ax()
        try:
            finish(ax)  # second call -- first was inside violin()
            for coll in _violin_body_collections(ax):
                for lw in coll.get_linewidth():
                    assert abs(lw - cfg.axis_linewidth) < 1e-6
            for line in ax.lines:
                assert abs(line.get_linewidth() - cfg.axis_linewidth) < 1e-6
        finally:
            plt.close(fig)


class TestFinishDoesNotCorruptPlainAxes:
    """finish() on a plain line/scatter axes must not alter data artist properties."""

    def test_finish_preserves_line_linewidth(self):
        """finish() does not change a user's explicitly-set Line2D linewidth."""
        from yplot2.style import finish

        fig, ax = plt.subplots()
        (line,) = ax.plot([0, 1], [0, 1], linewidth=3.0, color="blue")
        finish(ax)
        try:
            assert abs(line.get_linewidth() - 3.0) < 1e-6, (
                f"finish() changed line lw from 3.0 to {line.get_linewidth()}"
            )
        finally:
            plt.close(fig)

    def test_finish_preserves_scatter_edgecolor(self):
        """finish() does not wipe a user's explicitly-set scatter edgecolor."""
        from yplot2.style import finish

        fig, ax = plt.subplots()
        sc = ax.scatter([0, 1], [0, 1], edgecolors="red", linewidths=1.5)
        finish(ax)
        try:
            ec = sc.get_edgecolor()
            expected_hex = mcolors.to_hex("red")
            for rgba in ec:
                actual_hex = mcolors.to_hex(rgba)
                assert actual_hex == expected_hex, (
                    f"finish() changed scatter edgecolor from red to {actual_hex}"
                )
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# Assertion (ii): exact palette hex
# ---------------------------------------------------------------------------


class TestExactPaletteHex:
    """Violin body facecolors match the house nucleotide palette exactly."""

    def test_body_facecolors_match_palette(self):
        """Each violin body carries the undiluted house palette hex."""
        nuc_order = ["A", "C", "G", "U"]
        fig, ax = _make_violin_ax()
        try:
            bodies = _violin_body_collections(ax)
            body_hexes = set()
            for body in bodies:
                rgba = body.get_facecolor()[0]
                body_hexes.add(mcolors.to_hex(rgba))

            for nuc in nuc_order:
                expected_hex = palette_hex("nucleotide", nuc)
                assert expected_hex in body_hexes, (
                    f"Palette hex {expected_hex} for '{nuc}' not found in violin bodies. "
                    f"Body hexes: {body_hexes}"
                )
        finally:
            plt.close(fig)


# ---------------------------------------------------------------------------
# Assertion (iii): font
# ---------------------------------------------------------------------------


class TestFont:
    """Tick labels report family Arimo after finish()."""

    def test_tick_labels_arimo(self):
        """X-axis tick labels use the Arimo font family."""
        fig, ax = _make_violin_ax()
        try:
            labels = ax.get_xticklabels()
            assert labels, "No x-tick labels found"
            for label in labels:
                fontname = label.get_fontname()
                assert "Arimo" in fontname or fontname == "Arimo", (
                    f"Tick label font is '{fontname}', expected 'Arimo'"
                )
        finally:
            plt.close(fig)

    def test_bold_arimo_distinct_from_regular(self):
        """Arimo Bold resolves to a distinct file from Arimo Regular."""
        from matplotlib.font_manager import FontProperties

        bold_path = fm.findfont(FontProperties(family="Arimo", weight="bold"))
        reg_path = fm.findfont(FontProperties(family="Arimo", weight="normal"))
        assert bold_path != reg_path, (
            "Arimo bold resolves to same file as regular -- genuine bold TTF missing"
        )


# ---------------------------------------------------------------------------
# Assertion (iv): determinism with strip jitter
# ---------------------------------------------------------------------------


class TestDeterminism:
    """Seeded RNG produces byte-identical renders; different seeds differ."""

    def test_same_seed_byte_identical(self):
        """Two renders with seed=0 produce identical PNG bytes."""
        fig1, ax1 = _make_violin_ax(seed=0, strip=True)
        png1 = _render_to_bytes(fig1)
        plt.close(fig1)

        fig2, ax2 = _make_violin_ax(seed=0, strip=True)
        png2 = _render_to_bytes(fig2)
        plt.close(fig2)

        assert png1 == png2, (
            f"seed=0 renders differ: {len(png1)} vs {len(png2)} bytes. "
            "Strip jitter is not deterministic."
        )

    def test_different_seed_differs(self):
        """A render with seed=1 differs from seed=0 (proves seed is live)."""
        fig0, ax0 = _make_violin_ax(seed=0, strip=True)
        png0 = _render_to_bytes(fig0)
        plt.close(fig0)

        fig1, ax1 = _make_violin_ax(seed=1, strip=True)
        png1 = _render_to_bytes(fig1)
        plt.close(fig1)

        assert png0 != png1, (
            "seed=0 and seed=1 produced identical renders. "
            "Strip jitter seed is dead code."
        )


# ---------------------------------------------------------------------------
# Additional: use_style(), style() context manager, and palette integration
# ---------------------------------------------------------------------------


class TestUseStyle:
    """use_style() correctly pushes rcParams."""

    def test_rcparams_updated(self):
        """After use_style(), font.family and axes.linewidth are set from config."""
        import matplotlib as mpl

        cfg = get_config()
        yplot2.use_style()
        assert mpl.rcParams["axes.linewidth"] == cfg.axis_linewidth
        family_setting = mpl.rcParams["font.family"]
        if isinstance(family_setting, list):
            assert "Arimo" in family_setting
        else:
            assert "Arimo" in family_setting

    def test_style_context_manager_restores(self):
        """style() context manager restores prior rcParams on exit."""
        import matplotlib as mpl
        from yplot2.style import style

        mpl.rcParams["axes.linewidth"] = 99.0
        with style():
            pass  # restores on exit
        assert mpl.rcParams["axes.linewidth"] == 99.0
        # Restore
        mpl.rcParams["axes.linewidth"] = get_config().axis_linewidth

    def test_palette_hex(self):
        """palette_hex('nucleotide', 'A') returns the house hex for A."""
        from yplot2.plots.colors import palette_hex as phex

        result = phex("nucleotide", "A")
        expected = mcolors.to_hex("red")
        assert result == expected, f"Expected {expected}, got {result}"
