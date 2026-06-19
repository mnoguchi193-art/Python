"""
Flow — the psychology of optimal experience (Csikszentmihalyi)

A close companion of ikigai: "flow" is the state of complete, energized absorption
in an activity. Mihaly Csikszentmihalyi mapped it to the balance between the
CHALLENGE of a task and your SKILL at it. Too much challenge for your skill brings
anxiety; too little brings boredom; when both are high and matched, you enter
flow — the channel where engagement and growth happen.
"""

from __future__ import annotations


def mental_state(challenge: float, skill: float, low: float = 4.0,
                 balance_tol: float = 2.0) -> str:
    """Classify the experiential state from challenge and skill (0-10)."""
    hi_c, hi_s = challenge >= low, skill >= low
    if hi_c and hi_s and abs(challenge - skill) <= balance_tol:
        return "FLOW — absorbed and growing"
    if challenge - skill > balance_tol:
        return "Anxiety — challenge exceeds skill"
    if skill - challenge > balance_tol:
        return "Boredom — skill exceeds challenge"
    if not hi_c and not hi_s:
        return "Apathy — low challenge and low skill"
    return "Control / Arousal — near the flow channel"


if __name__ == "__main__":
    print("Flow channel: challenge vs skill\n")
    print(f"  {'challenge':>9}  {'skill':>6}  state")
    cases = [(9, 9), (8, 7), (9, 3), (3, 9), (2, 2), (6, 5), (5, 8)]
    for challenge, skill in cases:
        print(f"  {challenge:>9}  {skill:>6}  {mental_state(challenge, skill)}")

    print("\n  Flow lives on the diagonal where high challenge meets high skill.")
    print("  As skill grows, seek harder challenges to stay in the channel —")
    print("  the engine of mastery, and a path toward ikigai.")
