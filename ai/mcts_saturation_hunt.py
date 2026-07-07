"""
MCTS scaling study III: capturing the 5x5 saturation point
（ミニ研究III: 5x5・四目並べの飽和点を実際に捕まえる）

Study II (ai/mcts_game_size.py) found that on 5x5 four-in-a-row, doubling
compute still won clearly at N = 200 vs 400 — the saturation point was
somewhere beyond the tested range. This study extends the doubling ladder
until the wall is actually found.

QUESTION   At what budget does 5x5 four-in-a-row stop rewarding doubled
           compute?

METHOD     Continue the doubling test MCTS(2N) vs MCTS(N), sides swapped,
           up the ladder N = 200, 400, 800, 1600, 3200, stopping early
           if a saturation signature appears. Two signatures are checked,
           because "the 2N side stops winning" can happen two ways:
             - draws dominate        → the game is a draw when played well
             - first-player (X) wins dominate → the game is an X win when
               played well, and both budgets are strong enough to find it
           m,n,k-game theory says (5,5,4) is a draw under perfect play,
           so the draw signature is EXPECTED — but the measurement checks
           both rather than assuming the answer.
           A third outcome is possible: the doubling premium collapses
           while NEITHER signature appears. That would mean the plateau
           belongs to the algorithm, not the game — random playouts have
           stopped converting extra simulations into better evaluations
           long before the game is solved (the very ceiling AlphaGo broke
           by replacing random playouts with a learned policy).

METRIC     score of the 2N side = (wins + 0.5*draws) / games,
           plus the draw fraction and the first-player win fraction.

NOTE       This study deliberately trades runtime for an answer: the top
           rung plays 3200- and 6400-simulation players against each
           other, and the whole ladder takes a few minutes in pure
           Python.
"""

from __future__ import annotations

import random

from mcts_game_size import KInARow, play

GAMES_PER_PAIR = 30
LADDER = [200, 400, 800, 1600, 3200]


def doubling_test_detailed(
    game: KInARow, budget: int, games: int, rng: random.Random
) -> dict[str, int]:
    """Like study II's doubling test, but also tallies first-player wins."""
    tally = {"wins": 0, "draws": 0, "losses": 0, "x_wins": 0}
    for game_index in range(games):
        big_side = "X" if game_index % 2 == 0 else "O"
        small_side = "O" if big_side == "X" else "X"
        result = play(game, {big_side: 2 * budget, small_side: budget}, rng)
        if result == "X":
            tally["x_wins"] += 1
        if result == "draw":
            tally["draws"] += 1
        elif result == big_side:
            tally["wins"] += 1
        else:
            tally["losses"] += 1
    return tally


def verdict(tally: dict[str, int], games: int) -> tuple[str, bool]:
    """Classify a rung of the ladder; returns (label, is_saturated)."""
    score = (tally["wins"] + 0.5 * tally["draws"]) / games
    if score >= 0.60:
        return "compute still pays", False
    if tally["draws"] / games >= 0.60:
        return "SATURATED — draws dominate", True
    if tally["x_wins"] / games >= 0.80:
        return "SATURATED — first player wins", True
    return "even but decisive", False


# ── Demo ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("── Hunting the saturation point of 5x5, 4 in a row ──")
    print(f"   doubling test, {GAMES_PER_PAIR} games per rung, sides swapped;")
    print("   study II ended unsaturated at 200 vs 400 — we climb from there\n")

    game = KInARow(5, 5, 4)
    rng = random.Random(21)

    print("     N vs 2N     2N wins  draws  2N losses  X wins   2N score")
    captured: int | None = None
    scores: list[tuple[int, float]] = []
    draw_counts: list[int] = []
    for budget in LADDER:
        tally = doubling_test_detailed(game, budget, GAMES_PER_PAIR, rng)
        score = (tally["wins"] + 0.5 * tally["draws"]) / GAMES_PER_PAIR
        scores.append((budget, score))
        draw_counts.append(tally["draws"])
        label, saturated = verdict(tally, GAMES_PER_PAIR)
        print(
            f"    {budget:>4} vs {2 * budget:<5} {tally['wins']:>5}"
            f"   {tally['draws']:>5}   {tally['losses']:>6}"
            f"   {tally['x_wins']:>5}      {score:>4.0%}   {label}"
        )
        if saturated:
            captured = budget
            break

    premium = ", ".join(
        f"{budget}: {100 * (score - 0.5):+.0f}" for budget, score in scores
    )
    draws_trend = " → ".join(str(d) for d in draw_counts)
    print(f"\n   doubling premium (score - 50%, in %-points):  {premium}")
    print(f"   draws per {GAMES_PER_PAIR} games up the ladder:  {draws_trend}")

    # Sampling noise for a score over GAMES_PER_PAIR games is ~±9 %-points,
    # so a premium inside that band is indistinguishable from zero.
    last_budget, last_score = scores[-1]
    draws_rising = draw_counts[-1] / GAMES_PER_PAIR >= 0.40
    if captured is not None:
        print(f"\n   VERDICT: saturation captured at N ≈ {captured}")
    elif last_score < 0.60 and draws_rising:
        print(f"""
   VERDICT: captured in the act of closing. The doubling premium is now
   within sampling noise of zero, and the draw fraction climbs steadily
   toward dominance — the draw signature that m,n,k-theory predicts for
   (5,5,4) is emerging. The wall sits at roughly N ≈ {last_budget // 2}-{last_budget}.""")
    elif last_score < 0.60:
        print("""
   VERDICT: the doubling premium has collapsed without either
   perfect-play signature — a plateau belonging to the ALGORITHM, not
   the game: random playouts stop converting extra simulations into
   strength while the game is still unsolved. Pushing further needs a
   better evaluator (cf. AlphaGo's learned playouts), not more budget.""")
    else:
        print(f"""
   VERDICT: not captured — doubling still pays at {last_budget} vs
   {2 * last_budget}; the wall lies beyond this ladder.""")

    print("""
── Saturation points across the series (studies I-III) ──
   3x3, 3-in-a-row    N ≈ 50          (study II)
   4x4, 4-in-a-row    N ≈ 100-200     (study II)
   5x5, 4-in-a-row    see above       (this study)
   Deeper game → the wall moves out, roughly with game-tree size.""")
