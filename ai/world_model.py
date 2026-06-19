"""
World Models — learning the rules of a world, then planning inside it

NVIDIA's Cosmos and "world foundation models" embody a powerful idea: instead of
learning only by trial and error in the real world, an agent learns a *model* of
how the world works — its dynamics — and then trains or plans inside that learned
model ("in imagination"). This is model-based reinforcement learning.

Here an agent explores a gridworld, learns its transition and reward functions
from experience, then plans an optimal policy entirely from the learned model and
verifies that an imagined rollout matches reality.
"""

from __future__ import annotations

import random


ROWS, COLS, GOAL = 4, 4, (0, 3)
ACTIONS = {"^": (-1, 0), "v": (1, 0), "<": (0, -1), ">": (0, 1)}


def real_step(state, action):
    """The true (hidden) environment dynamics the agent must discover."""
    dr, dc = ACTIONS[action]
    r, c = state[0] + dr, state[1] + dc
    nxt = (r, c) if 0 <= r < ROWS and 0 <= c < COLS else state
    return nxt, (1.0 if nxt == GOAL else -0.04), nxt == GOAL


def learn_model(episodes=400, seed=0):
    """Explore randomly; record learned transitions T and rewards R."""
    rng = random.Random(seed)
    T, R = {}, {}
    for _ in range(episodes):
        state = (ROWS - 1, 0)
        for _ in range(20):
            if state == GOAL:
                break
            a = rng.choice(list(ACTIONS))
            nxt, reward, _ = real_step(state, a)
            T[(state, a)] = nxt           # learned dynamics
            R[(state, a)] = reward
            state = nxt
    return T, R


def plan(T, R, gamma=0.95, sweeps=100):
    """Value iteration on the LEARNED model (no real interaction)."""
    states = [(r, c) for r in range(ROWS) for c in range(COLS)]
    V = {s: 0.0 for s in states}
    for _ in range(sweeps):
        for s in states:
            if s == GOAL:
                continue
            options = [R[(s, a)] + gamma * V[T[(s, a)]]
                       for a in ACTIONS if (s, a) in T]
            if options:
                V[s] = max(options)
    policy = {}
    for s in states:
        if s == GOAL:
            continue
        acts = [(R[(s, a)] + gamma * V[T[(s, a)]], a)
                for a in ACTIONS if (s, a) in T]
        if acts:
            policy[s] = max(acts)[1]
    return policy


def rollout(policy, start, use_model=None):
    """Follow the policy; use the learned model if given, else the real world."""
    state, path = start, [start]
    for _ in range(20):
        if state == GOAL or state not in policy:
            break
        a = policy[state]
        state = use_model[(state, a)] if use_model else real_step(state, a)[0]
        path.append(state)
    return path


if __name__ == "__main__":
    T, R = learn_model()
    total = ROWS * COLS * len(ACTIONS)
    print("World model — learn the dynamics, then plan in imagination\n")
    print(f"  transitions learned by exploration: {len(T)} / {total}")

    policy = plan(T, R)
    print("\n  Policy planned purely from the learned model (G = goal):")
    for r in range(ROWS):
        print("    " + " ".join("G" if (r, c) == GOAL else policy.get((r, c), "·")
                                for c in range(COLS)))

    start = (ROWS - 1, 0)
    imagined = rollout(policy, start, use_model=T)
    real = rollout(policy, start)
    print(f"\n  imagined rollout: {imagined}")
    print(f"  real rollout    : {real}")
    print(f"  imagination matches reality? {imagined == real}")
    print("\n  The agent discovered the world's rules, then solved the task")
    print("  inside its own model — the essence of a world model.")
