# CLAUDE.md

Guidance for AI assistants (and humans) working in this repository.

## What this repository is

A **Python learning and reference repository** (`mnoguchi193-art/python`). Each
file is a self-contained, runnable demonstration of a Python concept, data
structure, or standard-library module. There is no application to build or
deploy — the code exists to be read and run for educational purposes.

The README is bilingual (Japanese / English); keep that spirit when editing
top-level docs, but code, docstrings, and comments are written in English.

## Layout

```
.
├── README.md
├── basics/              # language fundamentals (run as scripts)
│   ├── data_types.py        # numeric, str, bool, None, list/tuple/dict/set
│   ├── control_flow.py      # if/elif/else, loops, match/case, exceptions
│   ├── functions.py         # defaults, *args/**kwargs, closures, decorators, generators
│   └── comprehensions.py    # list/dict/set/generator comprehensions
├── data_structures/     # reusable classes + __main__ demos
│   ├── stack.py             # LIFO on a list
│   ├── queue_ds.py          # FIFO (deque) + PriorityQueue (heapq)
│   ├── linked_list.py       # singly linked list
│   └── binary_tree.py       # binary search tree
├── utilities/           # importable helper functions + __main__ demos
│   ├── file_utils.py        # file I/O; paths accept str or pathlib.Path
│   ├── string_utils.py      # string helpers (uses re)
│   └── datetime_utils.py    # datetime helpers, JST-aware (zoneinfo)
└── standard_library/    # stdlib module demos (run as scripts)
    ├── collections_demo.py  # Counter, defaultdict, OrderedDict, namedtuple, deque
    ├── itertools_demo.py    # chain, islice, groupby, combinations, accumulate
    └── pathlib_demo.py      # object-oriented filesystem paths
```

### Two file styles — match the one in the directory you edit

1. **Scripts** (`basics/`, `standard_library/`): code runs at module top level,
   no `if __name__ == "__main__":` guard. The whole file *is* the demo.
2. **Library + demo** (`data_structures/`, `utilities/`): define reusable
   classes/functions, then put the demonstration under an
   `if __name__ == "__main__":` guard so the module stays importable.

## Running the code

No installation step and **no external dependencies** — the standard library
only. Run any file directly:

```bash
python basics/data_types.py
python data_structures/linked_list.py
python standard_library/collections_demo.py
```

- **Python version:** target **3.11+**. The code uses `match`/`case`,
  `zoneinfo`, and `from __future__ import annotations`. Do not introduce syntax
  that breaks on 3.11.

## Conventions to follow

- **Stdlib only.** Never add a third-party dependency. There is no
  `requirements.txt`/`pyproject.toml`, and it should stay that way.
- **Module docstring** at the top of every file: a one-line title, optionally
  followed by a short description (see `queue_ds.py` for the multi-line form).
- **Type hints** on function signatures and notable variables. Use
  `from __future__ import annotations` when a class references itself (e.g.
  `Node.next: Optional[Node]`).
- **Section dividers** using box-drawing comments to break a script into topics:
  ```python
  # ── Section name ──────────────────────────────────────────────────────────
  ```
- **`print()`-driven demos.** Output is the teaching tool. Label output clearly
  (`print("Reversed:", ll)`); decorative Unicode like `→` is used in `__repr__`
  and output and is welcome.
- **Self-contained.** A file should not import from sibling files; each one
  stands alone so it can be read and run in isolation.
- Prefer clear, idiomatic, well-commented code over clever one-liners — this is
  reference material meant to be learned from.

## Testing / verification

There is no test suite or linter configured. To verify a change, **run the
affected file** and confirm it executes without error and prints sensible
output. When adding a `data_structures/` or `utilities/` module, exercise the
new code from its `__main__` block.

## Git workflow

- Active development branch: **`claude/claude-md-docs-7pWTR`**. Do not push to
  another branch without explicit permission.
- Commit message style (from history): Conventional Commits —
  `feat: …`, `docs: …`. Keep messages concise and descriptive.
- Push with `git push -u origin <branch-name>`.
- Do **not** open a pull request unless the user explicitly asks.

## Adding new content

When adding a new example, also:

1. Place it in the directory matching its category, following that directory's
   file style (script vs. library+demo).
2. Add a row/link in the relevant `README.md` table so it's discoverable.
3. Keep it stdlib-only and runnable with `python <path>`.
