"""
PERMA — a measurable model of well-being (Seligman)

Positive psychology's framework for flourishing breaks well-being into five
measurable pillars:

  P  Positive emotion   (joy, gratitude, contentment)
  E  Engagement         (flow, absorption in what you do)
  R  Relationships      (connection and support)
  M  Meaning            (serving something larger than yourself)
  A  Accomplishment     (progress toward goals)

Scoring each pillar reveals not just an overall level but the *weakest* one — the
highest-leverage place to invest, much as ikigai asks you to raise your lowest
circle.
"""

from __future__ import annotations

from statistics import mean


PILLARS = {
    "Positive emotion": "savor small joys, practice gratitude",
    "Engagement": "seek flow — matched challenge and skill",
    "Relationships": "invest time in the people who matter",
    "Meaning": "connect daily work to a larger purpose",
    "Accomplishment": "set and finish small, concrete goals",
}


def overall(scores: dict[str, float]) -> float:
    return mean(scores.values())


def weakest_pillar(scores: dict[str, float]) -> str:
    return min(scores, key=scores.get)


if __name__ == "__main__":
    profile = {
        "Positive emotion": 7,
        "Engagement": 8,
        "Relationships": 5,
        "Meaning": 9,
        "Accomplishment": 6,
    }

    print("PERMA well-being profile (0-10 per pillar)\n")
    for pillar, score in profile.items():
        bar = "#" * int(score)
        print(f"  {pillar:<18} {score:>2}  {bar}")

    print(f"\n  Overall well-being: {overall(profile):.1f}/10")
    weak = weakest_pillar(profile)
    print(f"  Highest-leverage pillar to raise: {weak} ({profile[weak]}/10)")
    print(f"    -> {PILLARS[weak]}")
    print("\n  Flourishing is balanced, like ikigai: lift the lowest pillar first.")
