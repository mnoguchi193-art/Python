"""
Voting Power Indices — measuring influence in weighted voting games

In bodies like the EU Council or the IMF, members cast different numbers of
votes. Raw vote share is *not* the same as power: a member's real influence is
how often they are *pivotal* in forming a winning coalition.

This module computes the two standard indices used in political methodology:
  - Banzhaf index        — share of "swing" votes across all coalitions
  - Shapley-Shubik index — share of "pivotal" positions across all orderings

A coalition wins when its total weight meets the `quota`.
"""

from __future__ import annotations

from itertools import combinations
from math import factorial


def banzhaf_index(weights: dict[str, int], quota: int) -> dict[str, float]:
    """Normalized Banzhaf power index for each player."""
    players = list(weights)
    swings: dict[str, int] = {p: 0 for p in players}

    for player in players:
        others = [p for p in players if p != player]
        for size in range(len(others) + 1):
            for coalition in combinations(others, size):
                base = sum(weights[p] for p in coalition)
                # `player` swings if they turn a losing coalition into a winner.
                if base < quota <= base + weights[player]:
                    swings[player] += 1

    total = sum(swings.values())
    return {p: swings[p] / total for p in players}


def shapley_shubik_index(weights: dict[str, int], quota: int) -> dict[str, float]:
    """Shapley-Shubik power index via combinatorial (not brute-force) weighting.

    A player is pivotal in an ordering when the coalition becomes winning
    exactly when they join. Summing over orderings is equivalent to weighting
    each coalition S (not containing the player) by |S|! * (n-|S|-1)!.
    """
    players = list(weights)
    n = len(players)
    pivotal: dict[str, float] = {p: 0.0 for p in players}

    for player in players:
        others = [p for p in players if p != player]
        for size in range(len(others) + 1):
            weight = factorial(size) * factorial(n - size - 1)
            for coalition in combinations(others, size):
                base = sum(weights[p] for p in coalition)
                if base < quota <= base + weights[player]:
                    pivotal[player] += weight

    return {p: pivotal[p] / factorial(n) for p in players}


if __name__ == "__main__":
    # Stylized weighted council: A holds half the votes, B/C/D split the rest.
    weights = {"A": 4, "B": 3, "C": 2, "D": 1}
    quota = 6  # simple majority of 10 total votes

    print(f"Weights: {weights}   quota: {quota}\n")

    print("Player  Vote%   Banzhaf  Shapley-Shubik")
    total_w = sum(weights.values())
    banzhaf = banzhaf_index(weights, quota)
    shapley = shapley_shubik_index(weights, quota)
    for p in weights:
        print(
            f"  {p}    {weights[p] / total_w:6.1%}  "
            f"{banzhaf[p]:7.1%}      {shapley[p]:7.1%}"
        )

    # A dummy player: D never swings any coalition -> 0 power despite holding votes.
    print("\nNote: D holds 10% of votes but can be powerless (a 'dummy').")
