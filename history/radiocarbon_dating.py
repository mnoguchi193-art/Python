"""
Radiocarbon Dating — turning carbon-14 decay into chronology

The workhorse of scientific archaeology. Living things absorb carbon-14 until
they die; afterwards it decays with a half-life of 5730 years. Measuring the
fraction remaining dates the sample:

    fraction = (1/2) ** (age / half_life)
    age      = -half_life * log2(fraction)

Two real-world subtleties are modeled: measurement uncertainty propagates into
the date, and raw "radiocarbon years" must be *calibrated* to calendar years
because atmospheric C-14 has varied over time.
"""

from __future__ import annotations

from math import log2


HALF_LIFE = 5730.0  # years (Cambridge value)


def age_from_fraction(fraction: float, half_life: float = HALF_LIFE) -> float:
    """Years since death from the fraction of C-14 remaining."""
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0, 1]")
    return -half_life * log2(fraction)


def fraction_after(age: float, half_life: float = HALF_LIFE) -> float:
    return 0.5 ** (age / half_life)


def age_uncertainty(fraction: float, sigma: float,
                    half_life: float = HALF_LIFE) -> float:
    """1-sigma error in the age from a measurement error in the fraction.

    Derivative of age wrt fraction: d(age)/d(f) = -half_life / (ln2 * f).
    """
    from math import log
    return half_life / (log(2) * fraction) * sigma


def calibrate(radiocarbon_age: float,
              curve: list[tuple[float, float]]) -> float:
    """Map a radiocarbon age to a calendar age via a piecewise-linear curve.

    `curve` is sorted (radiocarbon_age, calendar_age) control points.
    """
    for (x0, y0), (x1, y1) in zip(curve, curve[1:]):
        if x0 <= radiocarbon_age <= x1:
            t = (radiocarbon_age - x0) / (x1 - x0) if x1 != x0 else 0
            return y0 + t * (y1 - y0)
    return curve[-1][1] if radiocarbon_age > curve[-1][0] else curve[0][1]


if __name__ == "__main__":
    print(f"Carbon-14 half-life: {HALF_LIFE:.0f} years\n")
    print("  age (yr)   fraction remaining")
    for age in (0, 5730, 11460, 22920, 50000):
        print(f"  {age:>7,}   {fraction_after(age):.4f}")

    # Dating real-ish samples from measured C-14 fractions (+/- 0.005).
    samples = {
        "Linen wrapping": 0.7820,
        "Charcoal hearth": 0.5500,
        "Mammoth bone": 0.1400,
    }
    print("\nDated samples (1-sigma from +/-0.005 measurement error):")
    for name, frac in samples.items():
        age = age_from_fraction(frac)
        err = age_uncertainty(frac, 0.005)
        print(f"  {name:<16}: {age:7,.0f} +/- {err:.0f} years")

    # Calibration can map one radiocarbon age to an offset calendar age.
    curve = [(0, 0), (1000, 950), (2000, 1900), (3000, 3200)]
    rc_age = 2000
    print(f"\nRadiocarbon age {rc_age} yr  ->  calendar age "
          f"{calibrate(rc_age, curve):.0f} yr (after calibration)")
