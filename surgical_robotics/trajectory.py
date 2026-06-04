"""
Trajectory generation — smooth joint motion / 軌道生成(滑らかな関節運動)

A surgical instrument must move between points smoothly, without abrupt
velocity or acceleration changes that would jerk tissue. Polynomial
trajectories interpolate from a start to an end value over a fixed duration:

    cubic   — zero velocity at both ends
    quintic — zero velocity AND acceleration at both ends (lowest jerk)

Standard library only.
"""


class CubicTrajectory:
    """Position with zero endpoint velocity over [0, duration]."""

    def __init__(self, q0: float, qf: float, duration: float) -> None:
        if duration <= 0:
            raise ValueError("duration must be positive")
        self.q0, self.qf, self.T = q0, qf, duration
        d = qf - q0
        self.a = [q0, 0.0, 3 * d / duration**2, -2 * d / duration**3]

    def position(self, t: float) -> float:
        t = max(0.0, min(self.T, t))
        a = self.a
        return a[0] + a[1] * t + a[2] * t**2 + a[3] * t**3

    def velocity(self, t: float) -> float:
        t = max(0.0, min(self.T, t))
        a = self.a
        return a[1] + 2 * a[2] * t + 3 * a[3] * t**2

    def sample(self, n: int = 5) -> list[tuple[float, float]]:
        return [
            (self.T * i / (n - 1), self.position(self.T * i / (n - 1)))
            for i in range(n)
        ]


class QuinticTrajectory:
    """Position with zero endpoint velocity and acceleration (low jerk)."""

    def __init__(self, q0: float, qf: float, duration: float) -> None:
        if duration <= 0:
            raise ValueError("duration must be positive")
        self.q0, self.qf, self.T = q0, qf, duration
        d, T = qf - q0, duration
        self.a = [q0, 0.0, 0.0, 10 * d / T**3, -15 * d / T**4, 6 * d / T**5]

    def position(self, t: float) -> float:
        t = max(0.0, min(self.T, t))
        return sum(c * t**i for i, c in enumerate(self.a))

    def velocity(self, t: float) -> float:
        t = max(0.0, min(self.T, t))
        return sum(i * c * t ** (i - 1) for i, c in enumerate(self.a) if i >= 1)


if __name__ == "__main__":
    cubic = CubicTrajectory(q0=0.0, qf=90.0, duration=2.0)
    print("Cubic trajectory (t, position):")
    for t, q in cubic.sample(5):
        print(f"  t={t:.2f}s  q={q:6.2f}  v={cubic.velocity(t):6.2f}")

    quintic = QuinticTrajectory(q0=0.0, qf=90.0, duration=2.0)
    print(f"Quintic midpoint velocity: {quintic.velocity(1.0):.2f} "
          f"(peaks higher, but starts/ends with zero accel)")
    print(f"Endpoint velocities: {quintic.velocity(0.0):.2f}, {quintic.velocity(2.0):.2f}")
