"""
Atomic file write — never leave a half-written file, even on crash or
concurrent writers.

Pattern: write a unique temporary file in the SAME directory, then swap it
into place with os.replace() (a single atomic rename in the OS).
"""

import json
import os
import tempfile

workspace = tempfile.TemporaryDirectory(prefix="atomic-write-demo-")
DIR = workspace.name
CONFIG = os.path.join(DIR, "config.json")


def write_initial_config() -> None:
    with open(CONFIG, "w") as f:
        json.dump({"host": "example.com", "port": 443}, f)


def risky_chunks():
    """A data source that fails partway through."""
    yield '{"host": "localhost",'
    raise ValueError("generation failed")


# ── why naive overwrite is dangerous ──────────────────────────────────────
write_initial_config()
try:
    with open(CONFIG, "w") as f:       # truncates the file immediately!
        for chunk in risky_chunks():
            f.write(chunk)
except ValueError:
    pass
print("After naive overwrite failure:", repr(open(CONFIG).read()))
print("→ broken JSON, original data lost\n")

# ── atomic write: tmp file + os.replace ───────────────────────────────────
def atomic_write(path: str, content: str) -> None:
    """All-or-nothing file write.

    The temp file lives in the same directory as `path` — os.replace() is
    only atomic within one filesystem.  mkstemp gives a unique name
    (concurrent writers cannot collide), exclusive creation, and 0600 perms.
    """
    dir_ = os.path.dirname(os.path.abspath(path))
    fd, tmp_path = tempfile.mkstemp(dir=dir_, prefix=".tmp-")
    try:
        with os.fdopen(fd, "w") as f:  # wrap the fd; closing f closes fd too
            f.write(content)           # 1) prepare — may fail
        os.replace(tmp_path, path)     # 2) commit — atomic rename
    except BaseException:
        os.unlink(tmp_path)            # clean up the debris on failure
        raise


write_initial_config()
try:
    atomic_write(CONFIG, "".join(risky_chunks()))
except ValueError:
    pass
print("After atomic write failure:", repr(open(CONFIG).read()))
print("→ original intact, no temp-file debris:",
      [n for n in os.listdir(DIR) if n.startswith(".tmp")] or "clean")

atomic_write(CONFIG, json.dumps({"host": "new-server.com", "port": 9090}))
print("\nAfter atomic write success:", open(CONFIG).read())

# Readers see either the complete old file or the complete new file —
# never a partially written one.  This is how pip, apt, and browsers
# save files that must not be corrupted.

workspace.cleanup()
