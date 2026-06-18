"""
Population Genetics — how allele frequencies evolve

The mathematics of evolution. The Hardy-Weinberg principle predicts genotype
frequencies from allele frequencies in an idealized, infinite population. Real,
finite populations also feel *genetic drift* — random sampling each generation,
modeled by Wright-Fisher — which can fix or eliminate an allele purely by chance,
while natural selection biases the outcome.
"""

from __future__ import annotations

import random


def hardy_weinberg(p: float) -> dict[str, float]:
    """Genotype frequencies for allele frequency p (q = 1 - p)."""
    q = 1 - p
    return {"AA": p * p, "Aa": 2 * p * q, "aa": q * q}


def wright_fisher(p0: float, pop_size: int, generations: int,
                  selection: float = 0.0, rng: random.Random | None = None
                  ) -> list[float]:
    """Simulate allele-frequency drift (with optional selection). Returns trajectory."""
    rng = rng or random.Random()
    p = p0
    trajectory = [p]
    for _ in range(generations):
        # Selection biases the expected frequency before random sampling.
        weighted = p * (1 + selection) / (p * (1 + selection) + (1 - p))
        # Drift: draw 2N alleles (diploid) from the weighted frequency.
        copies = sum(1 for _ in range(2 * pop_size) if rng.random() < weighted)
        p = copies / (2 * pop_size)
        trajectory.append(p)
        if p in (0.0, 1.0):                       # fixed or lost
            break
    return trajectory


if __name__ == "__main__":
    print("Hardy-Weinberg genotype frequencies (p = 0.7):")
    for genotype, freq in hardy_weinberg(0.7).items():
        print(f"  {genotype}: {freq:.3f}")
    print("  (sum to 1.0; this is the no-evolution baseline)\n")

    rng = random.Random(3)
    print("Genetic drift in a small population (N=25, start p=0.5):")
    outcomes = {"fixed": 0, "lost": 0, "ongoing": 0}
    for run in range(10):
        traj = wright_fisher(0.5, 25, 200, rng=rng)
        end = traj[-1]
        result = "fixed" if end == 1.0 else "lost" if end == 0.0 else "ongoing"
        outcomes[result] += 1
        print(f"  run {run + 1:>2}: ended p={end:.2f} after "
              f"{len(traj) - 1:>3} generations ({result})")
    print(f"  summary: {outcomes}  -> drift alone fixes or loses alleles\n")

    print("Natural selection (N=200, start p=0.05, +10% advantage):")
    traj = wright_fisher(0.05, 200, 120, selection=0.1, rng=rng)
    print(f"  p: {traj[0]:.2f} -> {traj[len(traj)//2]:.2f} -> {traj[-1]:.2f}")
    print("  A favored allele sweeps toward fixation despite drift.")
