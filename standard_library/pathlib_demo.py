"""
pathlib module — modern, object-oriented filesystem paths
"""

import tempfile
from pathlib import Path

# ── Basic path operations ──────────────────────────────────────────────────
cwd  = Path.cwd()
home = Path.home()
print("CWD: ", cwd)
print("Home:", home)

# Path arithmetic with /
config = home / ".config" / "myapp" / "settings.json"
print("Config path:", config)
print("  parent:   ", config.parent)
print("  name:     ", config.name)
print("  stem:     ", config.stem)
print("  suffix:   ", config.suffix)

# ── Read / write ──────────────────────────────────────────────────────────
with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp)

    # Write text
    f = base / "hello.txt"
    f.write_text("Hello, pathlib!\n", encoding="utf-8")
    print("\nRead back:", f.read_text(encoding="utf-8").strip())

    # Create subdirectories
    (base / "src" / "utils").mkdir(parents=True, exist_ok=True)
    (base / "src" / "utils" / "helper.py").write_text("# helper\n")
    (base / "src" / "main.py").write_text("# main\n")

    # Glob
    py_files = sorted(base.glob("**/*.py"))
    print("Python files found:")
    for p in py_files:
        print(" ", p.relative_to(base))

# ── os.path equivalent comparison ────────────────────────────────────────
# Old style:  os.path.join(os.path.expanduser("~"), "docs", "report.pdf")
# pathlib:    Path.home() / "docs" / "report.pdf"
report = Path.home() / "docs" / "report.pdf"
print("\nReport path:", report)
print("Exists:", report.exists())
