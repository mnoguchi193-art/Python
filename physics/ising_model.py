"""
The Ising Model — a phase transition from first principles

The canonical model of statistical physics, solved here by Metropolis Monte
Carlo. Spins on a lattice prefer to align with their neighbours, but temperature
randomizes them. Below a critical temperature (Tc ~= 2.27 for the 2D square
lattice) the system spontaneously magnetizes into order; above it, thermal noise
wins and the magnetization collapses — emergent collective behaviour and a sharp
phase transition arising from a simple local rule.
"""

from __future__ import annotations

import math
import random


def simulate(size: int, temperature: float, sweeps: int = 800,
             equilibrate: int = 400, seed: int = 0) -> float:
    """Return the mean magnetization per spin |M| at a given temperature."""
    rng = random.Random(seed)
    lattice = [[rng.choice((-1, 1)) for _ in range(size)] for _ in range(size)]
    # Precompute Boltzmann acceptance factors for the possible positive dE.
    boltz = {dE: math.exp(-dE / temperature) for dE in (4, 8)}

    def sweep():
        for _ in range(size * size):
            i, j = rng.randrange(size), rng.randrange(size)
            s = lattice[i][j]
            neighbors = (lattice[(i + 1) % size][j] + lattice[(i - 1) % size][j]
                         + lattice[i][(j + 1) % size] + lattice[i][(j - 1) % size])
            dE = 2 * s * neighbors
            if dE <= 0 or rng.random() < boltz[dE]:
                lattice[i][j] = -s

    for _ in range(equilibrate):
        sweep()
    total = 0.0
    for _ in range(sweeps):
        sweep()
        total += abs(sum(sum(row) for row in lattice))
    return total / sweeps / (size * size)


if __name__ == "__main__":
    size = 16
    print(f"2D Ising model ({size}x{size}), Metropolis Monte Carlo\n")
    print("  critical temperature Tc ~= 2.27\n")
    print(f"  {'T':>5}  {'|magnetization|':>15}  {'phase':>12}")
    for t in (1.0, 1.5, 2.0, 2.27, 2.5, 3.0, 4.0):
        m = simulate(size, t)
        bar = "#" * round(m * 20)
        phase = "ordered" if m > 0.5 else "disordered"
        print(f"  {t:>5.2f}  {m:>15.3f}  {phase:>12}  {bar}")
    print("\n  Magnetization collapses as temperature crosses Tc — a phase")
    print("  transition emerging purely from spins aligning with neighbours.")
