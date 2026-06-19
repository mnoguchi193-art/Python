"""
Opinion Dynamics — the Hegselmann-Krause bounded-confidence model

A cornerstone of computational political science / sociophysics: how do
opinions in a population polarize, fragment, or reach consensus?

Each agent holds an opinion in [0, 1]. On every step an agent moves to the
*average* opinion of everyone within its confidence radius `epsilon` — it only
listens to people it already broadly agrees with. Large epsilon -> consensus;
small epsilon -> several stable, polarized clusters.
"""

from __future__ import annotations

import random
from statistics import mean


def step(opinions: list[float], epsilon: float) -> list[float]:
    """One synchronous update of all agents."""
    updated = []
    for x in opinions:
        neighbors = [y for y in opinions if abs(y - x) <= epsilon]
        updated.append(mean(neighbors))
    return updated


def simulate(
    opinions: list[float],
    epsilon: float,
    max_steps: int = 100,
    tol: float = 1e-6,
) -> tuple[list[float], int]:
    """Run until opinions stop moving. Returns (final opinions, steps taken)."""
    for t in range(1, max_steps + 1):
        nxt = step(opinions, epsilon)
        if max(abs(a - b) for a, b in zip(nxt, opinions)) < tol:
            return nxt, t
        opinions = nxt
    return opinions, max_steps


def clusters(opinions: list[float], tol: float = 1e-3) -> list[float]:
    """Collapse converged opinions into distinct cluster centers."""
    centers: list[float] = []
    for x in sorted(opinions):
        if not centers or abs(x - centers[-1]) > tol:
            centers.append(x)
    return centers


if __name__ == "__main__":
    random.seed(42)
    population = [random.random() for _ in range(60)]

    print("Hegselmann-Krause bounded-confidence model (60 agents)\n")
    print(f"{'epsilon':>8}  {'steps':>5}  {'#clusters':>9}  cluster centers")
    for epsilon in (0.05, 0.15, 0.25, 0.40):
        final, steps = simulate(list(population), epsilon)
        centers = clusters(final)
        pretty = ", ".join(f"{c:.2f}" for c in centers)
        print(f"{epsilon:8.2f}  {steps:5d}  {len(centers):9d}  {pretty}")

    print(
        "\nSmaller confidence radii leave society fragmented into rival camps;"
        "\na wide enough radius pulls everyone into a single consensus."
    )
