# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

A Python learning/reference repository (Python の学習・参照用リポジトリ). Each file is a self-contained, runnable demonstration of a Python concept or pattern. There is no application here — modules are meant to be read and executed individually.

## Running modules

Every file is executable as a script. There is no build step, no test runner, no package layout (no `__init__.py`, no `setup.py`/`pyproject.toml`).

```bash
python basics/data_types.py
python data_structures/linked_list.py
python standard_library/collections_demo.py
```

**Standard library only — do not introduce external dependencies.** The README explicitly states 外部ライブラリは不要です (no external libraries needed). If a task seems to require a third-party package, prefer a stdlib equivalent (e.g. `heapq` over a priority-queue lib, `csv`/`json` over pandas).

Target Python is 3.10+ — code uses `match/case`, walrus `:=`, PEP 604 unions (`int | float`), and `zoneinfo` (3.9+). The environment runs Python 3.11.

## Conventions to follow when adding/editing files

These patterns are consistent across the repo; match them when extending it.

- **Self-contained demos.** A module either runs its examples at top level (see `basics/data_types.py`, `basics/comprehensions.py`) or wraps them in `if __name__ == "__main__":` when it also defines reusable classes/functions (see everything under `data_structures/` and `utilities/`). Use the `__main__` guard whenever the file defines a public class or helper; otherwise top-level is fine.
- **Module docstring at the top** describing the topic, followed by section dividers using box-drawing characters: `# ── Section title ──...`. This is the visual style throughout — keep it.
- **Type hints everywhere**, including return types. Use PEP 604 unions (`int | float`, `dict | list`) rather than `Optional[...]`/`Union[...]`. `Optional` is only used in the linked-list/BST modules where `from __future__ import annotations` is already present.
- **Demos `print` their results** — there are no assertions, no `unittest`, no `pytest`. "Testing" means running the file and reading the output. If you change behavior, run the file and confirm the output still makes sense.
- **Bilingual JP/EN is fine** in comments and the README, but most identifiers and docstrings stay English. The datetime utilities are intentionally JST-centric (`ZoneInfo("Asia/Tokyo")`).

## Layout

Four parallel topic directories, each flat (no nesting):

- `basics/` — language fundamentals (`data_types`, `control_flow`, `functions`, `comprehensions`)
- `data_structures/` — hand-rolled `Stack`, `Queue`/`PriorityQueue`, `LinkedList`, `BinarySearchTree`. `queue_ds.py` is named with the `_ds` suffix to avoid shadowing the stdlib `queue` module — keep that convention if adding similarly-named files.
- `utilities/` — small reusable helpers (`file_utils`, `string_utils`, `datetime_utils`)
- `standard_library/` — guided tours of stdlib modules (`collections_demo`, `itertools_demo`, `pathlib_demo`)

Cross-directory imports are not used; each file stands alone. If you find yourself wanting to import from a sibling directory, prefer duplicating the small helper inline instead — that matches the "each file is a self-contained reference" intent of the repo.
