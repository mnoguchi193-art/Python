"""
The Error-Correction Threshold — why more qubits can mean fewer errors

Google Quantum AI's Willow chip (2024) demonstrated *below-threshold* quantum
error correction: as they grew the surface code from distance 3 to 5 to 7, the
logical error rate fell by roughly half at each step. That was the long-sought
crossover — proof that adding physical qubits makes a logical qubit *better*, not
worse, the essential precondition for a scalable fault-tolerant machine.

The same threshold behaviour appears in the simplest code, the distance-d
repetition code with majority-vote decoding: a logical error happens only if more
than half of the d physical bits flip, an exact binomial tail.

  below threshold (p < p_th): logical error shrinks exponentially with distance
  above threshold (p > p_th): logical error grows with distance
"""

from __future__ import annotations

from math import comb


def logical_error_rate(p: float, distance: int) -> float:
    """Probability a distance-d repetition code fails (majority of bits flip)."""
    need = distance // 2 + 1
    return sum(comb(distance, k) * p ** k * (1 - p) ** (distance - k)
               for k in range(need, distance + 1))


if __name__ == "__main__":
    distances = [3, 5, 7, 9, 11]
    rates = [0.05, 0.10, 0.20, 0.40, 0.50, 0.60]
    threshold = 0.50   # exact threshold of the repetition code

    print("Logical error rate vs code distance (repetition code, p_th = 0.50)\n")
    header = "  phys p  " + "".join(f"  d={d:<8}" for d in distances)
    print(header)
    for p in rates:
        row = "".join(f"  {logical_error_rate(p, d):<8.1e}" for d in distances)
        regime = "below" if p < threshold else "above" if p > threshold else "at"
        print(f"  {p:<6.2f} {row}  ({regime} threshold)")

    print("\nError suppression per +2 distance, below threshold (p = 0.10):")
    for d in (3, 5, 7, 9):
        lo = logical_error_rate(0.10, d)
        hi = logical_error_rate(0.10, d + 2)
        print(f"  d={d} -> d={d + 2}:  {lo:.2e} -> {hi:.2e}   "
              f"(suppressed {lo / hi:.0f}x)")

    print("\n  Below threshold, each step up in distance suppresses errors")
    print("  exponentially — exactly the scaling Willow demonstrated.")
    print("  Above threshold (p=0.60) the opposite holds: bigger codes are worse.")
