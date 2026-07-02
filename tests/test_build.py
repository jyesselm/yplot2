"""
Tests for yplot2/build.py — figure-regeneration CLI.

Verifies target discovery, script/notebook execution, error handling,
and main() exit code.
"""

import os
from unittest.mock import patch, MagicMock


from yplot2.build import (
    build,
    discover_targets,
    main,
    run_notebook,
    run_script,
)


# ---------------------------------------------------------------------------
# discover_targets
# ---------------------------------------------------------------------------


class TestDiscoverTargets:
    """discover_targets returns sorted .py and .ipynb files only."""

    def test_sorted_and_filtered(self, tmp_path):
        """Only .py and .ipynb files are returned, in sorted order."""
        (tmp_path / "b.py").write_text("")
        (tmp_path / "a.py").write_text("")
        (tmp_path / "c.ipynb").write_text("")
        (tmp_path / "notes.txt").write_text("")
        targets = discover_targets(str(tmp_path))
        names = [os.path.basename(t) for t in targets]
        assert names == ["a.py", "b.py", "c.ipynb"]

    def test_empty_dir_returns_empty(self, tmp_path):
        """An empty directory returns an empty list."""
        assert discover_targets(str(tmp_path)) == []

    def test_nonexistent_dir_raises(self):
        """A nonexistent directory raises FileNotFoundError."""
        import pytest

        with pytest.raises(FileNotFoundError):
            discover_targets("/nonexistent/does/not/exist")


# ---------------------------------------------------------------------------
# run_script
# ---------------------------------------------------------------------------


class TestRunScript:
    """run_script executes a Python script in a fresh subprocess."""

    def test_success_script(self, tmp_path):
        """A script that exits 0 produces BuildResult(ok=True)."""
        script = tmp_path / "ok.py"
        script.write_text("import sys; sys.exit(0)")
        result = run_script(str(script))
        assert result.ok is True
        assert result.stderr == ""

    def test_failure_script(self, tmp_path):
        """A script that raises yields ok=False and non-empty stderr."""
        script = tmp_path / "bad.py"
        script.write_text("raise RuntimeError('boom')")
        result = run_script(str(script))
        assert result.ok is False
        assert result.stderr != ""

    def test_target_is_path(self, tmp_path):
        """BuildResult.target is set to the script path."""
        script = tmp_path / "fig.py"
        script.write_text("")
        result = run_script(str(script))
        assert result.target == str(script)


# ---------------------------------------------------------------------------
# run_notebook
# ---------------------------------------------------------------------------


class TestRunNotebook:
    """run_notebook handles missing nbconvert gracefully."""

    def test_missing_tool_graceful(self, tmp_path):
        """FileNotFoundError from subprocess becomes a failed BuildResult."""
        nb = tmp_path / "nb.ipynb"
        nb.write_text("{}")
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = run_notebook(str(nb))
        assert result.ok is False
        assert "nbconvert" in result.stderr.lower()

    def test_notebook_failure_captured(self, tmp_path):
        """A non-zero return code from nbconvert captures stderr."""
        nb = tmp_path / "nb.ipynb"
        nb.write_text("{}")
        mock_result = MagicMock(returncode=1, stderr="kernel died")
        with patch("subprocess.run", return_value=mock_result):
            result = run_notebook(str(nb))
        assert result.ok is False
        assert "kernel died" in result.stderr

    def test_notebook_success(self, tmp_path):
        """A zero return code produces ok=True."""
        nb = tmp_path / "nb.ipynb"
        nb.write_text("{}")
        mock_result = MagicMock(returncode=0, stderr="")
        with patch("subprocess.run", return_value=mock_result):
            result = run_notebook(str(nb))
        assert result.ok is True


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------


class TestBuild:
    """build() aggregates results from all targets."""

    def test_aggregates_results(self, tmp_path):
        """build() returns one result per target."""
        (tmp_path / "ok.py").write_text("")
        (tmp_path / "bad.py").write_text("raise ValueError('x')")
        results = build(str(tmp_path))
        assert len(results) == 2

    def test_mixed_results(self, tmp_path):
        """A mix of passing and failing scripts produces accurate results."""
        (tmp_path / "ok.py").write_text("")
        (tmp_path / "bad.py").write_text("raise ValueError('x')")
        results = build(str(tmp_path))
        ok_results = [r for r in results if r.ok]
        fail_results = [r for r in results if not r.ok]
        assert len(ok_results) == 1
        assert len(fail_results) == 1


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


class TestMain:
    """main() returns 0/1 based on build success."""

    def test_no_args_returns_1(self):
        """main() without arguments prints usage and returns 1."""
        assert main([]) == 1

    def test_all_pass_returns_0(self, tmp_path):
        """main() returns 0 when all targets succeed."""
        (tmp_path / "ok.py").write_text("")
        code = main([str(tmp_path)])
        assert code == 0

    def test_any_fail_returns_1(self, tmp_path):
        """main() returns 1 when at least one target fails."""
        (tmp_path / "bad.py").write_text("raise RuntimeError('fail')")
        code = main([str(tmp_path)])
        assert code == 1

    def test_empty_dir_returns_0(self, tmp_path):
        """main() returns 0 for an empty directory (no targets = no failures)."""
        code = main([str(tmp_path)])
        assert code == 0

    def test_nonexistent_dir_returns_1(self):
        """main(['/nonexistent']) returns 1 with a clean error message (no traceback)."""
        code = main(["/nonexistent/does/not/exist"])
        assert code == 1
