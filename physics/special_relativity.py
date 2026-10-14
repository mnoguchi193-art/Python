"""
Special Relativity — when speed warps space and time

Einstein's 1905 theory: the speed of light is the same for everyone, and the
price is that time, length and velocity stop behaving classically. The Lorentz
factor gamma governs it all — moving clocks run slow, moving rulers shrink, and
velocities add so that nothing ever exceeds c.

Velocities are given as fractions of the speed of light (beta = v/c).
"""

from __future__ import annotations

import math


def gamma(beta: float) -> float:
    """Lorentz factor 1/sqrt(1 - beta^2)."""
    if abs(beta) >= 1:
        raise ValueError("speed must be below c")
    return 1 / math.sqrt(1 - beta ** 2)


def time_dilation(proper_time: float, beta: float) -> float:
    """Elapsed time seen by a stationary observer for a moving clock."""
    return gamma(beta) * proper_time


def length_contraction(proper_length: float, beta: float) -> float:
    return proper_length / gamma(beta)


def velocity_addition(u: float, v: float) -> float:
    """Relativistic sum of two velocities (in units of c)."""
    return (u + v) / (1 + u * v)


def kinetic_energy_ratio(beta: float) -> float:
    """Relativistic KE divided by the classical 1/2 m v^2."""
    return (gamma(beta) - 1) / (0.5 * beta ** 2)


if __name__ == "__main__":
    print("Lorentz factor and its consequences:\n")
    print(f"  {'beta':>6}  {'gamma':>8}  {'clock slows':>12}  {'ruler shrinks':>14}")
    for beta in (0.1, 0.5, 0.9, 0.99, 0.999):
        g = gamma(beta)
        print(f"  {beta:>6}  {g:>8.3f}  {g:>11.2f}x  {1 / g:>13.1%}")

    print("\nTwin paradox: a 1-year trip at 0.99c...")
    print(f"  traveller ages 1.00 yr, Earth ages "
          f"{time_dilation(1.0, 0.99):.2f} yr")

    print("\nVelocity addition (c is the cosmic speed limit):")
    print(f"  0.9c + 0.9c = {velocity_addition(0.9, 0.9):.4f} c  (not 1.8c)")
    print(f"  0.5c + 0.5c = {velocity_addition(0.5, 0.5):.4f} c")

    print("\nKinetic energy diverges from the classical value near c:")
    for beta in (0.1, 0.9, 0.99):
        print(f"  beta={beta:<5} relativistic KE is "
              f"{kinetic_energy_ratio(beta):.2f}x the classical 1/2 m v^2")
