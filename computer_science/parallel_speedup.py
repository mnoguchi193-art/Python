"""
Parallel Speedup — Amdahl's and Gustafson's laws

A many-core CPU like NVIDIA's Vera (~88 custom Arm cores) only helps to the extent
that work can run in parallel. Amdahl's law gives the cold truth for a fixed
problem: if a fraction p is parallelizable, speedup is capped at 1/(1-p) no matter
how many cores you add — the serial part dominates at scale. Gustafson's law is
the optimistic counterpart: if you grow the problem with the cores, speedup scales
almost linearly. Both shape how real software uses many-core hardware.
"""

from __future__ import annotations


def amdahl(parallel_fraction: float, cores: int) -> float:
    """Speedup for a FIXED problem with `cores` processors."""
    return 1.0 / ((1 - parallel_fraction) + parallel_fraction / cores)


def amdahl_limit(parallel_fraction: float) -> float:
    """Maximum speedup as cores -> infinity."""
    return float("inf") if parallel_fraction >= 1 else 1.0 / (1 - parallel_fraction)


def gustafson(parallel_fraction: float, cores: int) -> float:
    """Scaled speedup when the problem GROWS with the number of cores."""
    return (1 - parallel_fraction) + parallel_fraction * cores


if __name__ == "__main__":
    cores_list = [1, 8, 22, 44, 88]
    fractions = [0.50, 0.90, 0.95, 0.99]

    print("Amdahl's law — speedup on a fixed problem (up to 88 cores)\n")
    print("  parallel%   " + "".join(f"{c:>7}c" for c in cores_list) + f"{'limit':>9}")
    for p in fractions:
        row = "".join(f"{amdahl(p, c):>8.1f}" for c in cores_list)
        print(f"  {p:>8.0%}   {row}  {amdahl_limit(p):>8.1f}")

    print("\n  Even 99% parallel code caps at ~100x — the serial 1% is the wall.")
    print(f"  Efficiency at 88 cores (99% parallel): "
          f"{amdahl(0.99, 88) / 88:.0%} of ideal\n")

    print("Gustafson's law — scaled speedup when the problem grows with cores:")
    print("  parallel%   " + "".join(f"{c:>7}c" for c in cores_list))
    for p in fractions:
        row = "".join(f"{gustafson(p, c):>8.1f}" for c in cores_list)
        print(f"  {p:>8.0%}   {row}")
    print("\n  Fixed work hits Amdahl's wall; bigger work scales with the cores —")
    print("  which is why HPC tackles ever-larger problems on ever-more cores.")
