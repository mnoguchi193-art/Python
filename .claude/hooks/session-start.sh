#!/bin/bash
set -euo pipefail

# Session start hook for "Claude Code on the web".
#
# This repository uses ONLY the Python standard library, so there are no
# third-party packages to install. The hook instead verifies the toolchain,
# makes the project root importable, and byte-compiles every module so that any
# syntax error surfaces before the session begins.

# Only run in the remote (Claude Code on the web) environment.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

echo "Python: $(python3 --version)"

# Make the repository root importable for any top-level imports.
echo 'export PYTHONPATH="$CLAUDE_PROJECT_DIR"' >> "$CLAUDE_ENV_FILE"

# Stdlib-only lint: compile all sources to catch syntax errors early.
echo "Byte-compiling all modules..."
python3 -m compileall -q .

echo "Setup complete: standard-library only, no dependencies to install."
