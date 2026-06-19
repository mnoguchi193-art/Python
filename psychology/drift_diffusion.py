"""
Drift Diffusion Model — decisions as noisy evidence accumulation

The dominant model of fast two-choice decisions in cognitive psychology and
neuroscience. Evidence accumulates from a starting point until it hits one of
two boundaries; which boundary, and how long it takes, jointly explain both the
*choice* and the *reaction time* — and naturally produce the speed-accuracy
trade-off.

  drift rate v : quality of evidence (higher = easier task)
  boundary a   : caution (higher = more accurate but slower)
"""

from __future__ import annotations

import random
from math import sqrt
from statistics import mean


def simulate_trial(drift: float, boundary: float, noise: float = 1.0,
                   dt: float = 0.001, t0: float = 0.2, max_t: float = 5.0
                   ) -> tuple[bool, float]:
    """One decision. Returns (chose_correct, reaction_time_seconds)."""
    x, t = 0.0, 0.0
    while abs(x) < boundary and t < max_t:
        x += drift * dt + noise * sqrt(dt) * random.gauss(0, 1)
        t += dt
    return x >= boundary, t + t0   # +t0 for non-decision (perception/motor) time


def run(drift: float, boundary: float, trials: int = 2000, seed: int = 0
        ) -> dict[str, float]:
    random.seed(seed)
    results = [simulate_trial(drift, boundary) for _ in range(trials)]
    correct_rts = [rt for ok, rt in results if ok]
    error_rts = [rt for ok, rt in results if not ok]
    return {
        "accuracy": len(correct_rts) / trials,
        "mean_rt": mean(rt for _, rt in results),
        "correct_rt": mean(correct_rts) if correct_rts else float("nan"),
        "error_rt": mean(error_rts) if error_rts else float("nan"),
    }


if __name__ == "__main__":
    drift = 1.0
    print(f"Drift Diffusion Model (drift rate v = {drift})\n")
    print("The speed-accuracy trade-off as caution (boundary) increases:\n")
    print(f"  {'boundary':>8}  {'accuracy':>8}  {'mean RT':>8}")
    for boundary in (0.5, 0.8, 1.2, 1.6):
        r = run(drift, boundary)
        print(f"  {boundary:>8.1f}  {r['accuracy']:>7.1%}  {r['mean_rt']:>7.2f}s")

    print("\nWider boundaries collect more evidence: accuracy rises but every")
    print("decision takes longer — the hallmark trade-off the model captures.")
