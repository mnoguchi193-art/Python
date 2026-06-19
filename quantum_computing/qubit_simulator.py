"""
Quantum State-Vector Simulator — qubits, gates, and entanglement

A qubit is not a 0 or 1 but a complex superposition of both; n qubits live in a
2**n-dimensional state vector. Gates are unitary matrices that rotate it. This
pure-Python simulator builds the canonical example of quantum weirdness — a Bell
state, where two qubits become *entangled* so that measuring one instantly fixes
the other, with no classical counterpart.
"""

from __future__ import annotations

import cmath
import math
import random


H = [[1 / math.sqrt(2), 1 / math.sqrt(2)],
     [1 / math.sqrt(2), -1 / math.sqrt(2)]]
X = [[0, 1], [1, 0]]
Z = [[1, 0], [0, -1]]


def zero_state(n: int) -> list[complex]:
    state = [0j] * (2 ** n)
    state[0] = 1 + 0j
    return state


def apply_gate(state: list[complex], gate, target: int) -> list[complex]:
    """Apply a single-qubit gate to `target` qubit (bit 0 = least significant)."""
    new = state[:]
    for i in range(len(state)):
        if (i >> target) & 1 == 0:
            j = i | (1 << target)
            a0, a1 = state[i], state[j]
            new[i] = gate[0][0] * a0 + gate[0][1] * a1
            new[j] = gate[1][0] * a0 + gate[1][1] * a1
    return new


def apply_cnot(state: list[complex], control: int, target: int) -> list[complex]:
    new = state[:]
    for i in range(len(state)):
        if (i >> control) & 1:
            new[i] = state[i ^ (1 << target)]
    return new


def probabilities(state: list[complex]) -> list[float]:
    return [abs(a) ** 2 for a in state]


def measure(state: list[complex], shots: int = 1000, seed: int = 0
            ) -> dict[str, int]:
    n = int(math.log2(len(state)))
    rng = random.Random(seed)
    outcomes = rng.choices(range(len(state)), weights=probabilities(state),
                           k=shots)
    counts: dict[str, int] = {}
    for o in outcomes:
        label = format(o, f"0{n}b")
        counts[label] = counts.get(label, 0) + 1
    return dict(sorted(counts.items()))


if __name__ == "__main__":
    # Build a Bell state: H on qubit 0, then CNOT(0 -> 1).
    state = zero_state(2)
    state = apply_gate(state, H, 0)
    state = apply_cnot(state, 0, 1)

    print("Bell state  (|00> + |11>) / sqrt(2)\n")
    for i, amp in enumerate(state):
        if abs(amp) > 1e-9:
            print(f"  |{format(i, '02b')}>: amplitude {amp.real:+.3f}  "
                  f"probability {abs(amp) ** 2:.2f}")

    print(f"\n  1000 measurements: {measure(state)}")
    print("  Only 00 and 11 ever appear — the qubits are perfectly correlated")
    print("  (entangled): measuring one determines the other.")
