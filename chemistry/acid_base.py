"""
Acid-Base Equilibrium — pH, buffers and titration

The chemistry of protons in solution. A strong acid dissociates completely, but a
weak acid only partially — its pH comes from solving an equilibrium quadratic.
Mixing a weak acid with its conjugate base makes a buffer (Henderson-Hasselbalch),
and titrating that acid with a strong base traces the classic S-curve with a flat
buffer region and a sharp jump at the equivalence point.
"""

from __future__ import annotations

import math


KW = 1e-14


def ph_strong_acid(conc: float) -> float:
    return -math.log10(conc)


def ph_weak_acid(conc: float, ka: float) -> float:
    """Solve Ka = x^2 / (conc - x) for [H+] = x, then pH."""
    x = (-ka + math.sqrt(ka ** 2 + 4 * ka * conc)) / 2
    return -math.log10(x)


def buffer_ph(ka: float, acid: float, base: float) -> float:
    """Henderson-Hasselbalch: pH = pKa + log10([A-]/[HA])."""
    return -math.log10(ka) + math.log10(base / acid)


def titration_ph(vol_base_ml: float, acid_conc: float = 0.1, acid_vol_ml: float = 50,
                 base_conc: float = 0.1, ka: float = 1.8e-5) -> float:
    """pH of a weak acid titrated by a strong base, by region."""
    na = acid_conc * acid_vol_ml / 1000          # moles acid
    nb = base_conc * vol_base_ml / 1000          # moles base added
    v_tot = (acid_vol_ml + vol_base_ml) / 1000
    if nb == 0:
        return ph_weak_acid(acid_conc, ka)
    if nb < na:                                  # buffer region
        return buffer_ph(ka, na - nb, nb)
    if abs(nb - na) < 1e-12:                      # equivalence: conjugate base
        conc = na / v_tot
        oh = math.sqrt(KW / ka * conc)
        return 14 + math.log10(oh)
    excess = (nb - na) / v_tot                    # excess strong base
    return 14 + math.log10(excess)


if __name__ == "__main__":
    print("pH of 0.1 M solutions:")
    print(f"  strong acid (HCl)        : {ph_strong_acid(0.1):.2f}")
    print(f"  weak acid (acetic, Ka=1.8e-5): {ph_weak_acid(0.1, 1.8e-5):.2f}\n")

    print(f"  acetate buffer (equal acid/base): "
          f"pH = {buffer_ph(1.8e-5, 0.1, 0.1):.2f} = pKa\n")

    print("Titration of 0.1 M acetic acid (50 mL) with 0.1 M NaOH:")
    print(f"  {'NaOH (mL)':>10}  {'pH':>5}  region")

    def region(vb: float) -> str:
        if vb == 0:
            return "weak acid"
        if vb == 25:
            return "half-equiv (pH=pKa)"
        if vb < 50:
            return "buffer"
        if vb == 50:
            return "equivalence"
        return "excess base"

    for vb in (0, 10, 25, 40, 49, 50, 51, 60):
        print(f"  {vb:>10}  {titration_ph(vb):>5.2f}  {region(vb)}")
    print("\n  Flat near pKa (buffering), then a sharp jump through the "
          "equivalence point.")
