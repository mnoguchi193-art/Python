"""
Cosmology — the expanding universe

Hubble's law (v = H0 * d) says distant galaxies recede faster, the signature of
an expanding universe. Run the expansion backwards and the inverse of the Hubble
constant gives the Hubble time — a first estimate of the age of the cosmos.
Redshift z measures how much a galaxy's light has been stretched; at large z the
relation between z and recession speed becomes relativistic.
"""

from __future__ import annotations

import math


H0 = 70.0                  # Hubble constant (km/s/Mpc)
C = 299_792.458            # speed of light (km/s)
MPC_KM = 3.085677e19       # one megaparsec in km


def recession_velocity(distance_mpc: float) -> float:
    return H0 * distance_mpc


def hubble_time_gyr() -> float:
    """1/H0 expressed in billions of years."""
    seconds = MPC_KM / H0
    return seconds / (3.1557e7 * 1e9)


def velocity_from_redshift(z: float, relativistic: bool = True) -> float:
    """Recession velocity (km/s) from redshift z."""
    if not relativistic:
        return C * z
    factor = (1 + z) ** 2
    return C * (factor - 1) / (factor + 1)


def distance_from_redshift(z: float) -> float:
    """Approximate distance (Mpc) using low-z Hubble law."""
    return velocity_from_redshift(z, relativistic=False) / H0


if __name__ == "__main__":
    print(f"Hubble constant H0 = {H0} km/s/Mpc\n")

    print("Hubble's law — recession with distance:")
    for d in (10, 100, 1000):
        print(f"  {d:>4} Mpc -> {recession_velocity(d):>7.0f} km/s")

    print(f"\nHubble time (age estimate): {hubble_time_gyr():.2f} billion years")

    print("\nRedshift and recession velocity:")
    for z in (0.01, 0.1, 1.0, 3.0):
        naive = velocity_from_redshift(z, relativistic=False)
        rel = velocity_from_redshift(z, relativistic=True)
        print(f"  z={z:<4}  naive cz = {naive / C:.2f} c   "
              f"relativistic = {rel / C:.2f} c")
    print("\n  At low z, v ~ cz; at high z the naive formula exceeds c and the")
    print("  relativistic Doppler relation must be used instead.")
