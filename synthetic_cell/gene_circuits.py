"""
Synthetic Gene Circuits (合成遺伝子回路) — the toggle switch and the
repressilator

Two foundational circuits of synthetic biology, both built from genes that
repress one another:

  * Toggle switch (Gardner et al., 2000) — two genes repressing each other.
    The system is *bistable*: it settles into one of two stable states and
    stays there, a one-bit cellular memory.
  * Repressilator (Elowitz & Leibler, 2000) — three genes in a repression
    cycle. No stable fixed point exists, so the concentrations *oscillate*,
    a synthetic clock.

Both are modelled with Hill-function repression and integrated with RK4
(standard library only).
"""

from __future__ import annotations
from typing import Callable

State = list[float]


# ── Integrator ────────────────────────────────────────────────────────────
def rk4_step(f: Callable[[State], State], state: State, dt: float) -> State:
    k1 = f(state)
    k2 = f([s + dt / 2 * a for s, a in zip(state, k1)])
    k3 = f([s + dt / 2 * a for s, a in zip(state, k2)])
    k4 = f([s + dt * a for s, a in zip(state, k3)])
    return [s + dt / 6 * (a + 2 * b + 2 * c + d)
            for s, a, b, c, d in zip(state, k1, k2, k3, k4)]


def integrate(f: Callable[[State], State], state: State, dt: float, steps: int
              ) -> list[State]:
    traj = [state]
    for _ in range(steps):
        state = rk4_step(f, state, dt)
        traj.append(state)
    return traj


# ── Toggle switch ─────────────────────────────────────────────────────────
def toggle(alpha: float = 4.0, n: float = 2.0) -> Callable[[State], State]:
    """du/dt = alpha/(1+v^n) - u ;  dv/dt = alpha/(1+u^n) - v."""
    def f(state: State) -> State:
        u, v = state
        return [alpha / (1 + v ** n) - u, alpha / (1 + u ** n) - v]
    return f


# ── Repressilator ─────────────────────────────────────────────────────────
def repressilator(alpha: float = 20.0, alpha0: float = 0.1, beta: float = 1.0,
                  n: float = 2.0) -> Callable[[State], State]:
    """Three genes i=0,1,2; gene i is repressed by protein i-1.
    state = [m0, m1, m2, p0, p1, p2] (mRNA then protein)."""
    def f(state: State) -> State:
        m, p = state[:3], state[3:]
        dm = [alpha / (1 + p[(i - 1) % 3] ** n) + alpha0 - m[i] for i in range(3)]
        dp = [beta * (m[i] - p[i]) for i in range(3)]
        return dm + dp
    return f


# ── Analysis helpers ──────────────────────────────────────────────────────
def peak_period(series: list[float], dt: float) -> float:
    """Mean spacing between successive local maxima in the second half."""
    start = len(series) // 2
    peaks = [i for i in range(start + 1, len(series) - 1)
             if series[i] > series[i - 1] and series[i] >= series[i + 1]]
    if len(peaks) < 2:
        return 0.0
    gaps = [(b - a) * dt for a, b in zip(peaks, peaks[1:])]
    return sum(gaps) / len(gaps)


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Toggle switch — same circuit, two initial conditions:")
    f = toggle()
    for u0, v0 in [(0.5, 0.1), (0.1, 0.5)]:
        final = integrate(f, [u0, v0], dt=0.02, steps=1500)[-1]
        winner = "gene U high" if final[0] > final[1] else "gene V high"
        print(f"  start (u,v)=({u0},{v0}) -> settles to "
              f"(u={final[0]:.2f}, v={final[1]:.2f})  [{winner}]")
    print("  => bistable: the starting state decides which gene wins (1-bit memory)\n")

    print("Repressilator — three repressing genes:")
    dt = 0.02
    traj = integrate(repressilator(), [0.2, 0.1, 0.3, 0.1, 0.4, 0.2], dt, steps=6000)
    p0 = [s[3] for s in traj]
    period = peak_period(p0, dt)
    lo, hi = min(p0[len(p0) // 2:]), max(p0[len(p0) // 2:])
    print(f"  protein 0 oscillates between {lo:.2f} and {hi:.2f}")
    print(f"  oscillation period ~= {period:.1f} (dimensionless time units)")

    print("\n  protein 0 over the last cycle:")
    span = int(period / dt)
    seg = p0[-span:] if span else p0[-100:]
    step = max(1, len(seg) // 20)
    for i in range(0, len(seg), step):
        bar = "#" * int(40 * (seg[i] - lo) / (hi - lo + 1e-12))
        print(f"    t={i * dt:5.1f} | {bar}")
