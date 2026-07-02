"""
Figure-regeneration CLI for yplot2.

Usage::

    python -m yplot2.build <directory>

Discovers all ``.py`` figure scripts and ``.ipynb`` notebooks in *directory*
(non-recursive), executes each in a fresh subprocess or clean kernel, and
prints a per-target PASS/FAIL summary.

PURE module: no matplotlib, seaborn, or pandas at import.
Notebook execution requires the ``[repro]`` extra (nbconvert, ipykernel).
"""

import os
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class BuildResult:
    """Outcome of regenerating one figure target."""

    target: str
    ok: bool
    stderr: str  # captured on failure; empty on success


def discover_targets(directory: str) -> list[str]:
    """Return sorted .py and .ipynb figure targets under *directory* (non-recursive).

    Args:
        directory: Path to scan for figure targets.

    Returns:
        Sorted list of absolute or relative paths ending in .py or .ipynb.

    Raises:
        FileNotFoundError: If *directory* does not exist.
    """
    entries = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith((".py", ".ipynb"))
    ]
    return sorted(entries)


def run_script(path: str) -> BuildResult:
    """Execute a .py figure script in a fresh subprocess.

    Args:
        path: Path to the Python script.

    Returns:
        BuildResult with ok=True on exit code 0, else ok=False + stderr.
    """
    result = subprocess.run(
        [sys.executable, path],
        capture_output=True,
        text=True,
    )
    return BuildResult(
        target=path,
        ok=result.returncode == 0,
        stderr=result.stderr if result.returncode != 0 else "",
    )


def run_notebook(path: str) -> BuildResult:
    """Execute a notebook in place headless via ``jupyter nbconvert --execute``.

    Requires the ``[repro]`` extra (nbconvert + ipykernel). Returns a failed
    BuildResult with an actionable message when nbconvert is absent.

    Args:
        path: Path to the .ipynb file.

    Returns:
        BuildResult with ok=True on exit code 0, else ok=False + stderr.
    """
    cmd = [
        "jupyter",
        "nbconvert",
        "--execute",
        "--inplace",
        "--to",
        "notebook",
        path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        return BuildResult(
            target=path,
            ok=False,
            stderr=(
                "nbconvert not found; install yplot2[repro] or run: pip install nbconvert"
            ),
        )
    return BuildResult(
        target=path,
        ok=result.returncode == 0,
        stderr=result.stderr if result.returncode != 0 else "",
    )


def build(directory: str) -> list[BuildResult]:
    """Regenerate all figure targets in *directory*; return per-target results.

    Args:
        directory: Directory containing .py and/or .ipynb figure targets.

    Returns:
        List of BuildResult instances, one per discovered target.

    Raises:
        FileNotFoundError: If *directory* does not exist.
    """
    results = []
    for path in discover_targets(directory):
        runner = run_script if path.endswith(".py") else run_notebook
        results.append(runner(path))
    return results


def main(argv: list[str] | None = None) -> int:
    """CLI entry: ``python -m yplot2.build <dir>``. Returns process exit code.

    Prints a per-target PASS/FAIL line and writes failure stderr to stderr.
    Returns 1 if any target failed or the directory does not exist, else 0.

    Args:
        argv: Argument list (default: sys.argv[1:]).

    Returns:
        0 on full success, 1 if any target failed.
    """
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("Usage: python -m yplot2.build <directory>", file=sys.stderr)
        return 1
    try:
        results = build(args[0])
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    any_failed = False
    for res in results:
        status = "PASS" if res.ok else "FAIL"
        print(f"[{status}] {res.target}")
        if not res.ok and res.stderr:
            print(f"  {res.stderr.strip()}", file=sys.stderr)
            any_failed = True
    return 1 if any_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
