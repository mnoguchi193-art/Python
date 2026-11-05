"""
Inverse Design (逆設計) — searching for a material that has a target property

  forward problem:  structure  ->  property   (what simulators compute)
  inverse problem:  property   ->  structure  (what designers actually want)

AI for Science turns the inverse problem into an optimisation over a cheap
forward model.  Here a toy "alloy" is a composition vector over five
elements; a nonlinear forward model gives its band gap, density and cost.
An evolutionary algorithm searches for compositions that hit a target band
gap while staying light and cheap, and is compared with random search at
the same evaluation budget.
"""

from __future__ import annotations
import random

ELEMENTS = ["A", "B", "C", "D", "E"]
GAP      = [0.4, 1.1, 2.3, 3.2, 0.9]    # eV, pure-element band gaps
DENSITY  = [2.3, 5.3, 4.1, 7.8, 3.0]    # g/cm^3
COST     = [1.0, 3.5, 2.0, 12.0, 0.8]   # relative $/kg
# Bowing parameters: mixing two elements lowers the gap below the linear
# interpolation (a real effect in semiconductor alloys).
BOWING   = {(0, 1): 0.6, (0, 2): 1.2, (1, 2): 0.3, (1, 3): 0.9, (2, 3): 0.5,
            (0, 4): 0.2, (3, 4): 1.5}

Composition = list[float]   # fractions summing to 1


# ── Forward model: composition -> properties ──────────────────────────────
def band_gap(c: Composition) -> float:
    linear = sum(ci * gi for ci, gi in zip(c, GAP))
    bowing = sum(b * c[i] * c[j] for (i, j), b in BOWING.items())
    return linear - bowing


def density(c: Composition) -> float:
    return sum(ci * di for ci, di in zip(c, DENSITY))


def cost(c: Composition) -> float:
    return sum(ci * ki for ci, ki in zip(c, COST))


# ── Design objective (lower is better) ────────────────────────────────────
TARGET_GAP = 1.5          # eV, e.g. for a tandem solar cell top layer
MAX_RARE   = 0.10         # element D is scarce: at most 10 % of the alloy


def objective(c: Composition) -> float:
    penalty = 100.0 * max(0.0, c[3] - MAX_RARE)
    return 10.0 * abs(band_gap(c) - TARGET_GAP) + 0.05 * density(c) + 0.1 * cost(c) + penalty


# ── Evolutionary search over the composition simplex ──────────────────────
def normalize(c: Composition) -> Composition:
    c = [max(ci, 0.0) for ci in c]
    total = sum(c) or 1.0
    return [ci / total for ci in c]


def random_composition(rng: random.Random) -> Composition:
    return normalize([rng.random() for _ in ELEMENTS])


def mutate(c: Composition, rng: random.Random, sigma: float = 0.08) -> Composition:
    return normalize([ci + rng.gauss(0, sigma) for ci in c])


def crossover(a: Composition, b: Composition, rng: random.Random) -> Composition:
    w = rng.random()
    return normalize([w * ai + (1 - w) * bi for ai, bi in zip(a, b)])


def evolve(generations: int, pop_size: int, rng: random.Random) -> tuple[Composition, int]:
    """Return the best composition and the number of forward evaluations."""
    pop = [random_composition(rng) for _ in range(pop_size)]
    scores = [objective(c) for c in pop]
    evals = pop_size
    for _ in range(generations):
        order = sorted(range(pop_size), key=scores.__getitem__)
        elite = [pop[i] for i in order[: pop_size // 4]]
        children = []
        while len(children) < pop_size - len(elite):
            p1, p2 = rng.choice(elite), rng.choice(elite)
            children.append(mutate(crossover(p1, p2, rng), rng))
        pop = elite + children
        scores = [objective(c) for c in pop]
        evals += len(children)
    best = min(range(pop_size), key=scores.__getitem__)
    return pop[best], evals


def random_search(evals: int, rng: random.Random) -> Composition:
    return min((random_composition(rng) for _ in range(evals)), key=objective)


def describe(label: str, c: Composition) -> None:
    comp = "  ".join(f"{e}={ci:.2f}" for e, ci in zip(ELEMENTS, c))
    print(f"{label}\n  {comp}")
    print(f"  gap={band_gap(c):.3f} eV  density={density(c):.2f}  cost={cost(c):.2f}"
          f"  objective={objective(c):.3f}")


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    rng = random.Random(3)
    print(f"Target: band gap {TARGET_GAP} eV, element D <= {MAX_RARE:.0%}, light and cheap\n")

    best, evals = evolve(generations=40, pop_size=40, rng=rng)
    describe(f"Evolutionary search ({evals} forward evaluations):", best)

    print()
    describe(f"Random search (same {evals} evaluations):", random_search(evals, random.Random(3)))

    print("\nNote: the forward model is cheap here, but the same loop works when")
    print("      'band_gap' is a DFT code or a trained surrogate (see surrogate_model.py).")
