"""
Monte Carlo Tree Search (MCTS) — planning by statistics, not by heuristics
（モンテカルロ木探索: 評価関数なしで先読みする）

A* (ai/agi_demo.py) needs a heuristic; minimax needs an evaluation function.
MCTS needs neither — only the rules of the game. It grows a lopsided search
tree by repeating four phases:

    1. SELECT     descend the tree, at each node picking the child that
                  maximizes UCB1 = win_rate + c·√(ln N / n)
                  (exploit what looks good + explore what is under-tried)
    2. EXPAND     add one new child position to the tree
    3. SIMULATE   play random moves from there to the end of the game
    4. BACKPROPAGATE  feed the result back up the path

Thousands of these cheap random playouts concentrate, via UCB1, on the most
promising lines — the tree grows deep exactly where it matters. This is the
algorithm behind AlphaGo (which replaced the random playouts with a neural
network's judgement), and it is an *anytime* planner: stop it whenever you
like and it gives its current best move.

The demo uses tic-tac-toe: small enough to verify that MCTS finds winning
moves, blocks threats, crushes a random player, and — since perfect play
makes tic-tac-toe a draw — always draws against itself.
"""

from __future__ import annotations

import math
import random
from typing import Callable, Optional

Board = tuple[str, ...]        # 9 cells: 'X', 'O' or ' '
State = tuple[Board, str]      # (board, player to move)
Player = Callable[[State], int]

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # columns
    (0, 4, 8), (2, 4, 6),              # diagonals
]


# ── The game: tic-tac-toe ─────────────────────────────────────────────────


class TicTacToe:
    """Rules only — no strategy, no evaluation. MCTS needs nothing more."""

    @staticmethod
    def initial() -> State:
        return ((" ",) * 9, "X")

    @staticmethod
    def winner(state: State) -> Optional[str]:
        """'X' or 'O' for a win, 'draw' for a full board, None if ongoing."""
        board, _ = state
        for a, b, c in WIN_LINES:
            if board[a] != " " and board[a] == board[b] == board[c]:
                return board[a]
        return "draw" if " " not in board else None

    @staticmethod
    def legal_moves(state: State) -> list[int]:
        if TicTacToe.winner(state) is not None:
            return []
        return [i for i, cell in enumerate(state[0]) if cell == " "]

    @staticmethod
    def apply(state: State, move: int) -> State:
        board, player = state
        new_board = board[:move] + (player,) + board[move + 1:]
        return new_board, ("O" if player == "X" else "X")

    @staticmethod
    def render(board: Board) -> str:
        rows = ["│".join(board[r * 3:(r + 1) * 3]) for r in range(3)]
        return "\n─┼─┼─\n".join(rows)


# ── The search ────────────────────────────────────────────────────────────


class _Node:
    """One position in the search tree."""

    def __init__(
        self, state: State, parent: Optional[_Node] = None, move: Optional[int] = None
    ) -> None:
        self.state = state
        self.parent = parent
        self.move = move                     # the move that led to this node
        self.children: list[_Node] = []
        self.untried = TicTacToe.legal_moves(state)
        self.visits = 0
        self.value = 0.0   # total reward, seen by the player who just moved

    def win_rate(self) -> float:
        return self.value / self.visits if self.visits else 0.0


def mcts_search(
    state: State,
    iterations: int = 500,
    exploration: float = 1.4,
    rng: Optional[random.Random] = None,
) -> tuple[int, _Node]:
    """Run MCTS from `state`; return (best move, root node with statistics)."""
    rng = rng or random.Random()
    root = _Node(state)

    for _ in range(iterations):
        node = root

        # 1. SELECT — descend while fully expanded, maximizing UCB1
        while not node.untried and node.children:
            node = max(
                node.children,
                key=lambda child: child.win_rate()
                + exploration * math.sqrt(math.log(node.visits) / child.visits),
            )

        # 2. EXPAND — try one new move from this position
        if node.untried:
            move = node.untried.pop(rng.randrange(len(node.untried)))
            child = _Node(TicTacToe.apply(node.state, move), parent=node, move=move)
            node.children.append(child)
            node = child

        # 3. SIMULATE — random playout to the end of the game
        playout = node.state
        result = TicTacToe.winner(playout)
        while result is None:
            playout = TicTacToe.apply(playout, rng.choice(TicTacToe.legal_moves(playout)))
            result = TicTacToe.winner(playout)

        # 4. BACKPROPAGATE — credit the result to every node on the path
        while node is not None:
            node.visits += 1
            just_moved = "O" if node.state[1] == "X" else "X"
            if result == "draw":
                node.value += 0.5
            elif result == just_moved:
                node.value += 1.0
            node = node.parent

    best = max(root.children, key=lambda child: child.visits)
    return best.move, root  # type: ignore[return-value]


# ── Players and matches ───────────────────────────────────────────────────


def mcts_player(iterations: int, rng: random.Random) -> Player:
    return lambda state: mcts_search(state, iterations, rng=rng)[0]


def random_player(rng: random.Random) -> Player:
    return lambda state: rng.choice(TicTacToe.legal_moves(state))


def play(player_x: Player, player_o: Player) -> str:
    state = TicTacToe.initial()
    players = {"X": player_x, "O": player_o}
    result = TicTacToe.winner(state)
    while result is None:
        state = TicTacToe.apply(state, players[state[1]](state))
        result = TicTacToe.winner(state)
    return result


def show_search(state: State, iterations: int, rng: random.Random) -> None:
    """Print how the search allocated its simulations across the moves."""
    board, player = state
    print("  " + TicTacToe.render(board).replace("\n", "\n  "))
    move, root = mcts_search(state, iterations, rng=rng)
    print(f"  '{player}' to move — {iterations} simulations:")
    for child in sorted(root.children, key=lambda c: c.visits, reverse=True):
        r, c = divmod(child.move, 3)
        print(f"    cell ({r},{c}): {child.visits:>5} visits, "
              f"win rate {child.win_rate():.2f}")
    r, c = divmod(move, 3)
    print(f"  chosen: ({r},{c})")


# ── Demo ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    rng = random.Random(0)

    print("── 1. Finding the winning move ──")
    # X can win immediately at (0,2); simulations should pile onto it.
    board = ("X", "X", " ",
             "O", "O", " ",
             " ", " ", " ")
    show_search((board, "X"), iterations=2000, rng=rng)

    print("\n── 2. Blocking the opponent's threat ──")
    # X threatens the diagonal (0,0)-(1,1)-(2,2); O must block at (2,2).
    board = ("X", " ", " ",
             " ", "X", "O",
             " ", " ", " ")
    show_search((board, "O"), iterations=2000, rng=rng)

    print("\n── 3. MCTS vs a random player (40 games, sides swapped) ──")
    scores = {"mcts": 0, "random": 0, "draw": 0}
    for game_index in range(40):
        strong = mcts_player(300, rng)
        weak = random_player(rng)
        if game_index % 2 == 0:
            result = play(strong, weak)
            mcts_side = "X"
        else:
            result = play(weak, strong)
            mcts_side = "O"
        if result == "draw":
            scores["draw"] += 1
        elif result == mcts_side:
            scores["mcts"] += 1
        else:
            scores["random"] += 1
    print(f"  MCTS {scores['mcts']} wins / {scores['draw']} draws "
          f"/ {scores['random']} losses")

    print("\n── 4. MCTS vs MCTS (6 games) ──")
    results = [play(mcts_player(500, rng), mcts_player(500, rng)) for _ in range(6)]
    draws = sum(r == "draw" for r in results)
    print(f"  {draws}/6 draws — perfect play makes tic-tac-toe a draw,")
    print("  so mutual draws are exactly what strong play looks like")
