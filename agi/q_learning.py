"""
Q-Learning (強化学習 / Reinforcement Learning)

試行錯誤を通じて環境から自律的に行動方針を学習するアルゴリズム。
「経験からの学習」は AGI に不可欠な要素のひとつ。

Q(s, a) <- Q(s, a) + α * (r + γ * max_a' Q(s', a') - Q(s, a))

- α (learning rate): 新しい経験をどれだけ反映するか
- γ (discount factor): 将来の報酬をどれだけ重視するか
- ε (epsilon): 探索 (exploration) と活用 (exploitation) のバランス
"""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Dict, List, Tuple

State = Tuple[int, int]
Action = str

ACTIONS: List[Action] = ["up", "down", "left", "right"]
MOVES: Dict[Action, Tuple[int, int]] = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}


class GridWorld:
    """壁と落とし穴のあるグリッド環境。G に到達すると成功。

    S . . .
    . # . X
    . # . .
    . . . G
    """

    def __init__(self):
        self.rows, self.cols = 4, 4
        self.start: State = (0, 0)
        self.goal: State = (3, 3)
        self.walls = {(1, 1), (2, 1)}
        self.pits = {(1, 3)}
        self.state = self.start

    def reset(self) -> State:
        self.state = self.start
        return self.state

    def step(self, action: Action) -> Tuple[State, float, bool]:
        """行動を実行し (次状態, 報酬, 終了フラグ) を返す。"""
        dr, dc = MOVES[action]
        r, c = self.state
        nr, nc = r + dr, c + dc
        # 盤外・壁は移動失敗 (その場に留まる)
        if not (0 <= nr < self.rows and 0 <= nc < self.cols) or (nr, nc) in self.walls:
            nr, nc = r, c
        self.state = (nr, nc)
        if self.state == self.goal:
            return self.state, 10.0, True
        if self.state in self.pits:
            return self.state, -10.0, True
        return self.state, -0.1, False  # 1歩ごとの小さなコスト


class QLearningAgent:
    def __init__(self, alpha: float = 0.1, gamma: float = 0.9, epsilon: float = 0.2):
        self.q: Dict[Tuple[State, Action], float] = defaultdict(float)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def choose_action(self, state: State) -> Action:
        """ε-greedy: 確率 ε でランダム探索、それ以外は最良の行動。"""
        if random.random() < self.epsilon:
            return random.choice(ACTIONS)
        return self.best_action(state)

    def best_action(self, state: State) -> Action:
        return max(ACTIONS, key=lambda a: self.q[(state, a)])

    def update(self, state: State, action: Action, reward: float,
               next_state: State, done: bool) -> None:
        target = reward
        if not done:
            target += self.gamma * max(self.q[(next_state, a)] for a in ACTIONS)
        self.q[(state, action)] += self.alpha * (target - self.q[(state, action)])


def train(episodes: int = 500, seed: int = 42) -> QLearningAgent:
    random.seed(seed)
    env = GridWorld()
    agent = QLearningAgent()
    for _ in range(episodes):
        state = env.reset()
        for _ in range(100):  # 1エピソードの最大ステップ数
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)
            agent.update(state, action, reward, next_state, done)
            state = next_state
            if done:
                break
    return agent


def show_policy(agent: QLearningAgent, env: GridWorld) -> None:
    arrows = {"up": "^", "down": "v", "left": "<", "right": ">"}
    for r in range(env.rows):
        row = []
        for c in range(env.cols):
            if (r, c) == env.goal:
                row.append("G")
            elif (r, c) in env.walls:
                row.append("#")
            elif (r, c) in env.pits:
                row.append("X")
            else:
                row.append(arrows[agent.best_action((r, c))])
        print(" ".join(row))


if __name__ == "__main__":
    agent = train()
    env = GridWorld()

    print("=== 学習後の方策 (Learned Policy) ===")
    show_policy(agent, env)

    # 学習した方策でゴールまで歩く
    state = env.reset()
    path = [state]
    for _ in range(20):
        state, reward, done = env.step(agent.best_action(state))
        path.append(state)
        if done:
            break
    print("\nPath:", " -> ".join(map(str, path)))
    print("Reached goal:", state == env.goal)
