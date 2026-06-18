# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A Python learning and reference repository (`Python の学習・参照用リポジトリ`). Each `.py` file is a self-contained, runnable demonstration of a topic. There is **no package, build system, or third-party dependency** — only the Python standard library is used. The README is bilingual (Japanese/English).

## Running code

Every file is executed directly as a script:

```bash
python basics/data_types.py
python data_structures/linked_list.py
python standard_library/collections_demo.py
```

There is no test runner, linter config, or `requirements.txt`. To "check" a file, run it and inspect its printed output.

## File conventions (two distinct styles)

The directories follow two different patterns — match the existing style of the directory you are editing:

- **`basics/` and `standard_library/`** — tutorial scripts. Demonstration code runs at **module top level** (bare `print(...)` statements), so importing these files executes their output. Organized into sections with `# ── Section ──` comment dividers.
- **`data_structures/` and `utilities/`** — reusable library code. Define `class`es and pure functions, then place all demonstration/usage code behind an `if __name__ == "__main__":` guard so the module can be imported without side effects.

## Style

- Module-level docstring at the top of every file describing the topic.
- Type hints on function signatures and return types throughout.
- Data-structure classes use a leading-underscore internal attribute (e.g. `self._data`), raise standard exceptions for invalid operations (e.g. `IndexError("pop from empty stack")`), and implement `__repr__`.
- `utilities/datetime_utils.py` works in JST.

## Git workflow

Branches use the `claude/<topic>` naming scheme. Commits follow Conventional Commits (`feat:`, `docs:`).
