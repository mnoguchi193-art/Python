"""
The Lorenz System — chaos and the limits of weather prediction

In 1963 Edward Lorenz distilled atmospheric convection into three equations and
discovered the "butterfly effect": deterministic yet unpredictable. Two states
differing by a millionth diverge exponentially, so beyond a horizon the forecast
is worthless however good the model. This is *why* modern weather prediction is
probabilistic.

    dx/dt = sigma (y - x)
    dy/dt = x (rho - z) - y
    dz/dt = x y - beta z
"""

from __future__ import annotations

from math import log, sqrt


def lorenz_step(state: tuple[float, float, float], dt: float = 0.01,
                sigma: float = 10.0, rho: float = 28.0, beta: float = 8 / 3
                ) -> tuple[float, float, float]:
    x, y, z = state
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    return (x + dx * dt, y + dy * dt, z + dz * dt)


def integrate(state: tuple[float, float, float], steps: int, dt: float = 0.01,
              **params) -> list[tuple[float, float, float]]:
    trajectory = [state]
    for _ in range(steps):
        state = lorenz_step(state, dt, **params)
        trajectory.append(state)
    return trajectory


def distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return sqrt(sum((p - q) ** 2 for p, q in zip(a, b)))


def lyapunov_exponent(state: tuple[float, float, float], steps: int = 60000,
                      dt: float = 0.01, d0: float = 1e-8, renorm: int = 10,
                      spinup: int = 2000) -> float:
    """Largest Lyapunov exponent via the Benettin renormalization method.

    Repeatedly let a tiny perturbation grow, accumulate its log growth, then
    rescale it back to d0 — averaging the growth rate over the attractor.
    """
    base = state
    for _ in range(spinup):                      # settle onto the attractor
        base = lorenz_step(base, dt)
    pert = (base[0] + d0, base[1], base[2])
    total, count = 0.0, 0
    for i in range(1, steps + 1):
        base = lorenz_step(base, dt)
        pert = lorenz_step(pert, dt)
        if i % renorm == 0:
            d = distance(base, pert)
            total += log(d / d0)
            count += 1
            factor = d0 / d                      # rescale toward base
            pert = tuple(b + (p - b) * factor for b, p in zip(base, pert))
    return total / (count * renorm * dt)


if __name__ == "__main__":
    dt, steps = 0.01, 4000
    base = integrate((1.0, 1.0, 1.0), steps, dt)
    perturbed = integrate((1.0 + 1e-5, 1.0, 1.0), steps, dt)
    gaps = [distance(a, b) for a, b in zip(base, perturbed)]

    print("Lorenz system — the butterfly effect\n")
    print(f"  initial separation: {gaps[0]:.0e}")

    horizon = next((i * dt for i, g in enumerate(gaps) if g > 1.0), None)
    print(f"  forecast horizon (separation reaches 1.0): {horizon:.1f} time units")

    lam = lyapunov_exponent((1.0, 1.0, 1.0))
    print(f"  largest Lyapunov exponent: {lam:.2f} per time unit "
          f"(positive => chaos; literature ~0.9)")

    blocks = " .:-=+*#%@"
    sample = gaps[::steps // 80]
    hi = max(sample)
    chart = "".join(blocks[min(8, int(g / hi * 8))] for g in sample)
    print(f"\n  divergence over time:\n  {chart}")
    print("\nThe error explodes from negligible to attractor-sized — no model "
          "skill survives past the horizon.")
