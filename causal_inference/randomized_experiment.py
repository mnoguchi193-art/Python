"""
Randomized experiment — RCT / ランダム化比較試験

The "gold standard". Random assignment makes treatment independent of the
potential outcomes, so selection bias vanishes and the difference in mean
outcomes is an unbiased estimate of the ATE.

Reports the estimate, its standard error, and a t-statistic.
"""

from dataclasses import dataclass
from statistics import mean, variance


@dataclass
class ExperimentResult:
    ate: float
    std_error: float
    t_stat: float
    n_treated: int
    n_control: int


def estimate_ate(outcomes: list[float], treatment: list[int]) -> ExperimentResult:
    """Difference-in-means estimator with a heteroskedastic-robust SE."""
    treated = [y for y, d in zip(outcomes, treatment) if d]
    control = [y for y, d in zip(outcomes, treatment) if not d]
    if len(treated) < 2 or len(control) < 2:
        raise ValueError("each group needs at least 2 observations")

    ate = mean(treated) - mean(control)
    # Neyman variance: Var(treated)/n1 + Var(control)/n0.
    se = (variance(treated) / len(treated) + variance(control) / len(control)) ** 0.5
    t = ate / se if se else float("inf")
    return ExperimentResult(ate, se, t, len(treated), len(control))


if __name__ == "__main__":
    outcomes = [10, 12, 11, 13, 9, 7, 6, 8, 5, 7]
    treatment = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
    res = estimate_ate(outcomes, treatment)
    print(f"ATE estimate: {res.ate:.3f}")
    print(f"Std. error:   {res.std_error:.3f}")
    print(f"t-statistic:  {res.t_stat:.3f}")
    print(f"n (treated/control): {res.n_treated}/{res.n_control}")
