# Implementation Plan — yplot2 Phase 0 (go/no-go spike) + gated catalog seed

> Branch: `phase0-font-seaborn-spike`
> Source strategy: `~/.claude/plans/yplot2-lab-engine-strategy.md` (Phase 0).
> **This plan builds Phase 0 ONLY.** Phase 0 is a GO/NO-GO gate; do NOT build the
> catalog system, the seaborn wrapper suite, or the layout presets until the gate
> passes. The catalog-seed shape is described at the end for context, marked GATED.
> All dimensions in inches. House font decision: **Arimo** (OFL-1.1, metric-
> compatible with Arial), bundled in-package as genuine static Regular/Bold/Italic/
> BoldItalic faces (instanced from the variable font via fontTools; the old static
> `apache/arimo/*.ttf` paths no longer exist — Arimo moved to `ofl/arimo` VFs).

## Goal of Phase 0
Prove the two load-bearing assumptions of the whole strategy in ~2–3 days, cheaply,
before any build-out:
1. **Font determinism** — a bundled Arimo makes headless (Agg) text render identically
   on any machine (not dependent on a system Arial).
2. **Seaborn uniformity** — a seaborn violin can be made to match house style *exactly*
   (glyph linewidths + exact palette hex + deterministic render) via `saturation=1` +
   explicit palette + `hue_order` + a post-draw `finish(ax)` + seeded RNG.

If both hold AND rebuilding one real figure in yplot2 is cleaner than forking a
`plotting.py`, we proceed to Phase 1. If not, we take the documented fallback
(drop global-style ambition; ship per-axes `apply_style` wrappers).

---

## Toolchain / setup (run first, and after each task)
- `pip install -e ".[dev,stats]"` (adds seaborn — see Task 0.0).
- Tests: `pytest -q`
- Determinism runs must force the Agg backend: tests set
  `matplotlib.use("Agg")` before importing pyplot.
- No linter is configured; match existing style (type hints, docstrings, `Optional`).

---

## Task 0.0 — Deps + housekeeping
**Files:** `pyproject.toml`, delete `build/`
1. In `pyproject.toml`, add an optional extra:
   ```toml
   [project.optional-dependencies]
   stats = ["seaborn>=0.13,<0.14"]   # pinned; finish() introspects seaborn artists
   ```
   Keep `dev` as-is. (seaborn stays OPTIONAL — core must import without it.)
2. `rm -rf build/` — stale shadow copy of the whole package (already gitignored,
   git-untracked). It will otherwise poison future package-walking. Confirm
   `git status` shows nothing (it's ignored).
**Acceptance:** `python -c "import yplot2"` works with seaborn absent; `pip install -e
".[stats]"` pulls seaborn 0.13.x; `build/` gone.

## Task 0.1 — Bundle + register Arimo font
**Files:** `yplot2/fonts/` (new, with TTFs + LICENSE), `yplot2/_fonts.py` (new),
`yplot2/__init__.py` (register on import)
1. Vendicate Arimo TTFs into `yplot2/fonts/`: `Arimo-Regular.ttf`, `Arimo-Bold.ttf`,
   `Arimo-Italic.ttf`, `Arimo-BoldItalic.ttf`. Source: Google Fonts
   (`github.com/google/fonts/tree/main/ofl/arimo`), OFL-1.1 — instance static
   Regular(400)/Bold(700)/Italic/BoldItalic from the VFs via `fontTools.varLib.instancer`.
   **Also copy the OFL `LICENSE.txt` into `yplot2/fonts/` (redistribution requires it).**
2. Package data: ensure the TTFs ship — add to `pyproject.toml`:
   ```toml
   [tool.setuptools.package-data]
   yplot2 = ["fonts/*.ttf", "fonts/LICENSE.txt"]
   ```
3. `yplot2/_fonts.py`:
   ```python
   from pathlib import Path
   import matplotlib.font_manager as fm

   _FONT_DIR = Path(__file__).parent / "fonts"

   def register_bundled_fonts() -> None:
       """Register bundled Arimo with matplotlib. Idempotent."""
       for ttf in _FONT_DIR.glob("*.ttf"):
           try:
               fm.fontManager.addfont(str(ttf))
           except Exception:
               pass  # never break import on a font hiccup
   ```
4. Call `register_bundled_fonts()` once at the TOP of `yplot2/__init__.py` (before
   other imports that touch style). Must be side-effect-cheap and not render anything.
5. Make Arimo the house default: in `config.py`, change `Config.font_family` default
   from `"Arial"` to `"Arimo"`. In `style.py::_resolve_font_family`, **rewrite the
   `str` branch** (currently `style.py:38-40` returns the name unchanged with NO
   availability check): if the requested family is available, return it; else if the
   request is `"Arial"` (or Arial-family) and Arimo is available, return `"Arimo"`;
   else fall back to the current behavior. So legacy `"Arial"` requests resolve
   deterministically to the bundled metric-compatible face on any machine.
6. **Close the setter bypass** (plan-critic #5): `set_xlabel`/`set_ylabel`/`set_title`
   (`style.py:607,630,653`) and `text()` (`basic.py:482`) pass `fontname`/`fontfamily`
   straight to matplotlib, bypassing resolution — so explicit `fontname="Arial"` in
   `examples/example_10/11` would NOT resolve to Arimo on a non-Arial machine. Route
   these four call sites' font name through `_resolve_font_family(...)` before passing
   to matplotlib.
7. **Ship the TTFs in sdists too:** add a `MANIFEST.in` with
   `recursive-include yplot2/fonts *.ttf *.txt`, and add a
   `[tool.setuptools.packages.find]` block if package discovery needs it. (The Task 0.1
   acceptance below uses an editable install, which reads from the source tree and does
   NOT prove shipping — so also add the built-wheel check.)
**Acceptance (write `tests/test_fonts.py`):**
- `fm.findfont("Arimo", fallback_to_default=False)` resolves to a path **inside**
  `yplot2/fonts/`.
- After `register_bundled_fonts()`, `"Arimo"` is in
  `{f.name for f in fm.fontManager.ttflist}`.
- `_resolve_font_family("Arial")` returns `"Arimo"` when Arial is hidden (monkeypatch
  the available-fonts set) and returns `"Arial"` when it is present.
- Importing `yplot2` does not raise and does not create any figure.
- **Shipping check:** `python -m build --wheel` then assert the wheel zip contains
  `yplot2/fonts/Arimo-Regular.ttf` and `fonts/LICENSE.txt` (or skip if `build` absent,
  with an xfail note).

## Task 0.2 — `use_style()` rcParams bridge (coarse default, spike scope)
**Files:** `yplot2/style.py`, export in `__init__.py`
1. Add `use_style()` and a `style()` context manager that push a SUBSET of `Config`
   into `matplotlib.rcParams`: `font.family=Arimo`, `axes.linewidth`,
   `xtick.labelsize`/`ytick.labelsize` (use the x/y tick fontsizes — pick x for the
   single rcParam, document the limitation), `savefig.dpi`, `axes.prop_cycle` from the
   house palette (Task 0.3). This is the COARSE default for raw escape-hatch plots —
   it is explicitly NOT the uniformity guarantee (that's `finish`/`apply_style`).
   ```python
   def use_style() -> None:
       cfg = get_config()
       import matplotlib as mpl
       from .plots.colors import house_palette_colors  # LAZY import (plan-critic R2 #3):
       # a top-level import would trigger plots/__init__ -> pop_avg.py:18 importing from a
       # partially-initialized style module -> ImportError at `import yplot2`.
       mpl.rcParams.update({
           "font.family": _resolve_font_family(cfg.font_family),
           "axes.linewidth": cfg.axis_linewidth,
           "xtick.labelsize": cfg.x_axis_tick_fontsize,
           "ytick.labelsize": cfg.y_axis_tick_fontsize,
           "savefig.dpi": 300,
           "axes.prop_cycle": mpl.cycler(color=house_palette_colors()),
       })
   ```
**Acceptance:** after `yp.use_style()`, `mpl.rcParams["font.family"]` contains Arimo
and `axes.linewidth == cfg.axis_linewidth`.

## Task 0.3 — Palette registry (minimal, spike scope)
**Files:** `yplot2/plots/colors.py` (extend), export helpers
1. Add a named-palette dict seeded from the existing `NUCLEOTIDE_COLORS` plus a
   `"conditions"` palette (2–3 recurring paper hexes, e.g. `#2e89c7`, `#ff8b26`).
2. Add `palette(name) -> list[str]/dict`, `palette_hex(name, key) -> str`, and
   `house_palette_colors() -> list[str]` (the default prop_cycle).
3. Register nucleotide colors with seaborn as a named palette IF seaborn present
   (guarded import). Provide a `hue_order` helper so categorical hue→color is explicit.
**Acceptance:** `yp.palette_hex("nucleotide", "A")` returns the exact house hex for A.

## Task 0.4 — `finish(ax)` + prototype `violin` wrapper (the spike core)
**Files:** `yplot2/style.py` (`finish`), `yplot2/plots/statistical/__init__.py` (new,
seaborn-free at load), `yplot2/plots/statistical/violin.py` (new)
1. `finish(ax)`: re-assert house style on an already-drawn axes by reusing
   `apply_style` internals PLUS coercing artist linewidths across **all three** artist
   containers (plan-critic #1 — verified: seaborn's violin inner box/whisker/median are
   `Line2D` in `ax.lines`, NOT patches, and seaborn scales them to 1.125/3.375/1.5 even
   when you pass `linewidth=0.75`):
   - `ax.collections` (violin bodies / strip PathCollections) → edge/line width
   - `ax.patches` (box-type bodies) → edge width
   - `ax.lines` (inner box/whisker/median Line2D) → `set_linewidth`
   **House-look decision (explicit):** flatten the violin body + inner `Line2D` to
   `cfg.axis_linewidth` — we deliberately drop seaborn's median/box/whisker width
   hierarchy for a single uniform house weight. **EXCLUDE strip/scatter
   `PathCollection`s from the linewidth flatten** (plan-critic R2 #1): their marker
   linewidth is 0, and flattening to 0.75 would draw a gray edge ring on every jittered
   dot. Detect them (marker collections have `get_offsets()` with points / zero base
   linewidth) and either skip them or set their `edgecolor="none"`. Keep test (i) in
   sync so it doesn't then assert lw==0.75 on strip markers.
   (If we later want the median emphasized, that's a config knob, not Phase 0.)
   **Must be idempotent** — calling `finish` twice yields identical artist properties
   (add an explicit test).
2. `violin(ax, data, x, y, *, hue=None, palette_name="nucleotide", strip=True, seed=0, **kw)`:
   ```python
   def violin(ax, data, x, y, *, hue=None, palette_name="nucleotide",
              strip=True, seed=0, **kw):
       import numpy as np, seaborn as sns
       from ..colors import palette
       from ...style import finish
       from ...config import get_config
       rng_state = np.random.get_state()
       np.random.seed(seed)                       # determinism for strip jitter
       try:
           pal = palette(palette_name)            # explicit dict, not seaborn default
           sns.violinplot(ax=ax, data=data, x=x, y=y, hue=hue,
                          palette=pal, saturation=1,   # kill 0.75 desaturation
                          linewidth=get_config().axis_linewidth, **kw)
           if strip:                              # exercises the seed -> real jitter
               sns.stripplot(ax=ax, data=data, x=x, y=y, hue=hue,
                             palette=pal, size=2, jitter=True, dodge=bool(hue),
                             legend=False)
       finally:
           np.random.set_state(rng_state)         # don't leak global RNG state
       finish(ax)
       return ax
   ```
   `strip=True` by default so the determinism assertion (Task 0.5 iv) actually
   exercises RNG jitter — the real risk the strategy named (plan-critic #3).
3. **Optional-seaborn hole (plan-critic #2 — BLOCKING):** `statistical/__init__.py` must
   NOT import seaborn or the violin module at load. Do **NOT** add `violin` to
   `yplot2/plots/__init__.py`'s eager imports or to `yplot2/__init__.py`. `violin` is
   reachable only via `from yplot2.plots.statistical.violin import violin`. Same rule
   for any pandas-using helper (pandas is only present via `[stats]`).
**Acceptance:** covered by Task 0.5, plus the no-seaborn subprocess test there.

## Task 0.5 — The spike acceptance test (THE GATE, automated half)
**Files:** `tests/test_phase0_spike.py`, fixture in
`yplot2/plots/statistical/_sampledata.py` (NOT reachable from `yplot2/__init__`;
pandas-using, so it lives under the seaborn/`[stats]` side — plan-critic #2)
1. Add a deterministic synthetic RNA-shaped dataframe fixture (categories A/C/G/U,
   numeric reactivity, seeded) in `_sampledata.py`; NO external data dependency. Import
   it only inside the test, never at package load.
2. Test file sets `matplotlib.use("Agg")` before importing pyplot, and imports violin
   via `from yplot2.plots.statistical.violin import violin`. It asserts, on
   `violin(ax, sample, x="nuc", y="reactivity", hue="nuc", seed=0)`:
   - **(i) Linewidth:** across `ax.collections` + `ax.patches` + `ax.lines`, every
     style-bearing artist linewidth `== cfg.axis_linewidth` (within 1e-6). Explicitly
     iterate `ax.lines` (the inner box/whisker/median) — verified these render at
     1.125/3.375/1.5 pre-`finish`, so this catches whether `finish` flattened them.
   - **(ii) Exact palette hex:** for each category body, `to_hex(body.get_facecolor())`
     `== to_hex(palette_hex("nucleotide", <letter>))` — **both sides normalized through
     `matplotlib.colors.to_hex`** because `NUCLEOTIDE_COLORS` are named colors
     (`"red"`→`#ff0000`), not hex (plan-critic #4). This is the assertion seaborn's
     default `saturation=0.75` would fail.
   *Impl traps (plan-critic R2 #2):* `collection.get_linewidth()` returns an ARRAY
   (`[0.75]`), not a scalar — compare elementwise, not `== float`. For (ii), select the
   violin **body** collections (`FillBetweenPolyCollection`) and skip strip
   `PathCollection`s (they also carry the palette facecolor and return an `(N,4)` array
   that breaks `to_hex`); use `body.get_facecolor()[0]`.
   - **(iii) Font:** tick labels report family Arimo.
   - **(iv) Determinism (with jitter):** because `strip=True`, the strip overlay uses
     RNG — render twice with `seed=0` to separate PNG buffers (Agg, fixed dpi) and
     assert byte-identical; then render with `seed=1` and assert it DIFFERS (proves the
     seed is live, not dead code — plan-critic #3).
3. **No-seaborn import test** (`tests/test_no_seaborn_import.py`): run a subprocess with
   seaborn made unimportable (e.g. `sys.modules["seaborn"]=None` via a `-c` snippet, or
   a fake meta-path finder) and assert `import yplot2` still succeeds. This actually
   exercises the optional-dep guarantee (the `[stats]` extra otherwise installs seaborn
   into the test env, so it'd never be tested — plan-critic #2).
**Acceptance:** `pytest tests/test_phase0_spike.py tests/test_no_seaborn_import.py -q`
passes. If assertion (i), (ii), or (iv) fails, that is the spike telling us the design
needs adjustment (more `finish` coverage; palette normalization; jitter seeding) — fix
within Phase 0 scope before declaring GO. (All three now in the iterate clause.)

## Task 0.6 — Live-figure reproduction (THE GATE, human half) — NEEDS USER INPUT
**Files:** `scripts/phase0_live_figure.py`
1. Rebuild ONE real figure using the new path and eyeball it against the published
   version. Recommended target: a **`2025_dms_vs_tmo_paper` violin panel** (violins are
   ~40% of the lab's plots, so this is the highest-signal test).
2. **BLOCKED ON:** the user pointing at (a) which figure to reproduce and (b) the path
   to its analysis-ready dataframe. Until provided, implement the script against the
   synthetic fixture as a smoke run and leave a `TODO(user): wire real data`.
**Acceptance:** the figure renders house-styled with ≤1 explicit style call, and the
author judges it cleaner than the paper's `plotting.py` path.

---

## DECISION GATE (end of Phase 0)
**GO** (proceed to Phase 1 + catalog seed) iff:
- Task 0.5 passes all four assertions, AND
- Task 0.6 reproduces a real violin at house style with no per-figure restyling, AND
- doing so felt lighter than the existing per-paper `plotting.py`.

**NO-GO fallback** (documented in strategy): abandon the `use_style()` global-rcParams
ambition; keep `finish`/`apply_style` as explicit per-axes calls inside thin wrappers
(still one call per panel). Everything else in the strategy (font bundling, palette,
tests, catalog, repro spine) still proceeds — only the "coarse global default" is cut.

---

## GATED FOLLOW-ON (do NOT build until GATE passes) — catalog seed shape
For context only, so the coder knows where this heads (full spec in the strategy doc):
- `@catalog(tags, data_shape[, kind])` decorator that only **attaches attributes** to a
  plot function (no live global registry).
- Folder taxonomy `yplot2/plots/{primitives,statistical,domain,composites,templates}/`;
  category derived from folder.
- `vocab.py` controlled vocabulary for tags + data_shape tokens (build hard-fails on
  unknown token for a cataloged capsule; agents append tokens in-PR with justification).
- Each capsule ships a `demo_<name>()` (which ARE the migrated `examples/`); the demo is
  the gallery thumbnail + structural test + doc + `catalog.json` row.
- Style gate = **artist-property assertion** on the final demo figure (never a pixel
  hash). Membership requires a passing demo. Collector walks the package via
  `pkgutil.walk_packages(__path__)`, never the filesystem.
- Write the first real wrapper (`violin`, above) AS the first capsule when this lands —
  zero retrofit.

## Notes for the reviewer
- Verify Arimo LICENSE is present in `yplot2/fonts/` and package-data ships the TTFs.
- Verify `import yplot2` with seaborn UNINSTALLED still succeeds (optional-dep guard).
- Verify `finish` idempotency test exists and passes.
- Verify no code walks the filesystem for modules (guards against the `build/` shadow).
