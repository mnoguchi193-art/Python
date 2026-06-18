"""
Atmospheric Thermodynamics — humidity, lifting, and storm energy

The physics behind convective forecasting. From temperature and dewpoint we get
relative humidity; lifting a surface parcel dry-adiabatically until it saturates
gives the cloud base (LCL); continuing the ascent and comparing the parcel to the
environment yields CAPE — the reservoir of energy that powers thunderstorms.

Temperatures in degrees Celsius, heights in metres.
"""

from __future__ import annotations

from math import exp, log


G = 9.81            # gravity, m/s^2
DALR = 9.8 / 1000   # dry adiabatic lapse rate, K per metre
MALR = 6.0 / 1000   # representative moist adiabatic lapse rate, K per metre


def saturation_vapor_pressure(t_c: float) -> float:
    """Saturation vapour pressure (hPa) via the Magnus-Tetens formula."""
    return 6.112 * exp(17.67 * t_c / (t_c + 243.5))


def relative_humidity(t_c: float, dewpoint_c: float) -> float:
    return 100 * saturation_vapor_pressure(dewpoint_c) / saturation_vapor_pressure(t_c)


def dewpoint(t_c: float, rh_percent: float) -> float:
    gamma = log(rh_percent / 100) + 17.67 * t_c / (t_c + 243.5)
    return 243.5 * gamma / (17.67 - gamma)


def lcl_height(t_c: float, dewpoint_c: float) -> float:
    """Lifting condensation level (cloud base) height, Espy's approximation."""
    return 125.0 * (t_c - dewpoint_c)


def parcel_temperature(surface_t: float, surface_td: float, height: float
                       ) -> float:
    """Temperature of a lifted surface parcel at a given height."""
    z_lcl = lcl_height(surface_t, surface_td)
    if height <= z_lcl:
        return surface_t - DALR * height
    t_lcl = surface_t - DALR * z_lcl
    return t_lcl - MALR * (height - z_lcl)


def cape(surface_t: float, surface_td: float,
         sounding: list[tuple[float, float]]) -> float:
    """Convective Available Potential Energy (J/kg) from a parcel ascent.

    `sounding` is sorted (height_m, environment_temp_C). CAPE integrates the
    positive buoyancy of the parcel relative to the environment.
    """
    total = 0.0
    for (z0, te0), (z1, te1) in zip(sounding, sounding[1:]):
        dz = z1 - z0
        tp = (parcel_temperature(surface_t, surface_td, z0)
              + parcel_temperature(surface_t, surface_td, z1)) / 2
        te = (te0 + te1) / 2
        buoyancy = (tp - te) / (te + 273.15)
        if buoyancy > 0:
            total += G * buoyancy * dz
    return total


if __name__ == "__main__":
    surface_t, surface_td = 30.0, 22.0
    print("Surface parcel: T = 30 C, dewpoint = 22 C\n")
    print(f"  relative humidity : {relative_humidity(surface_t, surface_td):.0f}%")
    print(f"  cloud base (LCL)  : {lcl_height(surface_t, surface_td):.0f} m")
    print(f"  check dewpoint(T, RH): "
          f"{dewpoint(surface_t, relative_humidity(surface_t, surface_td)):.1f} C\n")

    # A warm, unstable environmental sounding.
    sounding = [(0, 30), (1000, 21), (2000, 14), (4000, 1),
                (6000, -12), (8000, -28), (10000, -45)]
    energy = cape(surface_t, surface_td, sounding)
    print(f"  CAPE: {energy:.0f} J/kg")
    severity = ("minimal" if energy < 1000 else
                "moderate (thunderstorms likely)" if energy < 2500 else
                "strong (severe storms possible)")
    print(f"  convective potential: {severity}")
