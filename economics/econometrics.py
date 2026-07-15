"""
Econometrics (計量経済学)

Simple linear regression (OLS) with inference statistics, implemented
from first principles with only the standard library:

    y = beta0 + beta1 * x + error

Includes R-squared, standard errors, t-statistics, and an elasticity
estimate via a log-log specification.
"""

from __future__ import annotations
import math
from dataclasses import dataclass


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def variance(xs: list[float]) -> float:
    """Sample variance (n - 1 denominator)."""
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def correlation(xs: list[float], ys: list[float]) -> float:
    mx, my = mean(xs), mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return cov / (sx * sy)


@dataclass
class OLSResult:
    intercept: float
    slope: float
    r_squared: float
    se_intercept: float
    se_slope: float
    n: int

    @property
    def t_slope(self) -> float:
        return self.slope / self.se_slope

    def predict(self, x: float) -> float:
        return self.intercept + self.slope * x

    def summary(self) -> str:
        return (
            f"y = {self.intercept:.4f} + {self.slope:.4f} * x\n"
            f"R-squared : {self.r_squared:.4f}\n"
            f"SE(slope) : {self.se_slope:.4f}\n"
            f"t(slope)  : {self.t_slope:.2f}\n"
            f"n         : {self.n}"
        )


def ols(xs: list[float], ys: list[float]) -> OLSResult:
    """Ordinary least squares for a single regressor."""
    if len(xs) != len(ys) or len(xs) < 3:
        raise ValueError("need equal-length samples with n >= 3")
    n = len(xs)
    mx, my = mean(xs), mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = my - slope * mx

    residuals = [y - (intercept + slope * x) for x, y in zip(xs, ys)]
    ss_res = sum(e ** 2 for e in residuals)
    ss_tot = sum((y - my) ** 2 for y in ys)
    sigma2 = ss_res / (n - 2)  # unbiased error variance

    return OLSResult(
        intercept=intercept,
        slope=slope,
        r_squared=1 - ss_res / ss_tot,
        se_intercept=math.sqrt(sigma2 * (1 / n + mx ** 2 / sxx)),
        se_slope=math.sqrt(sigma2 / sxx),
        n=n,
    )


def price_elasticity(prices: list[float], quantities: list[float]) -> float:
    """Elasticity from a log-log regression: ln Q = a + e * ln P."""
    log_p = [math.log(p) for p in prices]
    log_q = [math.log(q) for q in quantities]
    return ols(log_p, log_q).slope


if __name__ == "__main__":
    # Demand data: observed (price, quantity) pairs
    prices = [10.0, 12.0, 15.0, 18.0, 20.0, 24.0, 30.0, 35.0]
    quantities = [180.0, 152.0, 130.0, 105.0, 98.0, 82.0, 60.0, 52.0]

    print("OLS: quantity on price")
    result = ols(prices, quantities)
    print(result.summary())
    print(f"\nPredicted Q at P=25 : {result.predict(25):.1f}")
    print(f"Correlation(P, Q)   : {correlation(prices, quantities):.4f}")
    print(f"Price elasticity    : {price_elasticity(prices, quantities):.3f}")
