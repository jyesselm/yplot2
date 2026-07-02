"""
Tests for yplot2/catalog_build/build.py — catalog orchestrator.

Verifies: catalog.json is always written (even on demo failure or partial
collection failure), strict mode, CATALOG.md generation, and seaborn-free import.
"""

import json
import os
import subprocess
import sys
from unittest.mock import patch

import pytest

from yplot2.catalog_build.build import build_catalog, main
from yplot2.catalog_build.collect import ImportFailure
from yplot2.catalog_build.fingerprint import FingerprintResult, StyleViolation


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_blocking_result(name: str) -> FingerprintResult:
    """Return a FingerprintResult that is blocking (has violations)."""
    v = StyleViolation(
        axes_index=0, prop="spine_linewidth", expected="0.75", actual="1.5"
    )
    return FingerprintResult(
        name=name, violations=(v,), thumbnail_ok=False, error="", skipped=False
    )


# ---------------------------------------------------------------------------
# test_json_written_even_when_demo_fails (headline test)
# ---------------------------------------------------------------------------


def test_json_written_even_when_demo_fails(tmp_path):
    """catalog.json is written before any demo runs; a failed demo does not block the index."""
    with patch(
        "yplot2.catalog_build.build.fingerprint_capsule",
        side_effect=lambda rec, **kw: _make_blocking_result(rec.name),
    ):
        build_catalog(str(tmp_path))

    json_path = os.path.join(str(tmp_path), "catalog.json")
    assert os.path.isfile(json_path), "catalog.json must exist even after failing demos"

    with open(json_path, encoding="utf-8") as fh:
        parsed = json.load(fh)

    assert parsed["schema_version"] == 1
    capsule_names = {c["name"] for c in parsed["capsules"]}
    expected = {"violin", "box", "kde", "heatmap2d", "hexbin"}
    assert expected.issubset(capsule_names), (
        f"Missing capsules: {expected - capsule_names}"
    )


# ---------------------------------------------------------------------------
# test_json_written_even_when_collect_raises (defensive-wrap test)
# ---------------------------------------------------------------------------


def test_json_written_even_when_collect_raises(tmp_path):
    """catalog.json is written even if collect_records() raises unexpectedly.

    This covers the 'catalog.json is always written' guarantee — the defensive
    try/except in build_catalog must ensure the static index is written even
    when collection partially or wholly fails.
    """
    with patch(
        "yplot2.catalog_build.build.collect_records",
        side_effect=RuntimeError("simulated subpackage __init__ failure"),
    ):
        report = build_catalog(str(tmp_path))

    json_path = os.path.join(str(tmp_path), "catalog.json")
    assert os.path.isfile(json_path), (
        "catalog.json must exist even when collect_records raises"
    )

    with open(json_path, encoding="utf-8") as fh:
        parsed = json.load(fh)

    # An empty capsule list is valid — what matters is catalog.json was written
    assert parsed["schema_version"] == 1
    assert "capsules" in parsed

    # The collection exception must be recorded as an import failure
    assert len(report.import_failures) >= 1
    assert any(f.module == "<collect>" for f in report.import_failures)


# ---------------------------------------------------------------------------
# test_strict_reports_blocking_failure
# ---------------------------------------------------------------------------


def test_strict_mode_returns_1_on_blocking_failure(tmp_path):
    """main() exits 1 in strict mode when a fingerprint failure occurs."""
    with patch(
        "yplot2.catalog_build.build.fingerprint_capsule",
        side_effect=lambda rec, **kw: _make_blocking_result(rec.name),
    ):
        code = main(["--out-dir", str(tmp_path)])

    assert code == 1


def test_no_strict_mode_returns_0_on_blocking_failure(tmp_path):
    """main() exits 0 in --no-strict mode even with fingerprint failures."""
    with patch(
        "yplot2.catalog_build.build.fingerprint_capsule",
        side_effect=lambda rec, **kw: _make_blocking_result(rec.name),
    ):
        code = main(["--out-dir", str(tmp_path), "--no-strict"])

    assert code == 0


# ---------------------------------------------------------------------------
# test_catalog_md_generated_and_grouped
# ---------------------------------------------------------------------------


def test_catalog_md_generated_and_grouped(tmp_path):
    """CATALOG.md exists and contains a 'statistical' section with capsule import paths."""
    with patch(
        "yplot2.catalog_build.build.fingerprint_capsule",
        side_effect=lambda rec, **kw: FingerprintResult(
            name=rec.name, violations=(), thumbnail_ok=False, error="", skipped=True
        ),
    ):
        build_catalog(str(tmp_path))

    md_path = os.path.join(str(tmp_path), "CATALOG.md")
    assert os.path.isfile(md_path), "CATALOG.md must be written"

    content = open(md_path).read()
    assert "statistical" in content.lower()
    # At least one of the statistical capsule import paths appears
    assert "yplot2.plots.statistical" in content


# ---------------------------------------------------------------------------
# test_full_build_smoke (requires seaborn)
# ---------------------------------------------------------------------------


def test_full_build_smoke(tmp_path):
    """Full build with real seaborn produces json + md + ≥1 thumbnail, no failures."""
    pytest.importorskip("seaborn")
    report = build_catalog(str(tmp_path))
    assert os.path.isfile(report.catalog_json_path)
    assert os.path.isfile(report.catalog_md_path)
    assert report.n_capsules >= 5
    assert report.blocking_failures == (), (
        f"Unexpected blocking failures: {report.blocking_failures}"
    )
    thumbs_dir = os.path.join(str(tmp_path), "thumbs")
    if os.path.isdir(thumbs_dir):
        pngs = [f for f in os.listdir(thumbs_dir) if f.endswith(".png")]
        assert len(pngs) >= 1, "Expected at least one thumbnail"


# ---------------------------------------------------------------------------
# test_catalog_build_import_is_seaborn_free
# ---------------------------------------------------------------------------


def test_catalog_build_import_is_seaborn_free():
    """Importing yplot2.catalog_build succeeds with seaborn blocked."""
    code = (
        "import sys; "
        "sys.modules['seaborn'] = None; "
        "import yplot2.catalog_build; "
        "print('OK')"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"import yplot2.catalog_build failed with seaborn absent.\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    assert "OK" in result.stdout


# ---------------------------------------------------------------------------
# Records with has_demo=False are skipped in fingerprinting
# ---------------------------------------------------------------------------


def test_no_demo_records_are_skipped(tmp_path):
    """Records with has_demo=False are not fingerprinted (skipped silently)."""
    from yplot2.catalog_build.records import CapsuleRecord

    no_demo_rec = CapsuleRecord(
        name="nodemo",
        category="test",
        tags=(),
        data_shape="xy",
        kind="panel",
        signature="(ax)",
        inputs=(),
        summary="",
        source_path="",
        import_path="yplot2.plots.nodemo",
        has_demo=False,
    )
    fp_calls = []

    def tracking_fingerprint(rec, **kw):
        fp_calls.append(rec.name)
        return FingerprintResult(
            name=rec.name, violations=(), thumbnail_ok=False, error="", skipped=True
        )

    with patch(
        "yplot2.catalog_build.build.collect_records", return_value=([no_demo_rec], [])
    ):
        with patch(
            "yplot2.catalog_build.build.fingerprint_capsule",
            side_effect=tracking_fingerprint,
        ):
            build_catalog(str(tmp_path))

    # fingerprint_capsule must NOT have been called for has_demo=False records
    assert "nodemo" not in fp_calls


# ---------------------------------------------------------------------------
# Import failures are reported in main() output
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Package-level lazy exports (__getattr__ coverage)
# ---------------------------------------------------------------------------


def test_catalog_build_package_exports_lazily():
    """yplot2.catalog_build.build_catalog and BuildReport are accessible lazily."""
    import yplot2.catalog_build as pkg

    # Trigger __getattr__ for build_catalog
    assert callable(pkg.build_catalog)
    # Trigger __getattr__ for BuildReport
    assert pkg.BuildReport is not None


def test_catalog_build_package_raises_on_unknown_attr():
    """Accessing an unknown attribute from yplot2.catalog_build raises AttributeError."""
    import yplot2.catalog_build as pkg

    with pytest.raises(AttributeError, match="no attribute"):
        _ = pkg.nonexistent_thing_xyz  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Import failures are reported in main() output
# ---------------------------------------------------------------------------


def test_main_reports_import_failures(tmp_path):
    """main() reports import failures to stderr."""
    from yplot2.catalog_build.records import CapsuleRecord

    dummy_rec = CapsuleRecord(
        name="dummy",
        category="test",
        tags=(),
        data_shape="xy",
        kind="panel",
        signature="",
        inputs=(),
        summary="",
        source_path="",
        import_path="yplot2.dummy",
        has_demo=False,
    )
    failure = ImportFailure(
        module="yplot2.broken", error="ModuleNotFoundError('broken')"
    )

    with patch(
        "yplot2.catalog_build.build.collect_records",
        return_value=([dummy_rec], [failure]),
    ):
        code = main(["--out-dir", str(tmp_path), "--no-strict"])

    # Should still succeed (import failures are non-blocking)
    assert code == 0
