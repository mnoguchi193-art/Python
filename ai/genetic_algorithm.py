"""
Genetic algorithm — evolution as a general-purpose optimizer
（遺伝的アルゴリズム: 勾配が使えないときの最適化）

Gradient descent needs a differentiable landscape; Q-learning needs a reward
signal per step. A genetic algorithm (GA) needs neither — only a way to
*score* a complete candidate solution. It keeps a population of candidates
and repeats nature's loop:

    evaluate → select the fit → recombine (crossover) → perturb (mutation)

In AGI research this family matters because it optimizes things gradients
cannot reach: discrete structures, program-like genomes, even the
architecture of a neural network itself (neuroevolution, NEAT).

Three demos below share one generic engine:

1. evolve a target string   — the mechanics, visible generation by generation
2. 0/1 knapsack             — a classic NP-hard problem, checked against the
                              exact dynamic-programming optimum
3. maze policy evolution    — gradient-free search over action sequences for
                              the grid world from ai/agi_demo.py
"""

from __future__ import annotations

import random
import string
from typing import Callable, Optional, TypeVar

from agi_demo import GridWorld

T = TypeVar("T")

# ── The engine ────────────────────────────────────────────────────────────


def evolve(
    population: list[T],
    fitness: Callable[[T], float],
    crossover: Callable[[T, T], T],
    mutate: Callable[[T], T],
    *,
    generations: int = 100,
    elite: int = 2,
    tournament_k: int = 3,
    target_fitness: Optional[float] = None,
    rng: Optional[random.Random] = None,
    report: Optional[Callable[[int, float, T], None]] = None,
) -> tuple[T, float, int]:
    """Run a genetic algorithm; return (best individual, fitness, generations).

    - selection:  tournament — pick `tournament_k` at random, the fittest wins;
                  gentle pressure that never lets one lucky genome take over
    - elitism:    the best `elite` individuals survive unchanged, so the best
                  score can never get worse between generations
    - early stop: quits as soon as `target_fitness` is reached, if given
    """
    rng = rng or random.Random()

    def tournament(scored: list[tuple[float, T]]) -> T:
        contenders = rng.sample(scored, tournament_k)
        return max(contenders, key=lambda pair: pair[0])[1]

    scored = [(fitness(ind), ind) for ind in population]
    for generation in range(1, generations + 1):
        scored.sort(key=lambda pair: pair[0], reverse=True)
        best_fit, best = scored[0]
        if report:
            report(generation, best_fit, best)
        if target_fitness is not None and best_fit >= target_fitness:
            return best, best_fit, generation

        next_population = [ind for _, ind in scored[:elite]]
        while len(next_population) < len(population):
            child = mutate(crossover(tournament(scored), tournament(scored)))
            next_population.append(child)
        scored = [(fitness(ind), ind) for ind in next_population]

    scored.sort(key=lambda pair: pair[0], reverse=True)
    best_fit, best = scored[0]
    return best, best_fit, generations


# ── Demo 1: evolving a target string ──────────────────────────────────────


def string_demo(rng: random.Random) -> None:
    target = "EVOLUTION IS OPTIMIZATION"
    charset = string.ascii_uppercase + " "

    def fitness(text: str) -> float:
        return sum(a == b for a, b in zip(text, target))

    def crossover(p1: str, p2: str) -> str:
        # uniform crossover: each character comes from either parent
        return "".join(rng.choice(pair) for pair in zip(p1, p2))

    def mutate(text: str) -> str:
        return "".join(
            rng.choice(charset) if rng.random() < 0.02 else ch for ch in text
        )

    population = [
        "".join(rng.choice(charset) for _ in target) for _ in range(200)
    ]
    checkpoints = {1, 5, 10, 15, 40, 80}

    def report(generation: int, best_fit: float, best: str) -> None:
        if generation in checkpoints:
            print(f"  gen {generation:>3}: {best_fit:>4.0f}/{len(target)}  '{best}'")

    best, best_fit, gens = evolve(
        population, fitness, crossover, mutate,
        generations=300, target_fitness=len(target), rng=rng, report=report,
    )
    print(f"  gen {gens:>3}: {best_fit:>4.0f}/{len(target)}  '{best}'  <- done")


# ── Demo 2: 0/1 knapsack ──────────────────────────────────────────────────

Item = tuple[int, int]  # (weight, value)


def knapsack_optimum(items: list[Item], capacity: int) -> int:
    """Exact optimum by dynamic programming, for checking the GA's answer."""
    best_value = [0] * (capacity + 1)
    for weight, value in items:
        for cap in range(capacity, weight - 1, -1):
            best_value[cap] = max(best_value[cap], best_value[cap - weight] + value)
    return best_value[capacity]


def knapsack_demo(rng: random.Random) -> None:
    items: list[Item] = [(rng.randint(1, 10), rng.randint(1, 20)) for _ in range(15)]
    capacity = 30

    def fitness(genome: tuple[int, ...]) -> float:
        weight = sum(w for bit, (w, _) in zip(genome, items) if bit)
        value = sum(v for bit, (_, v) in zip(genome, items) if bit)
        # overweight solutions score negative — evolution weeds them out
        return value if weight <= capacity else capacity - weight

    def crossover(p1: tuple[int, ...], p2: tuple[int, ...]) -> tuple[int, ...]:
        cut = rng.randrange(1, len(p1))
        return p1[:cut] + p2[cut:]

    def mutate(genome: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(
            1 - bit if rng.random() < 1 / len(genome) else bit for bit in genome
        )

    population = [
        tuple(rng.randint(0, 1) for _ in items) for _ in range(100)
    ]
    optimum = knapsack_optimum(items, capacity)
    best, best_fit, gens = evolve(
        population, fitness, crossover, mutate,
        generations=200, target_fitness=optimum, rng=rng,
    )
    chosen = [i for i, bit in enumerate(best) if bit]
    weight = sum(items[i][0] for i in chosen)
    print(f"  15 items, capacity {capacity}; exact optimum (DP) = {optimum}")
    print(f"  GA found value {best_fit:.0f} in {gens} generations "
          f"(weight {weight}/{capacity}, items {chosen})")


# ── Demo 3: evolving a maze policy ────────────────────────────────────────


def maze_demo(rng: random.Random) -> None:
    world = GridWorld()
    actions = list(world.ACTIONS)
    genome_length = 20  # long enough for any route in this maze

    def simulate(genome: tuple[str, ...]) -> tuple[float, list]:
        state = world.start
        path = [state]
        for step, action in enumerate(genome, start=1):
            state, _, done = world.step(state, action)
            path.append(state)
            if done:
                return 100.0 - step, path  # reached the goal: fewer steps = fitter
        gr, gc = world.goal
        return -(abs(state[0] - gr) + abs(state[1] - gc)), path

    def fitness(genome: tuple[str, ...]) -> float:
        return simulate(genome)[0]

    def crossover(p1: tuple[str, ...], p2: tuple[str, ...]) -> tuple[str, ...]:
        cut = rng.randrange(1, len(p1))
        return p1[:cut] + p2[cut:]

    def mutate(genome: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(
            rng.choice(actions) if rng.random() < 0.05 else action
            for action in genome
        )

    population = [
        tuple(rng.choice(actions) for _ in range(genome_length))
        for _ in range(150)
    ]
    # optimal route is 8 steps (see a_star in agi_demo) → fitness 92
    best, best_fit, gens = evolve(
        population, fitness, crossover, mutate,
        generations=100, target_fitness=92.0, rng=rng,
    )
    _, path = simulate(best)
    steps = len(path) - 1 if best_fit > 0 else genome_length
    print(f"  no gradients, no reward-per-step — just 'did the sequence work?'")
    print(f"  evolved a {steps}-step route in {gens} generations "
          f"(fitness {best_fit:.0f}):")
    print("  " + world.render(path).replace("\n", "\n  "))


# ── Demo ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("── 1. Evolving a string toward a target ──")
    string_demo(random.Random(7))

    print("\n── 2. 0/1 knapsack vs the exact optimum ──")
    knapsack_demo(random.Random(11))

    print("\n── 3. Evolving a maze policy (gradient-free) ──")
    maze_demo(random.Random(9))
