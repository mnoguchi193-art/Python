"""
Gerrymandering and the Efficiency Gap

Districting can hand one party a majority of seats from a minority of votes by
"packing" the opponent into a few districts and "cracking" them thinly across the
rest. The efficiency gap quantifies the unfairness by counting *wasted* votes —
votes for a loser, plus a winner's votes beyond the bare majority. A large gap is
the statistical fingerprint of a gerrymander.
"""

from __future__ import annotations


def district(a_votes: int, b_votes: int) -> tuple[str, int, int]:
    """Returns (winner, wasted A votes, wasted B votes) for one district."""
    needed = (a_votes + b_votes) // 2 + 1
    if a_votes >= b_votes:
        return "A", a_votes - needed, b_votes
    return "B", a_votes, b_votes - needed


def efficiency_gap(districts: list[tuple[int, int]]) -> tuple[float, dict[str, int]]:
    """Efficiency gap (positive favors A) and the seat count."""
    wasted_a = wasted_b = total = 0
    seats = {"A": 0, "B": 0}
    for a, b in districts:
        winner, wa, wb = district(a, b)
        seats[winner] += 1
        wasted_a += wa
        wasted_b += wb
        total += a + b
    return (wasted_b - wasted_a) / total, seats


if __name__ == "__main__":
    # Same 500 voters (240 A, 260 B) districted two ways.
    fair = [(48, 52), (48, 52), (48, 52), (48, 52), (48, 52)]
    rigged = [(20, 80), (20, 80), (66, 34), (66, 34), (68, 32)]  # pack & crack

    print("Gerrymandering — same votes (A=240, B=260), two district maps\n")
    for name, dmap in (("Fair-ish (uniform)", fair), ("Gerrymandered for A", rigged)):
        gap, seats = efficiency_gap(dmap)
        print(f"  {name}:")
        print(f"    seats: A={seats['A']}, B={seats['B']}")
        print(f"    efficiency gap: {gap:+.1%} "
              f"({'favors A' if gap > 0 else 'favors B'})\n")

    print("  B wins the popular vote both times, yet the rigged map gives A the")
    print("  seat majority — and the efficiency gap flags it (>~7% is suspect).")
