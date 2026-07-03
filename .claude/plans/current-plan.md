# Phase 4 Plan — "anti-fork lint" (`python -m yplot2.lint`)

> Supersedes the Phase 3 plan (Phase 3 committed as `6ce53d6`). This is the ONLY
> remaining code deliverable of Phase 4. The `~/.claude` skill is already written
> (separate). The compat shim and paper migration are **out of scope** — do not
> plan or write them.

## Goal
Ship a pure-stdlib lint that makes the per-paper `plotting.py` habit fail: it flags
figure code that reinvents what yplot2 already provides, pointing each finding at the
yplot2 replacement. Runs as `python -m yplot2.lint <paths...>`; exits nonzero when any
ERROR-level finding is present, so it can be wired as an optional pre-commit / CI check
in a paper repo. The #1 design goal is a **low false-positive rate** — a noisy lint gets
disabled. When in doubt, do NOT flag.

## Design resolutions (Q1–Q5 — AUTHORITATIVE; override conflicting task text below)

- **Q1 severity (low-friction adoption):** ONLY **YP001 = ERROR** (the one unambiguous
  fork signal — a locally-defined house-style function). **YP002, YP003, YP004, YP005 =
  WARNING.** `main` exits nonzero only when an ERROR-level finding survives filtering, so
  by default only YP001 blocks. Document that severity is configurable (a `--error CODE`
  flag to promote a rule, or note it for a future config). Rationale: a lint that ERRORs on
  every `figsize=`/`savefig` gets disabled; nudge broadly, block only on the clearest fork.
- **Q2 ignore syntax:** keep `# yplot2: ignore` and `# yplot2: ignore=YP002,YP003`
  (comma-separated). Do NOT use `# noqa:` (collides with ruff's own noqa handling).
- **Q3 raw seaborn (YP006): OPT-IN ONLY.** YP006 is NOT in the default rule set; it fires
  only when explicitly requested via `--select YP006`. yplot2 EMBRACES raw seaborn drawn
  into a panel followed by `yp.finish(ax)` (the escape hatch), so flagging `sns.violinplot`
  by default is both noisy and contrary to the design. Keep the rule defined + tested, but
  excluded from the default set.
- **Q4 YP001 curated names:** `publication_style_ax`, `format_small_plot`, `publication_style`,
  `publication_scatter`, `publication_line`. EXACT-name match only (never substring/heuristic —
  that is the top false-positive risk).
- **Q5 directory excludes:** `check_paths` walks `**/*.py` but skips these dir names:
  `__pycache__`, `.git`, `.venv`, `venv`, `build`, `dist`, `.eggs`, `.ipynb_checkpoints`,
  `node_modules`, and any `*.egg-info`. Do not attempt to honor `.gitignore`.

---

## Non-negotiable constraints
- `yplot2/lint.py`'s OWN module body is **pure stdlib only**: `ast`, `re`, `sys`,
  `pathlib`, `dataclasses`, `enum`, `argparse`. NO import of matplotlib / seaborn /
  pandas / numpy and no import of sibling yplot2 modules IN lint.py itself.
  NOTE (plan-critic): `import yplot2.lint` still executes `yplot2/__init__.py`, which
  loads matplotlib — so lint is NOT matplotlib-free at runtime, and that is fine. The
  meaningful, testable guarantee is **seaborn-free** (already enforced by
  `tests/test_no_seaborn_import.py`). Do NOT write a matplotlib-free import test; the
  step-1 check is seaborn blocked via `sys.modules['seaborn']=None` then import succeeds.
- Do NOT regress the existing 285 tests. Keep the diff to Phase-4 lint files only:
  `yplot2/lint.py`, `tests/test_lint.py`, a short README section, and (if needed) one
  line in `[tool.ruff.lint.per-file-ignores]` / `[tool.coverage.report]`.
- Do NOT run repo-wide `ruff format` or touch legacy files. Run ruff/mypy only on the
  two new files.
- The lint must NOT flag yplot2's own library code or correct yplot2 usage (see
  acceptance tests). It is never run against `yplot2/` itself in CI.

## Ground truth (the habit we are killing)
Derived from the two real per-paper modules:
- `~/Dropbox/papers/2025_dms_vs_tmo_paper/dms_vs_tmo_paper/plotting.py`
- `~/Dropbox/papers/2025-dms-3d-features/dms_3d_features/plotting.py`

What is actually there (drives the rules):
- Locally DEFINED house-style functions: `def publication_style_ax(...)`,
  `def format_small_plot(...)`, plus `publication_scatter`, `publication_line`.
- Inline `figsize=(2.0, 1.5)` (and `figsize=(10, 5)`, `(20, 4)`) literals passed to
  `plt.subplots(...)` all over the figure functions, often with `dpi=200`.
- `plt.subplots_adjust(left=0.3, bottom=0.21, top=0.98)` inside `format_small_plot`.
- Palettes built from **named colors** (`{"A": "red", ...}`) and **RGBA tuples**
  (`{"TMO": (0.70, 0.0, 0.0, 1.0)}`), passed to seaborn via a **variable** `palette=`.
- Raw `sns.violinplot(...)` / `sns.boxplot(...)` / `sns.stripplot(...)` calls.

IMPORTANT design fact confirmed by grep: these two files contain **no `#hex` literals**,
pass `palette=` a *variable* (not an inline dict), and contain **no `savefig`**.
Therefore the hex-palette rule (YP005) and the savefig rule (YP004) are *preventive*
(they guard against the general anti-pattern) and will legitimately NOT fire on these
two files. The rules that actually fire on the real files are **YP001, YP002, YP003**.
Do not "fix" YP004/YP005 to fire on these files — that would raise false positives.

## Design

### Module: `yplot2/lint.py` (~240 lines, target <300)
Pure stdlib. Public surface:

```python
from dataclasses import dataclass
from enum import Enum

class Level(str, Enum):
    """Severity of a lint finding."""
    ERROR = "error"      # exit nonzero
    WARNING = "warning"  # reported, does not fail the run

@dataclass(frozen=True)
class Finding:
    """One anti-pattern occurrence in a source file."""
    path: str      # file path as given/resolved
    line: int      # 1-based line number of the triggering node
    code: str      # e.g. "YP002"
    message: str   # human message incl. the yplot2 replacement
    level: Level

def check_source(source: str, path: str) -> list[Finding]:
    """Parse *source* and return findings for *path* (ignore comments applied)."""

def check_file(path: str | Path) -> list[Finding]:
    """Read and lint a single .py file. Syntax errors -> single YP000 WARNING."""

def check_paths(paths: Iterable[str | Path]) -> list[Finding]:
    """Lint files and/or directories (dirs walked for **/*.py). Sorted output."""

def main(argv: list[str] | None = None) -> int:
    """CLI entry: `python -m yplot2.lint [--select C,..] [--ignore C,..] <paths...>`.
    Returns 1 if any ERROR-level finding survives filtering, else 0."""
```

Internal structure (each helper ≤30 lines, complexity ≤10):
- Module-level `RULES: dict[str, tuple[Level, str]]` mapping code -> (level, message).
  Single source of truth for severity + message text.
- Module-level `_HOUSE_STYLE_FUNCS: frozenset[str]` = the curated house-style function
  names (see YP001). Curated names only — do NOT flag by heuristic/substring, that is
  the main false-positive risk.
- `_PLT_FIGURE_CALLERS: frozenset[str]` = `{"plt.subplots", "plt.figure",
  "plt.subplot", "pyplot.subplots", "pyplot.figure"}` — dotted callee strings that YP002
  restricts itself to.
- `_HEX_RE = re.compile(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?(?:[0-9a-fA-F]{2})?$")`.
- `class _RuleVisitor(ast.NodeVisitor)`: holds `self.findings: list[Finding]` and
  `self.path`. Methods: `visit_FunctionDef` / `visit_AsyncFunctionDef` (YP001),
  `visit_Call` (YP002, YP003, YP004, YP005-on-`palette=`, YP006), `visit_Dict` (YP005
  standalone dict literals). Each `visit_*` appends via a small `self._add(node, code)`
  helper that looks up level+message from `RULES` and uses `node.lineno`. Always call
  `self.generic_visit(node)` to keep descending.
- `_dotted_name(node: ast.expr) -> str | None`: resolve `ast.Attribute`/`ast.Name`
  chains to a dotted string (`plt.subplots`, `fig.savefig`, `sns.violinplot`) so rules
  match on the tail (`.savefig`, `.subplots_adjust`) or full dotted name. Returns None
  for non-name callees.
- `_is_hex_palette_dict(node: ast.Dict) -> bool`: True iff ≥2 values are string
  constants matching `_HEX_RE`. (≥2 avoids flagging a lone `"#000"` used as one color.)
- Ignore handling: `_apply_ignores(findings, source) -> list[Finding]` splits `source`
  into lines once and drops any finding whose line carries the ignore marker.
- Selection: `_filter_codes(findings, select, ignore) -> list[Finding]`.
- Formatting: `_format(finding) -> str` -> `"{path}:{line}: {CODE} [{level}] {message}"`.
- CLI: `_parse_args(argv)` (plain, no argparse subcommands needed — argparse is stdlib
  and fine) returning `(paths, select, ignore)`; `main` orchestrates and prints.

### The rule set (codes, triggers, level, message)

| Code  | Level   | AST trigger | Message (points to replacement) |
|-------|---------|-------------|---------------------------------|
| YP001 | ERROR   | `FunctionDef`/`AsyncFunctionDef` whose `name` is in `_HOUSE_STYLE_FUNCS` | `defines house-style function '{name}()' — use yp.finish(ax) / yp.apply_style() instead` |
| YP002 | WARNING | `Call` whose dotted callee is in `_PLT_FIGURE_CALLERS` AND has a `figsize=` keyword whose value is a `Tuple`/`List` literal | `inline figsize on plt.subplots/plt.figure — use yp.subplots(subplotsize=...) or yp.figure7()` |
| YP003 | WARNING | `Call` whose dotted callee ends in `.subplots_adjust` (or bare `subplots_adjust`) | `manual subplots_adjust — use yp absolute layout (yp.subplots / yp.figure7)` |
| YP004 | WARNING | `Call` whose dotted callee ends in `.savefig` (`plt.savefig`, `fig.savefig`) | `raw savefig loses provenance — use yp.save(fig, path, source=...)` |
| YP005 | WARNING | `Dict` literal with ≥2 hex-string values, OR a `palette=` keyword whose value is such a `Dict` | `hardcoded hex color palette — use yp.palette()` |
| YP006 | WARNING | `Call` whose dotted callee is `sns.violinplot` / `sns.boxplot` / `sns.stripplot` | `raw seaborn plot — prefer yp.boxplot()/yp wrappers, then yp.finish(ax)` |

`_HOUSE_STYLE_FUNCS` (YP001, curated exact names): `publication_style_ax`,
`format_small_plot`, `publication_style`, `publication_scatter`, `publication_line`.
Curated-name matching only — no substring/prefix heuristics.

Severity rationale (per authoritative Q1 — low-friction adoption):
- **ERROR** (fails the run): **YP001 only** — a locally-defined house-style function is
  the one unambiguous fork signal.
- **WARNING** (reported, exit 0): YP002, YP003, YP004, YP005 — real nudges, but common
  enough in legit exploratory code that blocking on them gets the lint disabled.
- **Opt-in only (not in default set):** YP006 — fires solely under `--select YP006`.
- `RULES` maps YP002/YP003/YP004/YP005 → WARNING and YP001 → ERROR (single source of truth).
- Define `_OPT_IN = frozenset({"YP006"})`. `check_source` returns RAW findings for all rules
  (incl. YP006). Default exclusion of opt-in codes happens in `main`/`_filter_codes`: a code
  in `_OPT_IN` is dropped UNLESS it appears in an explicit `--select`. `main` exits nonzero
  only if a surviving finding is ERROR-level (i.e. only YP001 by default).

False-positive guards baked into triggers:
- YP002 is restricted to `plt.`/`pyplot.` callers, so `yp.subplots(subplotsize=(2,1.5))`
  (different kwarg) and `yp.figure7(...)` never match; a `figsize=` passed to any yplot2
  function never matches.
- YP001 matches only the curated name set, never arbitrary `def apply_style` in yplot2's
  own source (and the lint is never run on `yplot2/`).
- YP005 requires ≥2 hex string values, so the named-color/RGBA-tuple palettes in the real
  files do not trip it, and a single stray hex constant does not either.
- YP006 is the lowest-confidence rule; document that teams commonly `--ignore YP006`.

### Ignore mechanism
1. Inline comment on the triggering line:
   - `# yplot2: ignore` suppresses ALL codes on that line.
   - `# yplot2: ignore=YP002` (comma-separated codes) suppresses only those codes.
   Implemented in `_apply_ignores` via a small regex on the finding's source line
   (`re.search(r"#\s*yplot2:\s*ignore(=([A-Z0-9,]+))?", line)`); no tokenize needed.
2. CLI `--select YP001,YP002` (allowlist) and `--ignore YP003,YP006` (denylist) applied
   in `_filter_codes`. `--select` given -> keep only those codes; `--ignore` removes
   codes; if both given, `--select` first then `--ignore`.

### CLI behavior
- `python -m yplot2.lint <paths...>`: prints one `_format(...)` line per surviving
  finding (sorted by path, then line, then code); prints nothing on a clean run.
- Exit code 1 iff any surviving finding has `level == Level.ERROR`; else 0. Warnings
  alone do not fail the run.
- No paths given -> print usage to stderr, return 1 (mirror `build.py`).
- A file that fails to parse -> one `YP000` WARNING (`syntax error: {msg}`); never crash.
- `if __name__ == "__main__": raise SystemExit(main())` (mirror `build.py`).

## Style notes
- Follows `~/.claude/standards/python-style.md`: full type hints + Args/Returns/Raises
  docstrings on every function; ≤4 positional params (use keyword-only where natural);
  early returns; ≤3 nesting depth; complexity ≤10.
- Likely-longest functions to watch (keep ≤30 lines / complexity ≤10 by extracting
  helpers): `visit_Call` (four rules) — split per-rule logic into
  `_check_figsize(call)`, `_check_savefig(call)`, `_check_subplots_adjust(call)`,
  `_check_seaborn(call)`, `_check_palette_kw(call)` each returning `str | None` code, so
  `visit_Call` is a short dispatch loop. `main` stays a thin orchestrator.
- Module size: ~240 lines projected. RISK: with six rules + CLI + docstrings it may
  approach 300. If it exceeds 300, extract the CLI (`_parse_args`, `_format`, `main`)
  into the same file is still fine per the "length is a smell not a limit" guidance —
  do NOT split into a second module unless it genuinely passes 300 and reads better
  split; if so, move the rule visitor + `check_*` into `lint.py` and keep CLI there,
  or factor pure helpers into a private `_lint_ast.py`. Prefer one module.

## Files
| File | Action | Lines Est. | What |
|------|--------|------------|------|
| `yplot2/lint.py` | create | ~240 | Findings, rules, AST visitor, ignore/select, CLI |
| `tests/test_lint.py` | create | ~200 | Per-rule + ignore + select + CLI + no-false-positive tests |
| `README.md` | edit | +~30 | "Anti-fork lint" section: usage + pre-commit + CI snippets |
| `pyproject.toml` | edit (maybe) | +~2 | Only if coverage/ruff config needs the new files acknowledged |

## Steps (ordered, each independently verifiable)

1. [ ] **Skeleton + data model.** Add `Level`, `Finding`, `RULES`,
   `_HOUSE_STYLE_FUNCS`, `_PLT_FIGURE_CALLERS`, `_HEX_RE`, and stub `check_source`/
   `check_file`/`check_paths`/`main`. No rule logic yet.
   - Verify: `python -c "import yplot2.lint"` works with seaborn blocked
     (`python -c "import sys; sys.modules['seaborn']=None; import yplot2.lint"`).
   - Verify: mypy clean on `yplot2/lint.py`.

2. [ ] **AST helpers.** Implement `_dotted_name`, `_is_hex_palette_dict`, and the
   `_RuleVisitor` scaffold with `_add` + `generic_visit`.
   - Test: `test_dotted_name_resolves_plt_subplots`, `test_dotted_name_none_for_call`.

3. [ ] **YP001 — house-style function definitions.**
   `visit_FunctionDef`/`visit_AsyncFunctionDef`.
   - Test: `test_yp001_flags_publication_style_ax`,
     `test_yp001_flags_format_small_plot`, `test_yp001_ignores_ordinary_def`.

4. [ ] **YP002 — inline figsize on plt callers.** `_check_figsize`.
   - Test: `test_yp002_flags_plt_subplots_figsize`,
     `test_yp002_not_flag_yp_subplots_subplotsize` (correct usage, no finding),
     `test_yp002_not_flag_figure7`.

5. [ ] **YP003/YP004/YP006 — attribute-call rules.** `_check_subplots_adjust`,
   `_check_savefig`, `_check_seaborn`; wire the `visit_Call` dispatch loop.
   - Test: `test_yp003_flags_subplots_adjust` (WARNING), `test_yp004_flags_savefig`
     (WARNING level), `test_yp006_flags_sns_violinplot` — YP006 is opt-in, so this test
     must enable it (call `check_source` then filter with `select={"YP006"}`, or assert
     YP006 is in the RAW `check_source` output). YP006 must NOT appear in a default `main` run.

6. [ ] **YP005 — hex palettes.** `_check_palette_kw` + `visit_Dict`.
   - Test: `test_yp005_flags_hex_dict`, `test_yp005_not_flag_named_color_dict`
     (the real-file pattern `{"A": "red"}` must NOT fire),
     `test_yp005_not_flag_single_hex`.

7. [ ] **Ignore + selection.** `_apply_ignores`, `_filter_codes`; wire into
   `check_source`.
   - Test: `test_ignore_all_on_line`, `test_ignore_specific_code`,
     `test_select_keeps_only_listed`, `test_ignore_removes_code`.

8. [ ] **File / path plumbing + syntax error handling.** `check_file`, `check_paths`
   (dir walk `**/*.py`, sorted), YP000 on `SyntaxError`. `check_paths` MUST skip the Q5
   exclude dirs: `__pycache__`, `.git`, `.venv`, `venv`, `build`, `dist`, `.eggs`,
   `.ipynb_checkpoints`, `node_modules`, and any `*.egg-info`.
   - Test: `test_check_file_reads_source` (tmp_path),
     `test_check_paths_walks_directory` (tmp_path with nested .py),
     `test_check_paths_skips_excluded_dirs` (a .py under `build/` and `.venv/` is NOT linted),
     `test_syntax_error_yields_yp000_warning`.

9. [ ] **CLI `main`.** `_parse_args`, `_format`, exit-code logic, usage message,
   `__main__` guard. Exits nonzero ONLY on a surviving ERROR (YP001 by default).
   - Test: `test_main_exit_1_on_error` (source with **YP001** — the only default ERROR),
     `test_main_exit_0_on_warning_only` (source with only YP002/YP003 → exit 0),
     `test_main_yp006_absent_by_default` and `test_main_yp006_present_with_select`,
     `test_main_no_paths_usage_returns_1`,
     `test_main_clean_source_returns_0`.

10. [ ] **Integration acceptance tests.** One "bad" plotting.py source string built from
    the real anti-patterns (defines `publication_style_ax` + `format_small_plot`, calls
    `plt.subplots(figsize=(2.0,1.5), dpi=200)`, calls `plt.subplots_adjust(...)`, calls
    `sns.violinplot(...)`) → a DEFAULT `check_source` asserts YP001×2, YP002, YP003 present
    and **YP006 ABSENT** (opt-in); a second assert with `select={"YP006"}` shows YP006 fires.
    One "good" yplot2 script string (`import yplot2 as yp; fig, ax = yp.subplots(subplotsize=(2,1.5));
    yp.finish(ax); yp.save(fig, "f.png", source=__file__)`) → asserts ZERO findings.
    - Test: `test_bad_plotting_triggers_expected_codes` (YP006 absent by default),
      `test_yp006_fires_only_with_select`,
      `test_good_yplot2_script_is_clean`.

11. [ ] **Docs snippet in README.md.** Add an "Anti-fork lint" section:
    `python -m yplot2.lint <paths>`, the `--select/--ignore` and `# yplot2: ignore`
    mechanisms, a `.pre-commit-config.yaml` hook snippet, and a GitHub Actions step.
    Explicitly note it is for **paper repos**, not enforced on yplot2 itself, and that
    YP006 (raw seaborn) is OPT-IN — add `--select YP001,YP002,YP003,YP004,YP005,YP006` to
    also flag raw seaborn; the default set intentionally allows raw seaborn + `yp.finish`.
    - Verify: snippets are copy-paste correct (hook `entry: python -m yplot2.lint`,
      `language: system`, `types: [python]`).

12. [ ] **Toolchain gate (new files only).**
    - `ruff check yplot2/lint.py tests/test_lint.py` (and `ruff format` on just these two).
    - `mypy yplot2/lint.py --ignore-missing-imports`.
    - `pytest tests/test_lint.py --cov=yplot2/lint.py --cov-report=term-missing` → ≥90%.
    - `pytest` (full suite) → still 285 passing + the new tests; no regressions.
    - Confirm `yplot2/lint.py` is NOT added to the coverage `omit` list (it must count).

## Ready-to-use snippets to include in README (for the plan's docs step)

Pre-commit (`.pre-commit-config.yaml` in a paper repo):
```yaml
-   repo: local
    hooks:
    -   id: yplot2-anti-fork
        name: yplot2 anti-fork lint
        entry: python -m yplot2.lint
        language: system
        types: [python]
        # optional: keep raw seaborn allowed
        args: ["--ignore", "YP006"]
```

CI (GitHub Actions step):
```yaml
      - name: yplot2 anti-fork lint
        run: python -m yplot2.lint src/ figures/
```

## Test mocking / fixtures
- No mocking of matplotlib/seaborn — everything is exercised through `check_source`
  with inline source strings, so tests need zero heavy deps and run fast.
- `tmp_path` only for `check_file` / `check_paths` directory-walk tests.
- Do NOT create fixture `.py` files under a collected test path (they would be linted by
  ruff/pytest); use inline triple-quoted source instead.

## Reviewer notes
- Confirm `yplot2/lint.py` imports nothing heavy (grep the import block; only stdlib).
- Confirm running the lint on `yplot2/` source is NOT part of CI and that the acceptance
  "good script" test proves correct yplot2 usage yields zero findings.
- Confirm ERROR vs WARNING mapping matches the table and that exit code is driven only by
  ERROR-level survivors after ignore/select filtering.
- Confirm diff is limited to the four files above; no legacy files reformatted.

## Open questions (flag for the user before/while coding)
1. **ERROR vs WARNING split** — plan sets YP001/YP002/YP004 = ERROR (block) and
   YP003/YP005/YP006 = WARNING. Is YP003 (`subplots_adjust`) strong enough to be an
   ERROR, or is WARNING right? (Kept WARNING to avoid blocking legit manual layout.)
2. **Ignore syntax** — plan uses `# yplot2: ignore` / `# yplot2: ignore=YP002`. Prefer
   the ruff-style `# noqa: YP002` spelling instead, for muscle-memory familiarity?
3. **YP006 (raw seaborn)** — included as an off-by-recommendation WARNING (docs suggest
   `--ignore YP006`). Keep it in the default rule set, or make it opt-in via `--select`
   only (i.e. excluded unless explicitly requested)?
4. **YP001 name list** — include the thin wrappers `publication_scatter` /
   `publication_line` (they reinvent `yp.scatter`/`yp.line`, not styling), or restrict
   YP001 to the pure styling names and leave the wrappers alone?
5. **Directory recursion** — `check_paths` walks dirs for `**/*.py`. Should it honor a
   `.gitignore` / skip `build/`, `.venv/`, `__pycache__`? (Plan currently skips only
   `__pycache__`; add more excludes if paper repos need it.)
