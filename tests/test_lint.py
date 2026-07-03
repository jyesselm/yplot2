"""
Tests for yplot2.lint — anti-fork AST lint.

Each rule has a true-positive and a near-miss (false-positive guard) test.
Integration tests use a "bad" plotting.py pattern and a "good" yplot2 script.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from yplot2.lint import (
    Finding,
    Level,
    _dotted_name,
    _filter_codes,
    _format,
    _is_hex_palette_dict,
    check_file,
    check_paths,
    check_source,
    main,
)

# ---------------------------------------------------------------------------
# Source snippets used across tests
# ---------------------------------------------------------------------------

_BAD_PLOTTING = """\
import matplotlib.pyplot as plt
import seaborn as sns

def publication_style_ax(ax):
    ax.spines["top"].set_visible(False)

def format_small_plot(ax):
    fig, ax2 = plt.subplots(figsize=(1.50, 1.25), dpi=200)
    plt.subplots_adjust(left=0.3, bottom=0.21, top=0.98)

def plot_something(df, ax):
    fig, ax3 = plt.subplots(figsize=(2.0, 1.5), dpi=200)
    sns.violinplot(x="x", y="y", data=df, ax=ax3)
"""

_GOOD_YPLOT2_SCRIPT = """\
import yplot2 as yp

fig, ax = yp.subplots(subplotsize=(2, 1.5))
yp.finish(ax)
yp.save(fig, "f.png", source=__file__)
"""

# ---------------------------------------------------------------------------
# AST helper tests
# ---------------------------------------------------------------------------


def test_dotted_name_resolves_name() -> None:
    """_dotted_name returns bare identifier for ast.Name nodes."""
    import ast

    node = ast.parse("foo", mode="eval").body
    assert _dotted_name(node) == "foo"  # type: ignore[arg-type]


def test_dotted_name_resolves_attribute() -> None:
    """_dotted_name resolves dotted attribute chains to a string."""
    import ast

    node = ast.parse("plt.subplots", mode="eval").body
    assert _dotted_name(node) == "plt.subplots"  # type: ignore[arg-type]


def test_dotted_name_none_for_call() -> None:
    """_dotted_name returns None for non-name expressions like Call nodes."""
    import ast

    node = ast.parse("foo()()", mode="eval").body
    # outer call's func is also a Call
    assert _dotted_name(node) is None  # type: ignore[arg-type]


def test_is_hex_palette_dict_true() -> None:
    """_is_hex_palette_dict returns True for a dict with ≥2 hex string values."""
    import ast

    node = ast.parse('{"A": "#ff0000", "B": "#00ff00"}', mode="eval").body
    assert _is_hex_palette_dict(node)  # type: ignore[arg-type]


def test_is_hex_palette_dict_false_single_hex() -> None:
    """_is_hex_palette_dict returns False when only 1 hex value is present."""
    import ast

    node = ast.parse('{"A": "#ff0000", "B": "red"}', mode="eval").body
    assert not _is_hex_palette_dict(node)  # type: ignore[arg-type]


def test_is_hex_palette_dict_false_no_hex() -> None:
    """_is_hex_palette_dict returns False for named-color dict (real-file pattern)."""
    import ast

    node = ast.parse('{"A": "red", "C": "blue"}', mode="eval").body
    assert not _is_hex_palette_dict(node)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# YP001 — house-style function definitions
# ---------------------------------------------------------------------------


def test_yp001_flags_publication_style_ax() -> None:
    """YP001 fires on def publication_style_ax(...)."""
    findings = check_source("def publication_style_ax(ax): pass", "f.py")
    codes = [f.code for f in findings]
    assert "YP001" in codes


def test_yp001_flags_format_small_plot() -> None:
    """YP001 fires on def format_small_plot(...)."""
    findings = check_source("def format_small_plot(ax): pass", "f.py")
    assert any(f.code == "YP001" for f in findings)


def test_yp001_flags_publication_style() -> None:
    """YP001 fires on def publication_style(...)."""
    findings = check_source("def publication_style(ax): pass", "f.py")
    assert any(f.code == "YP001" for f in findings)


def test_yp001_flags_publication_scatter() -> None:
    """YP001 fires on def publication_scatter(...)."""
    findings = check_source("def publication_scatter(ax, x, y): pass", "f.py")
    assert any(f.code == "YP001" for f in findings)


def test_yp001_flags_publication_line() -> None:
    """YP001 fires on def publication_line(...)."""
    findings = check_source("def publication_line(ax, x, y): pass", "f.py")
    assert any(f.code == "YP001" for f in findings)


def test_yp001_ignores_ordinary_def() -> None:
    """YP001 does NOT fire on unrelated function names."""
    findings = check_source("def apply_style(ax): pass", "f.py")
    assert not any(f.code == "YP001" for f in findings)


def test_yp001_ignores_partial_name_match() -> None:
    """YP001 uses exact-name matching, not substring; prefix matches must not fire."""
    findings = check_source("def pub_style_ax(ax): pass", "f.py")
    assert not any(f.code == "YP001" for f in findings)


def test_yp001_is_error_level() -> None:
    """YP001 findings carry ERROR level."""
    findings = check_source("def publication_style_ax(ax): pass", "f.py")
    yp001 = [f for f in findings if f.code == "YP001"]
    assert all(f.level == Level.ERROR for f in yp001)


# ---------------------------------------------------------------------------
# YP002 — inline figsize on plt callers
# ---------------------------------------------------------------------------


def test_yp002_flags_plt_subplots_figsize() -> None:
    """YP002 fires on plt.subplots(figsize=(...))."""
    src = "import matplotlib.pyplot as plt\nfig, ax = plt.subplots(figsize=(2, 1.5))\n"
    findings = check_source(src, "f.py")
    assert any(f.code == "YP002" for f in findings)


def test_yp002_flags_plt_figure_figsize() -> None:
    """YP002 fires on plt.figure(figsize=(...))."""
    src = "import matplotlib.pyplot as plt\nfig = plt.figure(figsize=(4, 3))\n"
    findings = check_source(src, "f.py")
    assert any(f.code == "YP002" for f in findings)


def test_yp002_not_flag_yp_subplots_subplotsize() -> None:
    """YP002 must NOT fire on yp.subplots(subplotsize=(...)) — correct yplot2 usage."""
    src = "import yplot2 as yp\nfig, ax = yp.subplots(subplotsize=(2, 1.5))\n"
    findings = check_source(src, "f.py")
    assert not any(f.code == "YP002" for f in findings)


def test_yp002_not_flag_variable_figsize_on_plt() -> None:
    """YP002 does NOT fire when figsize= is a variable (not a tuple/list literal)."""
    src = "import matplotlib.pyplot as plt\nfig, ax = plt.subplots(figsize=my_size)\n"
    findings = check_source(src, "f.py")
    assert not any(f.code == "YP002" for f in findings)


def test_yp002_not_flag_non_plt_callee() -> None:
    """YP002 does NOT fire for df.plot(figsize=(...)) — wrong callee."""
    src = "ax = df.plot(kind='bar', figsize=(10, 4))\n"
    findings = check_source(src, "f.py")
    assert not any(f.code == "YP002" for f in findings)


def test_yp002_not_flag_function_default_param() -> None:
    """YP002 does NOT fire on figsize=(2,1.5) as a function default parameter."""
    src = "def make_plot(figsize=(2, 1.5)): pass\n"
    findings = check_source(src, "f.py")
    assert not any(f.code == "YP002" for f in findings)


def test_yp002_is_warning_level() -> None:
    """YP002 findings carry WARNING level."""
    src = "import matplotlib.pyplot as plt\nfig, ax = plt.subplots(figsize=(2, 1.5))\n"
    findings = check_source(src, "f.py")
    yp002 = [f for f in findings if f.code == "YP002"]
    assert all(f.level == Level.WARNING for f in yp002)


# ---------------------------------------------------------------------------
# YP003 — subplots_adjust
# ---------------------------------------------------------------------------


def test_yp003_flags_subplots_adjust() -> None:
    """YP003 fires on plt.subplots_adjust(...)."""
    src = "import matplotlib.pyplot as plt\nplt.subplots_adjust(left=0.3)\n"
    findings = check_source(src, "f.py")
    assert any(f.code == "YP003" for f in findings)


def test_yp003_flags_bare_subplots_adjust() -> None:
    """YP003 fires on a bare subplots_adjust() call (imported directly)."""
    src = "from matplotlib.pyplot import subplots_adjust\nsubplots_adjust(left=0.3)\n"
    findings = check_source(src, "f.py")
    assert any(f.code == "YP003" for f in findings)


def test_yp003_not_flag_unrelated_call() -> None:
    """YP003 does NOT fire on unrelated function names."""
    src = "fig.tight_layout()\n"
    findings = check_source(src, "f.py")
    assert not any(f.code == "YP003" for f in findings)


def test_yp003_is_warning_level() -> None:
    """YP003 findings carry WARNING level."""
    src = "import matplotlib.pyplot as plt\nplt.subplots_adjust(left=0.3)\n"
    findings = check_source(src, "f.py")
    yp003 = [f for f in findings if f.code == "YP003"]
    assert all(f.level == Level.WARNING for f in yp003)


# ---------------------------------------------------------------------------
# YP004 — raw savefig
# ---------------------------------------------------------------------------


def test_yp004_flags_fig_savefig() -> None:
    """YP004 fires on fig.savefig(...)."""
    src = 'fig.savefig("out.png")\n'
    findings = check_source(src, "f.py")
    assert any(f.code == "YP004" for f in findings)


def test_yp004_flags_plt_savefig() -> None:
    """YP004 fires on plt.savefig(...)."""
    src = 'import matplotlib.pyplot as plt\nplt.savefig("out.png")\n'
    findings = check_source(src, "f.py")
    assert any(f.code == "YP004" for f in findings)


def test_yp004_not_flag_yp_save() -> None:
    """YP004 must NOT fire on yp.save(...) — correct yplot2 usage."""
    src = 'import yplot2 as yp\nyp.save(fig, "f.png", source=__file__)\n'
    findings = check_source(src, "f.py")
    assert not any(f.code == "YP004" for f in findings)


def test_yp004_is_warning_level() -> None:
    """YP004 findings carry WARNING level."""
    src = 'fig.savefig("out.png")\n'
    findings = check_source(src, "f.py")
    yp004 = [f for f in findings if f.code == "YP004"]
    assert all(f.level == Level.WARNING for f in yp004)


# ---------------------------------------------------------------------------
# YP005 — hardcoded hex palette
# ---------------------------------------------------------------------------


def test_yp005_flags_hex_dict() -> None:
    """YP005 fires on a dict with ≥2 hex string values."""
    src = 'palette = {"A": "#ff0000", "C": "#0000ff"}\n'
    findings = check_source(src, "f.py")
    assert any(f.code == "YP005" for f in findings)


def test_yp005_flags_palette_kwarg_with_hex_dict() -> None:
    """YP005 fires exactly ONCE on palette={hex,hex} — no double-report from visit_Dict."""
    src = 'sns.boxplot(data=df, palette={"A": "#ff0000", "C": "#0000ff"})\n'
    findings = check_source(src, "f.py")
    # Must fire exactly once — visit_Dict catches it; _check_palette_kw no longer exists.
    assert [f.code for f in findings].count("YP005") == 1


def test_yp005_not_flag_named_color_dict() -> None:
    """YP005 does NOT fire for named-color dicts (real-file pattern like {'A': 'red'})."""
    src = 'palette = {"A": "red", "C": "blue", "G": "orange", "U": "green"}\n'
    findings = check_source(src, "f.py")
    assert not any(f.code == "YP005" for f in findings)


def test_yp005_not_flag_single_hex() -> None:
    """YP005 does NOT fire when only one hex value is in the dict (≥2 required)."""
    src = 'palette = {"A": "#ff0000", "C": "blue"}\n'
    findings = check_source(src, "f.py")
    assert not any(f.code == "YP005" for f in findings)


def test_yp005_not_flag_rgba_tuple_dict() -> None:
    """YP005 does NOT fire for RGBA-tuple palette dicts (real-file pattern)."""
    src = 'palette = {"TMO": (0.70, 0.0, 0.0, 1.0), "A": (0.0, 0.0, 1.0, 1.0)}\n'
    findings = check_source(src, "f.py")
    assert not any(f.code == "YP005" for f in findings)


def test_yp005_is_warning_level() -> None:
    """YP005 findings carry WARNING level."""
    src = 'palette = {"A": "#ff0000", "C": "#0000ff"}\n'
    findings = check_source(src, "f.py")
    yp005 = [f for f in findings if f.code == "YP005"]
    assert all(f.level == Level.WARNING for f in yp005)


# ---------------------------------------------------------------------------
# YP006 — raw seaborn (opt-in only)
# ---------------------------------------------------------------------------


def test_yp006_present_in_raw_check_source() -> None:
    """YP006 appears in raw check_source output (before opt-in filtering)."""
    src = "import seaborn as sns\nsns.violinplot(x='x', y='y', data=df)\n"
    findings = check_source(src, "f.py")
    assert any(f.code == "YP006" for f in findings)


def test_yp006_absent_by_default_via_filter() -> None:
    """YP006 is dropped by _filter_codes when no explicit select is given."""
    src = "import seaborn as sns\nsns.violinplot(x='x', y='y', data=df)\n"
    findings = check_source(src, "f.py")
    filtered = _filter_codes(findings, select=None, ignore=None)
    assert not any(f.code == "YP006" for f in filtered)


def test_yp006_fires_with_explicit_select() -> None:
    """YP006 is present after _filter_codes when select includes YP006."""
    src = "import seaborn as sns\nsns.violinplot(x='x', y='y', data=df)\n"
    findings = check_source(src, "f.py")
    filtered = _filter_codes(findings, select={"YP006"}, ignore=None)
    assert any(f.code == "YP006" for f in filtered)


def test_yp006_flags_sns_boxplot() -> None:
    """YP006 fires in raw output for sns.boxplot(...)."""
    src = "import seaborn as sns\nsns.boxplot(x='x', y='y', data=df)\n"
    findings = check_source(src, "f.py")
    assert any(f.code == "YP006" for f in findings)


def test_yp006_flags_sns_stripplot() -> None:
    """YP006 fires in raw output for sns.stripplot(...)."""
    src = "import seaborn as sns\nsns.stripplot(x='x', y='y', data=df)\n"
    findings = check_source(src, "f.py")
    assert any(f.code == "YP006" for f in findings)


def test_yp006_is_warning_level() -> None:
    """YP006 findings carry WARNING level."""
    src = "import seaborn as sns\nsns.violinplot(x='x', y='y', data=df)\n"
    findings = check_source(src, "f.py")
    yp006 = [f for f in findings if f.code == "YP006"]
    assert all(f.level == Level.WARNING for f in yp006)


# ---------------------------------------------------------------------------
# Ignore mechanism
# ---------------------------------------------------------------------------


def test_ignore_all_on_line() -> None:
    """# yplot2: ignore suppresses all findings on that line."""
    src = "def publication_style_ax(ax): pass  # yplot2: ignore\n"
    findings = check_source(src, "f.py")
    assert not any(f.code == "YP001" for f in findings)


def test_ignore_specific_code() -> None:
    """# yplot2: ignore=YP001 suppresses only YP001 on that line."""
    src = (
        "import matplotlib.pyplot as plt\n"
        "fig, ax = plt.subplots(figsize=(2, 1.5))  # yplot2: ignore=YP002\n"
    )
    findings = check_source(src, "f.py")
    assert not any(f.code == "YP002" for f in findings)


def test_ignore_specific_code_keeps_other_codes() -> None:
    """# yplot2: ignore=YP003 keeps YP002 on a line that has both (separate lines here)."""
    src = (
        "import matplotlib.pyplot as plt\n"
        "def publication_style_ax(ax): pass  # yplot2: ignore=YP003\n"
    )
    # YP001 is NOT in the suppress list, so it should survive
    findings = check_source(src, "f.py")
    assert any(f.code == "YP001" for f in findings)


def test_ignore_multi_code() -> None:
    """# yplot2: ignore=YP002,YP003 suppresses both codes on the line."""
    src = (
        "import matplotlib.pyplot as plt\n"
        "plt.subplots_adjust(left=0.3)  # yplot2: ignore=YP002,YP003\n"
    )
    findings = check_source(src, "f.py")
    assert not any(f.code in ("YP002", "YP003") for f in findings)


# ---------------------------------------------------------------------------
# Selection and filtering
# ---------------------------------------------------------------------------


def test_select_keeps_only_listed() -> None:
    """_filter_codes with select={'YP001'} drops all other codes."""
    src = (
        "def publication_style_ax(ax): pass\n"
        "import matplotlib.pyplot as plt\n"
        "plt.subplots_adjust(left=0.3)\n"
    )
    findings = check_source(src, "f.py")
    filtered = _filter_codes(findings, select={"YP001"}, ignore=None)
    codes = {f.code for f in filtered}
    assert codes == {"YP001"}


def test_ignore_removes_code() -> None:
    """_filter_codes with ignore={'YP003'} removes YP003 from output."""
    src = (
        "def publication_style_ax(ax): pass\n"
        "import matplotlib.pyplot as plt\n"
        "plt.subplots_adjust(left=0.3)\n"
    )
    findings = check_source(src, "f.py")
    filtered = _filter_codes(findings, select=None, ignore={"YP003"})
    assert not any(f.code == "YP003" for f in filtered)
    assert any(f.code == "YP001" for f in filtered)


# ---------------------------------------------------------------------------
# File and path plumbing
# ---------------------------------------------------------------------------


def test_check_file_reads_source(tmp_path: Path) -> None:
    """check_file returns findings for a .py file on disk."""
    f = tmp_path / "bad.py"
    f.write_text("def publication_style_ax(ax): pass\n")
    findings = check_file(f)
    assert any(f2.code == "YP001" for f2 in findings)


def test_check_file_syntax_error_yields_yp000(tmp_path: Path) -> None:
    """check_file yields a single YP000 WARNING when the file has a syntax error."""
    f = tmp_path / "broken.py"
    f.write_text("def bad(:\n")
    findings = check_file(f)
    assert len(findings) == 1
    assert findings[0].code == "YP000"
    assert findings[0].level == Level.WARNING


def test_check_paths_walks_directory(tmp_path: Path) -> None:
    """check_paths recurses into directories and lints .py files."""
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "plot.py").write_text("def publication_style_ax(ax): pass\n")
    findings = check_paths([tmp_path])
    assert any(f.code == "YP001" for f in findings)


def test_check_paths_skips_excluded_dirs(tmp_path: Path) -> None:
    """check_paths skips __pycache__, .venv, build, node_modules, *.egg-info dirs."""
    for skip_dir in ("__pycache__", ".venv", "build", "node_modules", "mypkg.egg-info"):
        d = tmp_path / skip_dir
        d.mkdir()
        (d / "plot.py").write_text("def publication_style_ax(ax): pass\n")
    findings = check_paths([tmp_path])
    assert not any(f.code == "YP001" for f in findings)


def test_check_paths_lints_top_level_file(tmp_path: Path) -> None:
    """check_paths accepts a single file path directly."""
    f = tmp_path / "myplot.py"
    f.write_text("def publication_style_ax(ax): pass\n")
    findings = check_paths([f])
    assert any(f2.code == "YP001" for f2 in findings)


def test_syntax_error_yields_yp000_warning() -> None:
    """check_source returns a YP000 WARNING on unparseable source."""
    findings = check_source("def bad(:\n", "broken.py")
    assert len(findings) == 1
    assert findings[0].code == "YP000"
    assert findings[0].level == Level.WARNING


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def test_format_includes_all_fields() -> None:
    """_format output contains path, line, code, level, and message."""
    f = Finding(
        path="a/b.py",
        line=10,
        end_line=10,
        code="YP001",
        message="msg",
        level=Level.ERROR,
    )
    out = _format(f)
    assert "a/b.py" in out
    assert ":10:" in out
    assert "YP001" in out
    assert "error" in out
    assert "msg" in out


# ---------------------------------------------------------------------------
# CLI main() tests
# ---------------------------------------------------------------------------


def test_main_exit_1_on_error(tmp_path: Path) -> None:
    """main() returns 1 when a YP001 ERROR-level finding is present."""
    f = tmp_path / "bad.py"
    f.write_text("def publication_style_ax(ax): pass\n")
    rc = main([str(f)])
    assert rc == 1


def test_main_exit_0_on_warning_only(tmp_path: Path) -> None:
    """main() returns 0 when only WARNING-level findings are present (YP002/YP003)."""
    f = tmp_path / "warn.py"
    f.write_text(
        "import matplotlib.pyplot as plt\n"
        "fig, ax = plt.subplots(figsize=(2, 1.5))\n"
        "plt.subplots_adjust(left=0.3)\n"
    )
    rc = main([str(f)])
    assert rc == 0


def test_main_yp006_absent_by_default(tmp_path: Path) -> None:
    """main() drops YP006 by default (opt-in only)."""
    f = tmp_path / "sns_plot.py"
    f.write_text("import seaborn as sns\nsns.violinplot(x='x', y='y', data=df)\n")
    rc = main([str(f)])
    # exit 0 because YP006 is filtered out (no ERROR) and no other findings
    assert rc == 0


def test_main_yp006_present_with_select(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """main() includes YP006 when --select YP006 is given."""
    f = tmp_path / "sns_plot.py"
    f.write_text("import seaborn as sns\nsns.violinplot(x='x', y='y', data=df)\n")
    rc = main([str(f), "--select", "YP006"])
    captured = capsys.readouterr()
    assert "YP006" in captured.out
    assert rc == 0  # YP006 is WARNING, not ERROR


def test_main_no_paths_usage_returns_1(capsys: pytest.CaptureFixture) -> None:
    """main() prints usage to stderr and returns 1 when no paths given."""
    rc = main([])
    captured = capsys.readouterr()
    assert rc == 1
    assert "Usage" in captured.err


def test_main_clean_source_returns_0(tmp_path: Path) -> None:
    """main() returns 0 on a clean yplot2 script with no anti-patterns."""
    f = tmp_path / "clean.py"
    f.write_text(_GOOD_YPLOT2_SCRIPT)
    rc = main([str(f)])
    assert rc == 0


def test_main_select_flag(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """main() with --select YP001 only prints YP001 findings."""
    f = tmp_path / "mixed.py"
    f.write_text(
        "def publication_style_ax(ax): pass\n"
        "import matplotlib.pyplot as plt\n"
        "plt.subplots_adjust(left=0.3)\n"
    )
    rc = main([str(f), "--select", "YP001"])
    captured = capsys.readouterr()
    assert "YP001" in captured.out
    assert "YP003" not in captured.out
    assert rc == 1


def test_main_ignore_flag(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """main() with --ignore YP001 suppresses YP001 and exits 0."""
    f = tmp_path / "err.py"
    f.write_text("def publication_style_ax(ax): pass\n")
    rc = main([str(f), "--ignore", "YP001"])
    captured = capsys.readouterr()
    assert "YP001" not in captured.out
    assert rc == 0


# ---------------------------------------------------------------------------
# Integration acceptance tests
# ---------------------------------------------------------------------------


def test_bad_plotting_triggers_expected_codes() -> None:
    """YP001×2, YP002×2, YP003 appear in bad plotting source; YP006 absent by default."""
    findings = check_source(_BAD_PLOTTING, "plotting.py")
    filtered = _filter_codes(findings, select=None, ignore=None)
    codes = [f.code for f in filtered]
    # Exactly two YP001 (publication_style_ax + format_small_plot)
    assert codes.count("YP001") == 2
    # Two plt.subplots(figsize=...) calls
    assert codes.count("YP002") == 2
    # One plt.subplots_adjust
    assert codes.count("YP003") == 1
    # YP006 absent by default
    assert "YP006" not in codes


def test_yp006_fires_only_with_select() -> None:
    """YP006 fires on the bad source only when select={"YP006"} is passed."""
    findings = check_source(_BAD_PLOTTING, "plotting.py")
    filtered = _filter_codes(findings, select={"YP006"}, ignore=None)
    assert any(f.code == "YP006" for f in filtered)


def test_good_yplot2_script_is_clean() -> None:
    """A correct yplot2 script produces zero findings after filtering."""
    findings = check_source(_GOOD_YPLOT2_SCRIPT, "clean.py")
    filtered = _filter_codes(findings, select=None, ignore=None)
    assert filtered == []


# ---------------------------------------------------------------------------
# Multi-line ignore (Fix 2) — ignore marker on any line of the node's span
# ---------------------------------------------------------------------------


def test_yp002_multiline_ignore_bare_on_inner_line() -> None:
    """# yplot2: ignore on the figsize= line of a multi-line plt.subplots suppresses YP002."""
    src = (
        "import matplotlib.pyplot as plt\n"
        "fig, ax = plt.subplots(\n"
        "    figsize=(2, 2),  # yplot2: ignore\n"
        ")\n"
    )
    findings = check_source(src, "f.py")
    assert not any(f.code == "YP002" for f in findings)


def test_yp002_multiline_ignore_specific_code_on_inner_line() -> None:
    """# yplot2: ignore=YP002 on the figsize= line of a multi-line call suppresses YP002."""
    src = (
        "import matplotlib.pyplot as plt\n"
        "fig, ax = plt.subplots(\n"
        "    figsize=(2, 2),  # yplot2: ignore=YP002\n"
        ")\n"
    )
    findings = check_source(src, "f.py")
    assert not any(f.code == "YP002" for f in findings)


def test_yp002_multiline_ignore_wrong_code_does_not_suppress() -> None:
    """# yplot2: ignore=YP003 on inner line does NOT suppress YP002."""
    src = (
        "import matplotlib.pyplot as plt\n"
        "fig, ax = plt.subplots(\n"
        "    figsize=(2, 2),  # yplot2: ignore=YP003\n"
        ")\n"
    )
    findings = check_source(src, "f.py")
    assert any(f.code == "YP002" for f in findings)


def test_yp002_multiline_ignore_on_call_start_line() -> None:
    """# yplot2: ignore on the call's opening line also suppresses YP002."""
    src = (
        "import matplotlib.pyplot as plt\n"
        "fig, ax = plt.subplots(  # yplot2: ignore\n"
        "    figsize=(2, 2),\n"
        ")\n"
    )
    findings = check_source(src, "f.py")
    assert not any(f.code == "YP002" for f in findings)


# ---------------------------------------------------------------------------
# Bad path handling (Fix 3) — explicit non-existent paths must error
# ---------------------------------------------------------------------------


def test_main_bad_path_returns_nonzero(capsys: pytest.CaptureFixture) -> None:
    """main() returns 1 and prints an error when a path does not exist."""
    rc = main(["/no/such/file.py"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "error" in captured.err.lower()
    assert "/no/such/file.py" in captured.err


def test_main_bad_path_message_to_stderr(capsys: pytest.CaptureFixture) -> None:
    """main() writes 'path not found' message to stderr for a missing path."""
    rc = main(["/does/not/exist.py"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "not found" in captured.err


def test_main_mixed_good_and_bad_paths_returns_nonzero(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """main() returns nonzero even when some paths exist but one does not."""
    good = tmp_path / "clean.py"
    good.write_text("x = 1\n")
    rc = main([str(good), "/no/such.py"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "not found" in captured.err


# ---------------------------------------------------------------------------
# Documented limitations (SHOULD) — intentional known misses
# ---------------------------------------------------------------------------


def test_yp002_aliased_mpl_not_flagged() -> None:
    """YP002 does NOT fire on mpl.subplots(figsize=(2,2)) — aliased import not in callee set."""
    src = "import matplotlib as mpl\nfig, ax = mpl.subplots(figsize=(2, 2))\n"
    findings = check_source(src, "f.py")
    assert not any(f.code == "YP002" for f in findings)


def test_yp002_fully_qualified_not_flagged() -> None:
    """YP002 does NOT fire on matplotlib.pyplot.subplots() — fully qualified name not matched."""
    src = "import matplotlib.pyplot\nfig, ax = matplotlib.pyplot.subplots(figsize=(2, 2))\n"
    findings = check_source(src, "f.py")
    assert not any(f.code == "YP002" for f in findings)


def test_yp002_from_import_not_flagged() -> None:
    """YP002 does NOT fire on bare subplots(figsize=(2,2)) from a from-import."""
    src = "from matplotlib.pyplot import subplots\nfig, ax = subplots(figsize=(2, 2))\n"
    findings = check_source(src, "f.py")
    assert not any(f.code == "YP002" for f in findings)


def test_yp001_fires_in_class_body() -> None:
    """YP001 fires on def publication_style_ax(self) defined inside a class."""
    src = "class Plotter:\n    def publication_style_ax(self, ax):\n        pass\n"
    findings = check_source(src, "f.py")
    assert any(f.code == "YP001" for f in findings)


def test_yp004_fires_on_arbitrary_receiver() -> None:
    """YP004 fires on logger.savefig('x') — tail-name match is current behavior."""
    # This is intentional: savefig is mpl-specific enough in practice.
    src = 'logger.savefig("x")\n'
    findings = check_source(src, "f.py")
    assert any(f.code == "YP004" for f in findings)


# ---------------------------------------------------------------------------
# Seaborn-free import test for lint.py
# ---------------------------------------------------------------------------


def test_lint_import_with_seaborn_blocked() -> None:
    """yplot2.lint imports successfully even when seaborn is made unimportable."""
    code = "import sys; sys.modules['seaborn'] = None; import yplot2.lint; print('OK')"
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"import yplot2.lint failed with seaborn blocked.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "OK" in result.stdout
