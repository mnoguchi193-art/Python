"""
Quantum Mechanics — confinement and tunneling

Two hallmarks of the quantum world. Confine a particle in a box and its energy
becomes *quantized*: only discrete levels E_n ~ n^2 are allowed, unlike a
classical particle that can have any energy. And a particle can *tunnel* through a
barrier taller than its energy — classically forbidden, yet the basis of the
scanning tunneling microscope, flash memory and nuclear fusion in stars.
"""

from __future__ import annotations

import math


HBAR = 1.054571817e-34     # reduced Planck constant (J*s)
M_E = 9.1093837e-31        # electron mass (kg)
EV = 1.602176634e-19       # one electron-volt (J)


def energy_level(n: int, width_nm: float) -> float:
    """Energy (eV) of level n for an electron in an infinite square well."""
    width = width_nm * 1e-9
    return n ** 2 * math.pi ** 2 * HBAR ** 2 / (2 * M_E * width ** 2) / EV


def tunneling_probability(energy_ev: float, barrier_ev: float,
                          width_nm: float) -> float:
    """Transmission through a rectangular barrier for energy < barrier."""
    e, v0 = energy_ev * EV, barrier_ev * EV
    kappa = math.sqrt(2 * M_E * (v0 - e)) / HBAR
    s = math.sinh(kappa * width_nm * 1e-9)
    return 1 / (1 + barrier_ev ** 2 * s ** 2
                / (4 * energy_ev * (barrier_ev - energy_ev)))


if __name__ == "__main__":
    print("Particle in a box — energy is quantized (electron in a 1 nm well):\n")
    print(f"  {'level n':>8}  {'energy (eV)':>12}  {'ratio to E1':>12}")
    for n in range(1, 6):
        e = energy_level(n, 1.0)
        print(f"  {n:>8}  {e:>12.3f}  {e / energy_level(1, 1.0):>11.0f}x")
    print("  (E_n grows as n^2 — a classical particle could have any energy)\n")

    print("Quantum tunneling through a 2 eV barrier (electron at 1 eV):\n")
    print(f"  {'barrier width':>14}  {'transmission':>13}")
    for w in (0.1, 0.3, 0.5, 1.0):
        t = tunneling_probability(1.0, 2.0, w)
        print(f"  {w:>11} nm  {t:>13.2e}")
    print("\n  The particle's energy is below the barrier, yet transmission is")
    print("  nonzero — and falls off exponentially with barrier width.")
