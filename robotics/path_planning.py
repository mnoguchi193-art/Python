"""
A* Path Planning — the "plan" stage of a mobile robot

Given a map with obstacles, A* finds the shortest collision-free path from start
to goal. It expands the frontier in order of f = g + h, where g is the cost so
far and h is an admissible heuristic (here Manhattan distance) that guides the
search toward the goal — far fewer nodes than blind search, while still
guaranteeing the optimal path. (Sampling planners like RRT extend this idea to
high-dimensional robot configuration spaces.)
"""

from __future__ import annotations

import heapq


Grid = list[str]
Cell = tuple[int, int]


def astar(grid: Grid, start: Cell, goal: Cell) -> tuple[list[Cell], int]:
    """Return (path from start to goal, number of nodes expanded)."""
    rows, cols = len(grid), len(grid[0])

    def passable(r, c):
        return 0 <= r < rows and 0 <= c < cols and grid[r][c] != "#"

    def h(cell):
        return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])

    open_heap = [(h(start), 0, start)]
    came_from: dict[Cell, Cell] = {}
    g_score = {start: 0}
    expanded = 0

    while open_heap:
        _, g, current = heapq.heappop(open_heap)
        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1], expanded
        expanded += 1
        r, c = current
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (r + dr, c + dc)
            if not passable(*nxt):
                continue
            tentative = g + 1
            if tentative < g_score.get(nxt, 1 << 30):
                g_score[nxt] = tentative
                came_from[nxt] = current
                heapq.heappush(open_heap, (tentative + h(nxt), tentative, nxt))
    return [], expanded


def render(grid: Grid, path: list[Cell]) -> str:
    on_path = set(path)
    out = []
    for r, row in enumerate(grid):
        out.append("".join("*" if (r, c) in on_path and ch == "."
                           else ch for c, ch in enumerate(row)))
    return "\n".join(out)


if __name__ == "__main__":
    grid = [
        "S..........",
        ".####.####.",
        "....#....#.",
        "####.####..",
        "...#....#..",
        "..........G",
    ]
    # Locate S and G, then treat them as free cells for planning.
    start = next((r, c) for r, row in enumerate(grid) for c, ch in enumerate(row)
                 if ch == "S")
    goal = next((r, c) for r, row in enumerate(grid) for c, ch in enumerate(row)
                if ch == "G")
    clean = [row.replace("S", ".").replace("G", ".") for row in grid]

    path, expanded = astar(clean, start, goal)
    print("A* path planning (S=start, G=goal, *=path, #=obstacle)\n")
    decorated = render(clean, path).split("\n")
    decorated[start[0]] = decorated[start[0]][:start[1]] + "S" + decorated[start[0]][start[1] + 1:]
    decorated[goal[0]] = decorated[goal[0]][:goal[1]] + "G" + decorated[goal[0]][goal[1] + 1:]
    print("\n".join(decorated))
    print(f"\n  path length: {len(path) - 1} steps, nodes expanded: {expanded}")
