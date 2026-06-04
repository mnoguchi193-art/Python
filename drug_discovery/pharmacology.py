"""
Pharmacology — dose-response & pharmacokinetics / 薬理学(用量反応・薬物動態)

Two pillars of quantitative drug design:

  * Dose-response (the Hill equation): how drug concentration maps to effect,
    summarised by potency (EC50/IC50) and the Hill slope.
  * Pharmacokinetics (one-compartment model): how drug concentration in the
    body decays over time, summarised by half-life, clearance and exposure
    (AUC).

Standard library only.
"""

import math


def hill_response(
    concentration: float, ec50: float, emax: float = 1.0, hill: float = 1.0
) -> float:
    """Effect at a given concentration: E = Emax * C^n / (EC50^n + C^n)."""
    if concentration < 0:
        raise ValueError("concentration must be non-negative")
    c_n = concentration**hill
    return emax * c_n / (ec50**hill + c_n)


def concentration_for_response(
    fraction: float, ec50: float, hill: float = 1.0
) -> float:
    """Concentration achieving a target fraction (0-1) of Emax."""
    if not 0 < fraction < 1:
        raise ValueError("fraction must be in (0, 1)")
    # Invert the Hill equation: C = EC50 * (f / (1 - f))^(1/n).
    return ec50 * (fraction / (1 - fraction)) ** (1 / hill)


class OneCompartmentPK:
    """IV-bolus one-compartment model: C(t) = (Dose/Vd) * exp(-k t)."""

    def __init__(self, dose: float, volume: float, half_life: float) -> None:
        self.dose = dose
        self.volume = volume          # volume of distribution (Vd)
        self.half_life = half_life
        self.k = math.log(2) / half_life  # elimination rate constant

    def concentration(self, t: float) -> float:
        return (self.dose / self.volume) * math.exp(-self.k * t)

    @property
    def clearance(self) -> float:
        """CL = k * Vd."""
        return self.k * self.volume

    @property
    def auc(self) -> float:
        """Total exposure: AUC(0->inf) = Dose / Clearance."""
        return self.dose / self.clearance

    def time_to_concentration(self, target: float) -> float:
        """Time for concentration to fall to `target`."""
        c0 = self.dose / self.volume
        if not 0 < target < c0:
            raise ValueError("target must be between 0 and the initial concentration")
        return math.log(c0 / target) / self.k


if __name__ == "__main__":
    print("Dose-response (Hill equation):")
    for c in [1, 5, 10, 50, 100]:
        e = hill_response(c, ec50=10, emax=100, hill=1.5)
        print(f"  C={c:4d}  effect={e:6.2f}% of Emax")
    print(f"  EC90 concentration: {concentration_for_response(0.9, ec50=10, hill=1.5):.2f}")

    print("\nPharmacokinetics (one-compartment):")
    pk = OneCompartmentPK(dose=500, volume=35, half_life=4.0)
    print(f"  C(0h):   {pk.concentration(0):.2f}")
    print(f"  C(8h):   {pk.concentration(8):.2f}")
    print(f"  Clearance: {pk.clearance:.2f}")
    print(f"  AUC:       {pk.auc:.2f}")
    print(f"  Time to reach 1.0: {pk.time_to_concentration(1.0):.2f} h")
