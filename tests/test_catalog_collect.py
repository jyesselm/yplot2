"""
Tests for yplot2/catalog_build/collect.py — pkgutil collector.

Verifies that the five statistical capsules are found, that no record's
source_path points into build/lib, that import failures are captured
gracefully, and that seaborn is not required for static collection.
"""

import subprocess
import sys
import types
from unittest.mock import patch


from yplot2.catalog_build.collect import (
    ImportFailure,
    _build_record,
    _extract_inputs,
    _extract_summary,
    _make_source_path,
    _records_from_module,
    _safe_import,
    collect_records,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EXPECTED_NAMES = {"violin", "box", "kde", "heatmap2d", "hexbin"}


# ---------------------------------------------------------------------------
# collect_records
# ---------------------------------------------------------------------------


class TestCollectRecords:
    """collect_records discovers all five statistical capsules."""

    def test_collects_five_statistical_capsules(self):
        """All five expected capsule names are in the collected records."""
        records, failures = collect_records()
        names = {r.name for r in records}
        assert EXPECTED_NAMES.issubset(names)

    def test_all_statistical_category(self):
        """All five statistical capsules have category=='statistical'."""
        records, _ = collect_records()
        stat = {r for r in records if r.name in EXPECTED_NAMES}
        assert all(r.category == "statistical" for r in stat)

    def test_all_have_demo(self):
        """All five statistical capsules report has_demo=True."""
        records, _ = collect_records()
        stat = {r for r in records if r.name in EXPECTED_NAMES}
        assert all(r.has_demo for r in stat)

    def test_no_build_shadow(self):
        """No record's source_path contains 'build/lib'."""
        records, _ = collect_records()
        for rec in records:
            assert "build/lib" not in rec.source_path

    def test_no_duplicate_names(self):
        """Each capsule name appears at most once in the collected records."""
        records, _ = collect_records()
        names = [r.name for r in records]
        assert len(names) == len(set(names))


# ---------------------------------------------------------------------------
# Seaborn-free collection
# ---------------------------------------------------------------------------


def test_collect_is_seaborn_free():
    """collect_records() finds all five capsules even with seaborn blocked."""
    code = (
        "import sys; "
        "sys.modules['seaborn'] = None; "
        "from yplot2.catalog_build.collect import collect_records; "
        "records, _ = collect_records(); "
        "names = {r.name for r in records}; "
        f"expected = {EXPECTED_NAMES!r}; "
        "assert expected.issubset(names), f'Missing: {expected - names}'; "
        "print('OK')"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"collect_records failed with seaborn absent.\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    assert "OK" in result.stdout


# ---------------------------------------------------------------------------
# _safe_import
# ---------------------------------------------------------------------------


class TestSafeImport:
    """_safe_import sandboxes import failures."""

    def test_valid_module_returns_module(self):
        """Importing a known module returns (module, None)."""
        module, failure = _safe_import("yplot2.catalog")
        assert module is not None
        assert failure is None

    def test_invalid_module_returns_failure(self):
        """Importing a non-existent module returns (None, ImportFailure)."""
        module, failure = _safe_import("yplot2.__nonexistent_xyz__")
        assert module is None
        assert failure is not None
        assert isinstance(failure, ImportFailure)

    def test_failure_captured_not_raised(self):
        """A module that raises on import yields an ImportFailure, not an exception."""
        module, failure = _safe_import("yplot2.__nonexistent_xyz__")
        # If we reach here, the exception was absorbed.
        assert failure is not None


# ---------------------------------------------------------------------------
# Import failure is captured not raised (integration)
# ---------------------------------------------------------------------------


def test_import_failure_is_captured_not_raised():
    """A failing module import lands in failures; walk still returns good records."""
    original_safe_import = __import__(
        "yplot2.catalog_build.collect", fromlist=["_safe_import"]
    )._safe_import

    call_count = [0]

    def patched_safe_import(name: str):
        call_count[0] += 1
        if call_count[0] == 1:
            # Simulate the first module failing
            return None, ImportFailure(module=name, error="deliberate test failure")
        return original_safe_import(name)

    with patch(
        "yplot2.catalog_build.collect._safe_import", side_effect=patched_safe_import
    ):
        records, failures = collect_records()

    # At least one failure captured
    assert len(failures) >= 1
    # But good records were still collected
    assert len(records) > 0


def test_iter_module_names_onerror_captures_walk_failures():
    """When pkgutil calls onerror (subpackage __init__ raises), the failure is captured."""
    import pkgutil

    from yplot2.catalog_build.collect import ImportFailure, _iter_module_names

    failures: list[ImportFailure] = []
    original_walk = pkgutil.walk_packages

    def patched_walk(path, prefix="", onerror=None):
        # Simulate a broken subpackage __init__ raising RuntimeError during walk
        if onerror is not None:
            onerror("yplot2.broken_subpkg")
        yield from original_walk(path, prefix=prefix, onerror=onerror)

    with patch(
        "yplot2.catalog_build.collect.pkgutil.walk_packages", side_effect=patched_walk
    ):
        list(_iter_module_names(failures))

    assert any(f.module == "yplot2.broken_subpkg" for f in failures), (
        f"Expected 'yplot2.broken_subpkg' in failures; got {[f.module for f in failures]}"
    )


# ---------------------------------------------------------------------------
# _extract_summary
# ---------------------------------------------------------------------------


class TestExtractSummary:
    """_extract_summary returns the first non-blank docstring line."""

    def test_returns_first_non_blank_line(self):
        """Returns the first non-blank stripped line."""

        def fn():
            """First line.
            Second line.
            """
            pass

        assert _extract_summary(fn) == "First line."

    def test_returns_empty_for_no_doc(self):
        """Returns '' when the function has no docstring."""

        def fn():
            pass

        fn.__doc__ = None
        assert _extract_summary(fn) == ""

    def test_returns_empty_for_blank_doc(self):
        """Returns '' when the docstring contains only blank lines."""

        def fn():
            """ """
            pass

        assert _extract_summary(fn) == ""


# ---------------------------------------------------------------------------
# _extract_inputs
# ---------------------------------------------------------------------------


class TestExtractInputs:
    """_extract_inputs drops the leading ax/self parameter."""

    def test_drops_leading_ax(self):
        """Leading 'ax' is excluded from inputs."""

        def fn(ax, data, x, y):
            pass

        result = _extract_inputs(fn)
        assert "ax" not in result
        assert "data" in result

    def test_keeps_other_params(self):
        """Non-ax params are retained."""

        def fn(ax, x, y, hue=None):
            pass

        result = _extract_inputs(fn)
        assert result == ("x", "y", "hue")

    def test_builtin_returns_tuple(self):
        """A built-in with no inspectable signature returns a tuple (may be empty)."""
        result = _extract_inputs(len)
        assert isinstance(result, tuple)

    def test_raises_returns_empty_tuple(self):
        """A callable where inspect.signature raises returns ()."""
        from unittest.mock import patch

        def fn(ax, x):
            pass

        with patch("inspect.signature", side_effect=ValueError("no sig")):
            result = _extract_inputs(fn)
        assert result == ()


# ---------------------------------------------------------------------------
# _make_source_path
# ---------------------------------------------------------------------------


class TestMakeSourcePath:
    """_make_source_path returns a best-effort source path."""

    def test_returns_string(self):
        """Returns a string (possibly empty) for any callable."""

        def fn():
            pass

        result = _make_source_path(fn)
        assert isinstance(result, str)

    def test_returns_empty_for_builtin(self):
        """Built-ins with no source file return '' or an absolute path."""
        result = _make_source_path(len)
        assert isinstance(result, str)

    def test_no_source_file_returns_empty(self):
        """Returns '' when inspect.getsourcefile returns '' or None."""
        from unittest.mock import patch

        def fn():
            pass

        with patch("inspect.getsourcefile", return_value=""):
            result = _make_source_path(fn)
        assert result == ""

    def test_relpath_failure_returns_abs(self):
        """Falls back to absolute path when os.path.relpath raises ValueError."""
        from unittest.mock import patch

        def fn():
            pass

        with patch("os.path.relpath", side_effect=ValueError("cross-drive")):
            result = _make_source_path(fn)
        # Should return the absolute path rather than raising
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# _records_from_module re-import deduplication
# ---------------------------------------------------------------------------


def test_records_from_module_skips_reimports():
    """Functions imported from another module are excluded (fn.__module__ != module name)."""
    import yplot2.plots.statistical as stat_pkg

    # stat_pkg.__init__ has no @catalog-decorated functions directly, so should return []
    records = _records_from_module(stat_pkg)
    # Any records found must have __module__ == stat_pkg's module name
    assert all(r.import_path.startswith("yplot2.plots.statistical.") for r in records)


def test_records_from_module_skips_when_module_mismatch():
    """_records_from_module skips functions whose __module__ differs from the module."""

    # Create a fake module with a function that "belongs" to a different module
    host = types.ModuleType("fake_host")
    host.__name__ = "fake_host"

    def foreign_fn():
        pass

    foreign_fn.__module__ = "some_other_module"
    foreign_fn.__yp_catalog__ = {  # type: ignore[attr-defined]
        "category": "test",
        "tags": (),
        "data_shape": "xy",
        "kind": "panel",
    }
    host.foreign_fn = foreign_fn  # type: ignore[attr-defined]

    records = _records_from_module(host)
    # foreign_fn should be skipped because its __module__ != "fake_host"
    assert records == []


# ---------------------------------------------------------------------------
# _build_record with inspect.signature failure
# ---------------------------------------------------------------------------


def test_build_record_handles_signature_failure():
    """_build_record sets signature='' when inspect.signature raises."""
    from unittest.mock import patch

    mod = types.ModuleType("fake_module")
    mod.__name__ = "fake_module"

    def fn(ax, x, y):
        """A test function."""
        pass

    fn.__module__ = "fake_module"
    fn.__yp_catalog__ = {  # type: ignore[attr-defined]
        "category": "test",
        "tags": (),
        "data_shape": "xy",
        "kind": "panel",
    }

    with patch("inspect.signature", side_effect=ValueError("no sig")):
        rec = _build_record(fn, mod)

    assert rec.signature == ""


# ---------------------------------------------------------------------------
# _build_record with edge-case callable
# ---------------------------------------------------------------------------


def test_build_record_with_callable_object():
    """_build_record handles callables where inspect.signature may fail."""

    mod = types.ModuleType("fake_module")
    mod.__name__ = "fake_module"

    # Create a function-like object that has __yp_catalog__ but no signature
    class Weird:
        __name__ = "weird"
        __module__ = "fake_module"
        __doc__ = "Weird callable."
        __yp_catalog__ = {
            "category": "test",
            "tags": (),
            "data_shape": "xy",
            "kind": "panel",
        }

        def __call__(self):
            pass

    w = Weird()
    # Should not raise; signature may be "" on failure
    from yplot2.catalog_build.collect import _build_record

    rec = _build_record(w, mod)
    assert rec.name == "weird"


# ---------------------------------------------------------------------------
# signature and inputs (integration with real capsule)
# ---------------------------------------------------------------------------


def test_signature_and_inputs_extracted():
    """Violin record contains 'data' in signature and excludes 'ax' from inputs."""
    records, _ = collect_records()
    violin = next((r for r in records if r.name == "violin"), None)
    assert violin is not None
    assert "data" in violin.signature
    assert "ax" not in violin.inputs
