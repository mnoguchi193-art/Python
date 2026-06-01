#!/bin/bash
set -euo pipefail

# Only run in the remote environment (Claude Code on the web).
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# This repository uses only the Python standard library, so there are no
# project dependencies to install. We install ruff so linting works in
# web sessions, and make sure the user bin directory is on PATH.
python3 -m pip install --quiet --user --upgrade ruff

# Persist PATH so ruff (installed under ~/.local/bin) is found this session.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$CLAUDE_ENV_FILE"
fi
