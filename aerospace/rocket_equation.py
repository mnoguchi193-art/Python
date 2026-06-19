"""
The Tsiolkovsky Rocket Equation — why rockets have stages

A rocket's achievable velocity change depends only on its exhaust velocity and
the ratio of its full to empty mass:

    delta_v = Isp * g0 * ln(m_initial / m_final)

Because that ratio grows *exponentially* with delta-v, a single stage dragging
its empty tanks all the way to orbit needs an impossible mass ratio. Staging —
dropping dead structural mass partway — is the trick that makes spaceflight
possible, as the numbers below show.
"""

from __future__ import annotations

import math


G0 = 9.80665   # standard gravity (m/s^2)


def delta_v(isp: float, m_initial: float, m_final: float) -> float:
    return isp * G0 * math.log(m_initial / m_final)


def payload_fraction(target_dv: float, isp: float,
                     structural_coeff: float) -> float:
    """Payload mass fraction for a single stage achieving target_dv.

    structural_coeff = structure / (structure + propellant). A negative result
    means the stage is infeasible: the tanks alone are too heavy.
    """
    ve = isp * G0
    r = math.exp(-target_dv / ve)
    return (r - structural_coeff) / (1 - structural_coeff)


if __name__ == "__main__":
    print("Tsiolkovsky rocket equation\n")
    dv = delta_v(isp=350, m_initial=100_000, m_final=20_000)
    print(f"  Isp=350 s, mass 100 t -> 20 t  =>  delta-v = {dv:.0f} m/s\n")

    target, isp, eps = 9400, 350, 0.10     # ~LEO delta-v, kerolox Isp, 10% structure
    print(f"  Goal: {target} m/s to orbit (Isp={isp}s, structural fraction {eps:.0%})\n")

    single = payload_fraction(target, isp, eps)
    print(f"  Single stage payload fraction: {single:+.3f}")
    print("    -> negative: impossible, the empty structure can't reach orbit\n")

    per_stage_dv = target / 2
    stage = payload_fraction(per_stage_dv, isp, eps)
    two_stage = stage ** 2
    print(f"  Two stages, {per_stage_dv:.0f} m/s each:")
    print(f"    per-stage payload fraction: {stage:.3f}")
    print(f"    overall payload fraction  : {two_stage:.3f}  ({two_stage:.1%})")
    print("\n  Staging turns an impossible mission into a feasible one.")
