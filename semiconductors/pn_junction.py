"""
PN Junction Diode — the first semiconductor device

Joining p-type and n-type silicon creates the rectifying junction at the heart of
all electronics. Diffusion of carriers leaves a depleted region with a built-in
potential; an applied voltage then modulates the current exponentially via the
Shockley equation, so the diode conducts strongly in forward bias but barely at
all in reverse — it passes current one way only.
"""

from __future__ import annotations

from math import exp, log, sqrt


VT = 0.025852          # thermal voltage kT/q at 300 K (volts)
Q = 1.602e-19          # electron charge (C)
EPS_SI = 11.7 * 8.854e-14   # silicon permittivity (F/cm)
NI = 1.0e10            # silicon intrinsic concentration at 300 K (cm^-3)


def built_in_potential(na: float, nd: float) -> float:
    """Junction built-in potential (volts)."""
    return VT * log(na * nd / NI ** 2)


def depletion_width(na: float, nd: float) -> float:
    """Total depletion-region width at zero bias (cm)."""
    vbi = built_in_potential(na, nd)
    return sqrt(2 * EPS_SI * vbi / Q * (1 / na + 1 / nd))


def diode_current(voltage: float, i_sat: float = 1e-12, ideality: float = 1.0
                  ) -> float:
    """Shockley diode equation: current (A) at an applied voltage."""
    return i_sat * (exp(voltage / (ideality * VT)) - 1)


if __name__ == "__main__":
    na, nd = 1e17, 1e16
    vbi = built_in_potential(na, nd)
    width = depletion_width(na, nd)

    print(f"Silicon PN junction (Na={na:.0e}, Nd={nd:.0e} cm^-3)\n")
    print(f"  built-in potential : {vbi:.3f} V")
    print(f"  depletion width    : {width * 1e4:.3f} um\n")

    print("  Diode I-V (Shockley equation):")
    print(f"  {'V (V)':>7}  {'I (A)':>12}")
    for v in (-0.2, 0.0, 0.3, 0.5, 0.6, 0.7):
        print(f"  {v:>7.2f}  {diode_current(v):>12.2e}")
    print("\n  Forward current rises exponentially (~10x per 60 mV); reverse")
    print("  current is stuck at -I_sat. That asymmetry is rectification.")
