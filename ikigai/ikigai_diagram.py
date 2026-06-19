"""
Ikigai — modeling a "reason for being"

Ikigai (生き甲斐) is the Japanese idea of a life worth living. It is often drawn as
four overlapping circles: what you LOVE, what you are GOOD AT, what the world
NEEDS, and what you can be PAID FOR. Their pairwise overlaps are passion,
profession, vocation and mission; only where all four meet lies ikigai itself.

This module scores activities on the four axes (0-10) and names the region each
falls in — including the classic "three-of-four" near-misses.
"""

from __future__ import annotations


def classify(love: float, skill: float, need: float, pay: float,
             threshold: float = 6.0) -> str:
    """Name the ikigai region for the four scores."""
    high = {"love": love >= threshold, "skill": skill >= threshold,
            "need": need >= threshold, "pay": pay >= threshold}
    n = sum(high.values())
    if n == 4:
        return "IKIGAI — a reason for being"
    if n == 3:
        missing = next(k for k, v in high.items() if not v)
        return {
            "pay": "Delight and fullness, but no wealth (missing: paid for)",
            "need": "Satisfaction, but a feeling of uselessness (missing: world needs)",
            "love": "Comfortable, but a feeling of emptiness (missing: love)",
            "skill": "Excitement, but a sense of uncertainty (missing: skill)",
        }[missing]
    if n == 2:
        pair = frozenset(k for k, v in high.items() if v)
        return {
            frozenset({"love", "skill"}): "Passion",
            frozenset({"skill", "pay"}): "Profession",
            frozenset({"pay", "need"}): "Vocation",
            frozenset({"need", "love"}): "Mission",
        }.get(pair, "Two elements aligned")
    return "Not yet aligned"


def balance_score(love: float, skill: float, need: float, pay: float) -> float:
    """Ikigai needs ALL four, so the weakest axis sets the score."""
    return min(love, skill, need, pay)


if __name__ == "__main__":
    # (name, love, skill, need, pay)
    activities = [
        ("Teaching coding", 9, 8, 8, 7),
        ("Hobby painting", 9, 7, 3, 2),
        ("Corporate job", 3, 8, 7, 9),
        ("Volunteering", 8, 4, 9, 1),
        ("Day trading", 4, 7, 2, 9),
    ]

    print("Ikigai — the four circles (love / skill / need / pay)\n")
    print(f"  {'activity':<16}{'L':>2}{'S':>3}{'N':>3}{'P':>3}  region")
    for name, love, skill, need, pay in activities:
        region = classify(love, skill, need, pay)
        print(f"  {name:<16}{love:>2}{skill:>3}{need:>3}{pay:>3}  {region}")

    best = max(activities, key=lambda a: balance_score(*a[1:]))
    print(f"\n  Closest to ikigai: '{best[0]}' "
          f"(weakest axis = {balance_score(*best[1:])}/10)")
    print("  True ikigai is balanced across all four — raise the lowest circle.")
