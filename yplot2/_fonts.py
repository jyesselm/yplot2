"""
Bundled font registration for yplot2.

Registers the vendored Arimo TTFs (OFL-1.1) with matplotlib so that the
house font is always available, independent of the host system.
"""

from pathlib import Path
import matplotlib.font_manager as fm

_FONT_DIR = Path(__file__).parent / "fonts"


def register_bundled_fonts() -> None:
    """Register bundled Arimo with matplotlib.

    Idempotent: fonts already registered by path are skipped, so calling
    this multiple times (e.g. on module reload) does not accumulate duplicate
    entries in fontManager.ttflist.
    """
    registered_paths = {f.fname for f in fm.fontManager.ttflist}
    for ttf in _FONT_DIR.glob("*.ttf"):
        if str(ttf) in registered_paths:
            continue
        try:
            fm.fontManager.addfont(str(ttf))
        except Exception:
            pass  # never break import on a font hiccup
