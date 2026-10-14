"""
The Median Voter Theorem — why candidates crowd the center

Anthony Downs's spatial model of politics: place voters on a one-dimensional
policy spectrum, and let each vote for the nearest candidate (splitting ties).
Black's median voter theorem then says the *median voter's* position is the unique
equilibrium: a candidate there beats any challenger, and the best you can do
against an opponent at the median is to tie them by standing there too.
"""

from __future__ import annotations


def tally(positions: list[float], voters: list[float]) -> list[float]:
    """Each voter backs the nearest candidate; equidistant voters split."""
    counts = [0.0] * len(positions)
    for v in voters:
        distances = [abs(v - p) for p in positions]
        nearest = min(distances)
        winners = [i for i, d in enumerate(distances) if abs(d - nearest) < 1e-12]
        for i in winners:
            counts[i] += 1 / len(winners)
    return counts


def best_response(opponent: float, voters: list[float], grid: int = 201) -> float:
    """The position maximizing my vote share against a fixed opponent."""
    best_pos, best_votes = 0.0, -1.0
    for i in range(grid):
        p = i / (grid - 1)
        mine = tally([p, opponent], voters)[0]
        if mine > best_votes + 1e-9:
            best_votes, best_pos = mine, p
    return best_pos


if __name__ == "__main__":
    voters = [0.05, 0.1, 0.2, 0.3, 0.35, 0.5, 0.55, 0.6, 0.7, 0.8, 0.95]
    median = sorted(voters)[len(voters) // 2]
    n = len(voters)

    print("Median voter theorem\n")
    print(f"  {n} voters on [0, 1]; median voter at {median}\n")

    print("  A candidate AT the median beats a challenger anywhere:")
    print(f"    {'challenger B':>12}  {'A(median)':>10}  {'B':>5}  winner")
    for b in (0.2, 0.35, 0.65, 0.8):
        a_votes, b_votes = tally([median, b], voters)
        winner = "A" if a_votes > b_votes else "B" if b_votes > a_votes else "tie"
        print(f"    {b:>12.2f}  {a_votes:>10.1f}  {b_votes:>5.1f}  {winner}")

    br = best_response(median, voters)
    print(f"\n  Best response to an opponent at the median: {br:.2f} (= the median)")
    print("  You cannot beat the median — so both candidates converge there.")
