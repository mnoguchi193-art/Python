"""
Smoke tests — every example module must run to completion without error.

Each module in the repository is an executable script with a `__main__` demo.
This test runs every one of them in a subprocess and asserts a clean exit, so a
regression in any of the 75+ examples is caught automatically.

Run with:
    python -m unittest discover tests
    python tests/test_smoke.py
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"tests"}


def find_modules() -> list[Path]:
    """All runnable example scripts, one level deep under a category directory."""
    modules = []
    for path in sorted(ROOT.glob("*/*.py")):
        if path.parent.name in SKIP_DIRS or path.name.startswith("_"):
            continue
        modules.append(path)
    return modules


class SmokeTest(unittest.TestCase):
    def test_all_modules_run(self):
        modules = find_modules()
        self.assertGreater(len(modules), 0, "no example modules were discovered")
        for path in modules:
            rel = path.relative_to(ROOT)
            with self.subTest(module=str(rel)):
                result = subprocess.run(
                    [sys.executable, str(path)],
                    cwd=ROOT, capture_output=True, text=True, timeout=120,
                )
                self.assertEqual(
                    result.returncode, 0,
                    msg=f"{rel} exited with {result.returncode}:\n{result.stderr}",
                )


if __name__ == "__main__":
    mods = find_modules()
    print(f"Discovered {len(mods)} example modules across "
          f"{len({m.parent.name for m in mods})} categories.\n")
    unittest.main(verbosity=2)
