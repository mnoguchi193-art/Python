"""
Aerodynamics & the Standard Atmosphere — staying aloft

Flight is a balance: lift must equal weight, and lift falls with air density, so a
plane must fly faster as it climbs. This module models the International Standard
Atmosphere (how temperature, pressure and density vary with altitude) and the
basic aerodynamic forces:

    lift = 0.5 * rho * v^2 * S * C_L     drag = 0.5 * rho * v^2 * S * C_D

from which come the stall speed, the cruise speed, and the all-important
lift-to-drag ratio (an aircraft's aerodynamic efficiency).
"""

from __future__ import annotations

import math


G0 = 9.80665
R_AIR = 287.05      # specific gas constant for air (J/kg/K)
T0, P0, L = 288.15, 101325.0, 0.0065   # sea-level temp/pressure, lapse rate


def isa(altitude: float) -> tuple[float, float, float]:
    """International Standard Atmosphere -> (temperature K, pressure Pa, density)."""
    if altitude <= 11_000:
        t = T0 - L * altitude
        p = P0 * (t / T0) ** (G0 / (L * R_AIR))
    else:                                   # isothermal stratosphere
        t = T0 - L * 11_000
        p11 = P0 * (t / T0) ** (G0 / (L * R_AIR))
        p = p11 * math.exp(-G0 * (altitude - 11_000) / (R_AIR * t))
    return t, p, p / (R_AIR * t)


def lift(rho: float, v: float, wing_area: float, cl: float) -> float:
    return 0.5 * rho * v ** 2 * wing_area * cl


def level_flight_speed(weight: float, rho: float, wing_area: float,
                       cl: float) -> float:
    """Speed at which lift equals weight for a given lift coefficient."""
    return math.sqrt(2 * weight / (rho * wing_area * cl))


if __name__ == "__main__":
    print("International Standard Atmosphere:\n")
    print(f"  {'alt (km)':>8}  {'T (C)':>7}  {'p (kPa)':>8}  {'rho (kg/m3)':>11}")
    for km in (0, 5, 11, 15):
        t, p, rho = isa(km * 1000)
        print(f"  {km:>8}  {t - 273.15:>7.1f}  {p / 1000:>8.1f}  {rho:>11.3f}")

    # A small airliner.
    mass, S, cl_max, cl_cruise, cd = 70_000, 122.0, 1.5, 0.5, 0.030
    weight = mass * G0
    print(f"\nAircraft: {mass/1000:.0f} t, wing {S} m^2, "
          f"L/D = {cl_cruise / cd:.1f}\n")

    _, _, rho_sl = isa(0)
    _, _, rho_alt = isa(10_000)
    print(f"  stall speed at sea level (CLmax={cl_max}): "
          f"{level_flight_speed(weight, rho_sl, S, cl_max):.0f} m/s")
    print(f"  cruise speed at sea level: "
          f"{level_flight_speed(weight, rho_sl, S, cl_cruise):.0f} m/s")
    print(f"  cruise speed at 10 km    : "
          f"{level_flight_speed(weight, rho_alt, S, cl_cruise):.0f} m/s")
    print("\n  Thinner air aloft forces a higher true airspeed for the same lift.")
