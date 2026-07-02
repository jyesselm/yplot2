"""
Task 0.5 (plan-critic #2): verify import yplot2 succeeds with seaborn UNINSTALLED.

Uses a subprocess to block seaborn before the import, so it works even when
the [stats] extra has installed seaborn into the test environment.
"""

import subprocess
import sys


def test_import_yplot2_without_seaborn():
    """
    import yplot2 must succeed even when seaborn is made unimportable.

    Blocks seaborn via sys.modules["seaborn"] = None (the standard Python
    approach for making a module appear absent) before importing yplot2.
    """
    code = "import sys; sys.modules['seaborn'] = None; import yplot2; print('OK')"
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"import yplot2 failed with seaborn absent.\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    assert "OK" in result.stdout
