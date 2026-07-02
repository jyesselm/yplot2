"""
Provenance-stamping save function for yplot2 figures.

Enforces dpi, white facecolor, and stamps provenance (source path, git SHA,
optional data hashes) into PNG tEXt chunks or PDF info dict.

Output is deterministic: no wall-clock timestamps are written. Strict
byte-identical PDFs additionally require the ``SOURCE_DATE_EPOCH`` environment
variable (matplotlib honors it for font stream dates).

PURE module: only stdlib imports at module level.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import matplotlib.figure


_SUPPORTED_SUFFIXES = frozenset({".png", ".pdf"})


def _git_sha(start_dir: str | os.PathLike[str]) -> str | None:
    """Return best-effort git SHA from *start_dir*; None on any failure.

    Never raises — absorbs all exceptions including timeout, missing git, or
    running outside a repo.

    Args:
        start_dir: Directory passed to ``git -C`` as the working directory.

    Returns:
        40-char SHA (optionally suffixed with ``-dirty``) or None.
    """
    try:
        head = subprocess.run(
            ["git", "-C", str(start_dir), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if head.returncode != 0:
            return None
        sha = head.stdout.strip()
        dirty = subprocess.run(
            ["git", "-C", str(start_dir), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if dirty.returncode == 0 and dirty.stdout.strip():
            sha += "-dirty"
        return sha
    except Exception:
        return None


def _resolve_source(source: str | None) -> str:
    """Return *source* if given, else sys.argv[0]; falls back to 'unknown'.

    Args:
        source: Caller-supplied source path, or None.

    Returns:
        Non-empty string identifying the originating script.
    """
    if source:
        return source
    argv0 = sys.argv[0] if sys.argv else ""
    return argv0 or "unknown"


def _hash_str(data_hashes: dict[str, str] | None) -> str:
    """Encode *data_hashes* as a stable 'k=v;k2=v2' string (sorted keys).

    Args:
        data_hashes: Optional mapping of dataset name to hash string.

    Returns:
        Semicolon-delimited string, or '' when data_hashes is None/empty.
    """
    if not data_hashes:
        return ""
    return ";".join(f"{k}={v}" for k, v in sorted(data_hashes.items()))


def _build_provenance(
    source: str | None,
    data_hashes: dict[str, str] | None,
) -> dict[str, str]:
    """Assemble ordered provenance dict; looks up git SHA relative to *source*.

    Args:
        source: Caller-supplied source path (or None → sys.argv[0]).
        data_hashes: Optional dataset-name → hash mapping.

    Returns:
        Ordered dict with keys yplot2_source, yplot2_git_sha,
        yplot2_version, yplot2_data_hashes.
    """
    from . import __version__

    src = _resolve_source(source)
    start_dir = str(Path(src).parent) if src != "unknown" else "."
    sha = _git_sha(start_dir) or "unknown"
    return {
        "yplot2_source": src,
        "yplot2_git_sha": sha,
        "yplot2_version": __version__,
        "yplot2_data_hashes": _hash_str(data_hashes),
    }


def _png_metadata(prov: dict[str, str]) -> dict[str, str | None]:
    """Map provenance dict into PNG tEXt metadata dict.

    Matplotlib writes arbitrary string keys as tEXt chunks; no date is added
    by default, so PNG output is already deterministic.

    Args:
        prov: Provenance dict from _build_provenance.

    Returns:
        Metadata dict suitable for fig.savefig(metadata=...) with PNG backend.
    """
    parts = [
        f"source={prov['yplot2_source']}",
        f"git={prov['yplot2_git_sha']}",
        f"yplot2={prov['yplot2_version']}",
    ]
    if prov.get("yplot2_data_hashes"):
        parts.append(f"data={prov['yplot2_data_hashes']}")
    meta: dict[str, str | None] = {
        "Software": "yplot2",
        "Comment": "; ".join(parts),
    }
    meta.update(prov)
    return meta


def _pdf_metadata(prov: dict[str, str]) -> dict[str, str | None]:
    """Map provenance into PDF info dict, suppressing wall-clock dates.

    Setting CreationDate/ModDate to None tells matplotlib's PDF backend
    to omit those fields, preventing non-deterministic timestamps.

    Args:
        prov: Provenance dict from _build_provenance.

    Returns:
        Metadata dict suitable for fig.savefig(metadata=...) with PDF backend.
    """
    return {
        "Creator": f"yplot2/{prov['yplot2_version']}",
        "Subject": f"source={prov['yplot2_source']}; git={prov['yplot2_git_sha']}",
        "Keywords": prov.get("yplot2_data_hashes") or "",
        "CreationDate": None,
        "ModDate": None,
    }


def save(
    fig: "matplotlib.figure.Figure",
    path: str | os.PathLike[str],
    *,
    source: str | None = None,
    data_hashes: dict[str, str] | None = None,
    dpi: int = 300,
) -> None:
    """Save fig with white-background output + stamped provenance.

    Format is inferred from the path suffix (.png or .pdf). Provenance —
    the source script path, best-effort git SHA, and optional data hashes —
    is written into the image metadata (PNG tEXt chunks / PDF info dict).
    Output is deterministic: no wall-clock time is stamped.

    The saved image always has a white background (``facecolor="white"``
    is passed to savefig). The figure object is NOT mutated — its facecolor
    is left unchanged so callers can continue using it for display.

    Args:
        fig: Matplotlib figure to save.
        path: Output path. Suffix must be .png or .pdf.
        source: Source script path (recommend a repo-relative path).
            Defaults to sys.argv[0] when None.
        data_hashes: Optional dict mapping dataset name to hash string, for
            data provenance. Written verbatim into image metadata.
        dpi: Dots per inch (default 300).

    Raises:
        ValueError: If the path suffix is not .png or .pdf.
    """
    suffix = Path(str(path)).suffix.lower()
    if suffix not in _SUPPORTED_SUFFIXES:
        raise ValueError(f"Unsupported file format {suffix!r}. Use .png or .pdf.")
    prov = _build_provenance(source, data_hashes)
    metadata: dict[str, str | None]
    if suffix == ".png":
        metadata = _png_metadata(prov)
    else:
        metadata = _pdf_metadata(prov)
    fig.savefig(path, dpi=dpi, facecolor="white", metadata=metadata)
