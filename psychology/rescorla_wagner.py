"""
Rescorla-Wagner Model — learning as prediction error

The most influential model of associative learning. A cue's associative
strength grows in proportion to *surprise* — the gap between what actually
happened (lambda) and what was predicted (the sum of strengths of all present
cues):

    dV = alpha * (lambda - sum of present cue strengths)

This single equation explains classical conditioning AND the famous *blocking*
effect, and it is the direct ancestor of temporal-difference reinforcement
learning and the dopamine reward-prediction-error hypothesis.
"""

from __future__ import annotations


def train(trials: list[tuple[list[str], bool]], alpha: float = 0.3
          ) -> tuple[dict[str, float], list[dict[str, float]]]:
    """Run trials of (cues_present, us_present). Returns (final V, history)."""
    strengths: dict[str, float] = {}
    history = []
    for cues, us in trials:
        for c in cues:
            strengths.setdefault(c, 0.0)
        lam = 1.0 if us else 0.0
        prediction = sum(strengths[c] for c in cues)
        error = lam - prediction
        for c in cues:
            strengths[c] += alpha * error
        history.append(dict(strengths))
    return strengths, history


if __name__ == "__main__":
    # ── Acquisition: a single cue A predicting the US ──
    acq, history = train([(["A"], True)] * 15)
    print("Acquisition of cue A (associative strength per trial):")
    for t in (1, 3, 5, 10, 15):
        print(f"  trial {t:>2}: V_A = {history[t - 1]['A']:.3f}")
    print(f"  -> approaches asymptote lambda = 1.0\n")

    # ── Blocking (Kamin): pre-train A, then reinforce compound AB ──
    blocked, _ = train([(["A"], True)] * 20 + [(["A", "B"], True)] * 20)
    print("Blocking effect:")
    print(f"  Phase 1: A -> US (20 trials)  =>  V_A = {blocked['A']:.3f}")
    print(f"  Phase 2: AB -> US (20 trials) =>  V_B = {blocked['B']:.3f}")

    # Control: the same AB training WITHOUT pre-training A.
    control, _ = train([(["A", "B"], True)] * 20)
    print(f"  Control (no pre-training)     =>  V_B = {control['B']:.3f}")
    print("\n  A already predicts the US, so there is no surprise left for B")
    print("  to explain -> B is 'blocked' from being learned.")
