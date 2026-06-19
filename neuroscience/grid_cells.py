"""
Grid Cells — the brain's coordinate system

Grid cells in the entorhinal cortex fire whenever an animal is at any vertex of a
regular triangular lattice tiling its environment — a periodic "map" of space that
won the 2014 Nobel Prize (the Mosers; with O'Keefe's place cells). The hexagonal
firing pattern emerges from summing three plane waves oriented 60 degrees apart:

    rate(r) ~ sum over 3 directions of cos(k . r)

This module computes a grid cell's firing map over a 2D arena and renders it.
"""

from __future__ import annotations

import math


def grid_rate(x: float, y: float, spacing: float = 0.4,
              orientation: float = 0.0, phase: tuple[float, float] = (0.0, 0.0)
              ) -> float:
    """Firing rate (0..1) of a grid cell at position (x, y)."""
    k = 4 * math.pi / (math.sqrt(3) * spacing)
    total = 0.0
    for i in range(3):
        theta = orientation + i * math.pi / 3
        kx, ky = k * math.cos(theta), k * math.sin(theta)
        total += math.cos(kx * (x - phase[0]) + ky * (y - phase[1]))
    return max(0.0, (total + 1.5) / 4.5)        # normalize to [0, 1], rectify


def render(width: int = 60, height: int = 24, spacing: float = 0.45) -> str:
    palette = " .:-=+*#%@"
    lines = []
    for row in range(height):
        y = row / (height - 1)
        line = []
        for col in range(width):
            x = col / (width - 1) * 2          # arena wider than tall
            r = grid_rate(x, y, spacing)
            line.append(palette[min(len(palette) - 1, int(r * (len(palette) - 1)))])
        lines.append("".join(line))
    return "\n".join(lines)


if __name__ == "__main__":
    print("Grid cell firing map over a 2D arena (hexagonal lattice)\n")
    print(render())

    print("\n  Firing at sample positions (peaks at lattice vertices):")
    for x, y in [(0.0, 0.0), (0.2, 0.2), (0.45, 0.0), (0.9, 0.0)]:
        print(f"    ({x:.2f}, {y:.2f}) -> rate {grid_rate(x, y):.2f}")

    print("\n  Three plane waves 60 deg apart make a hexagonal code for space —")
    print("  a periodic neural coordinate system for navigation.")
