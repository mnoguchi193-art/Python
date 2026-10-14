"""
Balance Control — keeping a humanoid upright (inverted pendulum + PID)

A standing humanoid like Tesla's Optimus is, to first approximation, an inverted
pendulum: inherently unstable, it topples without constant correction. The robot
senses its tilt and applies a corrective torque through a feedback controller.
This module models that with a PID controller — proportional to the tilt, its
integral, and its rate — and shows it stabilizing a pendulum that would otherwise
fall.

    angular acceleration = (g/L) sin(theta) + torque / (m L^2)
    torque = -(Kp*theta + Ki*integral(theta) + Kd*theta_dot)
"""

from __future__ import annotations

import math


def simulate(theta0: float, kp: float = 0.0, ki: float = 0.0, kd: float = 0.0,
             controlled: bool = True, dt: float = 0.01, t_end: float = 5.0,
             g: float = 9.81, length: float = 1.0, mass: float = 1.0
             ) -> list[tuple[float, float]]:
    """Simulate the tilt angle theta (rad from vertical) over time."""
    theta, omega, integral = theta0, 0.0, 0.0
    traj = [(0.0, theta)]
    for step in range(1, int(t_end / dt) + 1):
        torque = 0.0
        if controlled:
            integral += theta * dt
            torque = -(kp * theta + ki * integral + kd * omega)
        alpha = (g / length) * math.sin(theta) + torque / (mass * length ** 2)
        omega += alpha * dt
        theta += omega * dt
        traj.append((step * dt, theta))
    return traj


def max_tilt(traj: list[tuple[float, float]]) -> float:
    return max(abs(theta) for _, theta in traj)


if __name__ == "__main__":
    start = 0.20   # initial tilt ~11.5 degrees off vertical

    uncontrolled = simulate(start, controlled=False)
    controlled = simulate(start, kp=25.0, ki=5.0, kd=8.0)

    print("Inverted-pendulum balance (start tilt = 11.5 deg)\n")
    print(f"  {'time (s)':>8}  {'no control':>12}  {'PID control':>12}")
    for t in (0.0, 0.5, 1.0, 2.0, 4.0):
        i = int(t / 0.01)
        u = math.degrees(uncontrolled[i][1])
        c = math.degrees(controlled[i][1])
        print(f"  {t:>8.1f}  {u:>11.1f}°  {c:>11.2f}°")

    print(f"\n  uncontrolled max tilt: {math.degrees(max_tilt(uncontrolled)):.0f}° "
          f"(falls over)")
    print(f"  PID-controlled max tilt: {math.degrees(max_tilt(controlled)):.1f}° "
          f"(recovers to upright)")

    blocks = " .:-=+*#%@"
    tail = [abs(math.degrees(th)) for _, th in controlled[::20]]
    hi = max(tail) or 1.0
    chart = "".join(blocks[min(8, int(v / hi * 8))] for v in tail)
    print(f"\n  |tilt| under PID control over time:\n  {chart}")
    print("\n  Feedback torque cancels the fall — the essence of how a humanoid")
    print("  (and a Segway, and a rocket landing) stays balanced.")
