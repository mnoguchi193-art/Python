"""
The Kuramoto Model — how brain rhythms synchronize

Neural populations oscillate, and cognition depends on them falling into and out
of synchrony (gamma, theta rhythms). The Kuramoto model is the canonical account:
many oscillators, each with its own natural frequency, nudge one another toward a
common phase. Below a critical coupling they drift incoherently; above it they
spontaneously lock — a phase transition to collective rhythm.

    d(phase_i)/dt = omega_i + (K/N) * sum_j sin(phase_j - phase_i)

The order parameter r (0 = incoherent, 1 = fully synchronized) measures it.
"""

from __future__ import annotations

import cmath
import math
import random


def order_parameter(phases: list[float]) -> float:
    """Synchrony r = |mean of e^{i*phase}|."""
    return abs(sum(cmath.exp(1j * p) for p in phases) / len(phases))


def simulate(coupling: float, n: int = 60, dt: float = 0.05, steps: int = 2000,
             seed: int = 0) -> float:
    """Mean order parameter over the last steps for a given coupling K."""
    rng = random.Random(seed)
    omega = [rng.gauss(0, 1) for _ in range(n)]
    phases = [rng.uniform(0, 2 * math.pi) for _ in range(n)]
    tail = []
    for step in range(steps):
        new = []
        for i in range(n):
            coupling_term = sum(math.sin(phases[j] - phases[i]) for j in range(n))
            new.append(phases[i] + dt * (omega[i] + coupling / n * coupling_term))
        phases = new
        if step > steps - 200:
            tail.append(order_parameter(phases))
    return sum(tail) / len(tail)


if __name__ == "__main__":
    print("Kuramoto model — synchronization of 60 coupled oscillators\n")
    print(f"  Gaussian natural frequencies => critical coupling Kc ~ 1.6\n")
    print(f"  {'coupling K':>10}  {'order r':>8}  state")
    for k in (0.5, 1.0, 1.6, 2.0, 3.0, 5.0):
        r = simulate(k)
        bar = "#" * round(r * 20)
        state = "synchronized" if r > 0.7 else "partial" if r > 0.3 else "incoherent"
        print(f"  {k:>10.1f}  {r:>8.2f}  {state:<13} {bar}")

    print("\n  Past the critical coupling the oscillators lock into a common")
    print("  rhythm — the mechanism behind large-scale brain synchrony.")
