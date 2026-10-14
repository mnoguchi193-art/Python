"""
Exoplanet Detection — finding other worlds

Two methods have found thousands of planets. The *transit* method watches a star
dim as a planet crosses it: the fractional drop is (Rp/Rs)^2. The *radial-
velocity* method (which won the 2019 Nobel Prize for the first exoplanet around a
Sun-like star) detects the star's tiny Doppler wobble as the planet tugs it
about. Both make small planets very hard to see — exactly why detecting Earth
analogues is at the frontier.
"""

from __future__ import annotations

import math


G = 6.674e-11
R_SUN, R_JUP, R_EARTH = 6.957e8, 7.149e7, 6.371e6
M_SUN, M_JUP, M_EARTH = 1.989e30, 1.898e27, 5.972e24
YEAR = 3.1557e7


def transit_depth(planet_radius: float, star_radius: float) -> float:
    """Fractional brightness drop during transit."""
    return (planet_radius / star_radius) ** 2


def planet_radius_from_depth(depth: float, star_radius: float) -> float:
    return star_radius * math.sqrt(depth)


def radial_velocity_amplitude(planet_mass: float, star_mass: float,
                              period_s: float) -> float:
    """Stellar reflex velocity semi-amplitude K (m/s), circular orbit."""
    return (2 * math.pi * G / period_s) ** (1 / 3) * \
        planet_mass / (star_mass + planet_mass) ** (2 / 3)


if __name__ == "__main__":
    print("Transit method — brightness dip as a planet crosses its star:\n")
    for name, rp in [("Jupiter", R_JUP), ("Earth", R_EARTH)]:
        depth = transit_depth(rp, R_SUN)
        print(f"  {name:<8}: depth {depth:.2e}  ({depth * 1e6:,.0f} ppm)")

    observed = 0.01
    inferred = planet_radius_from_depth(observed, R_SUN)
    print(f"\n  A 1% dip implies a planet of radius {inferred / R_JUP:.2f} R_Jupiter")

    print("\nRadial-velocity method — the star's Doppler wobble:\n")
    cases = [("Jupiter (P=11.9 yr)", M_JUP, 11.86 * YEAR),
             ("Earth (P=1 yr)", M_EARTH, 1.0 * YEAR),
             ("Hot Jupiter (P=4.2 d)", M_JUP, 4.23 * 86400)]
    for name, mp, period in cases:
        k = radial_velocity_amplitude(mp, M_SUN, period)
        print(f"  {name:<22}: K = {k:6.2f} m/s")
    print("\n  Jupiter wobbles the Sun ~12 m/s, but Earth only ~0.09 m/s — which")
    print("  is why detecting true Earth twins pushes the limits of precision.")
