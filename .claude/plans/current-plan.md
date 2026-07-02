# yplot2 Phase 2 — Seaborn wrapper suite + strip large-N fix + catalog SEED

> Handoff for `py-coder`. Self-contained. Do NOT deviate silently; if a signature
> below is impossible, stop and report rather than improvise.
> Style gate: `~/.claude/standards/python-style.md` (≤30-line functions, ≤3 indent
> levels, complexity ≤10, ≤4 params, full type hints + docstrings, ruff/mypy clean,
> ≥90% coverage on NEW modules). All 103 existing tests must stay green.

---

## Design resolutions (Q1–Q5 — AUTHORITATIVE; override any conflicting task text below)

- **Q1 heatmap2d / hexbin backend:** `heatmap2d()` = numpy `histogram2d` + `imshow` +
  a house-styled colorbar (`style_colorbar`); `hexbin()` = native `ax.hexbin` + styled
  colorbar. BOTH are **seaborn-free** and deterministic (this matches how the papers
  actually make 2D-hist/density plots — raw `imshow`/`hexbin`). Therefore ONLY
  `violin`/`box`/`kde` carry the lazy-seaborn import guard; `heatmap2d`/`hexbin` do not
  import seaborn at all. All four still house-style via `finish(ax)` (+ styled colorbar).
- **Q2 + Q5 strip policy:** strip overlays are **OPT-IN everywhere** — `violin(strip=False)`
  AND `box(strip=False)` by default (papers use `inner="box"` with no strip; this also
  removes the large-N footgun the real dms_vs_tmo Fig1D rebuild exposed). The concrete
  wrapper signatures below MUST read `strip=False` (do not copy any `strip=True` line).
  When a caller passes `strip=True`, apply a SEEDED per-group auto-subsample capped at
  `max_strip_points=1000` (param; `None` = no cap). **`cap_strip_groups` MUST use the
  CLAMP form** (plan-critic blocker 1): `df.groupby(keys, group_keys=False).apply(lambda
  g: g.sample(min(len(g), max_points), random_state=seed))`. Do NOT use
  `groupby(...).sample(n=max_points)` — it raises `ValueError` when any group is smaller
  than `max_points` (the everyday 40-pts/group path). **Dedupe `keys`** when `hue == x`
  (use `[x]`, not `[x, x]`). **NO test edit needed:** verified that
  `tests/test_phase0_spike.py` always calls `violin(..., strip=...)` with an explicit
  `strip`, so flipping the default to `False` leaves all 103 tests green untouched.
- **Q3 normalizer location:** shared `normalize_glyphs(ax, lw)` lives in
  `plots/statistical/_style.py` (seaborn-specific); do NOT promote to top-level `style.py`.
  Refactor `violin.py` to import it; delete `violin._normalize_seaborn_glyphs` and update
  the one `style.py` docstring mention.
- **Q4 demos & catalog exposure:** reuse the Phase-0 `make_sample_df` fixture + add one
  `make_xy_df`; `demo_<name>()` build a bare `plt.subplots()` panel (NOT `figure7`).
  Expose `catalog` at top-level `yplot2` (it's pure — no seaborn). CRITICAL: `demo_*`
  functions and the wrapper modules must NOT be import-time reachable from
  `yplot2/__init__` (mirror how `violin` is kept out of `plots/__init__`); `import yplot2`
  stays seaborn-free.

---

## What's already built (do NOT redo)

- **Phase 0** (a44e397): bundled Arimo font (`_fonts.register_bundled_fonts()` at import);
  `style.finish(ax)` (chrome-only, idempotent, does NOT touch data artists);
  `violin.py::_normalize_seaborn_glyphs(ax, lw)` (violin-local glyph flattener);
  palette registry in `plots/colors.py`: `palette()/palette_hex()/house_palette_colors()/`
  `hue_order()/register_seaborn_palettes()` (`nucleotide` + `conditions`);
  `violin()` wrapper (seaborn lazy, `import yplot2` seaborn-free); `use_style()/style()`.
  Sample data: `plots/statistical/_sampledata.py::make_sample_df(seed, n_per_nuc)`
  → long DataFrame `nuc`(str)/`reactivity`(float).
- **Phase 1** (39c064b): `canvas.figure()/figure7()`; `composite.annotate/line_annotation/`
  `distance_label`; `figure.coord_from_image`; single style engine `apply_style`+`finish`
  via `style._enforce_chrome`; `figure.add_colorbar(fig, ax, mappable, coord, fig_size, ...)`.
- **Config** (`config.get_config()`): fields used here — `axis_linewidth=0.75`,
  `colorbar_tick_fontsize=6`, `font_family="Arimo"`.
- **pyproject**: optional dep `stats = ["seaborn>=0.13,<0.14"]` (pandas arrives transitively
  via seaborn). Base deps: matplotlib, numpy only.
- **Contract to preserve**: `import yplot2` must NOT import seaborn/pandas. The statistical
  wrappers are reachable ONLY via explicit submodule import (mirror violin). They are NOT
  wired into `plots/__init__.py` or `yplot2/__init__.py`.

**Reference implementation — copy this pattern EXACTLY:** `yplot2/plots/statistical/violin.py`
(lazy `import seaborn` inside the fn with a helpful ImportError; explicit `palette` dict +
`hue_order` when `hue` given; `saturation=1` on categorical seaborn calls;
`linewidth=cfg.axis_linewidth`; save/restore `np.random` state around any jittered draw;
call the glyph normalizer then `finish(ax)`; `return ax`; `**kw` passthrough = escape hatch).

---

## Goal

Ship five house-styled statistical capsules (`violin` refactor + `box`, `kde`,
`heatmap2d`, `hexbin`), fix the large-N strip overlay that swamped the dms_vs_tmo Fig1D
rebuild, and lay a metadata-only catalog SEED (`@catalog` decorator + `vocab.py`), with
NO catalog build tooling (deferred to Phase 3).

---

## Design

New / changed modules (all under `yplot2/plots/statistical/` unless noted):

- `_style.py` (~55 lines) — shared post-draw styling of seaborn/mpl artists.
  `normalize_glyphs(ax, lw)` (the flattener factored out of violin.py) and
  `style_colorbar(cbar, cfg)` (house-style a colorbar's outline + tick labels).
- `_overlay.py` (~45 lines) — `cap_strip_groups(data, group_keys, max_points, seed)`
  returns a per-group seeded subsample so strip/point overlays never swamp large N.
- `violin.py` (refactor, stays ~120 lines) — drop the private flattener, import
  `normalize_glyphs`; add `max_strip_points` + `cap_strip_groups`; add `@catalog` + `demo_violin()`.
- `box.py` (~120 lines) — `box()` (+ opt-in strip overlay, same discipline) + `demo_box()`.
- `kde.py` (~110 lines) — `kde()` + `demo_kde()`.
- `heatmap2d.py` (~130 lines) — `heatmap2d()` (2D histogram, house-styled colorbar) + `demo_heatmap2d()`.
- `hexbin.py` (~120 lines) — `hexbin()` (native `ax.hexbin`, house-styled colorbar) + `demo_hexbin()`.
- `_sampledata.py` (extend, ~+20 lines) — add `make_xy_df(seed, n)` bivariate fixture for the 2D capsules.

Catalog seed (top-level, seaborn-free, pure):

- `yplot2/vocab.py` (~70 lines) — controlled vocabulary + validators. No seaborn/pandas/mpl.
- `yplot2/catalog.py` (~70 lines) — `@catalog(...)` decorator, attribute-attach + vocab
  validation ONLY. No registry, no collector, no json, no gallery (all Phase 3).

New tests (mirror src):

- `tests/test_shared_statistical_style.py`
- `tests/test_strip_threshold.py`
- `tests/test_statistical_wrappers.py`
- `tests/test_catalog.py`

---

## Style / structural decisions (restate the constraints)

- **Layer + raw-axes escape hatch.** Every wrapper is `fn(ax, data, ...) -> ax`, forwards
  `**kw` to the underlying seaborn/mpl call, and never blocks interop.
- **`import yplot2` stays seaborn-free.** `catalog.py`/`vocab.py` import nothing heavy.
  The wrapper modules keep seaborn/pandas imports *inside* the function body (lazy).
  They are NOT added to any `__init__`. A new subprocess test guards this.
- **Reuse, no duplication.** `normalize_glyphs` has ONE definition (`_style.py`); violin,
  box reuse it. `finish` is the only chrome enforcer. Palette via the existing
  `colors.palette()/hue_order()`. Colorbar tick font via `cfg.colorbar_tick_fontsize`.
- **Determinism.** Any jitter/subsample uses an explicit `seed`; save/restore global
  `np.random` state around seaborn draws (as violin already does).
- **@catalog is trivial** — attribute attach + vocab validation. The collector, gallery,
  fingerprint gate, and `catalog.json` are DEFERRED to Phase 3. Do NOT build them.
- **Do NOT move** basic.py / regression.py / pop_avg.py / lollipop.py into folders now
  (avoids import churn). Only `statistical/` wrappers are capsules this phase.

### Functions that may bump the ≤30-line limit (call-outs)

- `heatmap2d()` — compute hist2d + imshow + colorbar + house-style it can crowd 30 lines.
  **Mitigation:** push colorbar styling into `_style.style_colorbar()` and the histogram
  math into a private `_hist2d_image(...)` helper so the public body stays a short story.
- `box()` with the strip branch — keep the strip overlay in a private `_draw_strip(...)`
  helper shared in spirit with violin (do not over-abstract on the 2nd use; a per-module
  private helper is fine, the *data-capping* is the shared piece via `cap_strip_groups`).

---

## Files

| File | Action | Lines Est. | What |
|------|--------|-----------:|------|
| yplot2/plots/statistical/_style.py | create | ~55 | `normalize_glyphs`, `style_colorbar` |
| yplot2/plots/statistical/_overlay.py | create | ~45 | `cap_strip_groups` |
| yplot2/plots/statistical/violin.py | edit | ~120 | reuse `normalize_glyphs`; add cap + `@catalog` + demo |
| yplot2/plots/statistical/box.py | create | ~120 | `box()` (+strip) + `demo_box` |
| yplot2/plots/statistical/kde.py | create | ~110 | `kde()` + `demo_kde` |
| yplot2/plots/statistical/heatmap2d.py | create | ~130 | `heatmap2d()` + `demo_heatmap2d` |
| yplot2/plots/statistical/hexbin.py | create | ~120 | `hexbin()` + `demo_hexbin` |
| yplot2/plots/statistical/_sampledata.py | edit | +~20 | add `make_xy_df` |
| yplot2/vocab.py | create | ~70 | controlled vocabulary + validators |
| yplot2/catalog.py | create | ~70 | `@catalog` decorator (attach + validate) |
| yplot2/style.py | edit | ~1 | fix docstring ref to the moved helper |
| tests/test_shared_statistical_style.py | create | ~90 | `normalize_glyphs` + `style_colorbar` unit tests |
| tests/test_strip_threshold.py | create | ~110 | strip N-threshold + determinism |
| tests/test_statistical_wrappers.py | create | ~200 | per-wrapper structural + seaborn-optional |
| tests/test_catalog.py | create | ~130 | decorator attrs + vocab-raises + demos |

---

## API contracts (concrete signatures)

### `_style.py`
```python
def normalize_glyphs(ax: Axes, lw: float) -> None:
    """Flatten seaborn body/inner-line linewidths to lw; suppress point-collection edges.

    Verbatim behavior of the old violin._normalize_seaborn_glyphs: for every
    matplotlib.collections.PathCollection set edgecolor 'none'; for every other
    collection and every Line2D set_linewidth(lw)."""

def style_colorbar(cbar: Colorbar, cfg: Config) -> None:
    """House-style a colorbar: outline linewidth = cfg.axis_linewidth; tick-label
    font = Arimo at cfg.colorbar_tick_fontsize; tick marks = cfg.axis_linewidth."""
```
- `normalize_glyphs` is a byte-for-byte move of the current violin flattener (same loop).
- Import `Config` type for the annotation from `...config`; keep `_style.py` seaborn-free
  (it only touches already-drawn artists) so it is import-safe.

### `_overlay.py`
```python
def cap_strip_groups(
    data: Any,
    group_keys: list[str],
    max_points: int | None,
    seed: int,
) -> Any:
    """Return data with each (group_keys) group randomly subsampled to at most
    max_points rows, using a fixed random_state=seed (deterministic). When
    max_points is None, return data unchanged (draw every point).

    CLAMP form (plan-critic blocker 1) — never sample more than a group has:
    `data.groupby(group_keys, group_keys=False).apply(lambda g: g.sample(
    min(len(g), max_points), random_state=seed))`. Do NOT use
    `groupby(...).sample(n=max_points)` (raises ValueError when a group is smaller
    than max_points). Import pandas lazily inside the function so the module stays
    import-safe without the [stats] extra."""
```
- Rationale (put in docstring): the dms_vs_tmo Fig1D rebuild overlaid 236k strip points and
  visually swamped the violins. Capping points PER GROUP (not total) keeps every category
  legible and the render deterministic.

### `violin.py` (changed signature)
```python
def violin(ax, data, x, y, *, hue=None, palette_name="nucleotide",
           strip=False, max_strip_points=1000, seed=0, **kw) -> Axes: ...
```
- Param count: `ax, data, x, y` positional + keyword-only rest — the ≤4-positional rule is
  satisfied (keyword-only args don't count against readability here; violin already exceeds
  4 total and is the sanctioned pattern). Keep them keyword-only as today.
- When `strip`: build `keys = [x] if (hue is None or hue == x) else [x, hue]` (dedupe when
  hue==x — plan-critic concern 3), then
  `strip_df = cap_strip_groups(data, keys, max_strip_points, seed)` and stripplot on `strip_df`.
- Replace `_normalize_seaborn_glyphs(ax, cfg.axis_linewidth)` with
  `normalize_glyphs(ax, cfg.axis_linewidth)` (import from `._style`).
- Default is now `strip=False` (Q2). Existing `make_sample_df` has 40 pts/group < 1000, so
  the cap is a no-op; the Phase-0 tests call `violin(..., strip=True)` EXPLICITLY, so **no
  existing test changes** and strip PathCollections are still produced when opted in.

### `box.py`
```python
def box(ax, data, x, y, *, hue=None, palette_name="nucleotide",
        strip=False, max_strip_points=1000, seed=0, **kw) -> Axes: ...
```
- `sns.boxplot(ax=, data=, x=, y=, hue=, palette=pal, hue_order=hue_ord, saturation=1,
  linewidth=cfg.axis_linewidth, **kw)`. Box already shows the distribution, so strip is
  OFF by default (opt-in); when on, use the SAME `cap_strip_groups` discipline as violin.
- `normalize_glyphs(ax, cfg.axis_linewidth)` then `finish(ax)`.

### `kde.py`
```python
def kde(ax, data, x, *, hue=None, palette_name="nucleotide",
        fill=True, **kw) -> Axes: ...
```
- `sns.kdeplot(ax=, data=, x=, hue=, palette=pal, hue_order=hue_ord, fill=fill,
  linewidth=cfg.axis_linewidth, **kw)`. No jitter → no RNG dance. Note: `kdeplot` takes no
  `saturation`; do NOT pass it. `normalize_glyphs` then `finish(ax)`.

### `heatmap2d.py`  (2D histogram via numpy + imshow; RECOMMENDED, see open question Q1)
```python
def heatmap2d(ax, x, y, *, bins=50, cmap="magma", colorbar=True, **kw) -> Axes: ...
```
- `x, y`: array-likes (or column arrays the caller extracted). Compute
  `counts, xedges, yedges = np.histogram2d(x, y, bins=bins)`; draw with
  `ax.imshow(counts.T, origin="lower", extent=[...], aspect="auto", cmap=cmap, **kw)`.
- If `colorbar`: `cbar = ax.figure.colorbar(im, ax=ax)` then `style_colorbar(cbar, cfg)`.
- `finish(ax)` last. This capsule needs NO seaborn (numpy+mpl only) — but keep it in
  `statistical/` and OUT of the top-level `__init__` for taxonomy consistency. (If Q1 is
  resolved toward seaborn, switch the body to `sns.histplot(ax=, x=, y=, bins=, cbar=,
  cmap=)` with the lazy-import ImportError guard and style the returned `cbar`.)
- Keep the public body ≤30 lines by delegating to a private `_hist2d_image(ax, x, y, bins, cmap, **kw)`.

### `hexbin.py`  (native mpl `ax.hexbin`)
```python
def hexbin(ax, x, y, *, gridsize=30, cmap="magma", colorbar=True, **kw) -> Axes: ...
```
- `hb = ax.hexbin(x, y, gridsize=gridsize, cmap=cmap, **kw)`; if `colorbar`,
  `style_colorbar(ax.figure.colorbar(hb, ax=ax), cfg)`; `finish(ax)`. No seaborn needed
  (seaborn has no axes-level hexbin). Same taxonomy note as heatmap2d.

### `_sampledata.py` addition
```python
def make_xy_df(seed: int = 42, n: int = 2000) -> pd.DataFrame:
    """Deterministic bivariate-normal sample: columns x (float), y (float)."""
```

### `vocab.py`
```python
TAGS: frozenset[str] = frozenset({
    "distribution", "categorical", "density", "comparison",
    "points", "2d-histogram", "hexbin", "nucleotide", "seaborn",
})
DATA_SHAPES: frozenset[str] = frozenset({"long-df", "xy", "matrix"})
KINDS: frozenset[str] = frozenset({"panel", "figure"})

def validate_tags(tags: Sequence[str]) -> None:  # raises ValueError on unknown token
def validate_shape(shape: str) -> None:          # raises ValueError on unknown token
def validate_kind(kind: str) -> None:            # raises ValueError on unknown token
```
- Each validator raises `ValueError` naming the offending token AND listing the allowed set
  (so drift can't start silently). Module docstring states the governance rule: **an agent
  adding a new token appends it to `vocab.py` (with a one-line justification) in the same change.**

### `catalog.py`
```python
def catalog(*, tags: Sequence[str], data_shape: str, kind: str = "panel") -> Callable:
    """Attach a validated __yp_catalog__ metadata dict to a plot function.

    ONLY attaches attributes; there is NO global registry, collector, gallery, or
    catalog.json (all deferred to Phase 3). Validates tags/data_shape/kind against
    yplot2.vocab and raises ValueError on any unknown token."""
```
- The decorator calls the three `vocab` validators, then sets
  `fn.__yp_catalog__ = {"tags": tuple(tags), "data_shape": data_shape, "kind": kind,
  "category": _category_from_module(fn.__module__)}` and returns `fn`.
- `_category_from_module(module: str) -> str`: split on ".", return the segment immediately
  after `"plots"` (e.g. `yplot2.plots.statistical.violin` → `"statistical"`); if `"plots"`
  is absent or last, return `"uncategorized"`. (Name/signature/summary introspection is
  Phase 3 — do NOT add it here.)
- Decorate all five wrappers: `@catalog(tags=[...], data_shape="long-df"|"xy", kind="panel")`.
  Suggested tags — violin: `["distribution","categorical","nucleotide","seaborn"]`;
  box: `["distribution","categorical","comparison","seaborn"]`;
  kde: `["density","distribution","seaborn"]`;
  heatmap2d: `["2d-histogram","density"]`; hexbin: `["hexbin","density"]`.
- Each wrapper module also defines `demo_<name>() -> matplotlib.figure.Figure` that builds a
  small `fig, ax = plt.subplots(...)`, calls the wrapper on bundled sample data
  (`make_sample_df` for violin/box/kde; `make_xy_df` for heatmap2d/hexbin), and returns `fig`.
- **Where `catalog` is exposed:** import `catalog` into `yplot2/__init__` top-level (it is
  pure/seaborn-free) as `yp.catalog`, and add to `__all__`. Do NOT import any wrapper module
  there. (Confirm via Q4 if you'd rather keep it submodule-only.)

---

## Steps (ordered, each independently verifiable)

1. [ ] **`_style.py`** — move the glyph flattener out of violin.py verbatim as
   `normalize_glyphs`; add `style_colorbar`. Update violin.py to import + call
   `normalize_glyphs`; delete the private copy; fix BOTH docstring references that name the
   old symbol — `style.py:1025` AND the self-reference in `violin.py:52` (plan-critic
   concern 2) — else the grep gate below fails.
   - Test (`test_shared_statistical_style.py`): a violin drawn through `violin()` still has
     body/inner-line lw == `cfg.axis_linewidth` and strip edgecolor alpha == 0 (i.e. all
     `test_phase0_spike.py` glyph asserts still pass); a colorbar passed to `style_colorbar`
     reports outline lw == `axis_linewidth` and tick label fontname contains "Arimo".
   - Verify: `grep -r _normalize_seaborn_glyphs yplot2 tests` returns only history/none;
     ruff complexity ≤10.

2. [ ] **`_overlay.py`** — `cap_strip_groups`.
   - Test (`test_strip_threshold.py`): a df with one 5000-row group capped at
     `max_points=1000` returns exactly 1000 rows for that group; `max_points=None` returns
     all 5000; two calls with the same seed return identical row indices (determinism);
     different seeds differ.

3. [ ] **violin.py strip cap** — add `max_strip_points=1000`; route the strip overlay df
   through `cap_strip_groups`.
   - Test: build a synthetic df (5000 pts in group "A") via a local fixture, call
     `violin(..., strip=True, max_strip_points=1000)`, assert the strip PathCollection total
     offsets ≤ n_groups × 1000; assert `max_strip_points=None` draws all points; assert
     seed determinism of the overlay. **Existing `test_phase0_spike.py` unchanged and green.**

4. [ ] **vocab.py** then **catalog.py** — vocabulary + decorator.
   - Test (`test_catalog.py`): `@catalog(tags=["distribution"], data_shape="long-df")` on a
     dummy fn sets `__yp_catalog__` with the right tags/shape/kind and
     `category` derived from `__module__`; `catalog(tags=["nope"], ...)` raises `ValueError`;
     unknown `data_shape` raises; unknown `kind` raises; `_category_from_module` maps a
     `yplot2.plots.statistical.x` module to `"statistical"`.
   - Verify: no module-level mutable registry exists (grep for a global dict/list being
     appended in catalog.py — there must be none).

5. [ ] **Decorate violin + write `demo_violin`**; add `make_xy_df` to `_sampledata.py`.
   - Test: `violin.__yp_catalog__["category"] == "statistical"`; `demo_violin()` returns a
     `matplotlib.figure.Figure` with ≥1 axes; close the fig.

6. [ ] **box.py** (+ strip discipline) + `@catalog` + `demo_box`.
   - Test (`test_statistical_wrappers.py`): box bodies carry exact house palette hex
     (`palette_hex("nucleotide", n)` for each nuc) — proves `saturation=1` + palette dict;
     spine lw == `axis_linewidth`, tick label font contains "Arimo" (house style on seaborn
     artists); `strip=True` overlay respects `max_strip_points`; `__yp_catalog__` present.

7. [ ] **kde.py** + `@catalog` + `demo_kde`.
   - Test: kde line lw == `axis_linewidth`; tick font "Arimo"; hue path uses the registry
     `hue_order`; `demo_kde()` returns a Figure.

8. [ ] **heatmap2d.py** + `@catalog` + `demo_heatmap2d` (resolve Q1 first; default = numpy+imshow).
   - Test: an AxesImage is present; when `colorbar=True` a colorbar exists with outline
     lw == `axis_linewidth` and tick font "Arimo" (house-styled colorbar); spine/tick house
     style applied; `demo_heatmap2d()` returns a Figure.

9. [ ] **hexbin.py** + `@catalog` + `demo_hexbin`.
   - Test: a `PolyCollection` from `ax.hexbin` is present; colorbar house-styled when on;
     `demo_hexbin()` returns a Figure.

10. [ ] **seaborn-optional + import-safety** across the suite.
    - Test: extend the seaborn-absent guard — with `sys.modules["seaborn"]=None`, importing
      the *modules* still succeeds (imports are lazy) but calling `violin()/box()/kde()`
      raises `ImportError` whose message contains `pip install 'yplot2[stats]'`.
      `heatmap2d()/hexbin()` must still WORK with seaborn absent (numpy/mpl only) if Q1 keeps
      them seaborn-free — assert that. Add a subprocess test asserting `import yplot2` with
      seaborn blocked still succeeds (mirror `test_no_seaborn_import.py`).

11. [ ] **Wire `catalog` into `yplot2/__init__`** (top-level, `__all__`); confirm NO wrapper
    module is imported there.
    - Test: subprocess `import sys; sys.modules['seaborn']=None; import yplot2; yplot2.catalog`
      prints OK; `"seaborn" not in sys.modules` after `import yplot2`.

---

## Toolchain (MUST pass before handoff back)

```bash
cd /Users/jyesselman2/local/code/python/developing/yplot2
ruff check --fix .
ruff format .
mypy yplot2/ --ignore-missing-imports        # seaborn/pandas are untyped; data params are Any
python -m pytest                              # all 103 existing + new tests green
python -m pytest --cov=yplot2 --cov-report=term-missing   # ≥90% on NEW modules
# import-safety spot check:
python -c "import sys; sys.modules['seaborn']=None; import yplot2; assert 'seaborn' not in sys.modules; print('seaborn-free OK')"
```
- Coverage threshold is not globally enforced (see pyproject note); still hit ≥90% on the
  new `_style.py/_overlay.py/box.py/kde.py/heatmap2d.py/hexbin.py/vocab.py/catalog.py`.
- mypy: annotate `data` as `Any` (as violin does); `x/y` for heatmap2d/hexbin as
  `Any`/array-like. Type the colorbar as `matplotlib.colorbar.Colorbar`.

---

## Reviewer notes (`py-reviewer`, read-only, audit the diff)

- `normalize_glyphs` must have exactly ONE definition (`_style.py`); violin.py imports it
  and no longer defines a private flattener; `style.py` docstring no longer names the old symbol.
- `import yplot2` triggers no seaborn/pandas import (subprocess assertion). No wrapper module
  is referenced from any `__init__`.
- `catalog.py` has NO global registry / collector / json / gallery (that's Phase 3). It only
  attaches `__yp_catalog__` and validates against `vocab`.
- `vocab` validators raise `ValueError` on unknown tokens and name the allowed set.
- Determinism preserved: strip subsample + violin jitter both seeded; global `np.random`
  state restored around seaborn draws.
- Palette correctness: box/violin bodies carry undiluted `palette_hex(...)` (proves
  `saturation=1` + explicit palette dict + `hue_order` path).
- No existing plot files moved; `basic/regression/pop_avg/lollipop` untouched.
- All 103 prior tests still pass unmodified.

---

## Open design questions — RESOLVED (see the authoritative "Design resolutions (Q1–Q5)"
## block at the top of this plan; that block governs. Original notes retained below for
## context only — where they conflict with the top block, the top block WINS.)

- **Q1 — heatmap2d backend.** RESOLVED: numpy `histogram2d` + `imshow` + styled colorbar;
  `hexbin` = native `ax.hexbin`. Both seaborn-FREE. Only violin/box/kde carry the guard.
- **Q2 — strip large-N policy.** RESOLVED: strip OPT-IN, default `strip=False` on violin AND
  box; when on, seeded per-group CLAMP subsample at `max_strip_points=1000`. No Phase-0 test
  edit needed.
- **Q3 — normalizer.** RESOLVED: `plots/statistical/_style.py::normalize_glyphs`.
- **Q4 — demos & catalog.** RESOLVED: reuse `make_sample_df` + add `make_xy_df`; demos as
  bare `plt.subplots` panels; `yp.catalog` top-level; demos NOT import-time reachable.
- **Q5 — box strip default.** RESOLVED: BOTH `box(strip=False)` AND `violin(strip=False)` —
  strip is opt-in everywhere; there is NO asymmetry (the earlier `violin(strip=True)` idea
  was dropped in Q2). Points are opt-in on both.

> **pandas note (plan-critic concern):** the clamp `groupby(...).apply(...)` idiom emits a
> `FutureWarning` on pandas 2.3.3 but is not test-breaking (no `filterwarnings=error`). Do
> NOT silence it with `include_groups=False` — that drops the `x`/`hue` grouping columns
> `stripplot` needs. Leave the idiom as written (columns/index are preserved correctly).

