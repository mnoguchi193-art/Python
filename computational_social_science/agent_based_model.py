"""
Agent-based model — Schelling segregation / シェリングの分居モデル

A classic computational social science simulation: agents of two types live
on a grid and relocate when too few of their neighbours share their type.
Even a mild same-type preference produces strong global segregation — an
emergent macro pattern from simple micro rules.
"""

import random


class Schelling:
    EMPTY = 0

    def __init__(
        self,
        size: int = 20,
        empty_ratio: float = 0.1,
        tolerance: float = 0.3,
        seed: int | None = None,
    ) -> None:
        self.size = size
        self.tolerance = tolerance  # min fraction of same-type neighbours
        self.rng = random.Random(seed)
        self.grid = self._populate(empty_ratio)

    def _populate(self, empty_ratio: float) -> list[list[int]]:
        cells = []
        for _ in range(self.size * self.size):
            if self.rng.random() < empty_ratio:
                cells.append(self.EMPTY)
            else:
                cells.append(self.rng.choice([1, 2]))
        return [cells[i * self.size:(i + 1) * self.size] for i in range(self.size)]

    def _neighbours(self, r: int, c: int) -> list[int]:
        out = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r + dr, c + dc
                if 0 <= rr < self.size and 0 <= cc < self.size:
                    out.append(self.grid[rr][cc])
        return out

    def _is_happy(self, r: int, c: int) -> bool:
        agent = self.grid[r][c]
        if agent == self.EMPTY:
            return True
        nbrs = [n for n in self._neighbours(r, c) if n != self.EMPTY]
        if not nbrs:
            return True
        same = sum(1 for n in nbrs if n == agent)
        return same / len(nbrs) >= self.tolerance

    def step(self) -> int:
        """Move each unhappy agent to a random empty cell. Return moves made."""
        empties = [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if self.grid[r][c] == self.EMPTY
        ]
        self.rng.shuffle(empties)
        moves = 0
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] != self.EMPTY and not self._is_happy(r, c):
                    if not empties:
                        continue
                    er, ec = empties.pop()
                    self.grid[er][ec] = self.grid[r][c]
                    self.grid[r][c] = self.EMPTY
                    empties.append((r, c))
                    moves += 1
        return moves

    def segregation(self) -> float:
        """Average fraction of same-type neighbours across all agents."""
        ratios = []
        for r in range(self.size):
            for c in range(self.size):
                agent = self.grid[r][c]
                if agent == self.EMPTY:
                    continue
                nbrs = [n for n in self._neighbours(r, c) if n != self.EMPTY]
                if nbrs:
                    ratios.append(sum(1 for n in nbrs if n == agent) / len(nbrs))
        return sum(ratios) / len(ratios) if ratios else 0.0

    def run(self, steps: int = 30) -> None:
        for _ in range(steps):
            if self.step() == 0:
                break


if __name__ == "__main__":
    model = Schelling(size=30, empty_ratio=0.1, tolerance=0.3, seed=42)
    print(f"Initial segregation: {model.segregation():.3f}")
    model.run(steps=50)
    print(f"Final segregation:   {model.segregation():.3f}")
    print("(A mild same-type preference still drives strong segregation.)")
