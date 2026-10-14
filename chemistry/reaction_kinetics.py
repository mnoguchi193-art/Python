"""
Chemical Kinetics — how fast reactions go

Rate laws tell us how concentrations change with time. First-order decay falls
exponentially with a constant half-life (the same math as radioactive decay);
second-order decay slows as reactant runs out. For reaction networks with no
closed form, we integrate numerically — here the consecutive reaction
A -> B -> C, where the intermediate B rises and then falls.
"""

from __future__ import annotations

import math


def first_order(a0: float, k: float, t: float) -> float:
    return a0 * math.exp(-k * t)


def first_order_half_life(k: float) -> float:
    return math.log(2) / k


def second_order(a0: float, k: float, t: float) -> float:
    return 1.0 / (1.0 / a0 + k * t)


def consecutive(a0: float, k1: float, k2: float, t_end: float, dt: float = 0.01
                ) -> list[tuple[float, float, float, float]]:
    """Integrate A -> B -> C. Returns (time, [A], [B], [C]) samples."""
    a, b, c = a0, 0.0, 0.0
    history = [(0.0, a, b, c)]
    steps = int(t_end / dt)
    for s in range(1, steps + 1):
        da = -k1 * a
        db = k1 * a - k2 * b
        dc = k2 * b
        a += da * dt
        b += db * dt
        c += dc * dt
        history.append((s * dt, a, b, c))
    return history


if __name__ == "__main__":
    print("First-order decay (k = 0.1 /s):")
    k = 0.1
    print(f"  half-life = {first_order_half_life(k):.2f} s")
    for t in (0, 5, 10, 20):
        print(f"  t={t:>2}s  [A] = {first_order(1.0, k, t):.3f} M")

    print("\nFirst vs second order from [A]0 = 1.0 (same k = 0.5):")
    print(f"  {'t':>4}  {'first':>7}  {'second':>7}")
    for t in (0, 1, 2, 5):
        print(f"  {t:>4}  {first_order(1, 0.5, t):>7.3f}  "
              f"{second_order(1, 0.5, t):>7.3f}")

    print("\nConsecutive A -> B -> C (k1=0.3, k2=0.1): intermediate B peaks")
    history = consecutive(1.0, 0.3, 0.1, 40)
    print(f"  {'t':>4}  {'[A]':>6}  {'[B]':>6}  {'[C]':>6}")
    for t, a, b, c in history[::500]:
        print(f"  {t:>4.0f}  {a:>6.3f}  {b:>6.3f}  {c:>6.3f}")
    peak = max(history, key=lambda row: row[2])
    print(f"\n  [B] peaks at {peak[2]:.3f} M around t = {peak[0]:.1f} s")
