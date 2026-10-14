"""
Robot Arm Kinematics — forward and inverse (the "act" of a manipulator)

For a two-link planar arm, forward kinematics maps joint angles to the hand's
position; inverse kinematics solves the harder, practical problem — what joint
angles place the hand on a target? The IK generally has two solutions ("elbow
up" and "elbow down"), and none at all if the target is out of reach.
"""

from __future__ import annotations

import math


def forward(theta1: float, theta2: float, l1: float = 1.0, l2: float = 1.0
            ) -> tuple[float, float]:
    """Joint angles (radians) -> end-effector (x, y)."""
    x = l1 * math.cos(theta1) + l2 * math.cos(theta1 + theta2)
    y = l1 * math.sin(theta1) + l2 * math.sin(theta1 + theta2)
    return x, y


def inverse(x: float, y: float, l1: float = 1.0, l2: float = 1.0
            ) -> list[tuple[float, float]]:
    """Target (x, y) -> list of (theta1, theta2) solutions (0, 1 or 2)."""
    reach = math.hypot(x, y)
    if reach > l1 + l2 or reach < abs(l1 - l2):
        return []                                  # unreachable
    cos_t2 = (x * x + y * y - l1 * l1 - l2 * l2) / (2 * l1 * l2)
    cos_t2 = max(-1.0, min(1.0, cos_t2))
    solutions = []
    for sign in (1, -1):                            # elbow down / up
        t2 = sign * math.acos(cos_t2)
        t1 = math.atan2(y, x) - math.atan2(l2 * math.sin(t2),
                                           l1 + l2 * math.cos(t2))
        solutions.append((t1, t2))
    # Collapse duplicates (when the arm is straight).
    if len(solutions) == 2 and all(
            abs(a - b) < 1e-9 for a, b in zip(solutions[0], solutions[1])):
        solutions = solutions[:1]
    return solutions


if __name__ == "__main__":
    deg = math.degrees
    print("Two-link arm (L1 = L2 = 1.0)\n")

    pos = forward(math.radians(30), math.radians(60))
    print(f"  Forward: angles (30, 60) deg -> end-effector "
          f"({pos[0]:.3f}, {pos[1]:.3f})\n")

    target = (1.0, 1.0)
    print(f"  Inverse: reaching target {target}")
    for t1, t2 in inverse(*target):
        check = forward(t1, t2)
        print(f"    angles ({deg(t1):6.1f}, {deg(t2):6.1f}) deg  -> "
              f"({check[0]:.3f}, {check[1]:.3f})")

    print(f"\n  Unreachable target (3.0, 0.0): "
          f"{inverse(3.0, 0.0) or 'no solution'}")
