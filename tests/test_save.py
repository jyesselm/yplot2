"""
Tests for yplot2/save.py — provenance-stamping save.

Verifies round-trip of provenance metadata, figure non-mutation,
white-background PNG output, byte determinism, error handling,
and seaborn-free import.
"""

import matplotlib

matplotlib.use("Agg")


import matplotlib.pyplot as plt
import pytest

from yplot2.save import (
    _build_provenance,
    _git_sha,
    _pdf_metadata,
    _png_metadata,
    save,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_simple_fig() -> plt.Figure:
    """Return a minimal figure with one axes and a plotted line."""
    fig, ax = plt.subplots(figsize=(3, 2))
    ax.plot([0, 1], [0, 1])
    return fig


# ---------------------------------------------------------------------------
# PNG round-trip
# ---------------------------------------------------------------------------


class TestSavePngRoundtrip:
    """PNG metadata is written as tEXt chunks and byte-searchable."""

    def test_source_and_hash_in_bytes(self, tmp_path):
        """Source path and data hash appear as literal bytes in the PNG."""
        fig = _make_simple_fig()
        out = tmp_path / "fig.png"
        save(fig, out, source="figures/fig1.py", data_hashes={"counts": "abc123"})
        plt.close(fig)
        content = out.read_bytes()
        assert b"figures/fig1.py" in content
        assert b"abc123" in content

    def test_git_sha_key_in_bytes(self, tmp_path):
        """The yplot2_git_sha metadata key appears in the PNG bytes."""
        fig = _make_simple_fig()
        out = tmp_path / "fig.png"
        save(fig, out, source="figures/fig1.py")
        plt.close(fig)
        content = out.read_bytes()
        assert b"yplot2_git_sha" in content


# ---------------------------------------------------------------------------
# PDF round-trip and date suppression
# ---------------------------------------------------------------------------


class TestSavePdfRoundtrip:
    """PDF metadata is written and wall-clock dates are suppressed."""

    def test_source_in_pdf_bytes(self, tmp_path):
        """Source path substring appears in the PDF bytes."""
        fig = _make_simple_fig()
        out = tmp_path / "fig.pdf"
        save(fig, out, source="figures/fig1.py")
        plt.close(fig)
        content = out.read_bytes()
        assert b"figures/fig1.py" in content

    def test_pdf_metadata_suppresses_dates(self):
        """_pdf_metadata sets CreationDate and ModDate to None."""
        prov = {
            "yplot2_source": "s.py",
            "yplot2_git_sha": "abc",
            "yplot2_version": "0.1.0",
            "yplot2_data_hashes": "",
        }
        meta = _pdf_metadata(prov)
        assert meta["CreationDate"] is None
        assert meta["ModDate"] is None


# ---------------------------------------------------------------------------
# White facecolor
# ---------------------------------------------------------------------------


class TestSaveFacecolor:
    """save() does NOT mutate the caller's figure facecolor."""

    def test_save_does_not_mutate_facecolor(self, tmp_path):
        """Figure facecolor is unchanged after save — save() must NOT mutate it."""
        fig = _make_simple_fig()
        fig.set_facecolor("red")
        original_rgba = fig.get_facecolor()
        out = tmp_path / "fig.png"
        save(fig, out, source="test")
        after_rgba = fig.get_facecolor()
        plt.close(fig)
        assert all(abs(c - e) < 1e-6 for c, e in zip(after_rgba, original_rgba)), (
            f"save() mutated facecolor: was {original_rgba}, now {after_rgba}"
        )

    def test_saved_png_has_white_background(self, tmp_path):
        """Even with a red figure facecolor, the saved PNG uses a white background."""
        fig = _make_simple_fig()
        fig.set_facecolor("red")
        out = tmp_path / "fig.png"
        save(fig, out, source="test")
        plt.close(fig)
        # Re-read the PNG and check the figure background is white via matplotlib
        img = plt.imread(str(out))
        # Corner pixel (0,0) should be white (1.0, 1.0, 1.0, ...)
        top_left = img[0, 0]
        assert top_left[0] > 0.99 and top_left[1] > 0.99 and top_left[2] > 0.99, (
            f"PNG top-left pixel is not white: {top_left}"
        )


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


class TestSaveDeterminism:
    """Two saves of the same figure must produce byte-identical output."""

    def test_png_two_saves_byte_identical(self, tmp_path):
        """PNG output is byte-identical on two consecutive saves."""
        fig = _make_simple_fig()
        out1 = tmp_path / "fig1.png"
        out2 = tmp_path / "fig2.png"
        save(fig, out1, source="figures/fig.py")
        save(fig, out2, source="figures/fig.py")
        plt.close(fig)
        assert out1.read_bytes() == out2.read_bytes()


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestSaveErrors:
    """save() raises ValueError for unsupported suffixes."""

    def test_unsupported_suffix_raises(self, tmp_path):
        """A .svg path raises ValueError mentioning .png/.pdf."""
        fig = _make_simple_fig()
        out = tmp_path / "fig.svg"
        with pytest.raises(ValueError, match=r"\.png|\.pdf"):
            save(fig, out)
        plt.close(fig)


# ---------------------------------------------------------------------------
# _git_sha graceful outside repo
# ---------------------------------------------------------------------------


class TestGitSha:
    """_git_sha returns None gracefully when not in a git repo."""

    def test_graceful_outside_repo(self, tmp_path):
        """_git_sha on a fresh non-repo directory returns None without raising."""
        result = _git_sha(str(tmp_path))
        assert result is None


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


def test_save_exported():
    """yplot2.save is callable from the top-level namespace."""
    import yplot2

    assert callable(yplot2.save)


# ---------------------------------------------------------------------------
# _build_provenance smoke
# ---------------------------------------------------------------------------


class TestBuildProvenance:
    """_build_provenance assembles a deterministic provenance dict."""

    def test_keys_present(self):
        """All four provenance keys are present in the result."""
        prov = _build_provenance("figures/fig.py", {"data": "hash1"})
        assert "yplot2_source" in prov
        assert "yplot2_git_sha" in prov
        assert "yplot2_version" in prov
        assert "yplot2_data_hashes" in prov

    def test_source_stored_verbatim(self):
        """Source is stored exactly as passed."""
        prov = _build_provenance("my/custom/path.py", None)
        assert prov["yplot2_source"] == "my/custom/path.py"

    def test_data_hashes_sorted(self):
        """Data hashes are encoded with sorted keys for determinism."""
        prov = _build_provenance(None, {"z_hash": "zzz", "a_hash": "aaa"})
        assert prov["yplot2_data_hashes"] == "a_hash=aaa;z_hash=zzz"


# ---------------------------------------------------------------------------
# _png_metadata smoke
# ---------------------------------------------------------------------------


def test_png_metadata_contains_all_prov_keys():
    """_png_metadata writes every yplot2_* key into the result dict."""
    prov = {
        "yplot2_source": "fig.py",
        "yplot2_git_sha": "abc123",
        "yplot2_version": "0.1.0",
        "yplot2_data_hashes": "x=y",
    }
    meta = _png_metadata(prov)
    for key in prov:
        assert key in meta
