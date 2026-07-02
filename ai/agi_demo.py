"""
AGI-inspired cognitive architecture — a toy demonstration
（AGI 風・認知アーキテクチャのおもちゃデモ）

True AGI (Artificial General Intelligence) does not exist yet and cannot
simply be "coded up" — it is an open research problem. What this module does
instead is implement, in pure standard-library Python, small working versions
of the building blocks most AGI research programs discuss:

1. LEARNING     — a tiny neural network trained with backpropagation (XOR)
2. DECISION     — reinforcement learning (tabular Q-learning in a grid world)
3. PLANNING     — goal-directed search (A*)
4. MEMORY       — episodic + semantic memory with simple retrieval
5. INTEGRATION  — a CognitiveAgent running a perceive → recall → plan →
                  act → learn loop that combines the pieces above

Each piece is deliberately minimal and readable rather than powerful.
"""

from __future__ import annotations

import heapq
import math
import random
from collections import deque
from dataclasses import dataclass, field
from typing import Iterator, Optional, Sequence

# ── 1. Learning: a tiny neural network (backpropagation) ──────────────────


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


class TinyNeuralNetwork:
    """A minimal multi-layer perceptron trained with backpropagation.

    Weights are plain nested lists — no numpy — so every step of the
    forward/backward pass is visible.
    """

    def __init__(
        self,
        layer_sizes: Sequence[int],
        learning_rate: float = 0.5,
        seed: int = 42,
    ) -> None:
        rng = random.Random(seed)
        self.lr = learning_rate
        self.weights: list[list[list[float]]] = []
        self.biases: list[list[float]] = []
        for n_in, n_out in zip(layer_sizes, layer_sizes[1:]):
            self.weights.append(
                [[rng.uniform(-1, 1) for _ in range(n_in)] for _ in range(n_out)]
            )
            self.biases.append([rng.uniform(-1, 1) for _ in range(n_out)])

    def _forward(self, inputs: Sequence[float]) -> list[list[float]]:
        """Return the activations of every layer (input layer included)."""
        activations: list[list[float]] = [list(inputs)]
        for weights, biases in zip(self.weights, self.biases):
            prev = activations[-1]
            activations.append(
                [
                    _sigmoid(sum(w * p for w, p in zip(row, prev)) + b)
                    for row, b in zip(weights, biases)
                ]
            )
        return activations

    def predict(self, inputs: Sequence[float]) -> list[float]:
        return self._forward(inputs)[-1]

    def train(
        self,
        dataset: Sequence[tuple[Sequence[float], Sequence[float]]],
        epochs: int = 5000,
    ) -> None:
        for _ in range(epochs):
            for inputs, targets in dataset:
                activations = self._forward(inputs)

                # Output-layer error (derivative of MSE through sigmoid).
                deltas: list[list[float]] = [
                    [
                        (a - t) * a * (1 - a)
                        for a, t in zip(activations[-1], targets)
                    ]
                ]
                # Propagate the error backwards through hidden layers.
                for layer in range(len(self.weights) - 1, 0, -1):
                    next_delta = deltas[0]
                    layer_delta = []
                    for j, a in enumerate(activations[layer]):
                        err = sum(
                            self.weights[layer][k][j] * next_delta[k]
                            for k in range(len(next_delta))
                        )
                        layer_delta.append(err * a * (1 - a))
                    deltas.insert(0, layer_delta)

                # Gradient-descent update of weights and biases.
                for layer, delta in enumerate(deltas):
                    prev = activations[layer]
                    for j, d in enumerate(delta):
                        for i, p in enumerate(prev):
                            self.weights[layer][j][i] -= self.lr * d * p
                        self.biases[layer][j] -= self.lr * d


# ── 2. The world: a small grid maze ───────────────────────────────────────

Pos = tuple[int, int]  # (row, col)

DEFAULT_GRID = [
    "S..#.",
    ".#.#.",
    ".#...",
    ".#.#.",
    "...#G",
]


class GridWorld:
    """A grid maze: S = start, G = goal, # = wall, . = open floor."""

    ACTIONS: dict[str, Pos] = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1),
    }

    def __init__(self, grid: Sequence[str] = DEFAULT_GRID) -> None:
        self.grid = list(grid)
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.start: Pos = next(self._find("S"))
        self.goal: Pos = next(self._find("G"))

    def _find(self, char: str) -> Iterator[Pos]:
        for r, row in enumerate(self.grid):
            for c, cell in enumerate(row):
                if cell == char:
                    yield (r, c)

    def is_open(self, pos: Pos) -> bool:
        r, c = pos
        return 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] != "#"

    def neighbors(self, pos: Pos) -> Iterator[tuple[str, Pos]]:
        for action, (dr, dc) in self.ACTIONS.items():
            nxt = (pos[0] + dr, pos[1] + dc)
            if self.is_open(nxt):
                yield action, nxt

    def step(self, state: Pos, action: str) -> tuple[Pos, float, bool]:
        """Apply an action; bumping a wall keeps the agent in place."""
        dr, dc = self.ACTIONS[action]
        nxt = (state[0] + dr, state[1] + dc)
        if not self.is_open(nxt):
            nxt = state
        if nxt == self.goal:
            return nxt, 10.0, True
        return nxt, -0.1, False

    def render(self, path: Sequence[Pos] = ()) -> str:
        marks = set(path) - {self.start, self.goal}
        lines = []
        for r, row in enumerate(self.grid):
            lines.append(
                "".join("*" if (r, c) in marks else cell for c, cell in enumerate(row))
            )
        return "\n".join(lines)


# ── 3. Decision making: tabular Q-learning ────────────────────────────────


class QLearningAgent:
    """Learns action values by trial and error (no model of the world)."""

    def __init__(
        self,
        world: GridWorld,
        alpha: float = 0.5,
        gamma: float = 0.9,
        epsilon: float = 0.2,
        seed: int = 0,
    ) -> None:
        self.world = world
        self.alpha = alpha      # learning rate
        self.gamma = gamma      # discount factor
        self.epsilon = epsilon  # exploration rate
        self.rng = random.Random(seed)
        self.q: dict[tuple[Pos, str], float] = {}

    def _best_action(self, state: Pos) -> str:
        actions = list(self.world.ACTIONS)
        return max(actions, key=lambda a: self.q.get((state, a), 0.0))

    def train(self, episodes: int = 500, max_steps: int = 100) -> None:
        for _ in range(episodes):
            state = self.world.start
            for _ in range(max_steps):
                if self.rng.random() < self.epsilon:
                    action = self.rng.choice(list(self.world.ACTIONS))
                else:
                    action = self._best_action(state)
                nxt, reward, done = self.world.step(state, action)
                best_next = max(
                    self.q.get((nxt, a), 0.0) for a in self.world.ACTIONS
                )
                old = self.q.get((state, action), 0.0)
                self.q[(state, action)] = old + self.alpha * (
                    reward + self.gamma * best_next - old
                )
                state = nxt
                if done:
                    break

    def greedy_path(self, max_steps: int = 50) -> list[Pos]:
        """Follow the learned policy without exploration."""
        state = self.world.start
        path = [state]
        for _ in range(max_steps):
            state, _, done = self.world.step(state, self._best_action(state))
            path.append(state)
            if done:
                break
        return path


# ── 4. Planning: A* search ────────────────────────────────────────────────


def a_star(world: GridWorld, start: Pos, goal: Pos) -> Optional[list[Pos]]:
    """Shortest path via A* with a Manhattan-distance heuristic."""

    def heuristic(pos: Pos) -> int:
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    frontier: list[tuple[int, Pos]] = [(heuristic(start), start)]
    came_from: dict[Pos, Pos] = {}
    cost_so_far: dict[Pos, int] = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)
        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]
        for _, nxt in world.neighbors(current):
            new_cost = cost_so_far[current] + 1
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                came_from[nxt] = current
                heapq.heappush(frontier, (new_cost + heuristic(nxt), nxt))
    return None


# ── 5. Memory: episodic + semantic ────────────────────────────────────────


@dataclass
class Episode:
    """One remembered experience: what happened, and how it went."""

    situation: str
    action: str
    outcome: str
    reward: float


class EpisodicMemory:
    """Remembers individual experiences; recalls them by keyword overlap."""

    def __init__(self, capacity: int = 200) -> None:
        self._episodes: deque[Episode] = deque(maxlen=capacity)

    def store(self, episode: Episode) -> None:
        self._episodes.append(episode)

    def recall(self, query: str, k: int = 3) -> list[Episode]:
        query_words = set(query.lower().split())

        def score(ep: Episode) -> int:
            text = f"{ep.situation} {ep.action} {ep.outcome}".lower()
            return len(query_words & set(text.split()))

        ranked = sorted(self._episodes, key=score, reverse=True)
        return [ep for ep in ranked[:k] if score(ep) > 0]

    def __len__(self) -> int:
        return len(self._episodes)

    def __iter__(self) -> Iterator[Episode]:
        return iter(self._episodes)


class SemanticMemory:
    """Stores general facts distilled from experience."""

    def __init__(self) -> None:
        self.facts: dict[str, str] = {}

    def remember(self, key: str, fact: str) -> None:
        self.facts[key] = fact

    def lookup(self, key: str) -> Optional[str]:
        return self.facts.get(key)

    def consolidate(self, episodic: EpisodicMemory) -> None:
        """Turn raw episodes into general beliefs (a crude 'sleep phase')."""
        totals: dict[str, list[float]] = {}
        for ep in episodic:
            totals.setdefault(ep.action, []).append(ep.reward)
        for action, rewards in totals.items():
            avg = sum(rewards) / len(rewards)
            quality = "worthwhile" if avg > 0 else "costly"
            self.facts[f"action:{action}"] = (
                f"'{action}' has been {quality} (avg reward {avg:+.2f} "
                f"over {len(rewards)} experiences)"
            )


# ── 6. Integration: the cognitive agent ───────────────────────────────────


@dataclass
class CognitiveAgent:
    """Ties the pieces together in a perceive → recall → plan → act → learn
    loop. This orchestration — not any single component — is the part that
    AGI research is really about, and the part nobody has solved yet.
    """

    world: GridWorld
    episodic: EpisodicMemory = field(default_factory=EpisodicMemory)
    semantic: SemanticMemory = field(default_factory=SemanticMemory)

    def run_task(self) -> list[str]:
        """Navigate start → goal once, remembering everything on the way."""
        log: list[str] = []

        # Perceive: observe where we are and where we need to go.
        start, goal = self.world.start, self.world.goal
        log.append(f"perceive: I am at {start}, the goal is at {goal}")

        # Recall: have we seen anything like this before?
        prior = self.semantic.lookup("task:navigate")
        log.append(f"recall:   {prior or 'no prior knowledge of this task'}")

        # Plan: use the deliberate, model-based planner.
        path = a_star(self.world, start, goal)
        if path is None:
            log.append("plan:     no route exists — giving up")
            return log
        log.append(f"plan:     A* found a {len(path) - 1}-step route")

        # Act + learn: walk the plan, storing each step as an episode.
        state = start
        for nxt in path[1:]:
            action = next(
                a
                for a, (dr, dc) in self.world.ACTIONS.items()
                if (state[0] + dr, state[1] + dc) == nxt
            )
            state, reward, done = self.world.step(state, action)
            self.episodic.store(
                Episode(
                    situation=f"at {state}",
                    action=action,
                    outcome="reached the goal" if done else f"moved to {state}",
                    reward=reward,
                )
            )
        log.append(f"act:      executed the plan, arrived at {state}")

        # Reflect: distil the raw experience into general knowledge.
        self.semantic.consolidate(self.episodic)
        self.semantic.remember(
            "task:navigate",
            f"navigating {start} → {goal} takes {len(path) - 1} steps",
        )
        log.append(
            f"learn:    stored {len(self.episodic)} episodes, "
            f"{len(self.semantic.facts)} beliefs"
        )
        return log


# ── Demo ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("NOTE: real AGI does not exist; these are toy versions of the")
    print("components AGI research talks about. (本物のAGIは未実現です)")
    print("=" * 70)

    # 1. Learning — XOR is the classic "needs a hidden layer" problem.
    print("\n── 1. Learning: neural network learns XOR ──")
    xor_data = [
        ([0.0, 0.0], [0.0]),
        ([0.0, 1.0], [1.0]),
        ([1.0, 0.0], [1.0]),
        ([1.0, 1.0], [0.0]),
    ]
    net = TinyNeuralNetwork([2, 4, 1])
    net.train(xor_data, epochs=5000)
    for inputs, targets in xor_data:
        out = net.predict(inputs)[0]
        print(f"  {inputs} → {out:.3f}  (expected {targets[0]:.0f})")

    # 2. Decision — Q-learning discovers the maze by trial and error.
    print("\n── 2. Decision: Q-learning in a grid world ──")
    world = GridWorld()
    q_agent = QLearningAgent(world)
    q_agent.train(episodes=500)
    q_path = q_agent.greedy_path()
    print(f"  learned a {len(q_path) - 1}-step route after 500 episodes:")
    print("  " + world.render(q_path).replace("\n", "\n  "))

    # 3. Planning — A* finds the optimal route directly from the model.
    print("\n── 3. Planning: A* search ──")
    plan = a_star(world, world.start, world.goal)
    assert plan is not None
    print(f"  optimal route is {len(plan) - 1} steps: {plan}")

    # 4. Memory — store experiences, recall by similarity.
    print("\n── 4. Memory: episodic recall ──")
    memory = EpisodicMemory()
    memory.store(Episode("at the cliff edge", "step forward", "fell down", -5.0))
    memory.store(Episode("at the cliff edge", "step back", "stayed safe", 1.0))
    memory.store(Episode("in the meadow", "step forward", "found food", 3.0))
    for ep in memory.recall("standing at the cliff edge", k=2):
        print(f"  recalled: {ep.situation} / {ep.action} → {ep.outcome} "
              f"({ep.reward:+.1f})")

    # 5. Integration — the full cognitive loop.
    print("\n── 5. Integration: cognitive agent loop ──")
    agent = CognitiveAgent(world)
    for line in agent.run_task():
        print(f"  {line}")
    print("  beliefs after reflection:")
    for fact in agent.semantic.facts.values():
        print(f"    - {fact}")
