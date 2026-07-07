# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Overview

A Python learning and reference repository (学習・参照用). Each file is a
self-contained, runnable demo of a Python concept — data types, data
structures, utilities, and standard-library tours. **Standard library only;
no external dependencies and no package manager.**

## Layout

| Directory | Contents |
|---|---|
| `basics/` | data types, control flow, functions, comprehensions |
| `data_structures/` | stack, queue, singly linked list, binary search tree |
| `utilities/` | file I/O, string helpers, datetime (JST-aware) |
| `standard_library/` | `collections`, `itertools`, `pathlib` demos |
| `ai/` | AGI-inspired toy demos: neural net (backprop), Q-learning, A*, episodic/semantic memory, cognitive agent loop, feature-based transfer learning (multi-floor maze), model-based RL (Dyna-Q), genetic algorithm (string/knapsack/policy evolution), optimizer comparison (SGD/momentum/Adam), MCTS (tic-tac-toe), MCTS scaling studies (sims vs strength with minimax reference; game size vs saturation via doubling test on k-in-a-row) |

## Running

Each module runs directly and prints a demonstration:

```bash
python basics/data_types.py
python data_structures/linked_list.py
python standard_library/collections_demo.py
```

There is no build step, no test suite, and no requirements file.

## Conventions

When adding or editing files, match the existing style:

- **Module docstring** at the top of every file describing its purpose.
- **`if __name__ == "__main__":` block** at the bottom that demonstrates the
  module by printing example output. This is how each file is "tested" —
  run it and confirm the output looks right.
- **Type hints** on function signatures and notable variables. Reusable
  modules use `from __future__ import annotations` and `typing` imports.
- **Section headers** in demo scripts use box-drawing comment rules, e.g.
  `# ── Strings ───────────────`.
- **Reusable code** (`data_structures/`, `utilities/`) is organized into
  classes/functions; **demo scripts** (`basics/`, `standard_library/`) are
  more linear and illustrative.
- Timezone-aware datetime code uses JST (`ZoneInfo("Asia/Tokyo")`).
- Comments and prose may be in Japanese or English; keep both readable.

## Verifying changes

Since there is no test framework, verify a change by running the affected
module and checking its printed output:

```bash
python <path/to/module>.py
```
