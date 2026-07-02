"""
Transfer learning across mazes, including a multi-floor maze
（多層迷路への転移学習）

A plain tabular Q-learner keys its table by absolute positions, so nothing it
learns in one maze means anything in another maze. To make knowledge
transferable, this agent learns over *features* that keep their meaning in
any maze — two bits per possible move:

  - is that neighbouring cell open?
  - does moving there bring me closer to my current target?
    (the goal if it is on this floor, otherwise the nearest staircase
    leading toward the goal's floor)

A rule like "take an open move that gets me closer to the target" is true
everywhere, so an agent pre-trained on small single-floor mazes gets a large
head start in an unseen three-floor maze.

Stairs: '>' leads up, '<' leads down. Walking onto a staircase moves the
agent to the same (row, col) on the neighbouring floor.
"""

from __future__ import annotations

import random
from typing import Iterator, Optional, Sequence

State = tuple[int, int, int]  # (floor, row, col)
Features = tuple[int, ...]

# ── The world: a maze with multiple floors ────────────────────────────────


class MultiFloorMaze:
    """A grid maze spread over one or more floors connected by stairs."""

    ACTIONS: dict[str, tuple[int, int]] = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1),
    }

    def __init__(self, floors: Sequence[Sequence[str]]) -> None:
        self.floors = [list(rows) for rows in floors]
        self.rows = len(self.floors[0])
        self.cols = len(self.floors[0][0])
        self.start: State = next(self._find("S"))
        self.goal: State = next(self._find("G"))
        self.up_stairs: dict[int, list[tuple[int, int]]] = {
            f: [(s[1], s[2]) for s in self._find(">") if s[0] == f]
            for f in range(len(self.floors))
        }
        self.down_stairs: dict[int, list[tuple[int, int]]] = {
            f: [(s[1], s[2]) for s in self._find("<") if s[0] == f]
            for f in range(len(self.floors))
        }

    def _find(self, char: str) -> Iterator[State]:
        for f, floor in enumerate(self.floors):
            for r, row in enumerate(floor):
                for c, cell in enumerate(row):
                    if cell == char:
                        yield (f, r, c)

    def _open(self, floor: int, r: int, c: int) -> bool:
        return (
            0 <= r < self.rows
            and 0 <= c < self.cols
            and self.floors[floor][r][c] != "#"
        )

    def step(self, state: State, action: str) -> tuple[State, float, bool]:
        """Move one cell; walls block, stairs change floor."""
        f, r, c = state
        dr, dc = self.ACTIONS[action]
        nr, nc = r + dr, c + dc
        if not self._open(f, nr, nc):
            nr, nc = r, c
        cell = self.floors[f][nr][nc]
        nf = f
        if (nr, nc) != (r, c):  # standing still on a staircase is not a ride
            if cell == ">":
                nf = f + 1
            elif cell == "<":
                nf = f - 1
        nxt = (nf, nr, nc)
        if nxt == self.goal:
            return nxt, 10.0, True
        return nxt, -0.1, False

    def features(self, state: State) -> Features:
        """Maze-independent view of a state: two bits per possible move —
        is it open, and does it bring the agent closer to the target?

        The target is the goal when it is on the current floor, otherwise
        the nearest staircase heading toward the goal's floor — a built-in
        'take the stairs' subgoal. Encoding each move by its *effect on the
        target distance* (rather than by absolute direction) keeps the
        mapping from features to the right action nearly one-to-one, which
        is what lets the learned values transfer between mazes.
        """
        f, r, c = state
        gf, gr, gc = self.goal
        if gf == f:
            tr, tc = gr, gc
        else:
            stairs = self.up_stairs[f] if gf > f else self.down_stairs[f]
            tr, tc = min(stairs, key=lambda p: abs(p[0] - r) + abs(p[1] - c))

        here = abs(tr - r) + abs(tc - c)
        bits: list[int] = []
        for dr, dc in self.ACTIONS.values():
            nr, nc = r + dr, c + dc
            is_open = self._open(f, nr, nc)
            closer = is_open and abs(tr - nr) + abs(tc - nc) < here
            bits += [int(is_open), int(closer)]
        return tuple(bits)

    def render_route(self, states: Sequence[State]) -> str:
        """Draw all floors side by side, marking visited cells with '*'."""
        marks = set(states) - {self.start, self.goal}
        lines = []
        for r in range(self.rows):
            parts = []
            for f, floor in enumerate(self.floors):
                parts.append(
                    "".join(
                        "*" if (f, r, c) in marks else cell
                        for c, cell in enumerate(floor[r])
                    )
                )
            lines.append("   ".join(parts))
        header = "   ".join(f"[{f}F]".center(self.cols) for f in range(len(self.floors)))
        return header + "\n" + "\n".join(lines)


# ── The agent: Q-learning over transferable features ──────────────────────


class FeatureQAgent:
    """Q-learning keyed by features instead of positions.

    Because the features mean the same thing in every maze, the learned
    table is portable: train here, reuse there.
    """

    def __init__(
        self,
        alpha: float = 0.4,
        gamma: float = 0.9,
        epsilon: float = 0.2,
        seed: int = 1,
    ) -> None:
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.rng = random.Random(seed)
        self.q: dict[tuple[Features, str], float] = {}

    def _best_action(self, maze: MultiFloorMaze, feats: Features) -> str:
        # Break ties randomly: with a fixed order, two unseen states whose
        # best guesses point at each other become a deterministic loop.
        values = [(self.q.get((feats, a), 0.0), a) for a in maze.ACTIONS]
        best = max(v for v, _ in values)
        return self.rng.choice([a for v, a in values if v == best])

    def run_episode(
        self,
        maze: MultiFloorMaze,
        max_steps: int = 300,
        epsilon: Optional[float] = None,
        trace: Optional[list[State]] = None,
    ) -> int:
        """One learning episode; returns steps to goal (max_steps if failed)."""
        eps = self.epsilon if epsilon is None else epsilon
        state = maze.start
        if trace is not None:
            trace.append(state)
        for step in range(1, max_steps + 1):
            feats = maze.features(state)
            if self.rng.random() < eps:
                action = self.rng.choice(list(maze.ACTIONS))
            else:
                action = self._best_action(maze, feats)
            nxt, reward, done = maze.step(state, action)
            next_feats = maze.features(nxt)
            best_next = 0.0 if done else max(
                self.q.get((next_feats, a), 0.0) for a in maze.ACTIONS
            )
            old = self.q.get((feats, action), 0.0)
            self.q[(feats, action)] = old + self.alpha * (
                reward + self.gamma * best_next - old
            )
            state = nxt
            if trace is not None:
                trace.append(state)
            if done:
                return step
        return max_steps

    def train(self, maze: MultiFloorMaze, episodes: int) -> None:
        for _ in range(episodes):
            self.run_episode(maze)


# ── Mazes ─────────────────────────────────────────────────────────────────

# Small single-floor mazes for pre-training, with the goal in different
# directions so the agent experiences a variety of situations.
TRAINING_MAZES: list[list[str]] = [
    [
        "S....",
        ".##..",
        "..#..",
        "#....",
        "...#G",
    ],
    [
        "....G",
        ".##.#",
        "..#..",
        "S....",
    ],
    [
        "G....",
        "#.##.",
        "..#..",
        ".#...",
        "....S",
    ],
    [
        "..#..",
        ".....",
        "S...G",
    ],
]

# The unseen test maze: three floors connected by stairs.
# '>' goes up to the same (row, col) on the floor above, '<' goes down.
# The walls deflect the agent sideways but leave no dead-end pockets: the
# feature view (target direction + local walls) has no memory of visited
# cells, so a maze full of dead ends would trap any purely reactive policy.
TEST_FLOORS: list[list[str]] = [
    [
        "S....",
        ".#...",
        ".#...",
        "....>",
    ],
    [
        ">....",
        "...#.",
        ".#...",
        "...#<",
    ],
    [
        "<....",
        ".#.#.",
        "...#.",
        "....G",
    ],
]


# ── Demo ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("── Phase 1: pre-training on small single-floor mazes ──")
    transfer_agent = FeatureQAgent(seed=1)
    training_mazes = [MultiFloorMaze([floor]) for floor in TRAINING_MAZES]
    for maze in training_mazes:
        transfer_agent.train(maze, episodes=300)

    # Freeze the knowledge (alpha = 0): from here on it is reused as-is.
    # (If the agent kept learning, TD updates over shared features would
    # slowly erode it — a classic function-approximation instability.)
    transfer_agent.alpha = 0.0

    for i, maze in enumerate(training_mazes, start=1):
        check = transfer_agent.run_episode(maze, epsilon=0.0)
        print(f"  training maze {i}: solves it in {check} steps after training")
    print(f"  transferable knowledge: {len(transfer_agent.q)} feature-action values")

    print("\n── Phase 2: an unseen 3-floor maze (S on 0F, G on 2F) ──")
    test_maze = MultiFloorMaze(TEST_FLOORS)
    print("  " + test_maze.render_route([]).replace("\n", "\n  "))

    scratch_agent = FeatureQAgent(seed=2)
    print("\n  steps to reach the goal (cap 300, optimal is 21):")
    print("  scratch learns from zero; transfer reuses frozen knowledge")
    print("    episode   scratch   transfer")
    scratch_steps: list[int] = []
    transfer_steps: list[int] = []
    for episode in range(1, 16):
        scratch_steps.append(scratch_agent.run_episode(test_maze))
        transfer_steps.append(transfer_agent.run_episode(test_maze, epsilon=0.05))
        if episode <= 5 or episode % 5 == 0:
            print(f"    {episode:>7}   {scratch_steps[-1]:>7}"
                  f"   {transfer_steps[-1]:>8}")

    s_avg = sum(scratch_steps) / len(scratch_steps)
    t_avg = sum(transfer_steps) / len(transfer_steps)
    print(f"\n  15-episode average: scratch {s_avg:.0f} steps, "
          f"transfer {t_avg:.0f} steps ({s_avg / t_avg:.1f}x fewer)")

    trace: list[State] = []
    steps = transfer_agent.run_episode(test_maze, epsilon=0.0, trace=trace)
    if steps < 300:
        print(f"\n  transfer agent's route ({steps} steps, '*' = visited):")
        print("  " + test_maze.render_route(trace).replace("\n", "\n  "))
