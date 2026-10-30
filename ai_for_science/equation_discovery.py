"""
Equation Discovery (方程式の発見) — sparse regression over a library of
candidate terms (SINDy-style)

Given only time-series data, recover the governing differential equation:
  1. build a library Theta(X) of candidate functions of the state,
  2. estimate dX/dt numerically,
  3. solve a *sparse* least-squares problem  dX/dt = Theta(X) * Xi.
Sequential thresholded least squares (STLSQ) zeroes small coefficients and
refits until only the few terms that truly matter survive — the result is
a human-readable equation rather than a black box.

Demo: rediscover logistic growth and the Lotka-Volterra predator-prey
system from simulated (slightly noisy) trajectories.
"""

from __future__ import annotations
import random
from itertools import combinations_with_replacement
from typing import Callable

Matrix = list[list[float]]
Vector = list[float]


# ── Linear algebra (small dense systems) ──────────────────────────────────
def solve(A: Matrix, b: Vector) -> Vector:
    """Gaussian elimination with partial pivoting."""
    n = len(A)
    M = [row[:] + [bi] for row, bi in zip(A, b)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[pivot] = M[pivot], M[col]
        if abs(M[col][col]) < 1e-12:
            raise ValueError("singular matrix")
        for r in range(n):
            if r != col:
                f = M[r][col] / M[col][col]
                M[r] = [a - f * c for a, c in zip(M[r], M[col])]
    return [M[i][n] / M[i][i] for i in range(n)]


def least_squares(Theta: Matrix, y: Vector, cols: list[int]) -> Vector:
    """Solve the normal equations restricted to the selected columns."""
    A = [[sum(row[i] * row[j] for row in Theta) for j in cols] for i in cols]
    b = [sum(row[i] * yi for row, yi in zip(Theta, y)) for i in cols]
    return solve(A, b)


# ── Library of candidate terms ────────────────────────────────────────────
def build_library(X: Matrix, names: list[str], degree: int = 2
                  ) -> tuple[Matrix, list[str]]:
    """Polynomial terms up to `degree` in the state variables, incl. '1'."""
    idx = range(len(names))
    combos = [()] + [c for d in range(1, degree + 1)
                     for c in combinations_with_replacement(idx, d)]
    labels = ["1"] + ["*".join(names[i] for i in c) for c in combos[1:]]
    Theta = []
    for state in X:
        row = []
        for c in combos:
            term = 1.0
            for i in c:
                term *= state[i]
            row.append(term)
        Theta.append(row)
    return Theta, labels


def finite_difference(series: Vector, dt: float) -> Vector:
    """Central differences in the interior, one-sided at the ends."""
    n = len(series)
    d = [0.0] * n
    for i in range(1, n - 1):
        d[i] = (series[i + 1] - series[i - 1]) / (2 * dt)
    d[0] = (series[1] - series[0]) / dt
    d[-1] = (series[-1] - series[-2]) / dt
    return d


# ── STLSQ: sequential thresholded least squares ───────────────────────────
def stlsq(Theta: Matrix, dxdt: Vector, threshold: float, iters: int = 10) -> Vector:
    active = list(range(len(Theta[0])))
    coef = [0.0] * len(active)
    for _ in range(iters):
        fit = least_squares(Theta, dxdt, active)
        coef = [0.0] * len(coef)
        for i, c in zip(active, fit):
            coef[i] = c
        kept = [i for i in active if abs(coef[i]) >= threshold]
        if kept == active:
            break
        active = kept
    return coef


def format_equation(lhs: str, coef: Vector, labels: list[str]) -> str:
    terms = [f"{c:+.3f}{'' if l == '1' else ' ' + l}"
             for c, l in zip(coef, labels) if c != 0.0]
    return f"d{lhs}/dt = " + (" ".join(terms) if terms else "0")


# ── Data generation ───────────────────────────────────────────────────────
def rk4(f: Callable[[Vector], Vector], x0: Vector, dt: float, steps: int,
        noise: float, rng: random.Random) -> Matrix:
    x = x0[:]
    out = []
    for _ in range(steps):
        out.append([v + rng.gauss(0, noise) for v in x])
        k1 = f(x)
        k2 = f([xi + dt / 2 * k for xi, k in zip(x, k1)])
        k3 = f([xi + dt / 2 * k for xi, k in zip(x, k2)])
        k4 = f([xi + dt * k for xi, k in zip(x, k3)])
        x = [xi + dt / 6 * (a + 2 * b + 2 * c + d)
             for xi, a, b, c, d in zip(x, k1, k2, k3, k4)]
    return out


def discover(X: Matrix, names: list[str], dt: float, threshold: float) -> None:
    Theta, labels = build_library(X, names)
    for k, name in enumerate(names):
        dxdt = finite_difference([row[k] for row in X], dt)
        coef = stlsq(Theta, dxdt, threshold)
        print("  " + format_equation(name, coef, labels))


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    rng = random.Random(7)

    print("Logistic growth   truth: dx/dt = 0.800 x -0.080 x*x")
    logistic = rk4(lambda s: [0.8 * s[0] * (1 - s[0] / 10)], [0.5], 0.05, 200, 1e-3, rng)
    discover(logistic, ["x"], dt=0.05, threshold=0.02)

    print("\nLotka-Volterra    truth: dx/dt = 1.000 x -0.100 x*y")
    print("                         dy/dt = -1.500 y +0.075 x*y")
    lv = rk4(lambda s: [1.0 * s[0] - 0.1 * s[0] * s[1],
                        -1.5 * s[1] + 0.075 * s[0] * s[1]],
             [10.0, 5.0], 0.01, 1500, 1e-3, rng)
    discover(lv, ["x", "y"], dt=0.01, threshold=0.05)

    print("\nNote: the library held 6 candidate terms per equation; sparsity")
    print("      pruned all but the physically meaningful ones.")
