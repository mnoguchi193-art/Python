"""
Graph Search Algorithms: BFS, DFS, A*

探索はAIの最も基礎的なアルゴリズム。迷路 (グリッド) 上の最短経路探索で
幅優先探索・深さ優先探索・A* を比較する。
"""

from __future__ import annotations
from collections import deque
from heapq import heappush, heappop
from typing import Iterator, Optional

Point = tuple[int, int]  # (row, col)

MAZE = [
    "S.#.......",
    "..#.####..",
    "..#....#..",
    "..####.#..",
    ".....#.#..",
    "####.#.#..",
    "...#.#.#..",
    ".#...#.#..",
    ".#.###.##.",
    ".#.......G",
]


def parse_maze(maze: list[str]) -> tuple[Point, Point, set[Point]]:
    """Return (start, goal, walls)."""
    start = goal = None
    walls: set[Point] = set()
    for r, row in enumerate(maze):
        for c, ch in enumerate(row):
            if ch == "S":
                start = (r, c)
            elif ch == "G":
                goal = (r, c)
            elif ch == "#":
                walls.add((r, c))
    assert start is not None and goal is not None
    return start, goal, walls


def neighbors(pos: Point, maze: list[str], walls: set[Point]) -> Iterator[Point]:
    rows, cols = len(maze), len(maze[0])
    r, c = pos
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in walls:
            yield (nr, nc)


def reconstruct(came_from: dict[Point, Point], goal: Point) -> list[Point]:
    path = [goal]
    while path[-1] in came_from:
        path.append(came_from[path[-1]])
    return path[::-1]


def bfs(maze: list[str]) -> tuple[Optional[list[Point]], int]:
    """幅優先探索: 辺コストが等しいとき最短経路を保証する。"""
    start, goal, walls = parse_maze(maze)
    frontier = deque([start])
    came_from: dict[Point, Point] = {}
    visited = {start}
    explored = 0
    while frontier:
        current = frontier.popleft()
        explored += 1
        if current == goal:
            return reconstruct(came_from, goal), explored
        for nxt in neighbors(current, maze, walls):
            if nxt not in visited:
                visited.add(nxt)
                came_from[nxt] = current
                frontier.append(nxt)
    return None, explored


def dfs(maze: list[str]) -> tuple[Optional[list[Point]], int]:
    """深さ優先探索: メモリ効率は良いが最短経路は保証しない。"""
    start, goal, walls = parse_maze(maze)
    frontier = [start]
    came_from: dict[Point, Point] = {}
    visited = {start}
    explored = 0
    while frontier:
        current = frontier.pop()
        explored += 1
        if current == goal:
            return reconstruct(came_from, goal), explored
        for nxt in neighbors(current, maze, walls):
            if nxt not in visited:
                visited.add(nxt)
                came_from[nxt] = current
                frontier.append(nxt)
    return None, explored


def manhattan(a: Point, b: Point) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star(maze: list[str]) -> tuple[Optional[list[Point]], int]:
    """A*: ヒューリスティックで探索を誘導する。許容的なら最短経路を保証。"""
    start, goal, walls = parse_maze(maze)
    frontier: list[tuple[int, Point]] = [(manhattan(start, goal), start)]
    came_from: dict[Point, Point] = {}
    g_score = {start: 0}
    explored = 0
    while frontier:
        _, current = heappop(frontier)
        explored += 1
        if current == goal:
            return reconstruct(came_from, goal), explored
        for nxt in neighbors(current, maze, walls):
            tentative = g_score[current] + 1
            if tentative < g_score.get(nxt, float("inf")):
                g_score[nxt] = tentative
                came_from[nxt] = current
                heappush(frontier, (tentative + manhattan(nxt, goal), nxt))
    return None, explored


def render(maze: list[str], path: list[Point]) -> str:
    grid = [list(row) for row in maze]
    for r, c in path[1:-1]:
        grid[r][c] = "*"
    return "\n".join("".join(row) for row in grid)


if __name__ == "__main__":
    for name, algo in [("BFS", bfs), ("DFS", dfs), ("A*", a_star)]:
        path, explored = algo(MAZE)
        assert path is not None
        print(f"{name}: path length = {len(path)}, nodes explored = {explored}")
    path, _ = a_star(MAZE)
    print("\nA* path:")
    print(render(MAZE, path))
