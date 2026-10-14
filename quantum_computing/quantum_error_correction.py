"""
Quantum Error Correction — protecting a qubit from noise

Qubits decohere, so fault-tolerant quantum computing depends on *error
correcting codes*: spread one logical qubit across several physical ones, measure
"stabilizers" that reveal an error without disturbing the stored state, and
correct it. This is exactly the frontier IBM's experimental Quantum Loon chip
pushes on — demonstrating the long-range couplers and qLDPC codes that make
error correction practical on the road to a fault-tolerant machine.

Here is the conceptual foundation: the 3-qubit bit-flip repetition code, which
detects and corrects any single bit-flip via two parity (stabilizer) checks.
Built on the state-vector simulator in qubit_simulator.py.
"""

from __future__ import annotations

from qubit_simulator import apply_cnot, apply_gate, X


def encode(alpha: float, beta: float) -> list[complex]:
    """Encode a|0> + b|1> into the codeword a|000> + b|111>."""
    state = [0j] * 8
    state[0] = alpha            # |000>
    state[1] = beta             # |001>  (logical state lives on qubit 0)
    state = apply_cnot(state, 0, 1)
    state = apply_cnot(state, 0, 2)
    return state


def syndrome(state: list[complex]) -> tuple[int, int]:
    """Measure the two parity stabilizers Z0Z1 and Z1Z2 (no state collapse here).

    For a codeword plus at most one bit-flip the parities are well defined,
    so we read them off the supported basis states.
    """
    for i, amp in enumerate(state):
        if abs(amp) > 1e-12:
            b0, b1, b2 = i & 1, (i >> 1) & 1, (i >> 2) & 1
            return b0 ^ b1, b1 ^ b2
    return 0, 0


def correct(state: list[complex]) -> tuple[list[complex], int]:
    """Diagnose the error from the syndrome and flip the affected qubit."""
    s = syndrome(state)
    location = {(0, 0): None, (1, 0): 0, (1, 1): 1, (0, 1): 2}[s]
    if location is not None:
        state = apply_gate(state, X, location)
    return state, (-1 if location is None else location)


if __name__ == "__main__":
    alpha, beta = 0.6, 0.8                      # logical state 0.6|0> + 0.8|1>
    encoded = encode(alpha, beta)

    print("3-qubit bit-flip code: logical 0.6|0> + 0.8|1>")
    print("Encoded as 0.6|000> + 0.8|111>\n")
    print(f"  {'injected error':>14}  {'syndrome':>9}  {'diagnosed':>10}  {'recovered':>10}")

    for err in (None, 0, 1, 2):
        noisy = encoded[:] if err is None else apply_gate(encoded[:], X, err)
        s = syndrome(noisy)
        fixed, location = correct(noisy)
        ok = all(abs(a - b) < 1e-9 for a, b in zip(fixed, encoded))
        diagnosed = "none" if location == -1 else f"qubit {location}"
        injected = "none" if err is None else f"qubit {err}"
        print(f"  {injected:>14}  {str(s):>9}  {diagnosed:>10}  "
              f"{'OK' if ok else 'FAIL':>10}")

    print("\nThe stabilizers pinpoint the flipped qubit without ever measuring")
    print("the logical state itself — every single bit-flip is corrected.")
