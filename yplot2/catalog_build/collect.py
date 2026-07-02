"""
pkgutil-based collector for yplot2 @catalog capsules.

Walks the installed yplot2 package via ``pkgutil.walk_packages``
(NEVER a filesystem glob, so the build/lib/yplot2 shadow is unreachable).
Each submodule import is sandboxed — a failing import becomes an
``ImportFailure`` and never aborts the walk.

PURE module: no matplotlib, seaborn, or pandas at import.
Importing a capsule module is seaborn-free; seaborn is lazy inside
wrapper bodies only.
"""

import inspect
import os
import pkgutil
import sys
import types
from collections.abc import Iterator
from dataclasses import dataclass

from .records import CapsuleRecord


@dataclass(frozen=True)
class ImportFailure:
    """A module that could not be imported during collection."""

    module: str
    error: str


def _iter_module_names(failures: list[ImportFailure]) -> Iterator[str]:
    """Walk the installed yplot2 package, yielding dotted module names.

    Uses ``pkgutil.walk_packages`` over ``yplot2.__path__`` so the
    ``build/lib/yplot2`` shadow is never reachable. When a subpackage
    ``__init__`` raises during the walk, the error is appended to *failures*
    and the walk continues.

    Args:
        failures: Mutable list that receives ImportFailure entries for any
            package whose ``__init__`` raises during the walk.

    Yields:
        Dotted module name strings like ``"yplot2.plots.statistical.violin"``.
    """
    import yplot2

    def _on_error(name: str) -> None:
        exc = sys.exc_info()[1]
        failures.append(
            ImportFailure(module=name, error=repr(exc) if exc else "walk error")
        )

    for info in pkgutil.walk_packages(
        yplot2.__path__, prefix="yplot2.", onerror=_on_error
    ):
        yield info.name


def _safe_import(name: str) -> tuple[types.ModuleType | None, ImportFailure | None]:
    """Try to import *name*; return (module, None) on success or (None, failure).

    Args:
        name: Dotted module name to import.

    Returns:
        Tuple of (module, None) on success or (None, ImportFailure) on any error.
    """
    try:
        module = __import__(name, fromlist=[""])
        return module, None
    except Exception as exc:
        return None, ImportFailure(module=name, error=repr(exc))


def _extract_summary(fn: object) -> str:
    """Return the first non-blank line of fn.__doc__, or ''.

    Args:
        fn: Callable whose docstring to inspect.

    Returns:
        First non-blank stripped line, or empty string.
    """
    doc = getattr(fn, "__doc__", None) or ""
    for line in doc.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _extract_inputs(fn: object) -> tuple[str, ...]:
    """Return param names for fn, dropping a leading 'ax' or 'self'.

    Args:
        fn: Callable to inspect.

    Returns:
        Tuple of parameter names (excluding the leading ax/self).
    """
    try:
        sig = inspect.signature(fn)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return ()
    params = list(sig.parameters)
    if params and params[0] in ("ax", "self"):
        params = params[1:]
    return tuple(params)


def _make_source_path(fn: object) -> str:
    """Return a repo-relative source path for fn, best-effort.

    Falls back to absolute path if relpath cannot be computed, or '' on failure.

    Args:
        fn: Callable whose source file to locate.

    Returns:
        Source path string (relative to yplot2 package root when possible).
    """
    try:
        abs_path = inspect.getsourcefile(fn) or ""  # type: ignore[arg-type]
        if not abs_path:
            return ""
        import yplot2

        pkg_dir = os.path.dirname(yplot2.__file__ or "")
        try:
            return os.path.relpath(abs_path, start=pkg_dir)
        except ValueError:
            return abs_path
    except Exception:
        return ""


def _build_record(fn: object, module: types.ModuleType) -> CapsuleRecord:
    """Build a CapsuleRecord from a @catalog-decorated function.

    Args:
        fn: Callable carrying __yp_catalog__.
        module: The module where fn lives (used for has_demo lookup).

    Returns:
        CapsuleRecord with all fields populated from static introspection.
    """
    catalog_meta = getattr(fn, "__yp_catalog__", {})
    fn_name = getattr(fn, "__name__", "")
    try:
        sig = str(inspect.signature(fn))  # type: ignore[arg-type]
    except (ValueError, TypeError):
        sig = ""
    return CapsuleRecord(
        name=fn_name,
        category=catalog_meta.get("category", "uncategorized"),
        tags=tuple(catalog_meta.get("tags", ())),
        data_shape=catalog_meta.get("data_shape", ""),
        kind=catalog_meta.get("kind", "panel"),
        signature=sig,
        inputs=_extract_inputs(fn),
        summary=_extract_summary(fn),
        source_path=_make_source_path(fn),
        import_path=f"{getattr(fn, '__module__', '')}.{fn_name}",
        has_demo=hasattr(module, f"demo_{fn_name}"),
    )


def _records_from_module(module: types.ModuleType) -> list[CapsuleRecord]:
    """Extract CapsuleRecords from all @catalog-decorated functions in module.

    Only functions where ``fn.__module__ == module.__name__`` are included
    to avoid double-counting re-imported names.

    Args:
        module: Module to inspect.

    Returns:
        List of CapsuleRecords; empty when none are found.
    """
    records = []
    for _name, fn in inspect.getmembers(module, inspect.isfunction):
        if getattr(fn, "__yp_catalog__", None) is None:
            continue
        if fn.__module__ != module.__name__:
            continue
        records.append(_build_record(fn, module))
    return records


def collect_records() -> tuple[list[CapsuleRecord], list[ImportFailure]]:
    """Walk the yplot2 package and return (capsule records, import failures).

    Uses ``pkgutil.walk_packages`` over ``yplot2.__path__`` (NEVER a filesystem
    glob), imports each submodule in a try/except sandbox (a failing import
    becomes an ImportFailure, never aborts the walk), and extracts
    CapsuleRecords from every module-level function carrying ``__yp_catalog__``.

    A subpackage whose ``__init__`` raises during the walk is also captured as
    an ImportFailure (via the ``onerror`` callback) rather than aborting the
    entire walk.

    Returns:
        Tuple of (records, failures). Failures are non-blocking; remaining
        records are collected even when one module fails to import.
    """
    records: list[CapsuleRecord] = []
    failures: list[ImportFailure] = []
    for name in _iter_module_names(failures):
        module, failure = _safe_import(name)
        if failure is not None:
            failures.append(failure)
            continue
        if module is not None:
            records.extend(_records_from_module(module))
    return records, failures
