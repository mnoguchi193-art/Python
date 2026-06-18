"""
Ensemble Forecasting — probabilistic prediction under chaos

Because a chaotic atmosphere amplifies any error (see lorenz_system.py), a single
"deterministic" forecast is fragile. Operational centers instead run an
*ensemble*: many forecasts from slightly perturbed initial states. Their spread
estimates the forecast uncertainty, the ensemble mean beats most single members,
and the fraction of members in a given state gives a calibrated probability.

This demo runs an ensemble on the Lorenz system and tracks spread vs skill.
"""

from __future__ import annotations

import random
from statistics import mean, pstdev

from lorenz_system import integrate, distance


def ensemble(initial: tuple[float, float, float], size: int, steps: int,
             dt: float = 0.01, noise: float = 1e-3, seed: int = 0
             ) -> list[list[tuple[float, float, float]]]:
    """Trajectories from `size` perturbed copies of the initial state."""
    rng = random.Random(seed)
    members = []
    for _ in range(size):
        start = tuple(c + rng.gauss(0, noise) for c in initial)
        members.append(integrate(start, steps, dt))
    return members


if __name__ == "__main__":
    dt, steps, size = 0.01, 3000, 50
    truth = integrate((2.0, 1.0, 1.0), steps, dt)
    members = ensemble((2.0, 1.0, 1.0), size, steps, dt)

    print(f"Ensemble forecast on the Lorenz system ({size} members)\n")
    print(f"  {'lead (t)':>8}  {'spread':>7}  {'mean error':>10}")
    for step in (0, 250, 500, 700, 800, 1000, 1500, 2500):
        states = [m[step] for m in members]
        cx = mean(s[0] for s in states)
        cy = mean(s[1] for s in states)
        cz = mean(s[2] for s in states)
        spread = mean(distance(s, (cx, cy, cz)) for s in states)
        mean_error = distance((cx, cy, cz), truth[step])
        print(f"  {step * dt:>8.1f}  {spread:>7.2f}  {mean_error:>10.2f}")

    # Probabilistic forecast: which wing of the attractor at a chosen lead time?
    lead = 1500
    p_positive = sum(1 for m in members if m[lead][0] > 0) / size
    print(f"\n  At lead t={lead * dt:.0f}: P(x > 0, the 'warm' regime) = "
          f"{p_positive:.0%}")
    print("\nSpread grows until it saturates at the attractor size — the point")
    print("where the ensemble can only give climatology, not a real forecast.")
