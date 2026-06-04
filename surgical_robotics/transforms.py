"""
2D homogeneous transforms — coordinate frames / 同次変換(座標フレーム)

Surgical robots must relate several coordinate frames: the patient, the
imaging system, the robot base and the instrument tip. A 3x3 homogeneous
matrix represents a rigid 2D transform (rotation + translation), and composing
them registers one frame into another. Standard library only.
"""

import math


def _matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


class Transform2D:
    """A rigid 2D transform stored as a 3x3 homogeneous matrix."""

    def __init__(self, matrix: list[list[float]] | None = None) -> None:
        self.m = matrix or [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]

    @classmethod
    def rotation(cls, theta: float) -> "Transform2D":
        c, s = math.cos(theta), math.sin(theta)
        return cls([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])

    @classmethod
    def translation(cls, dx: float, dy: float) -> "Transform2D":
        return cls([[1.0, 0.0, dx], [0.0, 1.0, dy], [0.0, 0.0, 1.0]])

    def compose(self, other: "Transform2D") -> "Transform2D":
        """self * other: apply `other` first, then `self`."""
        return Transform2D(_matmul(self.m, other.m))

    def apply(self, point: tuple[float, float]) -> tuple[float, float]:
        x, y = point
        m = self.m
        return (
            m[0][0] * x + m[0][1] * y + m[0][2],
            m[1][0] * x + m[1][1] * y + m[1][2],
        )

    def inverse(self) -> "Transform2D":
        """Inverse of a rigid transform: R^T and -R^T t."""
        m = self.m
        r00, r01, r10, r11 = m[0][0], m[0][1], m[1][0], m[1][1]
        tx, ty = m[0][2], m[1][2]
        return Transform2D([
            [r00, r10, -(r00 * tx + r10 * ty)],
            [r01, r11, -(r01 * tx + r11 * ty)],
            [0.0, 0.0, 1.0],
        ])


if __name__ == "__main__":
    # Robot base is rotated 90deg and shifted relative to the patient frame.
    patient_to_robot = Transform2D.translation(10, 5).compose(
        Transform2D.rotation(math.radians(90))
    )
    target_in_patient = (3.0, 0.0)
    target_in_robot = patient_to_robot.apply(target_in_patient)
    print(f"Target in robot frame: ({target_in_robot[0]:.3f}, {target_in_robot[1]:.3f})")

    # Inverse maps it back to the patient frame.
    back = patient_to_robot.inverse().apply(target_in_robot)
    print(f"Mapped back to patient: ({back[0]:.3f}, {back[1]:.3f})")
