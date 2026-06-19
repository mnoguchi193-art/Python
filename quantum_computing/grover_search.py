"""
Grover's Algorithm — quantum search with a quadratic speedup

To find one marked item among N unsorted items, a classical search needs ~N/2
queries on average. Grover's quantum algorithm needs only ~(pi/4)*sqrt(N). It
starts in an equal superposition of all items, then repeatedly (1) flips the
phase of the marked item with an oracle and (2) reflects every amplitude about
their mean ("inversion about the mean"). Each round rotates probability toward
the answer, which a final measurement then reveals.

Amplitudes stay real here, so we track them directly.
"""

from __future__ import annotations

import math


def grover(n_qubits: int, marked: int) -> tuple[list[float], int]:
    """Search 2**n_qubits items for `marked`. Returns (probabilities, iterations)."""
    size = 2 ** n_qubits
    amp = [1 / math.sqrt(size)] * size
    iterations = round(math.pi / 4 * math.sqrt(size))
    for _ in range(iterations):
        amp[marked] = -amp[marked]                 # oracle: phase-flip the answer
        mean = sum(amp) / size
        amp = [2 * mean - a for a in amp]          # inversion about the mean
    return [a * a for a in amp], iterations


if __name__ == "__main__":
    n, marked = 4, 11                              # 16 items, answer = item 11
    size = 2 ** n

    amp0 = 1 / size
    print(f"Grover's search: {size} items, looking for item {marked}\n")
    print(f"  initial probability of the answer: {amp0:.4f} (uniform)")

    probs, iterations = grover(n, marked)
    print(f"  Grover iterations (queries)      : {iterations}")
    print(f"  classical average queries        : {size // 2}")
    print(f"  probability of the answer after  : {probs[marked]:.4f}")

    best = max(range(size), key=lambda i: probs[i])
    print(f"\n  most probable measurement: item {best} "
          f"({'correct' if best == marked else 'wrong'})")
    print("  A quadratic speedup — the heart of quantum search.")
