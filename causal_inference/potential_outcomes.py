"""
Potential outcomes — Rubin causal model / ルービンの潜在結果モデル

The foundation of the credibility revolution. Each unit has two potential
outcomes:  y1 (if treated) and y0 (if not). We only ever observe one of them
— the "fundamental problem of causal inference".

This teaching module assumes BOTH potential outcomes are known, so we can
show exactly what the naive treated-vs-control comparison misses:

    naive difference = ATT + selection bias
"""

from dataclasses import dataclass
from statistics import mean


@dataclass
class PotentialOutcomes:
    y1: list[float]  # potential outcome under treatment
    y0: list[float]  # potential outcome under control
    d: list[int]     # observed treatment assignment (0/1)

    def __post_init__(self) -> None:
        if not (len(self.y1) == len(self.y0) == len(self.d)):
            raise ValueError("y1, y0, d must have equal length")

    def observed(self) -> list[float]:
        """What an analyst actually sees: y = d*y1 + (1-d)*y0."""
        return [t1 if di else t0 for t1, t0, di in zip(self.y1, self.y0, self.d)]

    def ate(self) -> float:
        """Average Treatment Effect: E[y1 - y0]."""
        return mean(a - b for a, b in zip(self.y1, self.y0))

    def att(self) -> float:
        """Average Treatment effect on the Treated: E[y1 - y0 | d = 1]."""
        effects = [a - b for a, b, di in zip(self.y1, self.y0, self.d) if di]
        return mean(effects)

    def naive_difference(self) -> float:
        """E[y | d = 1] - E[y | d = 0] — the biased observational estimate."""
        y = self.observed()
        treated = [yi for yi, di in zip(y, self.d) if di]
        control = [yi for yi, di in zip(y, self.d) if not di]
        return mean(treated) - mean(control)

    def selection_bias(self) -> float:
        """E[y0 | d = 1] - E[y0 | d = 0]: do groups differ even untreated?"""
        treated_y0 = [b for b, di in zip(self.y0, self.d) if di]
        control_y0 = [b for b, di in zip(self.y0, self.d) if not di]
        return mean(treated_y0) - mean(control_y0)


if __name__ == "__main__":
    # Healthier people (high y0) are also more likely to take the treatment,
    # so the naive comparison overstates the true effect.
    po = PotentialOutcomes(
        y1=[6, 7, 8, 5, 6, 7],
        y0=[5, 5, 6, 2, 1, 2],
        d=[1, 1, 1, 0, 0, 0],
    )
    print(f"ATE:              {po.ate():.3f}")
    print(f"ATT:              {po.att():.3f}")
    print(f"Naive difference: {po.naive_difference():.3f}")
    print(f"Selection bias:   {po.selection_bias():.3f}")
    print(f"ATT + bias:       {po.att() + po.selection_bias():.3f}  (== naive)")
