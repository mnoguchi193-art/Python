# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A Python learning and reference repository (`basics`, `data_structures`, `utilities`, `standard_library`). Uses **only the Python standard library** — there are no third-party dependencies, no package manifest, and no build step.

## Running code

Every file is a standalone script. Run any module directly:

```bash
python basics/data_types.py
python data_structures/linked_list.py
python standard_library/collections_demo.py
```

There is no test runner, linter config, or CI. Modules verify their own behavior via a `if __name__ == "__main__":` block at the bottom that prints (and in `data_structures`/`utilities`, sometimes `assert`s) example output. To "test" a change, run the affected module and check its printed demo output.

## Conventions

- Each file opens with a module docstring summarizing its topic, and groups related examples under `# ── Section ──` comment dividers.
- `data_structures/` and `utilities/` expose reusable classes/functions with type hints, raising standard exceptions (e.g. `IndexError` on empty `Stack.pop`). `basics/` and `standard_library/` are demonstration scripts meant to be read and run top-to-bottom.
- Keep new code self-contained in its directory's theme; do not introduce external dependencies — the standard-library-only constraint is the point of the repo.
