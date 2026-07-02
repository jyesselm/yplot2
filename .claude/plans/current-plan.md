# yplot2 Phase 3 — Reproducibility spine + catalog BUILD tooling

> Handoff for `py-coder`. Self-contained; you do NOT see the planning conversation.
> Follow `~/.claude/standards/python-style.md`: functions ≤30 lines / complexity ≤10,
> ≤4 positional params (group extras into keyword-only or a dataclass), full type hints +
> Args/Returns/Raises docstrings, modules 200–300 lines, `ruff check`/`ruff format`/`mypy`
> clean, `pytest` with ≥90% coverage on NEW code.

---

## Design resolutions (Q1–Q7 — AUTHORITATIVE; override conflicting task text below)

- **Q1 PDF determinism:** `save()` sets `metadata={"CreationDate": None}` to suppress the
  wall-clock timestamp; do NOT stamp a fake fixed epoch. Document that strict byte-identical
  PDFs need `SOURCE_DATE_EPOCH` (mpl honors it). Determinism is best-effort; provenance is
  the goal.
- **Q2 source path:** store the caller-passed `source` VERBATIM in metadata; recommend
  (in docs) passing a repo-relative path. Do NOT force `os.path.relpath`. The best-effort
  git SHA is the real provenance anchor.
- **Q3 output location:** `catalog.json` + `CATALOG.md` + `thumbs/` live in a `catalog/`
  dir at the REPO ROOT (CLI `--out-dir` default `catalog/`), and are COMMITTED (agent- and
  human-readable). DEFER the "commit catalog.json into yplot2/ + `__init__` reads it"
  namespace idea to Phase 4.
- **Q4 notebook tool:** `nbconvert` (execute in a clean kernel), behind a new optional
  `[repro]` extra (`nbconvert`, `ipykernel`) so the base install stays light.
- **Q5 build CLI:** keep `python -m yplot2.build <dir>` (unit-testable, cross-platform);
  `figures/build.sh` is a thin wrapper over it.
- **Q6 missing seaborn in the fingerprint gate:** SKIP demos whose wrapper needs seaborn
  when seaborn is absent (base suite stays green); the CI `[stats]` job runs the FULL
  fingerprint gate. `catalog.json` static collection stays seaborn-free regardless.
- **Q7 curation:** `differentiator=` dup-lint + active/deprecated `status` are Phase 4 —
  OUT of Phase 3.
- **Fingerprint correctness (CORRECTED — plan-critic verified my earlier claim was wrong):**
  heatmap2d/hexbin MAIN panels ARE fully ticked and house-styled (Arimo/6 ticks, 0.75
  visible spines) — do NOT skip them. The correct mechanism (already in the plan body) is
  PER-ARTIST existence, not axis-type skipping: (a) assert `get_linewidth()==axis_linewidth`
  only on VISIBLE spines — this naturally covers a colorbar's visible `'outline'` spine
  (0.75) and ignores its invisible default-0.8 frame spines; do NOT hard-restrict the spine
  loop to `{left,right,bottom,top}` (that would skip the `'outline'` key); (b) assert
  tick-font/size only on ticks/labels that EXIST. For COLORBAR axes specifically, SKIP the
  tick-font/size assertion (check only the visible `'outline'` spine lw): `style_colorbar`
  sets colorbar tick labels to the RAW `cfg.font_family` + `colorbar_tick_fontsize`, whereas
  `finish` uses `_resolve_font_family(...)` + `x/y_axis_tick_fontsize`; they coincide today
  only because both are 6 and "Arimo" resolves to itself — asserting them equal would
  false-fail if a user set `font_family="Arial"`. Do NOT blanket-skip colorbar axes (keep the
  outline check). Required in the fingerprint acceptance tests.

---

## What's already built (do NOT redo)

- Phases 0–2 (last commit `5f98dcc`). Bundled Arimo font registered at import
  (`yplot2/_fonts.py`); single style engine `apply_style` / `finish` in `yplot2/style.py`;
  `figure7()` / `GridSpec7` canvas; composite/annotation helpers; palette registry.
- `yplot2/catalog.py` — `@catalog(tags=, data_shape=, kind=)` decorator that ONLY attaches
  a validated `fn.__yp_catalog__` dict (`tags`, `data_shape`, `kind`, `category`).
  `_category_from_module(module)` returns the segment after `"plots"`. There is deliberately
  NO registry / collector / gallery / json here — that is THIS phase.
- `yplot2/vocab.py` — controlled `TAGS` / `DATA_SHAPES` / `KINDS` frozensets +
  `validate_tags/validate_shape/validate_kind` (raise on unknown token).
- Five statistical capsules in `yplot2/plots/statistical/` (`violin`, `box`, `kde`,
  `heatmap2d`, `hexbin`). Each carries `@catalog` and a sibling `demo_<name>() -> Figure`
  that renders from `_sampledata.py` fixtures via a bare `plt.subplots()`. Seaborn is
  imported LAZILY inside wrapper bodies (`_require_seaborn`), so importing a capsule MODULE
  is seaborn-free; only RUNNING a demo needs `[stats]`.
- `Config` (`yplot2/config.py`): `axis_linewidth=0.75`, `axis_tick_width=0.75`,
  `x_axis_tick_fontsize=6`, `y_axis_tick_fontsize=6`, `font_family="Arimo"`,
  `colorbar_tick_fontsize=6`. Resolve the house font with
  `yplot2.style._resolve_font_family(cfg.font_family)` (returns `"Arimo"`).
- 186 tests green. `import yplot2` is seaborn-free (guarded by
  `tests/test_no_seaborn_import.py` via `sys.modules['seaborn']=None` in a subprocess).
- `build/lib/yplot2/**` is an on-disk SHADOW copy (gitignored, untracked). The collector
  must NEVER discover it.

---

## Goal

Ship Phase 3's two deliverables without regressing the 186 tests or determinism:
**(A)** a reproducibility spine — `yp.save()` with provenance stamping + a one-command
figure-regen convention that also executes notebooks; **(B)** catalog BUILD tooling that
consumes the Phase-2 `@catalog` seed — a `pkgutil` collector, a STATIC `catalog.json`, a
BLOCKING artist-property style-fingerprint gate with best-effort thumbnails, and a
generated `CATALOG.md` gallery — wired into `figures/build.sh` and CI.

---

## Hard constraints (restate — a reviewer will check these)

- `import yplot2` MUST stay seaborn-free. `yplot2/save.py`, `yplot2/build.py`, and the
  collector/records modules MUST be pure at import (NO seaborn / pandas / heavy deps).
  Only the fingerprint step (which runs demos) may pull seaborn — and only lazily, inside
  a function body, at build time.
- Collection walks the package via `pkgutil.walk_packages(yplot2.__path__, prefix=...)` —
  NEVER a filesystem glob (that would find the `build/lib/yplot2/**` shadow).
- STATIC `catalog.json` is DECOUPLED from fragile rendering: it is generated from pure
  static introspection and is ALWAYS written, even if every demo fails to render. This is
  the key robustness decision — do not couple json generation to demo execution.
- The style-fingerprint assertion is an ARTIST-PROPERTY / rcParams check (spine lw, tick
  font family/size). NEVER a pixel/PNG hash. It is BLOCKING (build fails). The thumbnail
  PNG render is BEST-EFFORT / non-blocking (a failed PNG is cosmetic).
- Determinism: `yp.save` output must be reproducible. Do NOT stamp wall-clock time. Stamp
  only source path + git SHA (best-effort) + caller-supplied data hashes. For PDF, suppress
  matplotlib's default `CreationDate`/`ModDate`.
- Reuse existing helpers (`finish`, `get_config`, `_resolve_font_family`, the structural
  assertion style of `tests/test_shared_statistical_style.py`). Layer + escape hatch; do
  not rewrite Phase 0–2 code.
- Solo maintainer / low ops: the build stays a simple, testable script — NOT a framework.

---

## Deferred to Phase 4 (do NOT build now)

pytest-mpl visual regression (mention as future only); the `~/.claude` agent skill; the
`yplot`→`yplot2` compat shim + atp-ttr-switch migration; the anti-fork lint;
figure-templates; migrating the 11 `examples/` into capsule demos.

---

## Module layout (new)

```
yplot2/
  save.py                    # ~150  yp.save() + provenance helpers (PURE)
  build.py                   # ~130  figure-regen CLI: python -m yplot2.build <dir> (PURE)
  catalog_build/
    __init__.py              # ~10   exports build_catalog(); no heavy imports
    records.py               # ~90   CapsuleRecord dataclass + SCHEMA_VERSION + json (PURE)
    collect.py               # ~150  pkgutil collector, sandboxed import, introspection (PURE)
    fingerprint.py           # ~140  style-fingerprint gate + best-effort thumbnail (mpl)
    build.py                 # ~150  orchestrator + CLI: python -m yplot2.catalog_build.build
figures/
  build.sh                   # template: regen figures + regen catalog (NOT python)
  requirements.lock.template # per-paper pin recommendation (text, not code)
.github/workflows/
  catalog.yml                # CI: run catalog build (static + blocking fingerprint gate)
```

`catalog_build` is a separate subpackage from the existing `catalog.py` decorator module —
they coexist (`yplot2.catalog` = decorator, `yplot2.catalog_build` = build tooling).

---

## Style notes (call-outs against the standard)

- `yplot2/style.py` is a legacy 1100-line file EXEMPT from the 300-line rule (out of scope;
  do not touch beyond importing `finish` / `_resolve_font_family`). All NEW modules obey the
  200–300 line target.
- `save()` and CLI `main()` functions risk exceeding 30 lines from argument wiring — keep
  them thin dispatchers that delegate to helpers (`_build_provenance`, `_png_metadata`,
  `_pdf_metadata`, `_discover_targets`, `_run_target`). Flag any that creep over 30.
- Keep every public function ≤4 positional params: `save(fig, path, *, source=None,
  data_hashes=None, dpi=300)` — only `fig`, `path` positional, rest keyword-only.
- pyproject: add the new modules to the coverage `include`/remove from `omit` as needed so
  the ≥90% gate actually measures them; subprocess/CLI glue that cannot be unit-tested must
  be marked `# pragma: no cover` sparingly and kept to a few lines.

---

## Toolchain (run before declaring done)

```bash
ruff check --fix yplot2 tests
ruff format yplot2 tests
mypy yplot2 --ignore-missing-imports
pytest --cov=yplot2 --cov-report=term-missing        # 186 existing MUST stay green
rm -rf build/                                          # housekeeping (Task 8)
python -m yplot2.catalog_build.build --out-dir catalog # smoke: writes catalog.json + CATALOG.md
```

---

## Ordered tasks

### Task 1 — `yplot2/save.py`: provenance-stamping save (PURE module)

Files: `yplot2/save.py` (new), `yplot2/__init__.py` (export), `tests/test_save.py` (new).

Public API:
```python
def save(
    fig: "matplotlib.figure.Figure",
    path: str | os.PathLike[str],
    *,
    source: str | None = None,
    data_hashes: dict[str, str] | None = None,
    dpi: int = 300,
) -> None:
    """Save fig with enforced dpi + white facecolor and stamped provenance.

    Format is inferred from the path suffix (.png or .pdf). Provenance —
    the source script path, best-effort git SHA, and optional data hashes —
    is written into the image metadata (PNG tEXt chunks / PDF info dict).
    Output is deterministic: no wall-clock time is stamped.
    """
```

Helpers (each ≤30 lines, one responsibility):
- `_git_sha(start_dir: str) -> str | None` — best-effort `git -C <dir> rev-parse HEAD` via
  `subprocess.run` with a short timeout; return `None` on any failure (not a repo, no git,
  timeout). MUST NOT raise. Optionally append `"-dirty"` if `git status --porcelain` is
  non-empty (nice-to-have; keep simple if it pushes complexity over 10).
- `_resolve_source(source: str | None) -> str` — `source` if given, else `sys.argv[0]`
  (graceful `"unknown"` when empty). Recommend callers pass a repo-relative path.
- `_build_provenance(source, data_hashes) -> dict[str, str]` — assemble ordered dict:
  `{"yplot2_source": <src>, "yplot2_git_sha": <sha or "unknown">, "yplot2_version":
  yplot2.__version__, "yplot2_data_hashes": <"k=v;..." or "">}`. Deterministic ordering.
- `_png_metadata(prov) -> dict[str, str]` — map provenance into PNG text keys: put the
  human summary under `"Software"`/`"Comment"` plus each `yplot2_*` key verbatim (matplotlib
  PNG backend writes arbitrary dict keys as tEXt chunks; PNG adds no date by default).
- `_pdf_metadata(prov) -> dict[str, str | None]` — map into PDF info keys
  (`Creator`/`Subject`/`Keywords`), AND set `"CreationDate": None` and `"ModDate": None`
  to suppress matplotlib's default wall-clock stamps (determinism).
- `save()` body: set `fig.set_facecolor("white")`, pick metadata builder by suffix (raise
  `ValueError` on an unsupported suffix listing `.png/.pdf`), call
  `fig.savefig(path, dpi=dpi, facecolor="white", metadata=<...>)`.

Export: add `save` to the imports and `__all__` in `yplot2/__init__.py` (near `finish`).
Confirm `save.py` imports NOTHING heavy at module top (only `os`, `sys`, `subprocess`,
`typing`; import `yplot2.__version__` lazily inside `_build_provenance` or via
`from . import __version__` guarded to avoid a cycle — prefer reading `__version__` lazily).

Acceptance tests (`tests/test_save.py`):
- `test_save_png_roundtrips_provenance`: save to a tmp `.png` with
  `source="figures/fig1.py"`, `data_hashes={"counts": "abc123"}`; read the file BYTES and
  assert `b"figures/fig1.py"` and `b"abc123"` and `b"yplot2_git_sha"` appear (PNG tEXt is
  literal ASCII — dependency-free round-trip).
- `test_save_pdf_roundtrips_provenance`: same for `.pdf`; assert the source substring is in
  the bytes AND assert NO literal wall-clock date leaked (assert the metadata builder set
  `CreationDate`/`ModDate` to `None` — unit-test `_pdf_metadata` directly for this).
- `test_save_sets_white_facecolor`: after `save()`, `fig.get_facecolor()` == white
  (`(1.0, 1.0, 1.0, 1.0)`).
- `test_save_deterministic`: save the same fig twice to two paths; assert the two files are
  byte-identical (proves no wall-clock stamp).
- `test_save_unsupported_suffix_raises`: `.svg` path → `ValueError` mentioning `.png/.pdf`.
- `test_git_sha_graceful_outside_repo`: `_git_sha(tmp_path)` (a fresh non-repo dir) returns
  `None` without raising.
- `test_save_exported`: `import yplot2; assert callable(yplot2.save)`.
- Verify: ruff complexity ≤10 on every helper.

### Task 2 — `yplot2/build.py`: one-command figure-regen CLI (PURE module)

Files: `yplot2/build.py` (new), `tests/test_build.py` (new).

Purpose: `python -m yplot2.build <dir>` regenerates every figure in a directory by running
each `*.py` script AND executing each `*.ipynb` notebook headless from a CLEAN kernel.

API:
```python
@dataclass(frozen=True)
class BuildResult:
    """Outcome of regenerating one figure target."""
    target: str          # path
    ok: bool
    stderr: str          # captured on failure (empty on success)

def discover_targets(directory: str) -> list[str]:
    """Return sorted .py and .ipynb figure targets under *directory* (non-recursive)."""

def run_script(path: str) -> BuildResult:
    """Execute a .py figure script in a fresh subprocess."""

def run_notebook(path: str) -> BuildResult:
    """Execute a notebook in place headless via `jupyter nbconvert --execute --inplace`."""

def build(directory: str) -> list[BuildResult]:
    """Regenerate all figure targets in *directory*; return per-target results."""

def main(argv: list[str] | None = None) -> int:
    """CLI entry: `python -m yplot2.build <dir>`. Returns process exit code."""
```

Notes:
- Notebook execution uses `jupyter nbconvert --execute --inplace --to notebook <path>` via
  `subprocess.run`. If `jupyter`/`nbconvert` is absent, `run_notebook` returns a FAILED
  `BuildResult` with a clear "install nbconvert" message rather than raising.
  (Recommend nbconvert over papermill — fewer deps; see open questions.)
- `run_script` uses `[sys.executable, path]` in a fresh subprocess (clean interpreter).
- `main` prints a per-target PASS/FAIL summary and returns `1` if any target failed, else `0`.
- Keep `subprocess.run(...)` calls behind the small `run_*` helpers so tests can monkeypatch
  them. `main` itself stays a thin dispatcher (≤30 lines).
- `python -m yplot2.build` works because `build.py` ends with
  `if __name__ == "__main__": raise SystemExit(main())`.

Acceptance tests (`tests/test_build.py`):
- `test_discover_targets_sorted`: tmp dir with `b.py`, `a.py`, `c.ipynb`, `notes.txt` →
  returns `[a.py, b.py, c.ipynb]` (sorted, txt excluded).
- `test_run_script_success` / `test_run_script_failure`: write a trivial script that exits
  0 / raises; assert `BuildResult.ok` and stderr capture.
- `test_run_notebook_missing_tool_graceful`: monkeypatch `subprocess.run` to raise
  `FileNotFoundError` → returns a FAILED result, no exception.
- `test_build_aggregates_and_main_exit_code`: mix a passing + failing script; `build()`
  returns both; `main([dir])` returns `1`.
- Mark any un-unit-testable subprocess line `# pragma: no cover` sparingly.

### Task 3 — `catalog_build/records.py`: record model + JSON schema (PURE)

Files: `yplot2/catalog_build/__init__.py`, `yplot2/catalog_build/records.py`,
`tests/test_catalog_records.py`.

```python
SCHEMA_VERSION = 1

@dataclass(frozen=True)
class CapsuleRecord:
    """Static, render-free description of one @catalog capsule."""
    name: str            # fn.__name__
    category: str        # from __yp_catalog__["category"]
    tags: tuple[str, ...]
    data_shape: str
    kind: str
    signature: str       # str(inspect.signature(fn))
    inputs: tuple[str, ...]   # parameter names excluding leading 'ax'/'self'
    summary: str         # first non-blank line of fn.__doc__ ("" if none)
    source_path: str     # inspect.getsourcefile(fn), repo-relative if possible
    import_path: str     # f"{fn.__module__}.{fn.__name__}"
    has_demo: bool       # sibling demo_<name> exists in the module

def record_to_dict(rec: CapsuleRecord) -> dict[str, object]: ...
def catalog_to_json(records: Sequence[CapsuleRecord]) -> str:
    """Serialize records to deterministic pretty JSON with a top-level
    {"schema_version": SCHEMA_VERSION, "capsules": [...]} shape, sorted by
    (category, name), indent=2, trailing newline."""
```

Pure: only `dataclasses`, `json`, `typing`, `collections.abc`. No matplotlib import.

Acceptance tests: round-trip a hand-built record → dict has all fields; `catalog_to_json`
output parses back, contains `schema_version==1`, capsules sorted by `(category, name)`,
and is byte-stable across two calls (determinism).

### Task 4 — `catalog_build/collect.py`: pkgutil collector (PURE, sandboxed)

Files: `yplot2/catalog_build/collect.py`, `tests/test_catalog_collect.py`.

```python
@dataclass(frozen=True)
class ImportFailure:
    """A module that could not be imported during collection."""
    module: str
    error: str

def collect_records() -> tuple[list[CapsuleRecord], list[ImportFailure]]:
    """Walk the yplot2 package and return (capsule records, import failures).

    Uses pkgutil.walk_packages over yplot2.__path__ (NEVER a filesystem glob),
    imports each submodule in a try/except sandbox (a failing import becomes an
    ImportFailure, never aborts the walk), and extracts CapsuleRecords from every
    module-level function carrying __yp_catalog__.
    """
```

Helpers:
- `_iter_module_names() -> Iterator[str]` — `pkgutil.walk_packages(yplot2.__path__,
  prefix="yplot2.")`, yielding `mod.name`. Because it walks `__path__` (the installed
  package location), the `build/lib/yplot2` shadow is never reachable.
- `_safe_import(name) -> tuple[ModuleType | None, ImportFailure | None]` — try/except; on
  ANY exception (incl. missing optional dep) return an `ImportFailure`. Importing a capsule
  module is seaborn-free (decorator runs without seaborn), so this rarely fails — but stay
  defensive.
- `_records_from_module(module) -> list[CapsuleRecord]` — `inspect.getmembers(module,
  inspect.isfunction)`, keep fns where `getattr(fn, "__yp_catalog__", None)` is set AND
  `fn.__module__ == module.__name__` (avoid double-counting re-imported names). Build a
  record via `_build_record(fn, module)`.
- `_build_record(fn, module) -> CapsuleRecord` — pull `__yp_catalog__`, `inspect.signature`,
  param names (drop a leading `ax`/`self`), docstring first line, `inspect.getsourcefile`
  (make repo-relative via `os.path.relpath` against `yplot2` package root, best-effort),
  and `has_demo = hasattr(module, f"demo_{fn.__name__}")`.

Static only — NEVER calls a demo.

Acceptance tests (`tests/test_catalog_collect.py`):
- `test_collects_five_statistical_capsules`: `records, failures = collect_records()`;
  assert names ⊇ {violin, box, kde, heatmap2d, hexbin}, each `category=="statistical"`,
  `has_demo is True`.
- `test_collect_is_seaborn_free`: run `collect_records()` in a subprocess with
  `sys.modules['seaborn']=None` (mirror `test_no_seaborn_import.py`); assert it still finds
  all five (proves static collection needs no seaborn).
- `test_collector_skips_build_shadow`: assert no record's `source_path` contains
  `"build/lib"` and no module name repeats.
- `test_import_failure_is_captured_not_raised`: monkeypatch `_safe_import` (or inject a
  deliberately broken temp module on a patched `__path__`) so one module raises; assert it
  lands in `failures` and the walk still returns the good records.
- `test_signature_and_inputs_extracted`: violin record `signature` contains `"data"`,
  `inputs` excludes `"ax"`.

### Task 5 — `catalog_build/fingerprint.py`: BLOCKING style gate + best-effort thumbnail

Files: `yplot2/catalog_build/fingerprint.py`, `tests/test_catalog_fingerprint.py`.

```python
@dataclass(frozen=True)
class StyleViolation:
    """One artist-property mismatch found on a demo figure."""
    axes_index: int
    prop: str            # e.g. "spine_linewidth", "tick_font_family"
    expected: str
    actual: str

def check_house_style(fig: "Figure") -> list[StyleViolation]:
    """Assert house chrome on every axes of a rendered demo figure.

    Artist-property checks ONLY (never a pixel hash): each visible spine's
    linewidth == cfg.axis_linewidth; every tick label's font family == the
    resolved house font (Arimo); tick-label fontsize == cfg tick fontsize.
    Returns an empty list when the figure is house-styled.
    """

def render_thumbnail(fig: "Figure", path: str) -> bool:
    """Best-effort thumbnail PNG. Returns True on success, False on any failure
    (never raises — a failed thumbnail is cosmetic, not a gate)."""

def fingerprint_capsule(rec: CapsuleRecord) -> "FingerprintResult":
    """Import rec's module, run its demo, style-check it, and (best-effort)
    write a thumbnail. Returns a result carrying violations + thumbnail status.
    A demo that raises yields a result with a populated `error` (blocking)."""
```

Details:
- Read expected values via `from yplot2.config import get_config` and
  `from yplot2.style import _resolve_font_family` — do NOT hard-code `0.75`/`"Arimo"`.
- `check_house_style` iterates `fig.axes`; for each, checks visible spines'
  `get_linewidth()`, and `get_xticklabels()/get_yticklabels()` `get_fontname()` +
  `get_fontsize()`. Use a small tolerance (`1e-6`) on floats. Skip empty/label-less axes
  (a demo axes with no ticks is fine — only assert on ticks that exist).
- `fingerprint.py` imports matplotlib (fine — not seaborn). Running a demo may pull seaborn
  LAZILY; guard with `try/except ImportError` → the result records "seaborn missing" as a
  SKIP (not a violation) so a `[stats]`-less environment does not falsely fail the gate.
  (A cataloged capsule whose demo needs seaborn is only fingerprinted in the `[stats]` build
  step — see open questions on whether missing-seaborn is a skip or a hard fail in CI.)
- `render_thumbnail` wraps `fig.savefig(path, dpi=72)` in try/except → bool.

`FingerprintResult` dataclass: `name: str`, `violations: tuple[StyleViolation, ...]`,
`thumbnail_ok: bool`, `error: str` (demo crash message; `""` if it ran), `skipped: bool`
(seaborn absent). `blocking_failed` property = `bool(error) or bool(violations)` and NOT
`skipped`.

Acceptance tests (`tests/test_catalog_fingerprint.py`):
- `test_styled_demo_passes`: build the five statistical records (or a fixture), run
  `fingerprint_capsule`; `pytest.importorskip("seaborn")`; assert `violations == ()` and
  `error == ""` for each renderable demo (the demos call `finish` → must be house-styled).
- `test_unstyled_demo_flagged` (the BLOCKING-gate test): craft a local demo returning a bare
  `plt.subplots()` axes with a plotted line and default matplotlib spines/fonts; call
  `check_house_style(fig)` → assert it returns a NON-EMPTY list naming `spine_linewidth`
  and/or `tick_font_family` (default spine 0.8 ≠ 0.75, DejaVu ≠ Arimo).
- `test_thumbnail_failure_is_nonblocking`: monkeypatch `fig.savefig` to raise →
  `render_thumbnail` returns `False`, no exception; and a `FingerprintResult` with a failed
  thumbnail but no violations has `blocking_failed is False`.
- `test_demo_crash_is_blocking`: a demo that raises → result `error` populated,
  `blocking_failed is True`.
- `test_missing_seaborn_is_skip_not_fail`: force `ImportError` from the demo → `skipped is
  True`, `blocking_failed is False`.

### Task 6 — `catalog_build/build.py`: orchestrator + CLI (json ALWAYS written)

Files: `yplot2/catalog_build/build.py`, `tests/test_catalog_build.py`.

```python
@dataclass(frozen=True)
class BuildReport:
    """Summary of a catalog build."""
    n_capsules: int
    import_failures: tuple[ImportFailure, ...]
    blocking_failures: tuple[str, ...]     # capsule names that failed the style gate
    catalog_json_path: str
    catalog_md_path: str

def build_catalog(out_dir: str, *, strict: bool = True) -> BuildReport:
    """Collect capsules, ALWAYS write catalog.json (static), then run the
    fingerprint gate + best-effort thumbnails and write CATALOG.md.

    Order guarantees catalog.json exists even if every demo fails. When strict
    is True, a blocking fingerprint failure makes `main` exit non-zero; the
    json + md are still written first.
    """

def _write_catalog_json(records, out_dir) -> str: ...
def _write_catalog_md(records, results, out_dir) -> str: ...   # grouped by category
def main(argv: list[str] | None = None) -> int:
    """CLI: python -m yplot2.catalog_build.build --out-dir catalog [--no-strict].
    Returns 1 if any blocking fingerprint failure occurred, else 0."""
```

Critical ordering (the robustness decision): `build_catalog` runs `collect_records()` →
writes `catalog.json` IMMEDIATELY → THEN loops `fingerprint_capsule` over records with
`has_demo` → writes `CATALOG.md` (embedding thumbnails that succeeded, skipping the rest).
`catalog.json` is never gated on rendering.

`_write_catalog_md`: group records by `category`; per capsule emit a heading with
`import_path`, `tags`, `data_shape`, `summary`, and an `![](thumb)` line only if the
thumbnail exists. Regenerated every build so it can't drift.

Thumbnails written under `<out_dir>/thumbs/<name>.png`.

`catalog_build/__init__.py` re-exports `build_catalog` and `BuildReport`; keep it light (no
matplotlib import at package import — import `build` lazily or accept that importing the
subpackage pulls matplotlib but NOT seaborn; add a test that importing `yplot2.catalog_build`
does not import seaborn).

Acceptance tests (`tests/test_catalog_build.py`):
- `test_json_written_even_when_demo_fails` (static-index-survives-render-failure): monkeypatch
  `fingerprint_capsule` to raise/return a blocking error for every capsule; call
  `build_catalog(tmp, strict=False)`; assert `catalog.json` EXISTS, parses, has
  `schema_version==1`, and lists ALL five statistical capsules. This is the headline test.
- `test_strict_reports_blocking_failure`: with a monkeypatched blocking result,
  `main(["--out-dir", tmp])` returns `1`; without, returns `0`.
- `test_catalog_md_generated_and_grouped`: `CATALOG.md` exists, contains a `statistical`
  section and each capsule's `import_path`.
- `test_full_build_smoke` (guarded `pytest.importorskip("seaborn")`): real
  `build_catalog(tmp)` → json + md + ≥1 thumbnail png written; report `blocking_failures`
  empty (the five demos are house-styled).
- `test_catalog_build_import_is_seaborn_free`: subprocess with `sys.modules['seaborn']=None`,
  `import yplot2.catalog_build` → succeeds.

### Task 7 — Wire into `figures/build.sh`, per-paper lockfile, and CI

Files: `figures/build.sh` (new, template), `figures/requirements.lock.template` (new, text),
`.github/workflows/catalog.yml` (new).

`figures/build.sh` (documented template, not Python — a reviewer reads it as the CONVENTION):
```bash
#!/usr/bin/env bash
# One-command regen for a paper's figures + the plot catalog.
# Usage: bash figures/build.sh
set -euo pipefail
# 1. Regenerate every figure (scripts AND notebooks, clean kernel):
python -m yplot2.build figures
# 2. Regenerate the plot catalog (static json + blocking style gate + gallery):
python -m yplot2.catalog_build.build --out-dir catalog
```
Add header comments: "Pin the environment first — see requirements.lock.template" and
"'Raw data' means an analysis-ready dataframe; the fastq/BAM pipeline is OUT of scope."

`figures/requirements.lock.template` (text): recommend per-paper pinning of `yplot2==`,
`matplotlib==`, `seaborn==`, `nbconvert==` (comment that exact versions are filled in with
`pip freeze` per paper).

`.github/workflows/catalog.yml`: on push/PR, `pip install -e .[stats,dev]` + nbconvert,
then `python -m yplot2.catalog_build.build --out-dir catalog` (the fingerprint gate is
BLOCKING → CI fails on an unstyled cataloged demo; thumbnails best-effort). Keep it a
single minimal job. Do NOT commit generated `catalog/` back in CI (just gate).

Acceptance: `bash -n figures/build.sh` parses; the workflow YAML is valid
(`python -c "import yaml,sys; yaml.safe_load(open('.github/workflows/catalog.yml'))"` — but
yaml is a dev-only check; if PyYAML absent, just eyeball). No unit test required for these
text artifacts beyond shellcheck-style parse.

### Task 8 — Housekeeping: delete the on-disk build shadow + pyproject wiring

Files: delete `build/`; edit `pyproject.toml`.

- `rm -rf build/` (gitignored + untracked — safe; documented in the strategy as a required
  housekeeping step so the collector cannot ever see it).
- `pyproject.toml`: ensure NEW modules are measured by coverage — remove them from any
  `[tool.coverage.report] omit` and confirm `--cov=yplot2` includes them; keep the ≥90%
  target for new code. Add `nbconvert` to a new optional extra if you want notebook regen
  installable (e.g. `repro = ["nbconvert>=7"]`) — OR leave nbconvert to the per-paper lock
  (see open questions). Add ruff per-file-ignores only if genuinely needed (prefer none).

Acceptance: full `pytest` run is green (186 existing + new), `mypy` clean on `yplot2`,
`ruff check` clean, coverage ≥90% on the new modules.

---

## Risks / uncertainties

- **PNG/PDF metadata backend behavior** — matplotlib PNG writes dict keys as tEXt (no date);
  PDF stamps `CreationDate`/`ModDate` from wall-clock unless suppressed. The plan suppresses
  them via `metadata={"CreationDate": None, "ModDate": None}`; verify on the pinned mpl
  3.10.x. If a backend rejects arbitrary keys, fall back to a single `"Comment"`/`"Subject"`
  key holding the whole provenance string.
- **Fingerprint on tick-less demo axes** — some demos (heatmap/hexbin) may hide ticks or use
  a colorbar axes; `check_house_style` must skip axes with no tick labels rather than
  false-fail. The tests must cover a colorbar/`imshow` demo.
- **`inspect.getsourcefile` for installed (`pip install .`, non-editable) packages** returns
  a site-packages path; repo-relative conversion is best-effort. Store the absolute path if
  relpath fails; note this is acceptable (source_path is informational).
- **Coverage of subprocess/CLI glue** in `build.py` — keep the subprocess calls in thin
  helpers and unit-test the pure parts; a few `# pragma: no cover` lines are acceptable to
  hold ≥90%.

---

## Open design questions (resolve before plan-critic)

1. **`yp.save` PDF determinism** — confirm `metadata={"CreationDate": None, "ModDate":
   None}` fully suppresses wall-clock on pinned mpl 3.10.x, or do we set a FIXED epoch
   (e.g. `SOURCE_DATE_EPOCH`-style) instead? (Plan assumes `None` suppresses.)
2. **Source path form** — store `source` as caller-passed (recommend repo-relative) or force
   `os.path.relpath` against the repo root? Absolute paths hurt cross-machine byte-identity
   but the round-trip/determinism tests use same-machine. (Plan: store as given; recommend
   relative in docs.)
3. **Where do `catalog.json` + `CATALOG.md` live?** Plan writes them to a CLI `--out-dir`
   (default `catalog/`). Strategy hints at a "committed static namespace file `__init__`
   reads at runtime" — do we commit `catalog.json` into `yplot2/` and have `__init__` read
   it now, or defer that runtime-read to Phase 4? (Plan defers the runtime-read; only
   generates the files.)
4. **Notebook execution tool** — `jupyter nbconvert --execute` (recommended, fewer deps) vs
   `papermill` (parametrizable)? And do we add an optional `repro=["nbconvert"]` extra or
   push it into the per-paper lockfile only? (Plan: nbconvert, extra optional.)
5. **Is `python -m yplot2.build` worth it vs a plain `build.sh` loop?** Plan includes the
   module because it is unit-testable and cross-platform; confirm you want the extra module.
6. **Missing-seaborn in the CI fingerprint gate** — is a seaborn-backed demo that cannot run
   (no `[stats]`) a SKIP (plan default, so a base-install CI stays green) or a HARD FAIL
   (forcing `[stats]` in every catalog CI)? Plan treats it as a skip; CI installs `[stats]`
   so the gate actually runs.
7. **`differentiator=` dup-lint / `status` field** — the strategy's capsule-catalog section
   mentions a dup-lint and active/deprecated status. Those read as Phase-4 curation. Confirm
   they are OUT of Phase 3 (plan excludes them).
