# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

A Python learning / reference repository. Each file is a small, self-contained demo or utility module written with the **Python standard library only** — there are no `requirements.txt`, `pyproject.toml`, virtualenv, or third-party dependencies. Do not introduce external packages.

## Running code

Every script is runnable directly with the interpreter from the repo root:

```bash
python basics/data_types.py
python data_structures/linked_list.py
python utilities/datetime_utils.py
python standard_library/collections_demo.py
```

Requires Python 3.9+ (uses `zoneinfo`, PEP 604 `dict | list`, PEP 585 `list[str]`, `from __future__ import annotations` for forward refs in dataclasses).

There is no build system, test suite, linter config, or CI. "Verifying a change" means running the affected script and checking its `print` output.

## Two file conventions — follow the one that matches the directory

The repo uses two distinct styles depending on intent:

- **`basics/` and `standard_library/`** — pedagogical scripts. Code (including `print` statements) runs at **module load time**, with no `if __name__ == "__main__"` guard. Sections are delimited by Unicode box-drawing comment banners (`# ── Section ─────────`). When adding examples here, match that flat, top-to-bottom narrative style.
- **`data_structures/` and `utilities/`** — reusable modules. They define classes/functions at the top level and put all demo/`print` code inside an `if __name__ == "__main__":` block at the bottom so the module can be imported cleanly. Preserve this separation when editing.

## Style conventions observed across the codebase

- Module-level docstring on line 1 of every file (triple-quoted, one-liner describing the topic).
- Type hints on public function signatures; prefer modern syntax (`list[str]`, `dict | list`, `Optional[T]`).
- `from __future__ import annotations` is used in files with self-referential dataclasses (`linked_list.py`, `binary_tree.py`) so node types can reference themselves.
- Dataclasses for node-style records (`Node`, `TreeNode`) with `field(default=None, repr=False)` to keep `repr` output readable.
- `Path(path).read_text(encoding="utf-8")` style for file I/O — paths accept `str` or `pathlib.Path`.
- Timezone-aware datetimes use `zoneinfo.ZoneInfo("Asia/Tokyo")` (the repo defaults to JST).
- Error handling: data structures raise `IndexError` on empty pop/peek; search/delete return `bool`. Match these idioms when extending.

## When adding a new topic

1. Pick the directory by intent (demo vs. reusable module) and follow that directory's convention above.
2. Add a one-line entry to the table in `README.md` if you introduce a new category.
3. Keep the file self-contained — no cross-file imports between these directories; each script should run on its own.
