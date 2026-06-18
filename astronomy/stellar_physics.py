"""
Stellar Physics — reading a star from its light

The physics behind the Hertzsprung-Russell diagram. A star's luminosity follows
the Stefan-Boltzmann law (L = 4 pi R^2 sigma T^4); Wien's law turns its color into
a temperature; and on the main sequence luminosity scales steeply with mass
(L ~ M^3.5). The startling consequence: massive stars are brilliant but
short-lived, while small stars sip their fuel for trillions of years.
"""

from __future__ import annotations

import math


SIGMA = 5.670374e-8      # Stefan-Boltzmann constant (W/m^2/K^4)
WIEN_B = 2.897771e-3     # Wien displacement constant (m*K)
L_SUN = 3.828e26         # solar luminosity (W)
R_SUN = 6.957e8          # solar radius (m)
T_SUN = 5772             # solar effective temperature (K)
M_BOL_SUN = 4.74         # Sun's absolute bolometric magnitude


def luminosity(radius: float, temperature: float) -> float:
    """Stefan-Boltzmann luminosity (W)."""
    return 4 * math.pi * radius ** 2 * SIGMA * temperature ** 4


def wien_peak_nm(temperature: float) -> float:
    """Wavelength of peak emission (nanometres)."""
    return WIEN_B / temperature * 1e9


def main_sequence_lifetime(mass_solar: float) -> float:
    """Approximate main-sequence lifetime in years (L ~ M^3.5, fuel ~ M)."""
    return 1.0e10 * mass_solar / mass_solar ** 3.5


def absolute_magnitude(lum: float) -> float:
    return M_BOL_SUN - 2.5 * math.log10(lum / L_SUN)


if __name__ == "__main__":
    print("Sun check: luminosity from R and T ="
          f" {luminosity(R_SUN, T_SUN):.3e} W (actual {L_SUN:.3e})\n")

    print("Wien's law — color reveals temperature:")
    for label, t in [("red dwarf", 3000), ("Sun", 5772), ("blue giant", 25000)]:
        print(f"  {label:<11} T={t:>5} K  peak {wien_peak_nm(t):.0f} nm")

    print("\nMain sequence: mass sets brightness and lifespan")
    print(f"  {'mass (Msun)':>11}  {'L (Lsun)':>10}  {'lifetime':>14}  {'abs mag':>8}")
    for m in (0.2, 1.0, 3.0, 15.0):
        lum_solar = m ** 3.5
        life = main_sequence_lifetime(m)
        life_str = (f"{life / 1e9:.1f} Gyr" if life >= 1e9 else f"{life / 1e6:.0f} Myr")
        print(f"  {m:>11.1f}  {lum_solar:>10.2f}  {life_str:>14}  "
              f"{absolute_magnitude(lum_solar * L_SUN):>8.1f}")
    print("\n  A 15-Msun star outshines the Sun ~13,000x but lives <0.1% as long.")
