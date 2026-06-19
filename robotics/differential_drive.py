"""
Differential Drive — wheeled-robot kinematics and odometry drift

Most mobile robots steer like a tank: two independently driven wheels. The
forward speed and turn rate follow from the wheel speeds,

    v = (v_right + v_left) / 2,   omega = (v_right - v_left) / wheelbase,

and integrating them gives the pose (x, y, heading). "Odometry" estimates pose by
integrating the *commanded* wheel speeds — but real wheels slip, so dead reckoning
drifts ever further from the truth, which is why robots also need external
localization.
"""

from __future__ import annotations

import math
import random


def step(pose, v_left, v_right, wheelbase, dt):
    x, y, theta = pose
    v = (v_right + v_left) / 2
    omega = (v_right - v_left) / wheelbase
    return (x + v * math.cos(theta) * dt,
            y + v * math.sin(theta) * dt,
            theta + omega * dt)


def drive(commands, wheelbase=0.5, dt=0.1, slip=0.0, rng=None):
    """Run (v_left, v_right, steps) commands. slip adds wheel noise. Returns trace."""
    pose = (0.0, 0.0, 0.0)
    trace = [pose]
    for v_left, v_right, steps in commands:
        for _ in range(steps):
            vl, vr = v_left, v_right
            if slip:
                vl *= rng.gauss(1, slip)
                vr *= rng.gauss(1, slip)
            pose = step(pose, vl, vr, wheelbase, dt)
        trace.append(pose)
    return pose, trace


if __name__ == "__main__":
    # Drive forward, turn left 90 deg, repeat — tracing a square.
    fwd = (1.0, 1.0, 20)                          # straight 2 m
    turn = (-0.5, 0.5, int(round((math.pi / 2) * 0.5 / 0.1 / 1.0)))  # ~90 deg
    commands = [fwd, turn] * 4

    final, trace = drive(commands)
    print("Differential-drive robot tracing a square (ideal odometry)\n")
    print(f"  {'corner':>7}  {'x':>6}  {'y':>6}  {'heading':>8}")
    for i, (x, y, th) in enumerate(trace[::2]):
        print(f"  {i:>7}  {x:>6.2f}  {y:>6.2f}  {math.degrees(th) % 360:>7.0f}°")

    # Same commands, but with wheel slip -> the true path drifts from odometry.
    rng = random.Random(2)
    true_final, _ = drive(commands, slip=0.05, rng=rng)
    drift = math.hypot(true_final[0] - final[0], true_final[1] - final[1])
    print(f"\n  odometry estimate of final pose: "
          f"({final[0]:.2f}, {final[1]:.2f})")
    print(f"  true pose with 5% wheel slip   : "
          f"({true_final[0]:.2f}, {true_final[1]:.2f})")
    print(f"  accumulated drift              : {drift:.2f} m")
    print("\n  Small per-step wheel errors compound into large position error —")
    print("  why dead reckoning alone can't keep a robot localized for long.")
