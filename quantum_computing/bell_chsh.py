"""
The CHSH Inequality — proving the world is not locally real

Bell's theorem (and the CHSH form of it) gives a number S that any theory based
on local hidden variables must keep at or below 2. Quantum mechanics, using an
entangled pair, reaches up to 2*sqrt(2) ~= 2.828. Experiments confirm the quantum
value — the discovery honoured by the 2022 Nobel Prize in Physics (Aspect,
Clauser, Zeilinger).

We compute S directly from quantum mechanics: the correlation of two spin
measurements at angles a, b on the Bell state |Phi+> is <Phi+| M(a) (x) M(b) |Phi+>.
"""

from __future__ import annotations

import math


PHI_PLUS = [1 / math.sqrt(2), 0, 0, 1 / math.sqrt(2)]   # (|00> + |11>)/sqrt(2)


def observable(theta: float) -> list[list[float]]:
    """A spin measurement along angle theta in the X-Z plane (eigenvalues +-1)."""
    c, s = math.cos(theta), math.sin(theta)
    return [[c, s], [s, -c]]


def kron(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[a[i // 2][j // 2] * b[i % 2][j % 2] for j in range(4)]
            for i in range(4)]


def expectation(state: list[float], m: list[list[float]]) -> float:
    return sum(state[i] * m[i][j] * state[j] for i in range(4) for j in range(4))


def correlation(a: float, b: float) -> float:
    return expectation(PHI_PLUS, kron(observable(a), observable(b)))


if __name__ == "__main__":
    # Optimal CHSH angles (in radians).
    a, a2 = math.radians(0), math.radians(90)
    b, b2 = math.radians(45), math.radians(135)

    e_ab = correlation(a, b)
    e_ab2 = correlation(a, b2)
    e_a2b = correlation(a2, b)
    e_a2b2 = correlation(a2, b2)
    S = e_ab - e_ab2 + e_a2b + e_a2b2

    print("CHSH inequality test on the Bell state\n")
    print(f"  E(a, b)   = {e_ab:+.3f}")
    print(f"  E(a, b')  = {e_ab2:+.3f}")
    print(f"  E(a', b)  = {e_a2b:+.3f}")
    print(f"  E(a', b') = {e_a2b2:+.3f}\n")
    print(f"  S = {S:.3f}")
    print(f"  classical (local-realist) bound : 2")
    print(f"  Tsirelson (quantum) bound       : {2 * math.sqrt(2):.3f}")
    print(f"\n  S > 2, so no local hidden-variable theory can explain it —")
    print("  entanglement produces correlations stronger than any classical model.")
