"""
Ring Attractor — working memory as persistent neural activity

How does the brain *hold* a value in mind after the stimulus is gone? A ring of
neurons coding a circular variable (head direction, a remembered location) with
local excitation and broad inhibition supports a self-sustaining "bump" of
activity. Cue it, remove the input, and the bump persists where it was placed —
a continuous attractor, the leading model of spatial working memory and the
head-direction system.
"""

from __future__ import annotations

import math


def _decode(activity: list[float], angles: list[float]) -> float:
    """Population-vector readout of the remembered angle (radians)."""
    x = sum(a * math.cos(t) for a, t in zip(activity, angles))
    y = sum(a * math.sin(t) for a, t in zip(activity, angles))
    return math.atan2(y, x) % (2 * math.pi)


def simulate(cue_angle: float, n: int = 24, cue_steps: int = 80,
             memory_steps: int = 200) -> tuple[float, float]:
    """Cue a bump, then run with no input. Returns (decoded with cue, from memory)."""
    angles = [2 * math.pi * i / n for i in range(n)]
    activity = [0.0] * n
    j_exc, j_inh, dt, total = 3.0, 1.0, 0.2, n * 0.5

    def update(drive: list[float]) -> None:
        nonlocal activity
        new = []
        for i in range(n):
            rec = sum((j_exc * math.cos(angles[i] - angles[j]) - j_inh) * activity[j]
                      for j in range(n)) / n
            new.append(max(0.0, activity[i] + dt * (-activity[i] + rec + drive[i])))
        s = sum(new)
        activity = [v / s * total for v in new] if s > 0 else new  # stabilize bump

    cue = [max(0.0, math.cos(angles[i] - cue_angle)) for i in range(n)]
    for _ in range(cue_steps):
        update(cue)
    with_cue = _decode(activity, angles)
    for _ in range(memory_steps):                     # input removed
        update([0.0] * n)
    return with_cue, _decode(activity, angles)


if __name__ == "__main__":
    print("Ring attractor — holding an angle in working memory\n")
    print(f"  {'cued angle':>11}  {'after cue':>10}  {'after memory':>13}  {'error':>7}")
    for deg in (30, 90, 200, 315):
        cue = math.radians(deg)
        with_cue, remembered = simulate(cue)
        err = abs((math.degrees(remembered) - deg + 180) % 360 - 180)
        print(f"  {deg:>10}°  {math.degrees(with_cue):>9.0f}°  "
              f"{math.degrees(remembered):>12.0f}°  {err:>6.1f}°")

    print("\n  The activity bump stays put after the cue disappears — persistent")
    print("  activity is how a continuous attractor stores a value over time.")
