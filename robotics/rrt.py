"""
RRT — sampling-based motion planning

A* needs a grid; real robots plan in continuous, high-dimensional spaces where
that explodes. The Rapidly-exploring Random Tree grows a tree from the start by
repeatedly sampling a random point, steering the nearest tree node a short step
toward it, and keeping the move if it is collision-free. The tree rapidly fills
the free space and, with a goal bias, finds a path through cluttered environments.
"""

from __future__ import annotations

import math
import random


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _collision_free(p1, p2, obstacles, steps=20):
    for t in range(steps + 1):
        x = p1[0] + (p2[0] - p1[0]) * t / steps
        y = p1[1] + (p2[1] - p1[1]) * t / steps
        if any(math.hypot(x - ox, y - oy) <= r for ox, oy, r in obstacles):
            return False
    return True


def rrt(start, goal, obstacles, width, height, step=0.5, goal_bias=0.1,
        max_iter=5000, seed=0):
    """Return (path, node count) from start to goal, or (None, count) on failure."""
    rng = random.Random(seed)
    nodes, parent = [start], [None]
    for _ in range(max_iter):
        sample = goal if rng.random() < goal_bias else (
            rng.uniform(0, width), rng.uniform(0, height))
        ni = min(range(len(nodes)), key=lambda i: _dist(nodes[i], sample))
        near = nodes[ni]
        d = _dist(near, sample)
        if d == 0:
            continue
        new = (near[0] + (sample[0] - near[0]) / d * min(step, d),
               near[1] + (sample[1] - near[1]) / d * min(step, d))
        if not _collision_free(near, new, obstacles):
            continue
        nodes.append(new)
        parent.append(ni)
        if _dist(new, goal) <= step and _collision_free(new, goal, obstacles):
            nodes.append(goal)
            parent.append(len(nodes) - 2)
            path, i = [], len(nodes) - 1
            while i is not None:
                path.append(nodes[i])
                i = parent[i]
            return path[::-1], len(nodes)
    return None, len(nodes)


def render(path, obstacles, start, goal, width, height, cols=44, rows=20):
    grid = [[" "] * cols for _ in range(rows)]
    for ox, oy, r in obstacles:
        for r_ in range(rows):
            for c in range(cols):
                x, y = c / (cols - 1) * width, r_ / (rows - 1) * height
                if math.hypot(x - ox, y - oy) <= r:
                    grid[r_][c] = "#"
    for (x, y) in path or []:
        c = round(x / width * (cols - 1))
        r_ = round(y / height * (rows - 1))
        if grid[r_][c] == " ":
            grid[r_][c] = "*"
    for (px, py), ch in ((start, "S"), (goal, "G")):
        grid[round(py / height * (rows - 1))][round(px / width * (cols - 1))] = ch
    return "\n".join("".join(row) for row in grid)


if __name__ == "__main__":
    width, height = 10.0, 10.0
    start, goal = (0.5, 0.5), (9.5, 9.5)
    obstacles = [(3, 3, 1.5), (6, 5, 1.8), (4, 7, 1.2), (8, 3, 1.0)]

    path, count = rrt(start, goal, obstacles, width, height)
    print("RRT motion planning (S=start, G=goal, #=obstacle, *=path)\n")
    print(render(path, obstacles, start, goal, width, height))
    if path:
        length = sum(_dist(path[i], path[i + 1]) for i in range(len(path) - 1))
        print(f"\n  path found: {len(path)} waypoints, length {length:.1f}, "
              f"tree grew to {count} nodes")
    else:
        print("\n  no path found")
    print("\n  Random sampling explores continuous space without a grid — how")
    print("  robot arms and drones plan through clutter.")
