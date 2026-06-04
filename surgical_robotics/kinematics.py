"""
Kinematics — planar 2-link manipulator / 運動学(平面2リンクアーム)

Forward kinematics maps joint angles to the instrument-tip position; inverse
kinematics solves the reverse — which joint angles place the tip at a target.
A surgical manipulator must do both: report where the tool is, and compute how
to reach a commanded point. Standard library only.
"""

import math


def forward_kinematics(
    l1: float, l2: float, theta1: float, theta2: float
) -> tuple[float, float]:
    """Tip position (x, y) for link lengths l1, l2 and joint angles."""
    x = l1 * math.cos(theta1) + l2 * math.cos(theta1 + theta2)
    y = l1 * math.sin(theta1) + l2 * math.sin(theta1 + theta2)
    return x, y


def inverse_kinematics(
    l1: float, l2: float, x: float, y: float, elbow_up: bool = True
) -> tuple[float, float]:
    """Joint angles (theta1, theta2) reaching (x, y).

    Two solutions exist (elbow-up / elbow-down). Raises if the target is out
    of the arm's reachable workspace.
    """
    reach = math.hypot(x, y)
    if reach > l1 + l2 or reach < abs(l1 - l2):
        raise ValueError("target is outside the reachable workspace")

    cos_t2 = (x * x + y * y - l1 * l1 - l2 * l2) / (2 * l1 * l2)
    cos_t2 = max(-1.0, min(1.0, cos_t2))  # guard against rounding
    theta2 = math.acos(cos_t2)
    if not elbow_up:
        theta2 = -theta2
    theta1 = math.atan2(y, x) - math.atan2(
        l2 * math.sin(theta2), l1 + l2 * math.cos(theta2)
    )
    return theta1, theta2


if __name__ == "__main__":
    l1, l2 = 1.0, 0.8
    target = (1.2, 0.6)
    t1, t2 = inverse_kinematics(l1, l2, *target)
    print(f"IK joint angles: theta1={math.degrees(t1):.2f}deg, "
          f"theta2={math.degrees(t2):.2f}deg")

    # Round-trip: feeding the angles back through FK returns the target.
    x, y = forward_kinematics(l1, l2, t1, t2)
    print(f"FK check: ({x:.3f}, {y:.3f})  target ({target[0]}, {target[1]})")
