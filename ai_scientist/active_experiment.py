"""
Active Experiment Design (能動的な実験計画) — choosing experiments that
discriminate between theories

An AI Scientist with several competing theories should not collect data at
random: it should run the experiment whose outcome the theories *disagree*
about most, because that result is the most decisive.  This is optimal
experimental design for model discrimination.

Here four theories of a dose-response curve are nearly identical at low
dose and diverge only in a narrow window around x=4 (an activation bump, an
inhibition dip, a biphasic response, or no effect at all).  The agent keeps
a posterior over which theory is true and each round picks the dose where
the posterior-weighted spread of predictions is largest, observes a noisy
response from the hidden true theory, and updates by Bayes' rule.  Because
random sampling wastes most of its budget where the theories agree, active
design identifies the truth far sooner.
"""

from __future__ import annotations
import math
import random
from typing import Callable

SIGMA = 0.10                      # measurement noise (std)
X_GRID = [i * 5.0 / 50 for i in range(1, 51)]   # candidate doses in (0, 5]


def _bump(centre: float, height: float) -> Callable[[float], float]:
    return lambda x: height * math.exp(-((x - centre) ** 2) / 0.3)


_base = lambda x: x / (1 + x)     # shared background all theories agree on
HYPOTHESES: dict[str, Callable[[float], float]] = {
    "no-effect":  _base,
    "activation": lambda x: _base(x) + _bump(4.0, +0.35)(x),
    "inhibition": lambda x: _base(x) + _bump(4.0, -0.35)(x),
    "biphasic":   lambda x: _base(x) + _bump(2.0, +0.35)(x) + _bump(4.0, -0.35)(x),
}
TRUTH = "activation"


# ── Bayesian belief over hypotheses ───────────────────────────────────────
def update(posterior: dict[str, float], x: float, y: float) -> dict[str, float]:
    """Multiply in a Gaussian likelihood and renormalise."""
    new = {}
    for name, f in HYPOTHESES.items():
        resid = y - f(x)
        new[name] = posterior[name] * math.exp(-resid * resid / (2 * SIGMA ** 2))
    total = sum(new.values()) or 1.0
    return {k: v / total for k, v in new.items()}


def disagreement(posterior: dict[str, float], x: float) -> float:
    """Posterior-weighted variance of the hypotheses' predictions at x."""
    preds = {name: f(x) for name, f in HYPOTHESES.items()}
    mean = sum(posterior[name] * p for name, p in preds.items())
    return sum(posterior[name] * (p - mean) ** 2 for name, p in preds.items())


def observe(x: float, rng: random.Random) -> float:
    return HYPOTHESES[TRUTH](x) + rng.gauss(0, SIGMA)


# ── Two strategies ────────────────────────────────────────────────────────
def run(active: bool, budget: int, rng: random.Random) -> list[float]:
    """Return the posterior probability of the TRUE hypothesis after each run."""
    posterior = {name: 1 / len(HYPOTHESES) for name in HYPOTHESES}
    history = []
    for _ in range(budget):
        x = (max(X_GRID, key=lambda x: disagreement(posterior, x))
             if active else rng.choice(X_GRID))
        posterior = update(posterior, x, observe(x, rng))
        history.append(posterior[TRUTH])
    return history


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Four theories that agree at low dose and split near x=4; the true")
    print(f"one is '{TRUTH}'. The agent must identify it from noisy data.\n")

    budget = 12
    print("One active-design run (dose chosen to maximise disagreement):")
    posterior = {name: 1 / len(HYPOTHESES) for name in HYPOTHESES}
    rng = random.Random(5)
    for i in range(budget):
        x = max(X_GRID, key=lambda x: disagreement(posterior, x))
        y = observe(x, rng)
        posterior = update(posterior, x, y)
        top = max(posterior, key=posterior.get)
        print(f"  exp {i + 1:2d}: dose x={x:4.2f}  response={y:5.2f}  "
              f"-> P({TRUTH})={posterior[TRUTH]:.3f}  (leading: {top})")

    trials = 120
    active_curve = [0.0] * budget
    random_curve = [0.0] * budget
    for s in range(trials):
        a = run(True, budget, random.Random(s))
        r = run(False, budget, random.Random(7000 + s))
        active_curve = [c + v for c, v in zip(active_curve, a)]
        random_curve = [c + v for c, v in zip(random_curve, r)]
    active_curve = [v / trials for v in active_curve]
    random_curve = [v / trials for v in random_curve]

    print(f"\nMean P(true theory) over {trials} repeats:")
    print("  experiments:   1     3     6     9    12")
    pick = lambda c: "  ".join(f"{c[i]:.3f}" for i in [0, 2, 5, 8, 11])
    print(f"  active     : {pick(active_curve)}")
    print(f"  random     : {pick(random_curve)}")
    print("\n  Active design is almost certain after ~3 experiments; random")
    print("  sampling wastes most of its budget on doses where the theories")
    print("  agree. The win comes from asking the most decisive question.")
