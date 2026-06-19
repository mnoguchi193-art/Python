"""
Bayesian Cue Integration — the optimally inferring brain

When the brain estimates a property (say, where an object is) from several noisy
senses, it combines them like an ideal statistician: each cue is weighted by its
*reliability* (inverse variance). The fused estimate is more reliable than any
single sense, and the more reliable modality dominates — which explains the
ventriloquist effect, where precise vision "captures" imprecise sound.

Human behavior matches this near-optimal rule (Ernst & Banks, 2002).
"""

from __future__ import annotations

import random
from statistics import mean, pstdev


def integrate(mu_v: float, var_v: float, mu_a: float, var_a: float
              ) -> tuple[float, float, float, float]:
    """Optimal fusion of two Gaussian cues.

    Returns (combined mean, combined variance, visual weight, auditory weight).
    """
    w_v = (1 / var_v) / (1 / var_v + 1 / var_a)
    w_a = 1 - w_v
    combined_mean = w_v * mu_v + w_a * mu_a
    combined_var = 1 / (1 / var_v + 1 / var_a)
    return combined_mean, combined_var, w_v, w_a


if __name__ == "__main__":
    # True object at 0 deg. Vision is precise; hearing is vague and biased to +10.
    true_pos = 0.0
    mu_v, var_v = 0.0, 1.0     # visual cue:   reliable
    mu_a, var_a = 10.0, 9.0    # auditory cue: noisy, displaced

    mean_c, var_c, w_v, w_a = integrate(mu_v, var_v, mu_a, var_a)

    print("Bayesian multisensory integration (object truly at 0 deg)\n")
    print(f"  vision   : mean {mu_v:.1f}, std {var_v ** 0.5:.2f}, weight {w_v:.0%}")
    print(f"  audition : mean {mu_a:.1f}, std {var_a ** 0.5:.2f}, weight {w_a:.0%}")
    print(f"  combined : mean {mean_c:.2f}, std {var_c ** 0.5:.2f}")
    print(f"\n  Combined std ({var_c ** 0.5:.2f}) is lower than either cue alone")
    print("  => fusion improves reliability; vision dominates (ventriloquism).\n")

    # Monte-Carlo check that the optimal rule's variance matches simulation.
    random.seed(0)
    estimates = []
    for _ in range(20000):
        v = random.gauss(true_pos, var_v ** 0.5)
        a = random.gauss(10.0, var_a ** 0.5)
        estimates.append(w_v * v + w_a * a)
    print(f"  predicted combined std: {var_c ** 0.5:.3f}")
    print(f"  simulated  combined std: {pstdev(estimates):.3f}  "
          f"(mean {mean(estimates):.2f})")
