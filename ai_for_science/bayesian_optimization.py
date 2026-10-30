"""
Bayesian Optimization (ベイズ最適化) — choosing the next experiment

Self-driving laboratories model an unknown response surface (e.g. reaction
yield vs. temperature) with a Gaussian process (GP) and use an acquisition
function to pick the experiment that best balances exploring uncertain
regions against exploiting promising ones.  Each measurement updates the
model and the loop repeats, so a good optimum is found in far fewer
experiments than grid or random search.

Implemented from scratch: RBF-kernel GP regression (Cholesky solve) and
the Expected Improvement acquisition, benchmarked against random search.
"""

from __future__ import annotations
import math
import random

Matrix = list[list[float]]
Vector = list[float]

T_MIN, T_MAX = 20.0, 120.0           # reaction temperature range (°C)


# ── Hidden ground truth (the "lab") ───────────────────────────────────────
def true_yield(temp: float) -> float:
    """Two-peaked response: a broad low peak and a sharp high one."""
    x = (temp - T_MIN) / (T_MAX - T_MIN)
    return 0.55 * math.exp(-((x - 0.25) ** 2) / 0.02) + math.exp(-((x - 0.72) ** 2) / 0.004)


def run_experiment(temp: float, rng: random.Random, noise: float = 0.02) -> float:
    return true_yield(temp) + rng.gauss(0, noise)


# ── Gaussian process regression ───────────────────────────────────────────
def rbf(a: float, b: float, length: float, amp: float) -> float:
    return amp * math.exp(-((a - b) ** 2) / (2 * length ** 2))


def cholesky(A: Matrix) -> Matrix:
    n = len(A)
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = A[i][j] - sum(L[i][k] * L[j][k] for k in range(j))
            L[i][j] = math.sqrt(max(s, 1e-12)) if i == j else s / L[j][j]
    return L


def cho_solve(L: Matrix, b: Vector) -> Vector:
    """Solve (L L^T) x = b by forward then backward substitution."""
    n = len(L)
    y = [0.0] * n
    for i in range(n):
        y[i] = (b[i] - sum(L[i][k] * y[k] for k in range(i))) / L[i][i]
    x = [0.0] * n
    for i in reversed(range(n)):
        x[i] = (y[i] - sum(L[k][i] * x[k] for k in range(i + 1, n))) / L[i][i]
    return x


class GP:
    def __init__(self, length: float = 0.12, amp: float = 0.5, noise: float = 0.02):
        self.length, self.amp, self.noise = length, amp, noise
        self.X: Vector = []
        self.L: Matrix = []
        self.alpha: Vector = []

    def fit(self, X: Vector, y: Vector) -> None:
        self.X = X
        K = [[rbf(a, b, self.length, self.amp) + (self.noise ** 2 if i == j else 0.0)
              for j, b in enumerate(X)] for i, a in enumerate(X)]
        self.L = cholesky(K)
        self.alpha = cho_solve(self.L, y)

    def predict(self, x: float) -> tuple[float, float]:
        """Posterior mean and standard deviation at x."""
        k = [rbf(x, xi, self.length, self.amp) for xi in self.X]
        mean = sum(ki * ai for ki, ai in zip(k, self.alpha))
        v = cho_solve(self.L, k)
        var = self.amp - sum(ki * vi for ki, vi in zip(k, v))
        return mean, math.sqrt(max(var, 1e-12))


# ── Acquisition: Expected Improvement ─────────────────────────────────────
def expected_improvement(mean: float, std: float, best: float, xi: float = 0.01) -> float:
    z = (mean - best - xi) / std
    cdf = 0.5 * (1 + math.erf(z / math.sqrt(2)))
    pdf = math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
    return (mean - best - xi) * cdf + std * pdf


def to_unit(temp: float) -> float:
    return (temp - T_MIN) / (T_MAX - T_MIN)


def bayes_opt(budget: int, rng: random.Random, n_init: int = 3,
              verbose: bool = False) -> tuple[float, float]:
    """Return (best temperature, best observed yield) after `budget` runs."""
    temps = [rng.uniform(T_MIN, T_MAX) for _ in range(n_init)]
    ys = [run_experiment(t, rng) for t in temps]
    grid = [T_MIN + i * (T_MAX - T_MIN) / 400 for i in range(401)]
    gp = GP()
    for it in range(budget - n_init):
        gp.fit([to_unit(t) for t in temps], ys)
        best = max(ys)
        next_t = max(grid, key=lambda t: expected_improvement(*gp.predict(to_unit(t)), best))
        y = run_experiment(next_t, rng)
        temps.append(next_t)
        ys.append(y)
        if verbose:
            print(f"  run {n_init + it + 1:2d}: T={next_t:6.1f}°C  yield={y:.3f}  best={max(ys):.3f}")
    i = max(range(len(ys)), key=ys.__getitem__)
    return temps[i], ys[i]


def random_search(budget: int, rng: random.Random) -> tuple[float, float]:
    temps = [rng.uniform(T_MIN, T_MAX) for _ in range(budget)]
    ys = [run_experiment(t, rng) for t in temps]
    i = max(range(budget), key=ys.__getitem__)
    return temps[i], ys[i]


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    opt_t = max((T_MIN + i * 0.01 for i in range(10001)), key=true_yield)
    print(f"Hidden optimum: T={opt_t:.1f}°C  yield={true_yield(opt_t):.3f}\n")

    print("Bayesian optimization, 15 experiments (3 random + 12 guided):")
    t, y = bayes_opt(15, random.Random(1), verbose=True)
    print(f"  -> best T={t:.1f}°C  yield={y:.3f}\n")

    trials = 20
    bo = [true_yield(bayes_opt(15, random.Random(s))[0]) for s in range(trials)]
    rs = [true_yield(random_search(15, random.Random(s))[0]) for s in range(trials)]
    print(f"Over {trials} repeats (true yield at the chosen temperature):")
    print(f"  Bayesian opt : mean {sum(bo) / trials:.3f}  worst {min(bo):.3f}")
    print(f"  Random search: mean {sum(rs) / trials:.3f}  worst {min(rs):.3f}")
