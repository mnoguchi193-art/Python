"""
Spin-1/2 as a two-state quantum system — Stern-Gerlach in pure Python
（スピン1/2の量子ビット: 標準ライブラリの complex 型だけで量子測定を再現）

A spin-1/2 particle (an electron) is the simplest non-trivial quantum
system: its state lives in a 2-dimensional complex vector space, so it
needs nothing but Python's built-in `complex`. This module builds that
system from scratch and uses it to demonstrate the genuinely quantum
features of spin:

1. MEASUREMENT IS QUANTIZED  a Stern-Gerlach magnet along any axis yields
   only two outcomes (+ / -), never a continuum — the 1922 experiment
2. MEASUREMENT DISTURBS       measuring along z, then x, then z again shows
   the second measurement has erased the first (non-commuting observables)
3. THE cos²(θ/2) LAW          the probability of "up" along an axis tilted
   by angle θ follows cos²(θ/2); verified here by Monte Carlo
4. 720° NOT 360°              a full 360° rotation flips the state's sign;
   only 720° returns it — the spinor double-cover (SU(2), not SO(3))

Nothing here is an analogy to quantum mechanics; it is the actual linear
algebra of a qubit, done with two complex numbers.
"""

from __future__ import annotations

import cmath
import math
import random
from typing import Iterator

# A pure spin state is (alpha, beta): amplitudes for |up> and |down> along z,
# with |alpha|^2 + |beta|^2 = 1. Measurement probabilities are the squared
# magnitudes — Born's rule.
State = tuple[complex, complex]

# ── Axes and their spin-up eigenstates ────────────────────────────────────


def up_along(theta: float, phi: float = 0.0) -> State:
    """The spin-up eigenstate along a direction (polar angle theta, azimuth phi).

    theta = 0 is the +z axis (|up>); theta = pi/2, phi = 0 is the +x axis.
    This is the standard Bloch-sphere parameterization of a qubit.
    """
    return (math.cos(theta / 2), cmath.exp(1j * phi) * math.sin(theta / 2))


def down_along(theta: float, phi: float = 0.0) -> State:
    """The spin-down eigenstate — orthogonal to up_along(theta, phi)."""
    return (-math.sin(theta / 2), cmath.exp(1j * phi) * math.cos(theta / 2))


# Named axes used throughout the demo.
Z_UP: State = up_along(0.0)                    # (1, 0)
Z_DOWN: State = down_along(0.0)                # (0, 1)
X_UP: State = up_along(math.pi / 2)            # (1, 1)/sqrt(2)
X_DOWN: State = down_along(math.pi / 2)        # (-1, 1)/sqrt(2)


# ── Core quantum operations ───────────────────────────────────────────────


def inner_product(a: State, b: State) -> complex:
    """<a|b> — the overlap amplitude between two states."""
    return a[0].conjugate() * b[0] + a[1].conjugate() * b[1]


def probability(state: State, outcome: State) -> float:
    """Born's rule: P(outcome) = |<outcome|state>|^2."""
    return abs(inner_product(outcome, state)) ** 2


def measure(
    state: State, axis_up: State, axis_down: State, rng: random.Random
) -> tuple[int, State]:
    """Measure `state` along an axis; return (+1 or -1, collapsed state).

    The measurement is probabilistic (Born's rule) and the state COLLAPSES
    onto the observed eigenstate — the core non-classical move.
    """
    p_up = probability(state, axis_up)
    if rng.random() < p_up:
        return +1, axis_up
    return -1, axis_down


# ── Rotations: the spinor double cover ────────────────────────────────────


def rotate_about_z(state: State, angle: float) -> State:
    """Rotate the spin about the z-axis by `angle` radians.

    The rotation operator for spin-1/2 uses HALF the angle in the phases:
    exp(-i*angle*Sz/hbar) with Sz = hbar/2. That factor of 1/2 is exactly
    why 360 degrees (angle = 2*pi) multiplies the state by exp(-i*pi) = -1
    instead of leaving it unchanged.
    """
    alpha, beta = state
    return (
        cmath.exp(-1j * angle / 2) * alpha,
        cmath.exp(+1j * angle / 2) * beta,
    )


# ── Demo helpers ──────────────────────────────────────────────────────────


def fmt(state: State) -> str:
    a, b = state
    return f"({a.real:+.3f}{a.imag:+.3f}i)|↑⟩ + ({b.real:+.3f}{b.imag:+.3f}i)|↓⟩"


def counts_along(
    state: State, axis_up: State, axis_down: State, trials: int, rng: random.Random
) -> tuple[int, int]:
    """Run `trials` independent measurements; tally (+1 count, -1 count)."""
    plus = 0
    for _ in range(trials):
        outcome, _ = measure(state, axis_up, axis_down, rng)
        plus += outcome == +1
    return plus, trials - plus


# ── Demo ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    rng = random.Random(0)
    TRIALS = 10000

    print("── 1. Stern-Gerlach: only two outcomes, never a continuum ──")
    # A spin prepared "up" along z, measured along z, is always up.
    plus, minus = counts_along(Z_UP, Z_UP, Z_DOWN, TRIALS, rng)
    print(f"   |↑z⟩ measured along z  → +:{plus:>5}  -:{minus:>5}  "
          f"(deterministic: always +)")
    # The same state measured along x splits 50/50 — z and x are incompatible.
    plus, minus = counts_along(Z_UP, X_UP, X_DOWN, TRIALS, rng)
    print(f"   |↑z⟩ measured along x  → +:{plus:>5}  -:{minus:>5}  "
          f"(≈50/50: x is 'blind' to z)")

    print("\n── 2. Measurement disturbs: z → x → z erases the first result ──")
    # Classically, measuring z twice must agree. Quantum-mechanically, an
    # x-measurement in between destroys the z-information.
    kept = 0
    for _ in range(TRIALS):
        _, s1 = measure(Z_UP, Z_UP, Z_DOWN, rng)          # certainly +z
        _, s2 = measure(s1, X_UP, X_DOWN, rng)            # random x
        outcome, _ = measure(s2, Z_UP, Z_DOWN, rng)       # z again
        kept += outcome == +1
    print(f"   started at +z, remeasured z after an x-measurement:")
    print(f"   still +z in {kept}/{TRIALS} ({kept / TRIALS:.0%}) — the x step")
    print(f"   scrambled it back to 50/50, not the classical 100%")

    print("\n── 3. The cos²(θ/2) law, verified by Monte Carlo ──")
    print("   prepare |↑z⟩, measure along an axis tilted by θ from z:")
    print("      θ      P(+) measured   cos²(θ/2) predicted")
    for deg in (0, 30, 45, 60, 90, 120, 180):
        theta = math.radians(deg)
        axis_up, axis_down = up_along(theta), down_along(theta)
        plus, _ = counts_along(Z_UP, axis_up, axis_down, TRIALS, rng)
        measured = plus / TRIALS
        predicted = math.cos(theta / 2) ** 2
        print(f"    {deg:>4}°     {measured:>8.3f}         {predicted:>8.3f}")

    print("\n── 4. A 360° rotation flips the sign; only 720° restores it ──")
    print("   rotating |↑z⟩ about z (a global phase, invisible to measurement")
    print("   but real in interference):")
    for deg in (0, 180, 360, 540, 720):
        rotated = rotate_about_z(Z_UP, math.radians(deg))
        # overlap with the ORIGINAL state reveals the hidden phase
        overlap = inner_product(Z_UP, rotated)
        print(f"    {deg:>4}°:  ⟨↑z|R|↑z⟩ = {overlap.real:+.3f}{overlap.imag:+.3f}i"
              f"   {fmt(rotated)}")
    print("   note: 360° gives overlap -1 (state negated), 720° gives +1 —")
    print("   spin-1/2 lives on SU(2), the double cover of ordinary rotations")
