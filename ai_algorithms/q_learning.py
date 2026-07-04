"""
Q-Learning (強化学習)

グリッドワールドで、エージェントが試行錯誤からゴールへの最短経路を学習する。
Q(s, a) ← Q(s, a) + α [r + γ max_a' Q(s', a') − Q(s, a)]
"""

from __future__ import annotations
import random
from collections import defaultdict

State = tuple[int, int]  # (row, col)
Action = int             # 0=up, 1=down, 2=left, 3=right

GRID = [
    "....",
    ".#.X",  # X = 落とし穴 (報酬 -10)
    ".#..",
    "S..G",  # S = スタート, G = ゴール (報酬 +10)
]
ACTIONS: list[tuple[int, int]] = [(-1, 0), (1, 0), (0, -1), (0, 1)]
ACTION_NAMES = ["↑", "↓", "←", "→"]


class GridWorld:
    def __init__(self, grid: list[str]):
        self.grid = grid
        self.rows, self.cols = len(grid), len(grid[0])
        self.start = self._find("S")
        self.goal = self._find("G")
        self.pit = self._find("X")

    def _find(self, ch: str) -> State:
        for r, row in enumerate(self.grid):
            if ch in row:
                return (r, row.index(ch))
        raise ValueError(f"{ch} not found")

    def step(self, state: State, action: Action) -> tuple[State, float, bool]:
        """Return (next_state, reward, done). 壁・場外は元の位置に留まる。"""
        dr, dc = ACTIONS[action]
        nr, nc = state[0] + dr, state[1] + dc
        if not (0 <= nr < self.rows and 0 <= nc < self.cols) or self.grid[nr][nc] == "#":
            nr, nc = state
        nxt = (nr, nc)
        if nxt == self.goal:
            return nxt, 10.0, True
        if nxt == self.pit:
            return nxt, -10.0, True
        return nxt, -0.1, False  # 移動コストで最短経路を促す


def train(
    env: GridWorld,
    episodes: int = 500,
    alpha: float = 0.1,     # 学習率
    gamma: float = 0.9,     # 割引率
    epsilon: float = 1.0,   # 探索率 (減衰させる)
    seed: int = 42,
) -> dict[State, list[float]]:
    rng = random.Random(seed)
    q: dict[State, list[float]] = defaultdict(lambda: [0.0] * len(ACTIONS))
    for episode in range(episodes):
        state = env.start
        eps = max(0.05, epsilon * (0.99 ** episode))  # ε-greedy の減衰
        for _ in range(100):
            if rng.random() < eps:
                action = rng.randrange(len(ACTIONS))
            else:
                action = max(range(len(ACTIONS)), key=lambda a: q[state][a])
            nxt, reward, done = env.step(state, action)
            target = reward if done else reward + gamma * max(q[nxt])
            q[state][action] += alpha * (target - q[state][action])
            state = nxt
            if done:
                break
    return q


def greedy_path(env: GridWorld, q: dict[State, list[float]]) -> list[State]:
    path = [env.start]
    state = env.start
    for _ in range(50):
        action = max(range(len(ACTIONS)), key=lambda a: q[state][a])
        state, _, done = env.step(state, action)
        path.append(state)
        if done:
            break
    return path


def render_policy(env: GridWorld, q: dict[State, list[float]]) -> str:
    rows = []
    for r in range(env.rows):
        row = ""
        for c in range(env.cols):
            ch = env.grid[r][c]
            if ch in "#GX":
                row += ch
            else:
                best = max(range(len(ACTIONS)), key=lambda a: q[(r, c)][a])
                row += ACTION_NAMES[best]
        rows.append(row)
    return "\n".join(rows)


if __name__ == "__main__":
    env = GridWorld(GRID)
    q = train(env)
    path = greedy_path(env, q)
    print("Learned policy (best action per cell):")
    print(render_policy(env, q))
    print("\nGreedy path:", " -> ".join(map(str, path)))
    print("Reached goal:", path[-1] == env.goal)
