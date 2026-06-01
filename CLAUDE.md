# CLAUDE.md

Guidance for AI assistants (Claude Code and others) working in this repository.

## Overview

A Python **learning and reference** repository. Each file is a small,
self-contained demonstration of a Python concept, data structure, or
standard-library feature. There is no application to build or deploy — the
"product" is clear, idiomatic, runnable example code.

- **Python version:** 3.11 (uses `zoneinfo`, PEP 585 builtin generics like
  `dict[str, int]`, `from __future__ import annotations`).
- **Dependencies:** none. **Standard library only** — do not add third-party
  packages, and do not introduce `requirements.txt`/`pyproject.toml` unless
  explicitly asked.
- **Bilingual docs:** the README is written in Japanese and English. Keep both
  in sync when editing it.

## Structure

```
basics/             # Language fundamentals — run as scripts (top-level demos)
  data_types.py       numeric/str/bool/None/list/tuple/dict/set, conversions
  control_flow.py
  functions.py        defaults, *args/**kwargs, closures, decorators, generators
  comprehensions.py
data_structures/    # Reusable classes + __main__ demo block
  stack.py            Stack (LIFO) + is_balanced() bracket checker
  queue_ds.py
  linked_list.py
  binary_tree.py      BinarySearchTree with dataclass TreeNode
utilities/          # Reusable helper functions + __main__ demo block
  string_utils.py     slugify, truncate, count_words, is_palindrome, camel_to_snake
  datetime_utils.py   JST-aware helpers (zoneinfo), business-day math
  file_utils.py
standard_library/   # Stdlib feature demos — run as scripts (top-level demos)
  collections_demo.py Counter, defaultdict, OrderedDict, namedtuple, deque
  itertools_demo.py
  pathlib_demo.py
README.md
```

## Two file patterns — follow the one for the directory

1. **Demo scripts** (`basics/`, `standard_library/`): example code runs at
   **module top level** (no `if __name__ == "__main__"` guard). Sections are
   separated by box-drawing comment headers:
   ```python
   # ── Section name ──────────────────────────────────────────────
   ```

2. **Reusable modules** (`data_structures/`, `utilities/`): define classes /
   functions with type hints, then place runnable examples inside an
   `if __name__ == "__main__":` block at the bottom.

When adding a file, match the pattern already used in its directory.

## Conventions

- **Module docstring:** every file opens with a one-line `"""..."""` describing
  what it covers.
- **Type hints:** use them on function signatures and notable variables. Prefer
  builtin generics (`list`, `dict[str, int]`) and `Optional[...]` from `typing`
  where a forward reference is needed (`from __future__ import annotations`).
- **Self-documenting:** prefer clear names and small focused functions. Add a
  short docstring with an input→output example for non-obvious helpers
  (e.g. `"'Hello World!' → 'hello-world'"`).
- **Encapsulation:** internal state is prefixed with a single underscore
  (`self._data`). Provide `__repr__` on container classes.
- **Errors:** raise standard exceptions with messages (e.g.
  `raise IndexError("pop from empty stack")`).
- **Timezone:** datetime code is timezone-aware and uses JST
  (`ZoneInfo("Asia/Tokyo")`), not naive `datetime.now()`.

## Running

No build step. Run any file directly:

```bash
python basics/data_types.py
python data_structures/binary_tree.py
python standard_library/collections_demo.py
```

There is no test suite, linter config, or CI. The de-facto check for any file
is that it **runs cleanly and prints sensible output**. Always run a file after
editing it to confirm it works.

## Git workflow

- Active development branch for this work: `claude/claude-md-docs-XlDwu`.
- Commit messages follow **Conventional Commits**: `feat:`, `docs:`, etc.,
  with a concise scope summary (e.g.
  `feat: add data structures (stack, queue, linked list, binary tree)`).
- Push with `git push -u origin <branch-name>`. Do not open a pull request
  unless explicitly asked.

## When adding new examples

- Place the file in the directory matching its category, following that
  directory's file pattern (above).
- Keep it dependency-free and runnable on its own.
- Update the README's structure table (both Japanese and English columns) so it
  stays accurate.
