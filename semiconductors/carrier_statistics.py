"""
Semiconductor Carrier Statistics — where electrons live

The physics that makes transistors possible. Electrons fill states by the
Fermi-Dirac distribution; thermally excited carriers cross the band gap to give
the intrinsic concentration n_i, which depends exponentially on the gap and
temperature. Doping shifts the balance, but the mass-action law n * p = n_i^2
always holds. This is why a small gap (Ge) is far more conductive than a large
one (GaAs), and why electronics needs careful temperature design.
"""

from __future__ import annotations

from math import exp, sqrt


KB = 8.617333e-5      # Boltzmann constant, eV/K


def intrinsic_concentration(temp: float, band_gap: float = 1.12,
                            nc300: float = 2.8e19, nv300: float = 1.04e19
                            ) -> float:
    """Intrinsic carrier concentration n_i (cm^-3). Defaults are silicon."""
    nc = nc300 * (temp / 300) ** 1.5
    nv = nv300 * (temp / 300) ** 1.5
    return sqrt(nc * nv) * exp(-band_gap / (2 * KB * temp))


def fermi_dirac(energy: float, fermi_level: float, temp: float) -> float:
    """Probability a state at `energy` (eV) is occupied."""
    return 1.0 / (1.0 + exp((energy - fermi_level) / (KB * temp)))


def doped_carriers(donor: float, temp: float, band_gap: float = 1.12
                   ) -> tuple[float, float]:
    """n-type: returns (electrons, holes) via charge neutrality + mass action."""
    ni = intrinsic_concentration(temp, band_gap)
    n = donor / 2 + sqrt((donor / 2) ** 2 + ni ** 2)
    p = ni ** 2 / n
    return n, p


if __name__ == "__main__":
    print("Intrinsic carrier concentration n_i at 300 K (band gap matters):\n")
    for name, eg in [("Ge", 0.66), ("Si", 1.12), ("GaAs", 1.42)]:
        print(f"  {name:<5} Eg={eg} eV  n_i = {intrinsic_concentration(300, eg):.2e} cm^-3")

    print("\nSilicon n_i vs temperature:")
    for t in (250, 300, 350, 400):
        print(f"  T={t} K  n_i = {intrinsic_concentration(t):.2e} cm^-3")

    print("\nFermi-Dirac occupancy (Fermi level at 0 eV, 300 K):")
    for e in (-0.1, 0.0, 0.1):
        print(f"  E={e:+.1f} eV  f(E) = {fermi_dirac(e, 0.0, 300):.4f}")

    nd = 1e16
    n, p = doped_carriers(nd, 300)
    print(f"\nn-type silicon, Nd = {nd:.0e} cm^-3 at 300 K:")
    print(f"  electrons (majority): {n:.2e} cm^-3")
    print(f"  holes (minority)    : {p:.2e} cm^-3")
    print(f"  mass action n*p = {n * p:.2e} = n_i^2 "
          f"({intrinsic_concentration(300) ** 2:.2e})")
