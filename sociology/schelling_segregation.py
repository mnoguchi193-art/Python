"""
Schelling's Segregation Model — emergence from individual preference

Thomas Schelling's agent-based model showed that even a *mild* preference to not
be a small minority among one's neighbors can tip a whole city into stark
segregation — no one wants it, yet it emerges. A foundational result of
computational sociology and complexity science.

Grid cells are 0 (empty), 1 or 2 (two groups). Unhappy agents relocate to a
random empty cell until everyone is content.
"""

from __future__ import annotations

import random


Grid = list[list[int]]


def _neighbors(grid: Grid, r: int, c: int) -> list[int]:
    size = len(grid)
    return [grid[i][j]
            for i in range(max(0, r - 1), min(size, r + 2))
            for j in range(max(0, c - 1), min(size, c + 2))
            if (i, j) != (r, c)]


def fraction_same(grid: Grid, r: int, c: int) -> float | None:
    occupied = [v for v in _neighbors(grid, r, c) if v != 0]
    if not occupied:
        return None  # isolated agent
    return sum(1 for v in occupied if v == grid[r][c]) / len(occupied)


def segregation_index(grid: Grid) -> float:
    """Average share of same-group neighbors across all non-isolated agents."""
    shares = [f for r in range(len(grid)) for c in range(len(grid))
              if grid[r][c] != 0 and (f := fraction_same(grid, r, c)) is not None]
    return sum(shares) / len(shares)


def run(size: int = 20, empty: float = 0.1, tolerance: float = 0.30,
        max_steps: int = 100, seed: int = 0) -> tuple[Grid, Grid, int, float, float]:
    """Simulate until stable. Returns (initial, final, steps, seg0, seg_final)."""
    rng = random.Random(seed)
    grid = [[0 if rng.random() < empty else rng.choice([1, 2])
             for _ in range(size)] for _ in range(size)]
    initial = [row[:] for row in grid]
    seg0 = segregation_index(grid)

    for step in range(1, max_steps + 1):
        unhappy = [(r, c) for r in range(size) for c in range(size)
                   if grid[r][c] != 0
                   and (f := fraction_same(grid, r, c)) is not None
                   and f < tolerance]
        if not unhappy:
            return initial, grid, step - 1, seg0, segregation_index(grid)
        empties = [(r, c) for r in range(size) for c in range(size)
                   if grid[r][c] == 0]
        rng.shuffle(empties)
        for (r, c) in unhappy:
            if not empties:
                break
            er, ec = empties.pop()
            grid[er][ec], grid[r][c] = grid[r][c], 0
            empties.append((r, c))
    return initial, grid, max_steps, seg0, segregation_index(grid)


def render(grid: Grid) -> str:
    glyphs = {0: "·", 1: "A", 2: "B"}
    return "\n".join("".join(glyphs[v] for v in row) for row in grid)


if __name__ == "__main__":
    initial, final, steps, seg0, seg1 = run(size=20, empty=0.10, tolerance=0.30)

    print("Schelling segregation (tolerance 30% — agents only want 30% similar "
          "neighbors)\n")
    print(f"Initial segregation: {seg0:.0%}")
    print(render(initial))
    print(f"\nFinal segregation:   {seg1:.0%}  (stabilized after {steps} steps)")
    print(render(final))
    print("\nMild individual tolerance still produces sharp collective "
          "segregation.")
