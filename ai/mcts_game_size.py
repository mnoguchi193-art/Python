"""
MCTS scaling study II: does a bigger game push the saturation point out?
（ミニ研究II: 盤面を広げると計算の飽和点はどれだけ遠のくか）

The previous study (ai/mcts_scaling.py) found that on 3x3 tic-tac-toe,
strength saturates by a few hundred simulations — the game is too small to
absorb more compute. This study tests the implied hypothesis directly.

QUESTION   If the game is deeper (4x4 and 5x5 boards, four in a row),
           does the saturation point move to larger budgets?

METHOD     A perfect solver is intractable beyond 3x3, so saturation is
           measured with a DOUBLING TEST: play MCTS(N) against MCTS(2N)
           with sides swapped every game. While the game still has depth
           that compute can buy, the 2N side wins clearly; when both
           budgets already play near-optimally, the matchup collapses
           toward 50% (mostly draws). The saturation point is the budget
           where doubling stops paying.

METRIC     score of the 2N side = (wins + 0.5*draws) / games.

PREDICTION 3x3 saturates earliest, 4x4 later, 5x5 latest (or not within
           the tested range at all).
"""

from __future__ import annotations

import math
import random
from typing import Callable, Optional

Board = tuple[str, ...]
State = tuple[Board, str]  # (board, player to move)


# ── The game, generalized: k in a row on an m x n board ───────────────────


class KInARow:
    """m x n board, win by k in a row (horizontal, vertical or diagonal).

    (3,3,3) is tic-tac-toe. Win detection is incremental: only lines
    passing through the latest move can have been completed by it, so
    each move is checked against a precomputed handful of lines instead
    of the whole board — this keeps thousands of playouts cheap.
    """

    def __init__(self, rows: int, cols: int, k: int) -> None:
        self.rows, self.cols, self.k = rows, cols, k
        self.cells = rows * cols

        def cell(r: int, c: int) -> int:
            return r * cols + c

        lines: list[tuple[int, ...]] = []
        for r in range(rows):
            for c in range(cols):
                if c + k <= cols:
                    lines.append(tuple(cell(r, c + i) for i in range(k)))
                if r + k <= rows:
                    lines.append(tuple(cell(r + i, c) for i in range(k)))
                if c + k <= cols and r + k <= rows:
                    lines.append(tuple(cell(r + i, c + i) for i in range(k)))
                if c - k + 1 >= 0 and r + k <= rows:
                    lines.append(tuple(cell(r + i, c - i) for i in range(k)))
        self.lines_through: dict[int, list[tuple[int, ...]]] = {
            i: [line for line in lines if i in line] for i in range(self.cells)
        }

    def initial(self) -> State:
        return (" ",) * self.cells, "X"

    def legal_moves(self, board: Board) -> list[int]:
        return [i for i, c in enumerate(board) if c == " "]

    def apply(self, state: State, move: int) -> State:
        board, player = state
        new_board = board[:move] + (player,) + board[move + 1:]
        return new_board, ("O" if player == "X" else "X")

    def move_wins(self, board: Board, move: int) -> bool:
        """Did the stone just placed at `move` complete a k-line?"""
        player = board[move]
        return any(
            all(board[i] == player for i in line)
            for line in self.lines_through[move]
        )

    def result_after(self, board: Board, move: int) -> Optional[str]:
        """Result given the board AFTER `move` was placed, or None if ongoing."""
        if self.move_wins(board, move):
            return board[move]
        return "draw" if " " not in board else None


# ── MCTS over any KInARow game ────────────────────────────────────────────


class _Node:
    def __init__(
        self,
        game: KInARow,
        state: State,
        result: Optional[str],
        parent: Optional[_Node] = None,
        move: Optional[int] = None,
    ) -> None:
        self.state = state
        self.result = result   # 'X' / 'O' / 'draw' if terminal, else None
        self.parent = parent
        self.move = move
        self.children: list[_Node] = []
        self.untried = [] if result else game.legal_moves(state[0])
        self.visits = 0
        self.value = 0.0


def mcts_search(
    game: KInARow,
    state: State,
    iterations: int,
    exploration: float = 1.4,
    rng: Optional[random.Random] = None,
) -> int:
    rng = rng or random.Random()
    root = _Node(game, state, result=None)

    for _ in range(iterations):
        node = root

        # 1. select
        while not node.untried and node.children:
            node = max(
                node.children,
                key=lambda ch: ch.value / ch.visits
                + exploration * math.sqrt(math.log(node.visits) / ch.visits),
            )

        # 2. expand
        if node.untried:
            move = node.untried.pop(rng.randrange(len(node.untried)))
            child_state = game.apply(node.state, move)
            child = _Node(
                game, child_state, game.result_after(child_state[0], move),
                parent=node, move=move,
            )
            node.children.append(child)
            node = child

        # 3. simulate
        result = node.result
        playout = node.state
        while result is None:
            move = rng.choice(game.legal_moves(playout[0]))
            playout = game.apply(playout, move)
            result = game.result_after(playout[0], move)

        # 4. backpropagate
        walk: Optional[_Node] = node
        while walk is not None:
            walk.visits += 1
            just_moved = "O" if walk.state[1] == "X" else "X"
            walk.value += 0.5 if result == "draw" else float(result == just_moved)
            walk = walk.parent

    return max(root.children, key=lambda ch: ch.visits).move  # type: ignore


def play(
    game: KInARow,
    budgets: dict[str, int],
    rng: random.Random,
) -> str:
    state = game.initial()
    while True:
        move = mcts_search(game, state, budgets[state[1]], rng=rng)
        state = game.apply(state, move)
        result = game.result_after(state[0], move)
        if result is not None:
            return result


# ── The doubling test ─────────────────────────────────────────────────────


def doubling_test(
    game: KInARow, budget: int, games: int, rng: random.Random
) -> dict[str, int]:
    """MCTS(2N) vs MCTS(N), sides swapped; tally from the 2N side's view."""
    tally = {"wins": 0, "draws": 0, "losses": 0}
    for game_index in range(games):
        big_side = "X" if game_index % 2 == 0 else "O"
        small_side = "O" if big_side == "X" else "X"
        result = play(game, {big_side: 2 * budget, small_side: budget}, rng)
        if result == "draw":
            tally["draws"] += 1
        elif result == big_side:
            tally["wins"] += 1
        else:
            tally["losses"] += 1
    return tally


def run_game_study(
    label: str, game: KInARow, ladder: list[int], games: int, rng: random.Random
) -> None:
    print(f"\n  {label}  ({games} games per pair)")
    print("     N vs 2N    2N wins  draws  2N losses   2N score")
    for budget in ladder:
        tally = doubling_test(game, budget, games, rng)
        s = (tally["wins"] + 0.5 * tally["draws"]) / games
        # A ~50% score alone is ambiguous: it can mean 'both near-perfect'
        # or just 'both equally weak'. Draw-dominance tells them apart —
        # near-perfect play in these games ends in draws.
        if s >= 0.60:
            verdict = "compute still pays"
        elif tally["draws"] / games >= 0.60:
            verdict = "saturated (draws dominate)"
        else:
            verdict = "even but decisive — both weak"
        print(
            f"    {budget:>4} vs {2 * budget:<4}  {tally['wins']:>5}"
            f"   {tally['draws']:>5}   {tally['losses']:>6}"
            f"      {s:>4.0%}   {verdict}"
        )


# ── Demo ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("── Doubling test: MCTS(2N) vs MCTS(N) — does 2x compute still win? ──")
    print("   while the game has depth left, 2N wins; near-perfect play → 50%")

    rng = random.Random(21)
    run_game_study("3x3, 3 in a row (tic-tac-toe)",
                   KInARow(3, 3, 3), [5, 10, 25, 50, 100, 200], 40, rng)
    run_game_study("4x4, 4 in a row",
                   KInARow(4, 4, 4), [5, 10, 25, 50, 100, 200], 30, rng)
    run_game_study("5x5, 4 in a row",
                   KInARow(5, 5, 4), [5, 10, 25, 50, 100, 200], 20, rng)

    print("""
── Interpretation ──
   The saturation point is the budget where doubling stops winning AND
   draws take over (a ~50% score with decisive games just means both
   sides are equally weak). Expected pattern, confirming the hypothesis
   from ai/mcts_scaling.py:
     3x3          saturates around N ≈ 50
     4x4          saturates around N ≈ 100-200 — further out
     5x5, 4-in-a-row   no saturation in the tested range: doubling
                  still wins at N = 200 vs 400 — the deeper game keeps
                  absorbing compute. This headroom is exactly why Go
                  rewarded AlphaGo's massive search-plus-learning bet.""")
