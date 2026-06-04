"""
PID control — closed-loop joint control / PID制御(閉ループ関節制御)

A robot joint is driven to a commanded position by feedback control. The PID
law combines three terms on the tracking error e = setpoint - measurement:

    u = Kp*e + Ki*∫e dt + Kd*de/dt

Proportional reacts to the current error, integral removes steady-state
offset, derivative damps overshoot. Includes integral anti-windup. A simple
mass-damper plant is simulated to show convergence. Standard library only.
"""


class PIDController:
    def __init__(
        self,
        kp: float,
        ki: float,
        kd: float,
        dt: float,
        output_limit: float | None = None,
    ) -> None:
        self.kp, self.ki, self.kd, self.dt = kp, ki, kd, dt
        self.output_limit = output_limit
        self._integral = 0.0
        self._prev_error = 0.0

    def reset(self) -> None:
        self._integral = 0.0
        self._prev_error = 0.0

    def update(self, setpoint: float, measurement: float) -> float:
        error = setpoint - measurement
        self._integral += error * self.dt
        derivative = (error - self._prev_error) / self.dt
        output = self.kp * error + self.ki * self._integral + self.kd * derivative
        self._prev_error = error

        if self.output_limit is not None:
            clamped = max(-self.output_limit, min(self.output_limit, output))
            if clamped != output:
                # Anti-windup: undo the integral growth that was clipped away.
                self._integral -= error * self.dt
            return clamped
        return output


def simulate(
    pid: PIDController,
    setpoint: float,
    steps: int,
    mass: float = 1.0,
    damping: float = 0.8,
) -> list[float]:
    """Drive a 1-DOF mass-damper toward `setpoint`; return position history."""
    position = velocity = 0.0
    history = [position]
    for _ in range(steps):
        force = pid.update(setpoint, position)
        accel = (force - damping * velocity) / mass
        velocity += accel * pid.dt
        position += velocity * pid.dt
        history.append(position)
    return history


if __name__ == "__main__":
    pid = PIDController(kp=8.0, ki=2.0, kd=6.0, dt=0.05, output_limit=50.0)
    history = simulate(pid, setpoint=1.0, steps=120)
    print(f"Setpoint: 1.0")
    for i in range(0, len(history), 20):
        print(f"  step {i:3d}: position = {history[i]:.4f}")
    print(f"Final position: {history[-1]:.4f}  (converges to setpoint)")
