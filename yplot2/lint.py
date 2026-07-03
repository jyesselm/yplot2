"""
Anti-fork lint for paper repos that use yplot2.

Flags Python source patterns that re-invent yplot2 functionality, pointing
each finding at the yplot2 replacement. Designed for **low false-positives**;
when in doubt, it does not flag.

Usage::

    python -m yplot2.lint <paths...>
    python -m yplot2.lint --select YP001,YP002 src/
    python -m yplot2.lint --ignore YP003 figures/

Exit code 1 only when an ERROR-level finding survives filtering (by default
only YP001 is ERROR-level). Warnings alone exit 0.
"""

import argparse
import ast
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Public data model
# ---------------------------------------------------------------------------


class Level(str, Enum):
    """Severity of a lint finding."""

    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Finding:
    """One anti-pattern occurrence in a source file."""

    path: str
    line: int
    end_line: int  # inclusive; used for multi-line ignore suppression
    code: str
    message: str
    level: Level


# ---------------------------------------------------------------------------
# Rule table and constants
# ---------------------------------------------------------------------------

RULES: dict[str, tuple[Level, str]] = {
    "YP000": (
        Level.WARNING,
        "syntax error: {msg}",
    ),
    "YP001": (
        Level.ERROR,
        "defines house-style function '{name}()' — use yp.finish(ax) / yp.apply_style() instead",
    ),
    "YP002": (
        Level.WARNING,
        "inline figsize on plt.subplots/plt.figure — use yp.subplots(subplotsize=...) or yp.figure7()",
    ),
    "YP003": (
        Level.WARNING,
        "manual subplots_adjust — use yp absolute layout (yp.subplots / yp.figure7)",
    ),
    "YP004": (
        Level.WARNING,
        "raw savefig loses provenance — use yp.save(fig, path, source=...)",
    ),
    "YP005": (
        Level.WARNING,
        "hardcoded hex color palette — use yp.palette()",
    ),
    "YP006": (
        Level.WARNING,
        "raw seaborn plot — prefer yp.boxplot()/yp wrappers, then yp.finish(ax)",
    ),
}

# YP001 — exact names only; no substring/prefix heuristics (main FP risk).
_HOUSE_STYLE_FUNCS: frozenset[str] = frozenset(
    {
        "publication_style_ax",
        "format_small_plot",
        "publication_style",
        "publication_scatter",
        "publication_line",
    }
)

# YP002 — only flag figsize= on these callers (not on yp.* or df.plot etc.)
# Matches the standard plt./pyplot. aliases; unusual aliases are intentionally
# not matched to keep false-positives near zero.
_PLT_FIGURE_CALLERS: frozenset[str] = frozenset(
    {
        "plt.subplots",
        "plt.figure",
        "plt.subplot",
        "pyplot.subplots",
        "pyplot.figure",
    }
)

# YP006 — opt-in only; excluded from default run unless explicitly selected.
_OPT_IN: frozenset[str] = frozenset({"YP006"})

# YP005 — hex color pattern.
_HEX_RE = re.compile(r"^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?(?:[0-9a-fA-F]{2})?$")

# Directory names skipped during recursive walks.
_SKIP_DIRS: frozenset[str] = frozenset(
    {
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "build",
        "dist",
        ".eggs",
        ".ipynb_checkpoints",
        "node_modules",
    }
)

# YP006 — raw seaborn plot functions.
_SNS_PLOT_FUNCS: frozenset[str] = frozenset(
    {"sns.violinplot", "sns.boxplot", "sns.stripplot"}
)

# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def _dotted_name(node: ast.expr) -> str | None:
    """Resolve an Attribute or Name node to a dotted string, or None.

    Args:
        node: AST expression node.

    Returns:
        Dotted name string (e.g. ``'plt.subplots'``) or None for non-name nodes.
    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        value_name = _dotted_name(node.value)
        if value_name is None:
            return None
        return f"{value_name}.{node.attr}"
    return None


def _is_hex_palette_dict(node: ast.Dict) -> bool:
    """Return True iff the dict has ≥2 string values matching the hex color pattern.

    Requires ≥2 hex values so a lone ``"#000"`` used as a single color does not fire.

    Args:
        node: AST Dict literal node.

    Returns:
        True when ≥2 values are hex-color string constants.
    """
    hex_count = 0
    for value in node.values:
        if (
            isinstance(value, ast.Constant)
            and isinstance(value.value, str)
            and _HEX_RE.match(value.value)
        ):
            hex_count += 1
            if hex_count >= 2:
                return True
    return False


# ---------------------------------------------------------------------------
# Per-call rule checkers — each returns the rule code or None
# ---------------------------------------------------------------------------


def _check_figsize(call: ast.Call) -> str | None:
    """Return YP002 if call is a plt figure-maker with a literal figsize= tuple/list.

    Args:
        call: AST Call node.

    Returns:
        ``'YP002'`` on match, else None.
    """
    callee = _dotted_name(call.func)
    if callee not in _PLT_FIGURE_CALLERS:
        return None
    for kw in call.keywords:
        if kw.arg == "figsize" and isinstance(kw.value, (ast.Tuple, ast.List)):
            return "YP002"
    return None


def _check_subplots_adjust(call: ast.Call) -> str | None:
    """Return YP003 if call is subplots_adjust (bare or dotted).

    Args:
        call: AST Call node.

    Returns:
        ``'YP003'`` on match, else None.
    """
    callee = _dotted_name(call.func)
    if callee is None:
        return None
    tail = callee.split(".")[-1]
    return "YP003" if tail == "subplots_adjust" else None


def _check_savefig(call: ast.Call) -> str | None:
    """Return YP004 if call ends in .savefig (but NOT .save).

    Args:
        call: AST Call node.

    Returns:
        ``'YP004'`` on match, else None.
    """
    callee = _dotted_name(call.func)
    if callee is None:
        return None
    tail = callee.split(".")[-1]
    return "YP004" if tail == "savefig" else None


def _check_seaborn(call: ast.Call) -> str | None:
    """Return YP006 if call is a raw sns violin/box/strip plot.

    Args:
        call: AST Call node.

    Returns:
        ``'YP006'`` on match, else None.
    """
    callee = _dotted_name(call.func)
    return "YP006" if callee in _SNS_PLOT_FUNCS else None


# ---------------------------------------------------------------------------
# AST visitor
# ---------------------------------------------------------------------------


class _RuleVisitor(ast.NodeVisitor):
    """Walk the AST and collect lint findings.

    Attributes:
        findings: Accumulated findings after visiting the tree.
        path: File path associated with the source being visited.
    """

    def __init__(self, path: str) -> None:
        """Initialise visitor for *path*.

        Args:
            path: File path string used to label findings.
        """
        self.findings: list[Finding] = []
        self.path = path

    def _add(self, node: ast.AST, code: str, **fmt: str) -> None:
        """Append a Finding for *node* using the rule *code*.

        Uses ``node.end_lineno`` to record the span for multi-line ignore support.

        Args:
            node: AST node providing the line number.
            code: Rule code string (e.g. ``'YP001'``).
            **fmt: Format values substituted into the message template.
        """
        level, msg_template = RULES[code]
        message = msg_template.format(**fmt) if fmt else msg_template
        lineno = getattr(node, "lineno", 0)
        end_lineno = getattr(node, "end_lineno", None) or lineno
        self.findings.append(
            Finding(
                path=self.path,
                line=lineno,
                end_line=end_lineno,
                code=code,
                message=message,
                level=level,
            )
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Flag locally-defined house-style functions (YP001).

        Args:
            node: FunctionDef AST node.
        """
        if node.name in _HOUSE_STYLE_FUNCS:
            self._add(node, "YP001", name=node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Flag async house-style function definitions (YP001).

        Args:
            node: AsyncFunctionDef AST node.
        """
        if node.name in _HOUSE_STYLE_FUNCS:
            self._add(node, "YP001", name=node.name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Dispatch per-call rule checks (YP002–YP006).

        Args:
            node: Call AST node.
        """
        checkers = [
            _check_figsize,
            _check_subplots_adjust,
            _check_savefig,
            _check_seaborn,
        ]
        for checker in checkers:
            code = checker(node)
            if code is not None:
                self._add(node, code)
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:
        """Flag hex-color palette dict literals (YP005).

        Catches both standalone dicts and inline ``palette={...}`` kwargs,
        avoiding the double-report that a separate call-level check would cause.

        Args:
            node: Dict AST node.
        """
        if _is_hex_palette_dict(node):
            self._add(node, "YP005")
        self.generic_visit(node)


# ---------------------------------------------------------------------------
# Ignore and selection filtering
# ---------------------------------------------------------------------------

_IGNORE_RE = re.compile(r"#\s*yplot2:\s*ignore(=([A-Z0-9,]+))?")


def _is_suppressed_by_ignore(finding: Finding, lines: list[str]) -> bool:
    """Return True if any line in the finding's span carries a matching ignore comment.

    Scans ``[finding.line, finding.end_line]`` (1-based, inclusive) so that a
    ``# yplot2: ignore`` comment on *any* physical line of a multi-line node
    (e.g. the ``figsize=`` line inside a multi-line ``plt.subplots(...)`` call)
    correctly suppresses the finding.

    Args:
        finding: The finding to evaluate.
        lines: Source split into lines (0-indexed).

    Returns:
        True when a matching ignore marker is found in the node's span.
    """
    for line_idx in range(finding.line - 1, finding.end_line):
        if line_idx < 0 or line_idx >= len(lines):
            continue
        match = _IGNORE_RE.search(lines[line_idx])
        if match is None:
            continue
        codes_str = match.group(2)
        if codes_str is None:
            return True  # bare "ignore" — suppress everything
        suppressed = {c.strip() for c in codes_str.split(",")}
        if finding.code in suppressed:
            return True
    return False


def _apply_ignores(findings: list[Finding], source: str) -> list[Finding]:
    """Drop findings whose node span contains a matching yplot2 ignore comment.

    Args:
        findings: Raw findings from the visitor.
        source: Full source text (used to extract line comments).

    Returns:
        Filtered findings with ignored entries removed.
    """
    lines = source.splitlines()
    return [f for f in findings if not _is_suppressed_by_ignore(f, lines)]


def _filter_codes(
    findings: list[Finding],
    select: set[str] | None,
    ignore: set[str] | None,
) -> list[Finding]:
    """Apply --select and --ignore CLI filters, then drop opt-in-only codes.

    A code in ``_OPT_IN`` is removed unless it appears in *select*.

    Args:
        findings: Findings after inline-ignore processing.
        select: If given, keep only these codes.
        ignore: If given, drop these codes.

    Returns:
        Filtered findings list.
    """
    result = findings
    if select:
        result = [f for f in result if f.code in select]
    if ignore:
        result = [f for f in result if f.code not in ignore]
    # Drop opt-in codes unless explicitly selected.
    if not select or not select.intersection(_OPT_IN):
        result = [f for f in result if f.code not in _OPT_IN]
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def check_source(source: str, path: str = "<string>") -> list[Finding]:
    """Parse *source* and return ALL findings for *path* (ignore comments applied).

    YP006 is included in the raw output; callers should filter with
    ``_filter_codes`` or use the default ``main`` behaviour.

    Args:
        source: Python source text.
        path: File path label used in findings.

    Returns:
        List of findings sorted by line then code, with inline ignores applied.
    """
    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as exc:
        level, msg_template = RULES["YP000"]
        lineno = exc.lineno or 0
        return [
            Finding(
                path=path,
                line=lineno,
                end_line=lineno,
                code="YP000",
                message=msg_template.format(msg=str(exc)),
                level=level,
            )
        ]
    visitor = _RuleVisitor(path)
    visitor.visit(tree)
    findings = _apply_ignores(visitor.findings, source)
    return sorted(findings, key=lambda f: (f.line, f.code))


def check_file(path: str | Path) -> list[Finding]:
    """Read and lint a single .py file.

    A file that fails to parse yields one YP000 WARNING rather than raising.

    Args:
        path: Path to the Python source file.

    Returns:
        List of findings for the file.
    """
    path_str = str(path)
    try:
        source = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        level, msg_template = RULES["YP000"]
        return [
            Finding(
                path=path_str,
                line=0,
                end_line=0,
                code="YP000",
                message=msg_template.format(msg=str(exc)),
                level=level,
            )
        ]
    return check_source(source, path_str)


def _should_skip_dir(name: str) -> bool:
    """Return True if a directory name should be excluded from walks.

    Args:
        name: Directory base name.

    Returns:
        True when the directory should be skipped.
    """
    return name in _SKIP_DIRS or name.endswith(".egg-info")


def check_paths(paths: Iterable[str | Path]) -> list[Finding]:
    """Lint files and/or directories (dirs walked for *.py). Returns sorted findings.

    Skips ``__pycache__``, ``.git``, ``.venv``, ``venv``, ``build``, ``dist``,
    ``.eggs``, ``.ipynb_checkpoints``, ``node_modules``, and ``*.egg-info`` dirs.

    Args:
        paths: File or directory paths to lint.

    Returns:
        Findings sorted by path, line, then code.
    """
    all_findings: list[Finding] = []
    for raw in paths:
        p = Path(raw)
        if p.is_file():
            all_findings.extend(check_file(p))
        elif p.is_dir():
            for child in sorted(p.rglob("*.py")):
                if any(_should_skip_dir(part) for part in child.parts):
                    continue
                all_findings.extend(check_file(child))
    return sorted(all_findings, key=lambda f: (f.path, f.line, f.code))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _format(finding: Finding) -> str:
    """Format a finding as a single human-readable line.

    Args:
        finding: The finding to format.

    Returns:
        String of the form ``path:line: CODE [level] message``.
    """
    return (
        f"{finding.path}:{finding.line}: {finding.code}"
        f" [{finding.level.value}] {finding.message}"
    )


def _parse_args(
    argv: list[str] | None,
) -> tuple[list[str], set[str] | None, set[str] | None]:
    """Parse CLI arguments.

    Args:
        argv: Argument list or None to use sys.argv[1:].

    Returns:
        Tuple of (paths, select_set_or_None, ignore_set_or_None).
    """
    parser = argparse.ArgumentParser(
        prog="python -m yplot2.lint",
        description="Anti-fork lint for paper repos using yplot2.",
    )
    parser.add_argument(
        "paths", nargs="*", metavar="PATH", help="Files or directories to lint."
    )
    parser.add_argument(
        "--select",
        metavar="CODES",
        help="Comma-separated codes to check (allowlist).",
    )
    parser.add_argument(
        "--ignore",
        metavar="CODES",
        help="Comma-separated codes to skip (denylist).",
    )
    ns = parser.parse_args(argv)
    select = {c.strip() for c in ns.select.split(",")} if ns.select else None
    ignore = {c.strip() for c in ns.ignore.split(",")} if ns.ignore else None
    return ns.paths, select, ignore


def main(argv: list[str] | None = None) -> int:
    """CLI entry: ``python -m yplot2.lint [--select C,..] [--ignore C,..] <paths...>``.

    Exits nonzero only when an ERROR-level finding survives filtering, or when
    a path argument does not exist on disk (typo in CI = nonzero, not silent pass).
    Warnings alone do not cause a nonzero exit.

    Args:
        argv: Argument list (default: sys.argv[1:]).

    Returns:
        0 on clean run or warnings only; 1 if any ERROR-level finding survives
        or any explicit path does not exist.
    """
    paths, select, ignore = _parse_args(argv)
    if not paths:
        print("Usage: python -m yplot2.lint <paths...>", file=sys.stderr)
        return 1
    missing = [p for p in paths if not Path(p).exists()]
    if missing:
        for p in missing:
            print(f"error: path not found: {p}", file=sys.stderr)
        return 1
    findings = check_paths(paths)
    findings = _filter_codes(findings, select, ignore)
    for finding in findings:
        print(_format(finding))
    has_error = any(f.level == Level.ERROR for f in findings)
    return 1 if has_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
