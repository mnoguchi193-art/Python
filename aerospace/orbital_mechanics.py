"""
Orbital Mechanics — moving around a planet

The astrodynamics behind every satellite and space mission. The vis-viva equation
gives speed anywhere on an orbit; Kepler's third law gives the period; and a
Hohmann transfer is the fuel-optimal two-burn manoeuvre between circular orbits —
exactly how spacecraft climb from low Earth orbit to geostationary orbit.

SI units throughout (metres, seconds). Earth gravitational parameter mu = G*M.
"""

from __future__ import annotations

import math


MU = 3.986004418e14    # Earth's gravitational parameter (m^3/s^2)
R_EARTH = 6_371_000    # mean radius (m)


def circular_velocity(radius: float) -> float:
    return math.sqrt(MU / radius)


def vis_viva(radius: float, semi_major: float) -> float:
    """Speed at `radius` on an orbit of given semi-major axis."""
    return math.sqrt(MU * (2 / radius - 1 / semi_major))


def orbital_period(semi_major: float) -> float:
    return 2 * math.pi * math.sqrt(semi_major ** 3 / MU)


def escape_velocity(radius: float) -> float:
    return math.sqrt(2 * MU / radius)


def hohmann_transfer(r1: float, r2: float) -> dict[str, float]:
    """Delta-v budget and time for a Hohmann transfer between circular orbits."""
    a_t = (r1 + r2) / 2
    dv1 = vis_viva(r1, a_t) - circular_velocity(r1)
    dv2 = circular_velocity(r2) - vis_viva(r2, a_t)
    return {"dv1": dv1, "dv2": dv2, "total": dv1 + dv2,
            "time": orbital_period(a_t) / 2}


if __name__ == "__main__":
    leo = R_EARTH + 400_000          # 400 km altitude
    geo = 42_164_000                 # geostationary radius

    print("Orbital mechanics\n")
    print(f"  LEO (400 km): speed {circular_velocity(leo):.0f} m/s, "
          f"period {orbital_period(leo) / 60:.1f} min")
    print(f"  GEO         : speed {circular_velocity(geo):.0f} m/s, "
          f"period {orbital_period(geo) / 3600:.1f} h")
    print(f"  escape velocity at surface: {escape_velocity(R_EARTH):.0f} m/s\n")

    t = hohmann_transfer(leo, geo)
    print("  Hohmann transfer LEO -> GEO:")
    print(f"    burn 1 (raise apogee): {t['dv1']:.0f} m/s")
    print(f"    burn 2 (circularize) : {t['dv2']:.0f} m/s")
    print(f"    total delta-v        : {t['total']:.0f} m/s")
    print(f"    transfer time        : {t['time'] / 3600:.1f} h")
