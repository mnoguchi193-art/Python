"""
Autonomous Research Loop (自律研究ループ) — the AI Scientist end to end

This module wires the pieces of an AI Scientist into one closed loop that
discovers a hidden law on its own:

    propose hypotheses  ->  design the most informative experiment
         ^                              |
         |                              v
    write a report  <-  decide   <-  run it & refit

Each round the agent fits a library of candidate forms to the data it has,
selects the best by BIC, then queries the hidden "laboratory" at the dose
where its top candidates disagree most.  When one hypothesis is clearly
best and fits well, it stops and reports the discovered law.  Self-
contained (no imports from the sibling modules), standard library only.
"""

from __future__ import annotations
import math
import random
from typing import Callable

Vector = list[float]
Matrix = list[list[float]]


# ── Minimal regression + model selection ──────────────────────────────────
def solve(A: Matrix, b: Vector) -> Vector:
    n = len(A)
    M = [row[:] + [bi] for row, bi in zip(A, b)]
    for col in range(n):
        p = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[p] = M[p], M[col]
        if abs(M[col][col]) < 1e-12:
            M[col][col] = 1e-12
        for r in range(n):
            if r != col:
                f = M[r][col] / M[col][col]
                M[r] = [a - f * c for a, c in zip(M[r], M[col])]
    return [M[i][n] / M[i][i] for i in range(n)]


BASES: dict[str, Callable[[float], Vector]] = {
    "linear":    lambda x: [1.0, x],
    "quadratic": lambda x: [1.0, x, x * x],
    "sqrt":      lambda x: [1.0, math.sqrt(x)],
    "log":       lambda x: [1.0, math.log(x)],
}


def fit(name: str, xs: Vector, ys: Vector) -> tuple[Vector, float]:
    """Return (coefficients, BIC) for one hypothesis."""
    basis = BASES[name]
    Phi = [basis(x) for x in xs]
    m = len(Phi[0])
    A = [[sum(r[i] * r[j] for r in Phi) for j in range(m)] for i in range(m)]
    b = [sum(r[i] * y for r, y in zip(Phi, ys)) for i in range(m)]
    coef = solve(A, b)
    rss = sum((y - sum(c * p for c, p in zip(coef, basis(x)))) ** 2
              for x, y in zip(xs, ys))
    n = len(xs)
    return coef, n * math.log(rss / n + 1e-12) + m * math.log(n)


def predict(name: str, coef: Vector, x: float) -> float:
    return sum(c * p for c, p in zip(coef, BASES[name](x)))


# ── The hidden laboratory ─────────────────────────────────────────────────
X_GRID = [0.5 + i * 9.5 / 40 for i in range(41)]


def laboratory(x: float, rng: random.Random) -> float:
    """Undisclosed ground truth queried with measurement noise."""
    return 1.5 * math.sqrt(x) + 0.5 + rng.gauss(0, 0.2)


# ── Autonomous loop ───────────────────────────────────────────────────────
def research(rng: random.Random, max_experiments: int = 25) -> None:
    # Seed with three initial measurements so every form is fittable.
    xs = [1.0, 4.0, 7.0, 10.0]
    ys = [laboratory(x, rng) for x in xs]

    for step in range(len(xs), max_experiments):
        models = {name: fit(name, xs, ys) for name in BASES}
        ranked = sorted(models.items(), key=lambda kv: kv[1][1])   # by BIC
        (best_name, (best_coef, best_bic)) = ranked[0]
        (runner_name, (runner_coef, runner_bic)) = ranked[1]

        # Design: query where the two leading hypotheses disagree most.
        next_x = max(X_GRID, key=lambda x:
                     abs(predict(best_name, best_coef, x)
                         - predict(runner_name, runner_coef, x)))
        gap = runner_bic - best_bic
        print(f"  n={len(xs):2d}: best='{best_name}' (BIC {best_bic:6.1f}, "
              f"lead {gap:4.1f} over '{runner_name}')  next dose x={next_x:.2f}")

        # Stop when the best hypothesis is decisively ahead.
        if gap > 6.0 and len(xs) >= 8:
            print(f"\nDecision: '{best_name}' is decisively best "
                  f"(BIC lead {gap:.1f} > 6).")
            a, b = best_coef
            print("Report — discovered law:")
            print(f"  y = {a:.2f} + {b:.2f} * {best_name}(x)")
            print(f"  (hidden truth was  y = 0.50 + 1.50 * sqrt(x))")
            print(f"  experiments used: {len(xs)}")
            return

        xs.append(next_x)
        ys.append(laboratory(next_x, rng))

    print("\nStopped at the experiment budget without a decisive winner.")


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Autonomous research loop on a hidden law.")
    print("Candidate forms: linear, quadratic, sqrt, log.\n")
    research(random.Random(0))
