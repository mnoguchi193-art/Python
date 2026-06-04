"""
Instrumental variables (IV) / 操作変数法

When treatment D is correlated with the error term (endogeneity), OLS is
biased. A valid instrument Z affects the outcome Y *only* through D and is
otherwise unrelated to the error.

Single-instrument estimators:
    Wald (binary Z):  (E[Y|Z=1] - E[Y|Z=0]) / (E[D|Z=1] - E[D|Z=0])
    2SLS (general):   Cov(Z, Y) / Cov(Z, D)
"""

from statistics import mean


def _cov(xs: list[float], ys: list[float]) -> float:
    mx, my = mean(xs), mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / len(xs)


def wald_estimator(
    y: list[float], d: list[float], z: list[int]
) -> float:
    """Wald estimator for a binary instrument z (0/1)."""
    y1 = [yi for yi, zi in zip(y, z) if zi]
    y0 = [yi for yi, zi in zip(y, z) if not zi]
    d1 = [di for di, zi in zip(d, z) if zi]
    d0 = [di for di, zi in zip(d, z) if not zi]
    first_stage = mean(d1) - mean(d0)
    if first_stage == 0:
        raise ValueError("weak instrument: no first-stage variation in D")
    return (mean(y1) - mean(y0)) / first_stage


def iv_2sls(y: list[float], d: list[float], z: list[float]) -> float:
    """Just-identified 2SLS / IV slope: Cov(Z, Y) / Cov(Z, D)."""
    cov_zd = _cov(z, d)
    if cov_zd == 0:
        raise ValueError("weak instrument: Cov(Z, D) = 0")
    return _cov(z, y) / cov_zd


if __name__ == "__main__":
    # Z = randomized encouragement, D = take-up, Y = outcome.
    y = [4, 5, 3, 6, 2, 3, 7, 5, 1, 2]
    d = [1, 1, 0, 1, 0, 0, 1, 1, 0, 0]
    z = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
    print(f"Wald estimator (LATE): {wald_estimator(y, d, z):.3f}")

    zc = [float(v) for v in z]
    dc = [float(v) for v in d]
    print(f"2SLS estimator:        {iv_2sls(y, dc, zc):.3f}")
