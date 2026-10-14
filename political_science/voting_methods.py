"""
Voting Methods — computational social choice theory

Different electoral rules can pick different winners from the *same* ballots.
This module implements the classic methods studied in political science and
demonstrates Condorcet's paradox (a rule-dependent outcome).

Ballots are ranked preferences, e.g. ["A", "B", "C"] means A > B > C.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations


Ballot = list[str]


def candidates(ballots: list[Ballot]) -> list[str]:
    seen: dict[str, None] = {}
    for ballot in ballots:
        for c in ballot:
            seen.setdefault(c, None)
    return list(seen)


# ── Plurality (first-past-the-post) ───────────────────────────────────────
def plurality(ballots: list[Ballot]) -> str:
    """Winner is whoever gets the most first-choice votes."""
    tally = Counter(ballot[0] for ballot in ballots if ballot)
    return tally.most_common(1)[0][0]


# ── Borda count ───────────────────────────────────────────────────────────
def borda_count(ballots: list[Ballot]) -> str:
    """Rank r (0-indexed) of n candidates earns (n - 1 - r) points."""
    scores: Counter[str] = Counter()
    for ballot in ballots:
        n = len(ballot)
        for rank, c in enumerate(ballot):
            scores[c] += n - 1 - rank
    return scores.most_common(1)[0][0]


# ── Condorcet winner ──────────────────────────────────────────────────────
def _prefers(ballot: Ballot, a: str, b: str) -> bool:
    return ballot.index(a) < ballot.index(b)


def pairwise_winner(ballots: list[Ballot], a: str, b: str) -> str | None:
    """Head-to-head winner of a vs b (None on a tie)."""
    a_votes = sum(1 for ballot in ballots if _prefers(ballot, a, b))
    b_votes = len(ballots) - a_votes
    if a_votes == b_votes:
        return None
    return a if a_votes > b_votes else b


def condorcet_winner(ballots: list[Ballot]) -> str | None:
    """Candidate who beats every other in pairwise contests, if one exists."""
    cands = candidates(ballots)
    for c in cands:
        if all(
            pairwise_winner(ballots, c, other) == c
            for other in cands
            if other != c
        ):
            return c
    return None  # Condorcet's paradox: no such candidate


# ── Instant-runoff voting (ranked-choice) ─────────────────────────────────
def instant_runoff(ballots: list[Ballot]) -> str:
    """Eliminate the lowest first-choice candidate until someone has a majority."""
    remaining = set(candidates(ballots))
    while True:
        tally = Counter()
        for ballot in ballots:
            for c in ballot:
                if c in remaining:
                    tally[c] += 1
                    break
        total = sum(tally.values())
        leader, votes = tally.most_common(1)[0]
        if votes * 2 > total or len(remaining) == 1:
            return leader
        fewest = min(tally.values())
        losers = {c for c, v in tally.items() if v == fewest}
        # Drop the worst, but never everyone at once.
        remaining -= losers if len(losers) < len(remaining) else {leader}


if __name__ == "__main__":
    # A classic profile where the rule decides the winner.
    ballots = (
        [["A", "B", "C"]] * 10
        + [["B", "C", "A"]] * 8
        + [["C", "B", "A"]] * 7
    )
    print(f"Candidates: {candidates(ballots)}  (n={len(ballots)} voters)\n")
    print(f"Plurality       : {plurality(ballots)}")
    print(f"Borda count     : {borda_count(ballots)}")
    print(f"Instant-runoff  : {instant_runoff(ballots)}")
    print(f"Condorcet winner: {condorcet_winner(ballots)}")

    print("\nPairwise contests:")
    for a, b in combinations(candidates(ballots), 2):
        print(f"  {a} vs {b}: {pairwise_winner(ballots, a, b)} wins")

    # Condorcet's paradox: a cyclic majority with no Condorcet winner.
    cyclic = [["A", "B", "C"], ["B", "C", "A"], ["C", "A", "B"]]
    print(f"\nCyclic profile Condorcet winner: {condorcet_winner(cyclic)}")
