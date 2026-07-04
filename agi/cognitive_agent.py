"""
Cognitive Agent (認知アーキテクチャ)

AGI 研究で議論される認知アーキテクチャ (SOAR, ACT-R など) の
考え方を単純化した統合デモ。1つの能力に特化した AI と違い、
複数の認知機能をループとして統合するのが特徴。

    知覚 (perceive) -> 記憶 (remember) -> 推論 (reason)
        -> 計画 (plan) -> 行動 (act) -> 学習 (learn) -> ...

エージェントは未知の迷路に置かれ、地図を持たないまま
探索・記憶・推論を繰り返してゴールと宝物を見つける。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from typing import Dict, List, Optional, Set, Tuple

Pos = Tuple[int, int]

MAZE = [
    "S....#..",
    ".##..#.t",
    "..#..#..",
    "..#.....",
    "#.###.#.",
    "......#G",
]
MOVES: Dict[str, Tuple[int, int]] = {
    "up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1),
}


class Environment:
    """エージェントには全体地図を見せず、隣接マスの知覚のみ与える。"""

    def __init__(self, maze: List[str]):
        self.maze = maze
        self.rows, self.cols = len(maze), len(maze[0])
        for r, row in enumerate(maze):
            for c, ch in enumerate(row):
                if ch == "S":
                    self.start: Pos = (r, c)
                if ch == "G":
                    self.goal: Pos = (r, c)

    def cell(self, pos: Pos) -> str:
        r, c = pos
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return "#"
        return self.maze[r][c]

    def percept(self, pos: Pos) -> Dict[Pos, str]:
        """現在地と隣接4マスの状態 (局所的な知覚)。"""
        r, c = pos
        cells = [pos, (r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        return {p: self.cell(p) for p in cells}


@dataclass
class Memory:
    """エピソード記憶 (体験ログ) と意味記憶 (学習した地図) を持つ。"""
    world_map: Dict[Pos, str] = field(default_factory=dict)   # 意味記憶
    episodes: List[str] = field(default_factory=list)          # エピソード記憶
    visited: Set[Pos] = field(default_factory=set)

    def remember_percept(self, percept: Dict[Pos, str]) -> None:
        self.world_map.update(percept)

    def log(self, event: str) -> None:
        self.episodes.append(event)


class CognitiveAgent:
    def __init__(self, env: Environment):
        self.env = env
        self.pos = env.start
        self.memory = Memory()
        self.treasures: Set[Pos] = set()
        self.goal_seen: Optional[Pos] = None

    # --- 知覚: 環境から局所情報を取り込む ---
    def perceive(self) -> None:
        percept = self.env.percept(self.pos)
        self.memory.remember_percept(percept)
        self.memory.visited.add(self.pos)
        for p, ch in percept.items():
            if ch == "G" and self.goal_seen is None:
                self.goal_seen = p
                self.memory.log(f"{self.pos} でゴール {p} を発見")
            if ch == "t" and p not in self.treasures:
                self.treasures.add(p)
                self.memory.log(f"{self.pos} で宝物 {p} を発見")

    # --- 推論: 記憶に基づいて次の目的地を決める ---
    def reason(self) -> Optional[Pos]:
        # 未回収の宝物があればそちらを優先、次にゴール、
        # どちらも知らなければ未探索の場所 (フロンティア) へ
        unclaimed = self.treasures - self.memory.visited
        if unclaimed:
            return min(unclaimed)  # 決定的に選ぶ
        if self.goal_seen:
            return self.goal_seen
        frontier = [
            p for p, ch in self.memory.world_map.items()
            if ch != "#" and p not in self.memory.visited
        ]
        return min(frontier) if frontier else None

    # --- 計画: 記憶した地図の上を BFS して経路を立てる ---
    def plan(self, destination: Pos) -> List[Pos]:
        queue = deque([self.pos])
        came_from: Dict[Pos, Pos] = {}
        while queue:
            current = queue.popleft()
            if current == destination:
                path = [current]
                while current != self.pos:
                    current = came_from[current]
                    path.append(current)
                return path[::-1]
            r, c = current
            for nxt in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
                known = self.memory.world_map.get(nxt)
                if known is not None and known != "#" and nxt not in came_from \
                        and nxt != self.pos:
                    came_from[nxt] = current
                    queue.append(nxt)
        return []

    # --- 行動 + 学習のメインループ ---
    def run(self, max_steps: int = 200) -> bool:
        for step in range(max_steps):
            self.perceive()
            if self.pos == self.env.goal:
                self.memory.log(f"ステップ {step} でゴール到達")
                return True
            destination = self.reason()
            if destination is None:
                self.memory.log("行き先がない (探索完了)")
                return False
            path = self.plan(destination)
            if len(path) < 2:
                self.memory.visited.add(destination)  # 到達不能とみなし学習
                continue
            self.pos = path[1]  # 計画の最初の1歩だけ実行し、再度知覚する
        return False


if __name__ == "__main__":
    env = Environment(MAZE)
    agent = CognitiveAgent(env)

    print("=== 認知エージェントの迷路探索 ===")
    print("\n".join(MAZE))
    print()

    success = agent.run()
    print("ゴール到達:", success)
    print("宝物の発見数:", len(agent.treasures))
    print("探索したマス:", len(agent.memory.visited),
          "/ 地図として記憶したマス:", len(agent.memory.world_map))

    print("\n=== エピソード記憶 ===")
    for event in agent.memory.episodes:
        print(" -", event)
