"""
MCTS scaling study: simulation budget vs playing strength
（ミニ研究: MCTSのシミュレーション回数と棋力の関係）

A small, self-contained example of the research loop described in this
repository's discussions — question, controlled method, measurement,
interpretation — using the MCTS player from ai/mcts_demo.py.

QUESTION   How does playing strength grow as the MCTS player is given more
           simulations per move (i.e., more compute)?

METHOD     For each budget N, play many tic-tac-toe games with sides
           swapped every game (X moves first and has an advantage, so
           swapping controls for it), against two fixed opponents:
             - a random player          (measures raw skill)
             - a PERFECT minimax player (an exact game solver used as a
               reference instrument — it never makes a mistake)
           Every run uses one seeded RNG, so results are reproducible.

METRIC     score = wins + 0.5 * draws, as a fraction of games played.
           Against the perfect opponent the ceiling is exactly 0.5:
           tic-tac-toe is a draw under perfect play, so a win against
           minimax is impossible and "always draw" IS perfect play.

Spoiler: strength rises steeply at first, then saturates — the game is
too small to absorb more compute. In Go the same curve keeps climbing for
orders of magnitude longer; that difference is the compute-scaling story
behind AlphaGo (and, by analogy, LLM scaling laws).
"""

from __future__ import annotations

import random
from functools import lru_cache
from typing import Callable

from mcts_demo import State, TicTacToe, mcts_player, play, random_player

BUDGETS = [1, 5, 10, 25, 50, 100, 250, 500]

Player = Callable[[State], int]
OpponentFactory = Callable[[random.Random], Player]


# ── Reference instrument: a perfect player via memoized minimax ───────────


@lru_cache(maxsize=None)
def _game_value(state: State) -> int:
    """Exact value for the player to move: +1 win, 0 draw, -1 loss."""
    result = TicTacToe.winner(state)
    if result == "draw":
        return 0
    if result is not None:
        return -1  # the previous player completed a line: the mover lost
    return max(
        -_game_value(TicTacToe.apply(state, move))
        for move in TicTacToe.legal_moves(state)
    )


def minimax_player(rng: random.Random) -> Player:
    """Plays perfectly; picks randomly among equally-optimal moves."""

    def choose(state: State) -> int:
        scored = [
            (-_game_value(TicTacToe.apply(state, move)), move)
            for move in TicTacToe.legal_moves(state)
        ]
        best = max(value for value, _ in scored)
        return rng.choice([move for value, move in scored if value == best])

    return choose


def measure(
    budget: int,
    opponent_factory: OpponentFactory,
    games: int,
    rng: random.Random,
) -> dict[str, int]:
    """Play `games` games at the given budget, swapping sides each game."""
    tally = {"wins": 0, "draws": 0, "losses": 0}
    for game_index in range(games):
        subject = mcts_player(budget, rng)
        opponent = opponent_factory(rng)
        if game_index % 2 == 0:
            result, subject_side = play(subject, opponent), "X"
        else:
            result, subject_side = play(opponent, subject), "O"
        if result == "draw":
            tally["draws"] += 1
        elif result == subject_side:
            tally["wins"] += 1
        else:
            tally["losses"] += 1
    return tally


def score(tally: dict[str, int]) -> float:
    games = sum(tally.values())
    return (tally["wins"] + 0.5 * tally["draws"]) / games


def bar(fraction: float, width: int = 30) -> str:
    return "█" * round(fraction * width)


def run_study(
    title: str,
    opponent_factory: OpponentFactory,
    games: int,
    rng: random.Random,
) -> None:
    print(title)
    print("    sims   wins draws losses   score")
    for budget in BUDGETS:
        tally = measure(budget, opponent_factory, games, rng)
        s = score(tally)
        print(
            f"    {budget:>4}   {tally['wins']:>4}  {tally['draws']:>4}"
            f"   {tally['losses']:>4}    {s:>4.0%}  {bar(s)}"
        )


# ── Demo ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    rng = random.Random(42)

    print("── 1. Strength vs a random opponent (100 games per budget) ──")
    print("   measures raw skill; ceiling is 100%\n")
    run_study(
        "   score = wins + 0.5*draws",
        random_player,
        games=100,
        rng=rng,
    )

    print("\n── 2. Strength vs a PERFECT minimax player (30 games per budget) ──")
    print("   winning against perfect play is impossible, so the ceiling")
    print("   is exactly 50% — 'always draw' IS perfect play\n")
    run_study(
        "   score = wins + 0.5*draws",
        minimax_player,
        games=30,
        rng=rng,
    )

    print("""
── Interpretation ──
   - gains are steep at first and then flatten: each extra simulation
     is worth less than the one before (diminishing returns)
   - vs minimax the win column is all zeros, as theory demands — only
     the draw rate grows, approaching the 50% ceiling
   - small wobbles between adjacent budgets are sampling noise
     (30 games has roughly +/-9%-point noise; more games would smooth it)
   - the curve saturates because tic-tac-toe is tiny — once play is
     near-perfect there is nothing left for extra compute to buy
   - in Go the same curve keeps rising for orders of magnitude more
     compute; pairing that headroom with learned playouts is AlphaGo""")
