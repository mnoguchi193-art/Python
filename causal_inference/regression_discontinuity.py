"""
Regression discontinuity design (RDD) / 回帰不連続デザイン

When treatment switches on at a cutoff c of a running variable x (e.g. a test
score threshold for a scholarship), units just below and just above the cutoff
are comparable. The treatment effect is the jump in the outcome at c.

Sharp RDD with local linear regression on each side of the cutoff:
    tau = limit(x -> c+) E[Y|x] - limit(x -> c-) E[Y|x]
"""

from statistics import mean


def _ols_intercept_slope(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Fit y = a + b*x by least squares; return (a, b)."""
    mx, my = mean(xs), mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        raise ValueError("no variation in x")
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    return a, b


def sharp_rdd(
    x: list[float],
    y: list[float],
    cutoff: float,
    bandwidth: float | None = None,
) -> float:
    """Estimate the treatment effect as the outcome jump at the cutoff."""
    if bandwidth is not None:
        keep = [abs(xi - cutoff) <= bandwidth for xi in x]
        x = [xi for xi, k in zip(x, keep) if k]
        y = [yi for yi, k in zip(y, keep) if k]

    left = [(xi, yi) for xi, yi in zip(x, y) if xi < cutoff]
    right = [(xi, yi) for xi, yi in zip(x, y) if xi >= cutoff]
    if len(left) < 2 or len(right) < 2:
        raise ValueError("need >=2 points on each side of the cutoff")

    a_l, b_l = _ols_intercept_slope([p[0] for p in left], [p[1] for p in left])
    a_r, b_r = _ols_intercept_slope([p[0] for p in right], [p[1] for p in right])
    # Predicted outcome on each side AT the cutoff; their gap is the effect.
    return (a_r + b_r * cutoff) - (a_l + b_l * cutoff)


if __name__ == "__main__":
    # Outcome trends smoothly in x but jumps by ~5 at the cutoff of 50.
    x = [40, 44, 46, 48, 50, 52, 54, 56, 60]
    y = [10, 11, 11.5, 12, 17, 17.5, 18, 18.5, 20]
    print(f"RDD effect at cutoff 50: {sharp_rdd(x, y, cutoff=50):.3f}")
    print(f"RDD with bandwidth 6:    {sharp_rdd(x, y, cutoff=50, bandwidth=6):.3f}")
