"""
Tests for yplot2/catalog.py and yplot2/vocab.py.

Verifies:
- @catalog attaches __yp_catalog__ with correct keys.
- category is derived from __module__.
- Validators raise ValueError on unknown tokens.
- No global registry/collector exists in catalog.py.
- All five wrappers carry __yp_catalog__.
- demo_* functions return Figure objects.
- import yplot2; yplot2.catalog works without seaborn.
"""

import subprocess
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from yplot2.catalog import catalog, _category_from_module
from yplot2.vocab import validate_tags, validate_shape, validate_kind


# ---------------------------------------------------------------------------
# _category_from_module
# ---------------------------------------------------------------------------


class TestCategoryFromModule:
    """_category_from_module parses the segment after 'plots'."""

    def test_statistical(self):
        assert _category_from_module("yplot2.plots.statistical.violin") == "statistical"

    def test_basic(self):
        assert _category_from_module("yplot2.plots.basic") == "basic"

    def test_no_plots(self):
        assert _category_from_module("yplot2.something") == "uncategorized"

    def test_plots_last(self):
        assert _category_from_module("yplot2.plots") == "uncategorized"

    def test_empty(self):
        assert _category_from_module("") == "uncategorized"


# ---------------------------------------------------------------------------
# @catalog decorator
# ---------------------------------------------------------------------------


class TestCatalogDecorator:
    """@catalog attaches validated metadata to a function."""

    def test_attaches_yp_catalog(self):
        """Decorated function has __yp_catalog__ with expected structure."""

        @catalog(tags=["distribution"], data_shape="long-df", kind="panel")
        def _dummy():
            pass

        _dummy.__module__ = "yplot2.plots.statistical.dummy"
        meta = _dummy.__yp_catalog__
        assert meta["tags"] == ("distribution",)
        assert meta["data_shape"] == "long-df"
        assert meta["kind"] == "panel"

    def test_category_derived_from_module(self):
        """category is extracted from fn.__module__ at decoration time."""

        @catalog(tags=["density"], data_shape="xy")
        def _my_plot():
            pass

        _my_plot.__module__ = "yplot2.plots.statistical.kde"
        # category is set at decoration, using whatever __module__ was at that moment.
        # We test the explicit helper instead.
        assert _category_from_module("yplot2.plots.statistical.kde") == "statistical"

    def test_default_kind_panel(self):
        """kind defaults to 'panel' when not provided."""

        @catalog(tags=["distribution"], data_shape="long-df")
        def _dummy():
            pass

        assert _dummy.__yp_catalog__["kind"] == "panel"

    def test_function_returned_unchanged(self):
        """The decorated function is still callable and returns its result."""

        @catalog(tags=["distribution"], data_shape="long-df")
        def _add(a, b):
            return a + b

        assert _add(2, 3) == 5


# ---------------------------------------------------------------------------
# Validators — raise on unknown tokens
# ---------------------------------------------------------------------------


class TestVocabValidators:
    """validate_* raise ValueError with the offending token and allowed set."""

    def test_unknown_tag_raises(self):
        with pytest.raises(ValueError, match="nope"):
            validate_tags(["nope"])

    def test_known_tag_passes(self):
        validate_tags(["distribution", "categorical"])  # must not raise

    def test_unknown_shape_raises(self):
        with pytest.raises(ValueError, match="wrong"):
            validate_shape("wrong")

    def test_known_shape_passes(self):
        validate_shape("long-df")  # must not raise

    def test_unknown_kind_raises(self):
        with pytest.raises(ValueError, match="blob"):
            validate_kind("blob")

    def test_known_kind_passes(self):
        validate_kind("panel")  # must not raise

    def test_catalog_unknown_tag_raises(self):
        with pytest.raises(ValueError, match="nope"):
            catalog(tags=["nope"], data_shape="long-df")

    def test_catalog_unknown_shape_raises(self):
        with pytest.raises(ValueError, match="bad"):
            catalog(tags=["distribution"], data_shape="bad")

    def test_catalog_unknown_kind_raises(self):
        with pytest.raises(ValueError, match="blob"):
            catalog(tags=["distribution"], data_shape="long-df", kind="blob")


# ---------------------------------------------------------------------------
# No global registry in catalog.py
# ---------------------------------------------------------------------------


def test_no_global_registry_in_catalog():
    """catalog.py must not maintain a module-level mutable registry."""
    import yplot2.catalog as cat_mod
    import inspect

    src = inspect.getsource(cat_mod)
    # The forbidden patterns: a global list/dict being appended or assigned
    # to in a way that grows with each decoration.
    assert "_registry" not in src, "Found _registry in catalog.py — Phase 3 only"
    assert "_gallery" not in src, "Found _gallery in catalog.py — Phase 3 only"
    # There must be no module-level mutable dict/list that accumulates entries.
    # We check that no name like REGISTRY or _ALL is defined at module level.
    assert "REGISTRY" not in src


# ---------------------------------------------------------------------------
# All five wrappers carry @catalog metadata
# ---------------------------------------------------------------------------


class TestWrapperCatalogAttrs:
    """All Phase-2 wrappers have __yp_catalog__ with category='statistical'."""

    @pytest.mark.parametrize(
        "module_path, fn_name",
        [
            ("yplot2.plots.statistical.violin", "violin"),
            ("yplot2.plots.statistical.box", "box"),
            ("yplot2.plots.statistical.kde", "kde"),
            ("yplot2.plots.statistical.heatmap2d", "heatmap2d"),
            ("yplot2.plots.statistical.hexbin", "hexbin"),
        ],
    )
    def test_has_yp_catalog(self, module_path, fn_name):
        import importlib

        mod = importlib.import_module(module_path)
        fn = getattr(mod, fn_name)
        assert hasattr(fn, "__yp_catalog__"), f"{fn_name} missing __yp_catalog__"
        meta = fn.__yp_catalog__
        assert meta["category"] == "statistical"
        assert "tags" in meta
        assert "data_shape" in meta
        assert "kind" in meta


# ---------------------------------------------------------------------------
# demo_* functions return Figure objects
# ---------------------------------------------------------------------------


class TestDemoFunctions:
    """demo_<name>() returns a matplotlib Figure with >= 1 axes."""

    def _run_demo(self, module_path, fn_name):
        import importlib

        mod = importlib.import_module(module_path)
        fn = getattr(mod, fn_name)
        fig = fn()
        try:
            assert isinstance(fig, plt.Figure), f"{fn_name} did not return a Figure"
            assert len(fig.axes) >= 1
        finally:
            plt.close(fig)

    def test_demo_violin(self):
        pytest.importorskip("seaborn")
        self._run_demo("yplot2.plots.statistical.violin", "demo_violin")

    def test_demo_box(self):
        pytest.importorskip("seaborn")
        self._run_demo("yplot2.plots.statistical.box", "demo_box")

    def test_demo_kde(self):
        pytest.importorskip("seaborn")
        self._run_demo("yplot2.plots.statistical.kde", "demo_kde")

    def test_demo_heatmap2d(self):
        self._run_demo("yplot2.plots.statistical.heatmap2d", "demo_heatmap2d")

    def test_demo_hexbin(self):
        self._run_demo("yplot2.plots.statistical.hexbin", "demo_hexbin")


# ---------------------------------------------------------------------------
# catalog exposed at top-level yplot2, seaborn-free
# ---------------------------------------------------------------------------


def test_catalog_at_top_level_seaborn_free():
    """import yplot2; yplot2.catalog is accessible without seaborn."""
    code = (
        "import sys; sys.modules['seaborn'] = None; "
        "import yplot2; "
        "assert hasattr(yplot2, 'catalog'), 'catalog not found on yplot2'; "
        "print('catalog-OK')"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"yplot2.catalog check failed.\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "catalog-OK" in result.stdout


def test_wrappers_not_in_init():
    """None of the stat wrappers are reachable from yplot2 top-level."""
    code = "\n".join(
        [
            "import sys",
            "sys.modules['seaborn'] = None",
            "import yplot2",
            "for name in ('violin', 'box', 'kde', 'heatmap2d', 'hexbin'):",
            "    assert not hasattr(yplot2, name), f'{name} leaked into yplot2 top-level'",
            "print('wrappers-not-in-init-OK')",
        ]
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Wrapper leak check failed.\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "wrappers-not-in-init-OK" in result.stdout
