"""
MOSFET — the transistor that powers every chip

The metal-oxide-semiconductor field-effect transistor is the switch billions of
which sit on a modern processor. The gate voltage controls a channel between
source and drain. The square-law model captures its three regimes:

  cutoff      (Vgs < Vth)            : off, no current
  triode      (Vds < Vgs - Vth)      : acts like a voltage-controlled resistor
  saturation  (Vds >= Vgs - Vth)     : current ~ constant -> used as an amplifier

This Vds-independence in saturation is what makes clean digital logic possible.
"""

from __future__ import annotations


def drain_current(vgs: float, vds: float, vth: float = 1.0,
                  k: float = 1e-3, lam: float = 0.0) -> float:
    """N-channel drain current (A). k = mu*Cox*W/L; lam = channel-length mod."""
    overdrive = vgs - vth
    if overdrive <= 0:
        return 0.0                                    # cutoff
    if vds < overdrive:
        return k * (overdrive * vds - vds ** 2 / 2)   # triode
    return 0.5 * k * overdrive ** 2 * (1 + lam * vds)  # saturation


def region(vgs: float, vds: float, vth: float = 1.0) -> str:
    if vgs - vth <= 0:
        return "cutoff"
    return "triode" if vds < vgs - vth else "saturation"


if __name__ == "__main__":
    vth = 1.0
    vds_values = [0.0, 0.5, 1.0, 2.0, 3.0, 4.0]
    vgs_values = [1.5, 2.0, 2.5, 3.0]

    print(f"N-channel MOSFET output characteristics (Vth = {vth} V)\n")
    print("  Drain current I_D (mA):\n")
    print("   Vgs\\Vds " + "".join(f"{v:>8.1f}" for v in vds_values))
    for vgs in vgs_values:
        row = "".join(f"{drain_current(vgs, vds, vth) * 1e3:>8.3f}"
                      for vds in vds_values)
        print(f"   {vgs:>5.1f}   {row}")

    print("\n  Saturation onset (Vds = Vgs - Vth):")
    for vgs in vgs_values:
        print(f"    Vgs={vgs:.1f} -> saturates beyond Vds={vgs - vth:.1f} V, "
              f"I_D,sat = {drain_current(vgs, 10, vth) * 1e3:.3f} mA")
    print("\n  Beyond saturation the current barely changes with Vds — the")
    print("  transistor behaves as a controlled current source.")
