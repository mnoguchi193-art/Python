"""
Model-based reinforcement learning — Dyna-Q
（経験からの計画モデル学習）

The Q-learner in ai/agi_demo.py is *model-free*: every improvement requires a
real step in the world. Dyna-Q (Sutton, 1990) additionally remembers every
observed transition (state, action) → (next state, reward) as a learned model
of the world, and between real steps replays random remembered transitions as
imagined practice ("planning"). The same amount of real experience yields far
more learning.

The learned model is also a genuine *planning* model: once enough transitions
are remembered, the agent can search inside it — in its imagination, without
touching the real world at all — and extract a complete route to the goal.
"""

from __future__ import annotations

import random
from collections import deque
from typing import Optional

from agi_demo import GridWorld, Pos, a_star

Transition = tuple[Pos, float, bool]  # (next state, reward, episode done?)


# ── Model-free baseline: Q-learning with per-episode stats ────────────────


class MeasuredQAgent:
    """ε-greedy tabular Q-learning that reports steps needed per episode."""

    def __init__(
        self,
        world: GridWorld,
        alpha: float = 0.5,
        gamma: float = 0.9,
        epsilon: float = 0.15,
        seed: int = 3,
    ) -> None:
        self.world = world
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.rng = random.Random(seed)
        self.q: dict[tuple[Pos, str], float] = {}

    def _best_action(self, state: Pos) -> str:
        actions = list(self.world.ACTIONS)
        return max(actions, key=lambda a: self.q.get((state, a), 0.0))

    def _update(
        self, state: Pos, action: str, reward: float, nxt: Pos, done: bool
    ) -> None:
        best_next = 0.0 if done else max(
            self.q.get((nxt, a), 0.0) for a in self.world.ACTIONS
        )
        old = self.q.get((state, action), 0.0)
        self.q[(state, action)] = old + self.alpha * (
            reward + self.gamma * best_next - old
        )

    def _after_real_step(
        self, state: Pos, action: str, reward: float, nxt: Pos, done: bool
    ) -> None:
        """Hook for subclasses; the model-free baseline does nothing extra."""

    def run_episode(self, max_steps: int = 150) -> int:
        """One learning episode; returns real steps taken (max_steps if failed)."""
        state = self.world.start
        for step in range(1, max_steps + 1):
            if self.rng.random() < self.epsilon:
                action = self.rng.choice(list(self.world.ACTIONS))
            else:
                action = self._best_action(state)
            nxt, reward, done = self.world.step(state, action)
            self._update(state, action, reward, nxt, done)
            self._after_real_step(state, action, reward, nxt, done)
            state = nxt
            if done:
                return step
        return max_steps


# ── Dyna-Q: learn a model, practise inside it ─────────────────────────────


class DynaQAgent(MeasuredQAgent):
    """Q-learning plus a learned world model replayed as imagined practice."""

    def __init__(
        self, world: GridWorld, planning_steps: int = 25, **kwargs: float
    ) -> None:
        super().__init__(world, **kwargs)
        self.planning_steps = planning_steps
        self.model: dict[tuple[Pos, str], Transition] = {}

    def _after_real_step(
        self, state: Pos, action: str, reward: float, nxt: Pos, done: bool
    ) -> None:
        # Learn the model: remember exactly what the world just did.
        self.model[(state, action)] = (nxt, reward, done)
        # Planning: replay random remembered transitions as extra updates.
        known = list(self.model)
        for _ in range(self.planning_steps):
            s, a = self.rng.choice(known)
            s2, r, d = self.model[(s, a)]
            self._update(s, a, r, s2, d)


def plan_in_model(
    model: dict[tuple[Pos, str], Transition], start: Pos
) -> Optional[list[Pos]]:
    """BFS over remembered transitions only — planning in imagination.

    No calls to the real world here: every edge searched is a memory.
    """
    goals = {nxt for nxt, _, done in model.values() if done}
    neighbors: dict[Pos, list[Pos]] = {}
    for (state, _), (nxt, _, _) in model.items():
        if nxt != state:  # wall bumps are self-loops, useless for routing
            neighbors.setdefault(state, []).append(nxt)

    frontier: deque[Pos] = deque([start])
    came_from: dict[Pos, Optional[Pos]] = {start: None}
    while frontier:
        current = frontier.popleft()
        if current in goals:
            path = [current]
            while came_from[current] is not None:
                current = came_from[current]  # type: ignore[assignment]
                path.append(current)
            return path[::-1]
        for nxt in neighbors.get(current, []):
            if nxt not in came_from:
                came_from[nxt] = current
                frontier.append(nxt)
    return None


# ── Demo ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    world = GridWorld()
    EPISODES = 30

    baseline = MeasuredQAgent(world, seed=3)
    dyna = DynaQAgent(world, planning_steps=25, seed=3)
    baseline_steps = [baseline.run_episode() for _ in range(EPISODES)]
    dyna_steps = [dyna.run_episode() for _ in range(EPISODES)]

    optimal = a_star(world, world.start, world.goal)
    assert optimal is not None
    print(f"optimal route: {len(optimal) - 1} steps (for reference)\n")

    print("── Sample efficiency: model-free vs model-based ──")
    print("  real steps to reach the goal per episode (cap 150):")
    print("    episode   Q-learning   Dyna-Q(25)")
    for episode in [1, 2, 3, 4, 5, 10, 20, 30]:
        print(
            f"    {episode:>7}   {baseline_steps[episode - 1]:>10}"
            f"   {dyna_steps[episode - 1]:>10}"
        )
    print(f"    total real steps: Q-learning {sum(baseline_steps)}, "
          f"Dyna-Q {sum(dyna_steps)}")

    print("\n── Planning inside the learned model ──")
    reachable = sum(1 for row in world.grid for cell in row if cell != "#")
    print(f"  model learned from experience: {len(dyna.model)} transitions "
          f"(world has {reachable} open cells x 4 actions)")
    route = plan_in_model(dyna.model, world.start)
    if route is None:
        print("  the model does not yet contain a route to the goal")
    else:
        print(f"  route found purely in imagination: {len(route) - 1} steps")
        print("  " + world.render(route).replace("\n", "\n  "))
