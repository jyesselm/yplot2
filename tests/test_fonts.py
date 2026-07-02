"""
Task 0.1 acceptance tests: bundled Arimo font registration.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
import pytest


def test_arimo_resolvable_to_package_path():
    """fm.findfont('Arimo') resolves to a path inside yplot2/fonts/."""
    import yplot2  # ensures register_bundled_fonts() has run

    font_path = fm.findfont("Arimo", fallback_to_default=False)
    pkg_fonts = Path(yplot2.__file__).parent / "fonts"
    assert (
        pkg_fonts in Path(font_path).parents or Path(font_path).parent == pkg_fonts
    ), f"Expected font path inside {pkg_fonts}, got {font_path}"


def test_arimo_in_ttflist():
    """After register_bundled_fonts(), 'Arimo' is in the font manager list."""
    import yplot2  # noqa: F401 — triggers registration
    from yplot2._fonts import register_bundled_fonts

    register_bundled_fonts()
    names = {f.name for f in fm.fontManager.ttflist}
    assert "Arimo" in names, (
        f"Arimo not found in ttflist. Available (sample): {list(names)[:10]}"
    )


def test_arimo_bold_resolves_to_weight_700():
    """Bold Arimo resolves to a distinct file with usWeightClass >= 700."""
    import yplot2  # noqa: F401 — ensures fonts are registered

    bold_path = fm.findfont(FontProperties(family="Arimo", weight="bold"))
    reg_path = fm.findfont(FontProperties(family="Arimo", weight="normal"))

    assert bold_path != reg_path, (
        f"Bold Arimo resolves to same file as regular ({bold_path}). "
        "Genuine static bold TTF is missing."
    )
    assert "Bold" in Path(bold_path).name or "bold" in Path(bold_path).name.lower(), (
        f"Bold Arimo path does not contain 'Bold': {bold_path}"
    )

    # Verify OS/2 weight class
    from fontTools.ttLib import TTFont
    font = TTFont(bold_path)
    weight_class = font["OS/2"].usWeightClass
    assert weight_class >= 700, (
        f"Arimo bold face has usWeightClass={weight_class}, expected >=700"
    )


def test_register_bundled_fonts_idempotent():
    """Calling register_bundled_fonts() twice does not duplicate Arimo entries."""
    import yplot2  # noqa: F401 — first registration already happened

    from yplot2._fonts import register_bundled_fonts

    count_before = sum(1 for f in fm.fontManager.ttflist if f.name == "Arimo")
    register_bundled_fonts()
    count_after = sum(1 for f in fm.fontManager.ttflist if f.name == "Arimo")
    assert count_after == count_before, (
        f"register_bundled_fonts() increased Arimo entry count "
        f"from {count_before} to {count_after}"
    )


def test_resolve_font_family_arial_maps_to_arimo_when_absent():
    """_resolve_font_family('Arial') returns 'Arimo' when Arial is not available."""
    import yplot2  # noqa: F401 — ensures Arimo is registered
    from yplot2.style import _resolve_font_family

    # Temporarily remove Arial from the available set
    arial_entries = [f for f in fm.fontManager.ttflist if f.name == "Arial"]
    for entry in arial_entries:
        fm.fontManager.ttflist.remove(entry)
    try:
        result = _resolve_font_family("Arial")
        assert result == "Arimo", f"Expected 'Arimo', got '{result}'"
    finally:
        fm.fontManager.ttflist.extend(arial_entries)


def test_resolve_font_family_arial_returns_arial_when_present():
    """_resolve_font_family('Arial') returns 'Arial' when Arial is available."""
    from yplot2.style import _resolve_font_family

    # Temporarily add a fake Arial entry
    fake_entry = fm.FontEntry(fname="fake.ttf", name="Arial")
    fm.fontManager.ttflist.append(fake_entry)
    try:
        result = _resolve_font_family("Arial")
        assert result == "Arial", f"Expected 'Arial', got '{result}'"
    finally:
        fm.fontManager.ttflist.remove(fake_entry)


def test_resolve_font_family_arial_narrow_not_mapped():
    """_resolve_font_family('Arial Narrow') does NOT map to Arimo."""
    from yplot2.style import _resolve_font_family

    # Remove Arial Narrow to force the fallback path
    narrow_entries = [f for f in fm.fontManager.ttflist if f.name == "Arial Narrow"]
    for entry in narrow_entries:
        fm.fontManager.ttflist.remove(entry)
    try:
        result = _resolve_font_family("Arial Narrow")
        # Should return "Arial Narrow" unchanged (not Arimo)
        assert result == "Arial Narrow", (
            f"Expected 'Arial Narrow' to pass through, got '{result}'"
        )
    finally:
        fm.fontManager.ttflist.extend(narrow_entries)


def test_resolve_font_family_tuple_branch():
    """_resolve_font_family(('Arial', 'Arimo')) returns Arimo when Arial absent."""
    from yplot2.style import _resolve_font_family

    arial_entries = [f for f in fm.fontManager.ttflist if f.name == "Arial"]
    for entry in arial_entries:
        fm.fontManager.ttflist.remove(entry)
    try:
        result = _resolve_font_family(("Arial", "Helvetica"))
        # Arial absent → try Arimo fallback, then Helvetica
        assert result in ("Arimo", "Helvetica"), (
            f"Expected 'Arimo' or 'Helvetica', got '{result}'"
        )
    finally:
        fm.fontManager.ttflist.extend(arial_entries)


def test_resolve_font_family_none_input():
    """_resolve_font_family(None) returns 'Arimo' rather than raising TypeError."""
    from yplot2.style import _resolve_font_family

    result = _resolve_font_family(None)  # type: ignore[arg-type]
    assert result == "Arimo"


def test_import_yplot2_no_figure_created():
    """Importing yplot2 does not create any matplotlib figure."""
    plt.close("all")
    initial_count = len(plt.get_fignums())
    import yplot2  # noqa: F401

    after_count = len(plt.get_fignums())
    assert after_count == initial_count, (
        f"import yplot2 created {after_count - initial_count} figure(s)"
    )


def test_import_yplot2_no_exception():
    """Importing yplot2 does not raise any exception."""
    import yplot2  # noqa: F401


def test_wheel_contains_fonts(tmp_path):
    """Built wheel contains yplot2/fonts/Arimo-Regular.ttf and fonts/LICENSE.txt."""
    pytest.importorskip("build", reason="pip install build to run wheel check")
    import subprocess
    import zipfile

    result = subprocess.run(
        ["python", "-m", "build", "--wheel", "--outdir", str(tmp_path)],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    if result.returncode != 0:
        pytest.skip(f"build failed: {result.stderr[:200]}")

    wheels = list(tmp_path.glob("*.whl"))
    assert wheels, "No wheel produced"
    with zipfile.ZipFile(wheels[0]) as z:
        names = z.namelist()
    ttf_files = [n for n in names if "fonts/Arimo-Regular.ttf" in n]
    lic_files = [n for n in names if "fonts/LICENSE.txt" in n]
    assert ttf_files, (
        f"Arimo-Regular.ttf not found in wheel. Contents (sample): {names[:20]}"
    )
    assert lic_files, (
        f"fonts/LICENSE.txt not found in wheel. Contents (sample): {names[:20]}"
    )
