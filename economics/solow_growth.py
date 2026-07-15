"""
Solow-Swan Growth Model (ソロー成長モデル)

Capital accumulation:  k' = s * f(k) + (1 - delta - n) * k  (per-worker terms)
Production function:   f(k) = A * k^alpha  (Cobb-Douglas)

Demonstrates steady state, convergence dynamics, and the golden-rule
savings rate — foundations of modern growth theory.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator


@dataclass
class SolowModel:
    alpha: float = 0.33   # capital share
    s: float = 0.25       # savings rate
    delta: float = 0.05   # depreciation rate
    n: float = 0.01       # population growth rate
    A: float = 1.0        # total factor productivity

    def output(self, k: float) -> float:
        """Per-worker output f(k) = A * k^alpha."""
        return self.A * k ** self.alpha

    def next_capital(self, k: float) -> float:
        """One-period transition of capital per worker."""
        return (self.s * self.output(k) + (1 - self.delta) * k) / (1 + self.n)

    def steady_state_capital(self) -> float:
        """Closed-form steady state: k* = (s*A / (n + delta))^(1/(1-alpha))."""
        return (self.s * self.A / (self.n + self.delta)) ** (1 / (1 - self.alpha))

    def steady_state_output(self) -> float:
        return self.output(self.steady_state_capital())

    def golden_rule_savings(self) -> float:
        """Savings rate that maximizes steady-state consumption (= alpha)."""
        return self.alpha

    def simulate(self, k0: float, periods: int) -> Iterator[tuple[int, float, float]]:
        """Yield (t, capital, output) along the convergence path."""
        k = k0
        for t in range(periods + 1):
            yield t, k, self.output(k)
            k = self.next_capital(k)

    def half_life(self, k0: float, tol: float = 1e-9) -> int:
        """Periods until half the gap to the steady state is closed."""
        k_star = self.steady_state_capital()
        gap0 = abs(k_star - k0)
        if gap0 < tol:
            return 0
        k, t = k0, 0
        while abs(k_star - k) > gap0 / 2:
            k = self.next_capital(k)
            t += 1
        return t


if __name__ == "__main__":
    model = SolowModel()
    k_star = model.steady_state_capital()
    print(f"Steady-state capital k* : {k_star:.4f}")
    print(f"Steady-state output  y* : {model.steady_state_output():.4f}")
    print(f"Golden-rule savings s_g : {model.golden_rule_savings():.2f}")
    print(f"Half-life from k0=1     : {model.half_life(1.0)} periods")
    print("\nConvergence path (k0 = 1.0):")
    print(f"{'t':>4} {'k':>10} {'y':>10}")
    for t, k, y in model.simulate(k0=1.0, periods=100):
        if t % 20 == 0:
            print(f"{t:>4} {k:>10.4f} {y:>10.4f}")
