"""
Q-Learning — reinforcement learning from trial and error

The algorithm behind game-playing AI (and a building block of the RLHF used to
align language models). An agent with no model of the world learns the value of
each action in each state purely from rewards, via the Bellman update:

    Q(s,a) <- Q(s,a) + alpha * [ r + gamma * max_a' Q(s',a') - Q(s,a) ]

Here it learns to cross a gridworld to the goal (+1) while avoiding a pit (-1).
"""

from __future__ import annotations

import random


ROWS, COLS = 3, 4
GOAL, PIT = (0, 3), (1, 3)
ACTIONS = {"^": (-1, 0), "v": (1, 0), "<": (0, -1), ">": (0, 1)}


def step(state: tuple[int, int], action: str) -> tuple[tuple[int, int], float, bool]:
    dr, dc = ACTIONS[action]
    r, c = state[0] + dr, state[1] + dc
    if not (0 <= r < ROWS and 0 <= c < COLS):
        r, c = state                       # bump into the wall, stay put
    nxt = (r, c)
    if nxt == GOAL:
        return nxt, 1.0, True
    if nxt == PIT:
        return nxt, -1.0, True
    return nxt, -0.04, False               # small step cost rewards short paths


def train(episodes: int = 8000, alpha: float = 0.2, gamma: float = 0.95,
          epsilon: float = 0.1, seed: int = 0) -> dict:
    rng = random.Random(seed)
    q = {(r, c): {a: 0.0 for a in ACTIONS}
         for r in range(ROWS) for c in range(COLS)}
    for _ in range(episodes):
        state = (ROWS - 1, 0)              # start bottom-left
        while state not in (GOAL, PIT):
            if rng.random() < epsilon:
                action = rng.choice(list(ACTIONS))
            else:
                action = max(q[state], key=q[state].get)
            nxt, reward, done = step(state, action)
            best_next = 0.0 if done else max(q[nxt].values())
            q[state][action] += alpha * (reward + gamma * best_next
                                         - q[state][action])
            state = nxt
    return q


if __name__ == "__main__":
    q = train()

    print("Q-learning gridworld — learned policy (G=goal, X=pit)\n")
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            if (r, c) == GOAL:
                row.append(" G ")
            elif (r, c) == PIT:
                row.append(" X ")
            else:
                row.append(f" {max(q[(r, c)], key=q[(r, c)].get)} ")
        print("   " + "|".join(row))

    # Follow the greedy policy from the start to show the solved path.
    state, path = (ROWS - 1, 0), [(ROWS - 1, 0)]
    for _ in range(20):
        if state in (GOAL, PIT):
            break
        state, _, _ = step(state, max(q[state], key=q[state].get))
        path.append(state)
    print(f"\n  Greedy path from start: {path}")
    print("\nNo map, no rules given — the agent discovered the route from reward.")
