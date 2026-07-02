"""
Tests for yplot2/catalog_build/records.py — CapsuleRecord + JSON schema.

Verifies round-trip serialization, deterministic ordering, and schema_version.
"""

import json


from yplot2.catalog_build.records import (
    SCHEMA_VERSION,
    CapsuleRecord,
    catalog_to_json,
    record_to_dict,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_record(name: str = "violin", category: str = "statistical") -> CapsuleRecord:
    """Return a hand-built CapsuleRecord for testing."""
    return CapsuleRecord(
        name=name,
        category=category,
        tags=("distribution", "categorical"),
        data_shape="long-df",
        kind="panel",
        signature="(ax, data, x, y)",
        inputs=("data", "x", "y"),
        summary="Draw a house-styled violin plot.",
        source_path="plots/statistical/violin.py",
        import_path="yplot2.plots.statistical.violin.violin",
        has_demo=True,
    )


# ---------------------------------------------------------------------------
# record_to_dict
# ---------------------------------------------------------------------------


class TestRecordToDict:
    """record_to_dict serializes all fields correctly."""

    def test_all_fields_present(self):
        """All CapsuleRecord fields appear in the dict."""
        rec = _make_record()
        d = record_to_dict(rec)
        for field in (
            "name",
            "category",
            "tags",
            "data_shape",
            "kind",
            "signature",
            "inputs",
            "summary",
            "source_path",
            "import_path",
            "has_demo",
        ):
            assert field in d

    def test_tuples_become_lists(self):
        """Tuple fields tags and inputs are serialized as lists."""
        rec = _make_record()
        d = record_to_dict(rec)
        assert isinstance(d["tags"], list)
        assert isinstance(d["inputs"], list)

    def test_values_match(self):
        """Field values round-trip correctly."""
        rec = _make_record()
        d = record_to_dict(rec)
        assert d["name"] == "violin"
        assert d["category"] == "statistical"
        assert d["has_demo"] is True
        assert d["tags"] == ["distribution", "categorical"]


# ---------------------------------------------------------------------------
# catalog_to_json
# ---------------------------------------------------------------------------


class TestCatalogToJson:
    """catalog_to_json produces deterministic, parseable JSON."""

    def test_parses_back(self):
        """Output is valid JSON that parses back to expected shape."""
        records = [_make_record("violin"), _make_record("box")]
        out = catalog_to_json(records)
        parsed = json.loads(out)
        assert "schema_version" in parsed
        assert "capsules" in parsed

    def test_schema_version(self):
        """schema_version equals SCHEMA_VERSION (1)."""
        out = catalog_to_json([_make_record()])
        parsed = json.loads(out)
        assert parsed["schema_version"] == SCHEMA_VERSION
        assert SCHEMA_VERSION == 1

    def test_sorted_by_category_then_name(self):
        """Capsules are sorted by (category, name) for stable output."""
        records = [
            _make_record("z_plot", "basic"),
            _make_record("a_plot", "statistical"),
            _make_record("b_plot", "basic"),
        ]
        parsed = json.loads(catalog_to_json(records))
        names = [c["name"] for c in parsed["capsules"]]
        assert names == ["b_plot", "z_plot", "a_plot"]

    def test_byte_stable_across_two_calls(self):
        """catalog_to_json produces identical output on two calls."""
        records = [_make_record("violin"), _make_record("box")]
        out1 = catalog_to_json(records)
        out2 = catalog_to_json(records)
        assert out1 == out2

    def test_trailing_newline(self):
        """Output ends with a trailing newline."""
        out = catalog_to_json([_make_record()])
        assert out.endswith("\n")
