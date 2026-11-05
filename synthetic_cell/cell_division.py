"""
Cell Size Homeostasis (細胞サイズの恒常性) — the "adder" principle

A dividing synthetic cell must keep its size stable across generations.
Bacteria achieve this not by dividing at a fixed size ("sizer") nor after a
fixed time ("timer"), but by adding a roughly constant volume between birth
and division — the *adder* model (Amir 2014; Taheri-Araghi et al. 2015).

This Monte-Carlo model shows why adding a constant volume is self-correcting:
cells born too large or too small both relax toward the population mean
within a few generations, with no explicit size sensing.
"""

from __future__ import annotations
import random
import statistics


DELTA = 1.0          # mean volume added per cycle (the "adder" increment)
NOISE = 0.10         # CV of the added increment and of division symmetry


def simulate_lineage(birth_size: float, generations: int,
                     rng: random.Random) -> list[float]:
    """Follow one daughter per division; return birth size each generation."""
    sizes = [birth_size]
    size = birth_size
    for _ in range(generations):
        added = DELTA * (1 + rng.gauss(0, NOISE))
        division_size = size + max(added, 0.05)
        split = 0.5 * (1 + rng.gauss(0, NOISE))        # imperfect symmetry
        size = division_size * min(max(split, 0.1), 0.9)
        sizes.append(size)
    return sizes


def population(n_cells: int, generations: int, rng: random.Random
               ) -> list[list[float]]:
    starts = [0.2, 1.0, 3.0] * (n_cells // 3 + 1)
    return [simulate_lineage(starts[i], generations, rng) for i in range(n_cells)]


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    rng = random.Random(0)

    print("Adder model: each cycle adds ~constant volume, then divides in two.\n")
    print("Three lineages starting far from equilibrium (birth size over generations):")
    for start in [0.2, 1.0, 3.0]:
        sizes = simulate_lineage(start, 8, random.Random(int(start * 100)))
        track = "  ".join(f"{s:.2f}" for s in sizes)
        print(f"  start {start:4.2f}: {track}")
    print("  => large and small cells both converge toward the same size.\n")

    gens = 12
    pop = population(300, gens, rng)
    print(f"Population of {len(pop)} lineages, {gens} generations:")
    print("  gen   mean   stdev    CV")
    for g in [0, 1, 2, 4, 8, gens]:
        col = [lineage[g] for lineage in pop]
        mean = statistics.mean(col)
        sd = statistics.pstdev(col)
        print(f"  {g:3d}   {mean:.3f}  {sd:.3f}   {sd / mean:5.1%}")
    print(f"\n  The initial 3-fold spread in size collapses to a steady CV of"
          f" ~{sd / mean:.0%};")
    print("  adding a fixed volume (not dividing at a fixed size) is enough to")
    print("  stabilise cell size — homeostasis without a size sensor.")
