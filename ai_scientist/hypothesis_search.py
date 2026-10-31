"""
Automated Hypothesis Search (仮説の自動探索) — proposing and ranking
scientific models

The first job of an "AI Scientist" is to turn data into candidate
explanations and decide which one to believe.  Given noisy observations,
this module fits a library of competing functional forms (constant,
linear, polynomial, sqrt, log) by least squares and ranks them by the
Bayesian Information Criterion

    BIC = n * ln(RSS / n) + k * ln(n)

which rewards goodness of fit (small residuals) but *penalises* extra
parameters.  So a wiggly high-degree polynomial that memorises the noise
loses to the simpler form that actually generated the data.
"""

from __future__ import annotations
import math
import random
from typing import Callable

Matrix = list[list[float]]
Vector = list[float]


# ── Linear algebra ────────────────────────────────────────────────────────
def solve(A: Matrix, b: Vector) -> Vector:
    """Gaussian elimination with partial pivoting."""
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


def fit_linear(basis: Callable[[float], Vector], xs: Vector, ys: Vector) -> Vector:
    """Least-squares fit of y = coef . basis(x) via the normal equations."""
    Phi = [basis(x) for x in xs]
    m = len(Phi[0])
    A = [[sum(row[i] * row[j] for row in Phi) for j in range(m)] for i in range(m)]
    b = [sum(row[i] * y for row, y in zip(Phi, ys)) for i in range(m)]
    return solve(A, b)


def rss(basis: Callable[[float], Vector], coef: Vector, xs: Vector, ys: Vector) -> float:
    return sum((y - sum(c * p for c, p in zip(coef, basis(x)))) ** 2
               for x, y in zip(xs, ys))


# ── Hypothesis library ────────────────────────────────────────────────────
HYPOTHESES: dict[str, Callable[[float], Vector]] = {
    "constant":  lambda x: [1.0],
    "linear":    lambda x: [1.0, x],
    "quadratic": lambda x: [1.0, x, x * x],
    "cubic":     lambda x: [1.0, x, x * x, x ** 3],
    "sqrt":      lambda x: [1.0, math.sqrt(x)],
    "log":       lambda x: [1.0, math.log(x)],
}


def bic(n: int, residual_ss: float, k: int) -> float:
    return n * math.log(residual_ss / n) + k * math.log(n)


def rank_hypotheses(xs: Vector, ys: Vector) -> list[tuple[str, float, float, Vector]]:
    """Return (name, BIC, R^2, coef) for each hypothesis, best BIC first."""
    n = len(xs)
    mean_y = sum(ys) / n
    tss = sum((y - mean_y) ** 2 for y in ys)
    out = []
    for name, basis in HYPOTHESES.items():
        coef = fit_linear(basis, xs, ys)
        r = rss(basis, coef, xs, ys)
        out.append((name, bic(n, r, len(coef)), 1 - r / tss, coef))
    return sorted(out, key=lambda t: t[1])


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    rng = random.Random(11)

    # Hidden law the "AI Scientist" has never been told: y = 1.5*sqrt(x) + 0.5
    def truth(x: float) -> float:
        return 1.5 * math.sqrt(x) + 0.5

    xs = [rng.uniform(0.5, 10.0) for _ in range(40)]
    ys = [truth(x) + rng.gauss(0, 0.25) for x in xs]
    print("Observations: 40 noisy points from an undisclosed law.\n")

    ranked = rank_hypotheses(xs, ys)
    print(f"{'hypothesis':10s} {'params':>6s} {'R^2':>8s} {'BIC':>9s}")
    for name, b, r2, coef in ranked:
        print(f"{name:10s} {len(coef):6d} {r2:8.4f} {b:9.2f}")

    best = ranked[0]
    print(f"\nSelected hypothesis: '{best[0]}'  "
          f"(y = {best[3][0]:.2f} + {best[3][1]:.2f}*{best[0]}(x))")
    print("Truth was           : y = 0.50 + 1.50*sqrt(x)")
    print("\nNote: 'cubic' reaches a similar or better R^2 by bending to the noise,")
    print("      but BIC's parameter penalty keeps the simpler true form on top —")
    print("      automated Occam's razor.")
