"""
Metabolism (代謝) — Michaelis-Menten enzyme kinetics in a minimal cell

Enzymes turn the saturating Michaelis-Menten rate law

    v = Vmax * S / (Km + S)

into the chemistry of life.  This module shows (1) a single enzymatic
reaction depleting its substrate over time, (2) the saturation curve that
makes enzymes behave like rate-limited valves, and (3) a two-step linear
pathway  S -> A -> B  reaching a steady-state flux set by its slowest step.

Integrated with RK4; standard library only.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

State = list[float]


@dataclass
class Enzyme:
    name: str
    vmax: float      # maximum rate (concentration / time)
    km: float        # substrate concentration at half Vmax

    def rate(self, substrate: float) -> float:
        return self.vmax * substrate / (self.km + substrate)


# ── Integrator ────────────────────────────────────────────────────────────
def rk4_step(f: Callable[[State], State], state: State, dt: float) -> State:
    k1 = f(state)
    k2 = f([s + dt / 2 * a for s, a in zip(state, k1)])
    k3 = f([s + dt / 2 * a for s, a in zip(state, k2)])
    k4 = f([s + dt * a for s, a in zip(state, k3)])
    return [s + dt / 6 * (a + 2 * b + 2 * c + d)
            for s, a, b, c, d in zip(state, k1, k2, k3, k4)]


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    e1 = Enzyme("E1", vmax=1.0, km=0.5)
    e2 = Enzyme("E2", vmax=0.4, km=0.2)   # slower -> rate-limiting

    # 1. Saturation curve: rate levels off as substrate rises.
    print(f"{e1.name}: Vmax={e1.vmax}, Km={e1.km}")
    print("  [S]     v        v/Vmax")
    for s in [0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0]:
        v = e1.rate(s)
        print(f"  {s:4.2f}   {v:.3f}    {v / e1.vmax:4.0%}")
    print(f"  (at [S]=Km={e1.km}, rate is exactly half of Vmax)\n")

    # 2. Single reaction S -> P depleting its substrate.
    def single(state: State) -> State:
        s, _p = state
        v = e1.rate(s)
        return [-v, v]
    s, p = 5.0, 0.0
    dt = 0.05
    print("Substrate depletion (S -> P):")
    for step in range(401):
        if step % 50 == 0:
            print(f"  t={step * dt:4.1f}   S={s:5.3f}   P={p:5.3f}")
        s, p = rk4_step(single, [s, p], dt)

    # 3. Linear pathway S -> A -> B with constant supply of S.
    supply = 0.3
    def pathway(state: State) -> State:
        s, a, _b = state
        v1 = e1.rate(s)
        v2 = e2.rate(a)
        return [supply - v1, v1 - v2, v2]
    state = [0.0, 0.0, 0.0]
    dt = 0.05
    for _ in range(4000):
        state = rk4_step(pathway, state, dt)
    s, a, _b = state
    print("\nPathway S -> A -> B at steady state "
          f"(constant supply {supply}/time):")
    print(f"  [S]={s:.3f}  [A]={a:.3f}")
    print(f"  flux through E1 = {e1.rate(s):.3f}, through E2 = {e2.rate(a):.3f}")
    print(f"  => flux converges to the supply rate; the slower enzyme E2 "
          f"(Vmax={e2.vmax}) sets the ceiling.")
