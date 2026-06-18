"""
Stable Matching — the Gale-Shapley deferred-acceptance algorithm

Market design without money: matching doctors to hospitals, students to schools,
organ donors to patients. The Gale-Shapley algorithm (Roth & Shapley, Nobel
2012) always produces a *stable* matching — no pair would both rather abandon
their assigned partners for each other.

Preferences are ordered lists: proposers[p] = [most preferred, ..., least].
"""

from __future__ import annotations


Prefs = dict[str, list[str]]


def gale_shapley(proposers: Prefs, receivers: Prefs) -> dict[str, str]:
    """Deferred acceptance. Returns {proposer: receiver}.

    Proposers propose in preference order; each receiver tentatively holds its
    best offer so far and rejects the rest. The result is proposer-optimal.
    """
    free = list(proposers)
    next_choice = {p: 0 for p in proposers}      # index into p's pref list
    engaged: dict[str, str] = {}                 # receiver -> current proposer
    rank = {r: {p: i for i, p in enumerate(prefs)}
            for r, prefs in receivers.items()}   # receiver's ranking lookup

    while free:
        p = free.pop(0)
        r = proposers[p][next_choice[p]]
        next_choice[p] += 1
        if r not in engaged:
            engaged[r] = p
        elif rank[r][p] < rank[r][engaged[r]]:
            free.append(engaged[r])              # current partner is dumped
            engaged[r] = p
        else:
            free.append(p)                       # rejected, try again later
    return {p: r for r, p in engaged.items()}


def is_stable(matching: dict[str, str], proposers: Prefs, receivers: Prefs) -> bool:
    """True if no blocking pair (a, b) prefers each other to their match."""
    partner_of = {r: p for p, r in matching.items()}
    for p, r in matching.items():
        # Receivers p prefers over their current match r.
        for better_r in proposers[p][: proposers[p].index(r)]:
            holder = partner_of[better_r]
            if receivers[better_r].index(p) < receivers[better_r].index(holder):
                return False  # p and better_r form a blocking pair
    return True


if __name__ == "__main__":
    proposers = {
        "Alice": ["X", "Y", "Z"],
        "Beth":  ["Y", "X", "Z"],
        "Cara":  ["X", "Y", "Z"],
    }
    receivers = {
        "X": ["Beth", "Alice", "Cara"],
        "Y": ["Alice", "Beth", "Cara"],
        "Z": ["Alice", "Beth", "Cara"],
    }

    matching = gale_shapley(proposers, receivers)
    print("Stable matching (proposer-optimal):")
    for p, r in sorted(matching.items()):
        print(f"  {p} <-> {r}")
    print(f"\nStable? {is_stable(matching, proposers, receivers)}")
