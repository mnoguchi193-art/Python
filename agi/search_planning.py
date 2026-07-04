"""
Search & Planning (探索とプランニング)

「現在の状態からゴールに至る行動列を見つける」能力は、
知的エージェントの計画立案 (planning) の基礎。

- A* 探索: ヒューリスティック h(n) を使い最短経路を効率的に発見
  f(n) = g(n) + h(n)  (実コスト + ゴールまでの推定コスト)
- STRIPS 風プランナー: 前提条件と効果で行動を記述し、
  BFS で目標状態を達成する行動列を求める
"""

from __future__ import annotations

import heapq
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Tuple

Pos = Tuple[int, int]


# ---------------------------------------------------------------
# A* 探索 (経路プランニング)
# ---------------------------------------------------------------

def manhattan(a: Pos, b: Pos) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star(grid: List[str], start: Pos, goal: Pos) -> Optional[List[Pos]]:
    """'#' を壁とするグリッドで start から goal への最短経路を返す。"""
    rows, cols = len(grid), len(grid[0])
    open_heap: List[Tuple[int, Pos]] = [(manhattan(start, goal), start)]
    g_score: Dict[Pos, int] = {start: 0}
    came_from: Dict[Pos, Pos] = {}

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]
        r, c = current
        for nr, nc in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
            if not (0 <= nr < rows and 0 <= nc < cols) or grid[nr][nc] == "#":
                continue
            tentative = g_score[current] + 1
            if tentative < g_score.get((nr, nc), float("inf")):
                g_score[(nr, nc)] = tentative
                came_from[(nr, nc)] = current
                f = tentative + manhattan((nr, nc), goal)
                heapq.heappush(open_heap, (f, (nr, nc)))
    return None  # 到達不能


# ---------------------------------------------------------------
# STRIPS 風プランナー (記号的プランニング)
# ---------------------------------------------------------------

@dataclass(frozen=True)
class PlanAction:
    """前提条件 (preconditions) を満たす状態でのみ実行でき、
    実行すると効果 (add / delete) で世界の状態が変化する。"""
    name: str
    preconditions: FrozenSet[str]
    add_effects: FrozenSet[str] = field(default=frozenset())
    del_effects: FrozenSet[str] = field(default=frozenset())

    def applicable(self, state: FrozenSet[str]) -> bool:
        return self.preconditions <= state

    def apply(self, state: FrozenSet[str]) -> FrozenSet[str]:
        return (state - self.del_effects) | self.add_effects


def plan(initial: FrozenSet[str], goal: FrozenSet[str],
         actions: List[PlanAction]) -> Optional[List[str]]:
    """BFS で goal を含む状態に至る最短の行動列を探す。"""
    queue = deque([(initial, [])])
    visited = {initial}
    while queue:
        state, steps = queue.popleft()
        if goal <= state:
            return steps
        for action in actions:
            if action.applicable(state):
                nxt = action.apply(state)
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, steps + [action.name]))
    return None


if __name__ == "__main__":
    # --- A* デモ ---
    grid = [
        "S..#....",
        ".#.#.##.",
        ".#...#..",
        ".####.#.",
        "......#G",
    ]
    path = a_star(grid, start=(0, 0), goal=(4, 7))
    print("=== A* 経路探索 ===")
    marked = [list(row) for row in grid]
    for r, c in path or []:
        if marked[r][c] == ".":
            marked[r][c] = "*"
    print("\n".join("".join(row) for row in marked))
    print(f"経路長: {len(path) - 1} 歩\n")

    # --- STRIPS 風プランニングデモ: コーヒーを淹れる ---
    actions = [
        PlanAction("豆を挽く", frozenset({"豆がある"}),
                   add_effects=frozenset({"粉がある"}),
                   del_effects=frozenset({"豆がある"})),
        PlanAction("湯を沸かす", frozenset({"水がある"}),
                   add_effects=frozenset({"湯がある"}),
                   del_effects=frozenset({"水がある"})),
        PlanAction("ドリップする", frozenset({"粉がある", "湯がある"}),
                   add_effects=frozenset({"コーヒーがある"})),
    ]
    initial = frozenset({"豆がある", "水がある"})
    goal = frozenset({"コーヒーがある"})

    print("=== STRIPS 風プランニング ===")
    print("初期状態:", set(initial))
    print("目標:", set(goal))
    steps = plan(initial, goal, actions)
    print("計画:", " -> ".join(steps) if steps else "計画なし")
