"""
Radioisotope Power (MMRTG) — how Curiosity stays alive on Mars

NASA's Curiosity rover can't rely on solar panels through dust storms and long
nights, so it carries an MMRTG: a Multi-Mission Radioisotope Thermoelectric
Generator. The natural decay of plutonium-238 (half-life 87.7 years) produces a
steady ~2000 W of heat, and thermocouples convert a few percent of it to
electricity. Because the fuel decays, the available power slowly but inexorably
declines over the mission — a key constraint on what the rover can do each sol.
"""

from __future__ import annotations


HALF_LIFE = 87.7        # plutonium-238 half-life, years


def thermal_power(years: float, initial_thermal: float = 2000.0) -> float:
    """Decay heat (W) remaining after a given number of years."""
    return initial_thermal * 0.5 ** (years / HALF_LIFE)


def electrical_power(years: float, initial_thermal: float = 2000.0,
                     efficiency: float = 0.055) -> float:
    """Electrical output (W) — a few percent of the decay heat."""
    return thermal_power(years, initial_thermal) * efficiency


def daily_energy_wh(years: float) -> float:
    """Energy generated per Martian sol (24.6 h) at a given mission age."""
    return electrical_power(years) * 24.6


if __name__ == "__main__":
    bol = electrical_power(0)
    print("Curiosity MMRTG (plutonium-238, half-life 87.7 yr)\n")
    print(f"  beginning-of-life: ~{thermal_power(0):.0f} W thermal -> "
          f"{bol:.0f} W electric\n")

    print(f"  {'mission year':>12}  {'thermal (W)':>11}  {'electric (W)':>12}"
          f"  {'% of BOL':>9}")
    for year in (0, 1, 5, 10, 14):
        elec = electrical_power(year)
        print(f"  {year:>12}  {thermal_power(year):>11.0f}  {elec:>12.1f}"
              f"  {elec / bol:>8.1%}")

    print(f"\n  Energy budget per sol at year 10: {daily_energy_wh(10):.0f} Wh "
          f"(a rechargeable battery covers peak loads).")
    print("\n  Pure decay alone costs ~0.8%/yr; real thermocouple aging makes the")
    print("  decline steeper — which is why power budgeting drives daily planning.")
