"""
Surrogate Models (代理モデル) — replacing an expensive simulator with a
cheap learned emulator

A core "AI for Science" pattern: a physics simulation that costs seconds
or hours per run is replaced by a neural network trained on a few hundred
simulator outputs.  Once trained, the network answers in microseconds,
making parameter sweeps, uncertainty analysis and inverse problems
affordable.

Here the "expensive simulator" is a damped, driven oscillator integrated
with RK4; the surrogate is a one-hidden-layer MLP trained by plain
gradient descent (backprop written by hand, no autograd).
"""

from __future__ import annotations
import math
import random
import time


# ── Expensive simulator ───────────────────────────────────────────────────
def simulate_peak_amplitude(damping: float, drive_freq: float,
                            steps: int = 4000, dt: float = 0.01) -> float:
    """Integrate x'' + 2*zeta*x' + x = cos(omega*t) with RK4 and return the
    steady-state amplitude (max |x| over the final quarter of the run)."""
    def deriv(t: float, x: float, v: float) -> tuple[float, float]:
        return v, math.cos(drive_freq * t) - 2 * damping * v - x

    x = v = t = 0.0
    peak = 0.0
    for i in range(steps):
        k1x, k1v = deriv(t, x, v)
        k2x, k2v = deriv(t + dt / 2, x + dt / 2 * k1x, v + dt / 2 * k1v)
        k3x, k3v = deriv(t + dt / 2, x + dt / 2 * k2x, v + dt / 2 * k2v)
        k4x, k4v = deriv(t + dt, x + dt * k3x, v + dt * k3v)
        x += dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
        v += dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
        t += dt
        if i >= steps * 3 // 4:
            peak = max(peak, abs(x))
    return peak


DAMPING_RANGE = (0.15, 1.0)
FREQ_RANGE    = (0.2, 2.0)


def scale(value: float, lo_hi: tuple[float, float]) -> float:
    """Map a physical parameter onto [-1, 1] for the network."""
    lo, hi = lo_hi
    return 2 * (value - lo) / (hi - lo) - 1


# ── Surrogate: tiny MLP with hand-written backprop ────────────────────────
class MLP:
    """2 inputs -> `hidden` tanh units -> 1 linear output."""

    def __init__(self, hidden: int = 24, seed: int = 0):
        rng = random.Random(seed)
        self.w1 = [[rng.gauss(0, 0.8) for _ in range(2)] for _ in range(hidden)]
        self.b1 = [0.0] * hidden
        self.w2 = [rng.gauss(0, 0.5) for _ in range(hidden)]
        self.b2 = 0.0

    def forward(self, x: list[float]) -> tuple[list[float], float]:
        h = [math.tanh(w[0] * x[0] + w[1] * x[1] + b)
             for w, b in zip(self.w1, self.b1)]
        out = sum(wi * hi for wi, hi in zip(self.w2, h)) + self.b2
        return h, out

    def predict(self, x: list[float]) -> float:
        return self.forward(x)[1]

    def train(self, X: list[list[float]], y: list[float],
              epochs: int = 3000, lr: float = 0.02, momentum: float = 0.9) -> float:
        """Full-batch gradient descent with momentum on mean squared error."""
        n, hidden = len(X), len(self.w1)
        vw1 = [[0.0, 0.0] for _ in range(hidden)]
        vb1, vw2, vb2 = [0.0] * hidden, [0.0] * hidden, 0.0
        for _ in range(epochs):
            gw1 = [[0.0, 0.0] for _ in range(hidden)]
            gb1, gw2, gb2 = [0.0] * hidden, [0.0] * hidden, 0.0
            for x, target in zip(X, y):
                h, out = self.forward(x)
                d_out = 2 * (out - target) / n
                gb2 += d_out
                for j, hj in enumerate(h):
                    gw2[j] += d_out * hj
                    d_h = d_out * self.w2[j] * (1 - hj * hj)   # tanh'
                    gw1[j][0] += d_h * x[0]
                    gw1[j][1] += d_h * x[1]
                    gb1[j] += d_h
            for j in range(hidden):
                vw1[j][0] = momentum * vw1[j][0] - lr * gw1[j][0]
                vw1[j][1] = momentum * vw1[j][1] - lr * gw1[j][1]
                vb1[j] = momentum * vb1[j] - lr * gb1[j]
                vw2[j] = momentum * vw2[j] - lr * gw2[j]
                self.w1[j][0] += vw1[j][0]
                self.w1[j][1] += vw1[j][1]
                self.b1[j] += vb1[j]
                self.w2[j] += vw2[j]
            vb2 = momentum * vb2 - lr * gb2
            self.b2 += vb2
        return sum((self.predict(x) - t) ** 2 for x, t in zip(X, y)) / n


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    rng = random.Random(42)

    def sample() -> tuple[float, float]:
        return rng.uniform(*DAMPING_RANGE), rng.uniform(*FREQ_RANGE)

    # 1. Run the expensive simulator to build a training set (log-amplitude
    #    is smoother than raw amplitude near resonance, so learn that).
    train_params = [sample() for _ in range(200)]
    t0 = time.perf_counter()
    train_y = [math.log(simulate_peak_amplitude(z, w)) for z, w in train_params]
    sim_time = (time.perf_counter() - t0) / len(train_params)
    train_X = [[scale(z, DAMPING_RANGE), scale(w, FREQ_RANGE)] for z, w in train_params]
    print(f"Simulator: {len(train_params)} runs, {sim_time * 1e3:.2f} ms each")

    # 2. Fit the surrogate.
    model = MLP(hidden=24)
    t0 = time.perf_counter()
    mse = model.train(train_X, train_y)
    print(f"Surrogate trained in {time.perf_counter() - t0:.1f} s  (train MSE={mse:.4f})")

    # 3. Validate on unseen parameters.
    test_params = [sample() for _ in range(30)]
    errors = []
    for z, w in test_params:
        truth = simulate_peak_amplitude(z, w)
        pred = math.exp(model.predict([scale(z, DAMPING_RANGE), scale(w, FREQ_RANGE)]))
        errors.append(abs(pred - truth) / truth)
    print(f"Test median relative error: {sorted(errors)[len(errors) // 2]:.1%}  "
          f"(max {max(errors):.1%})")

    # 4. Use the surrogate for something the simulator makes expensive:
    #    locate the resonance frequency by brute-force sweep.
    zeta = 0.3
    grid = [FREQ_RANGE[0] + i * (FREQ_RANGE[1] - FREQ_RANGE[0]) / 2000 for i in range(2001)]
    t0 = time.perf_counter()
    best_w = max(grid, key=lambda w: model.predict([scale(zeta, DAMPING_RANGE), scale(w, FREQ_RANGE)]))
    sweep_time = time.perf_counter() - t0
    analytic = math.sqrt(1 - 2 * zeta ** 2)
    print(f"\nResonance sweep (2001 points) via surrogate: {sweep_time * 1e3:.0f} ms")
    print(f"  surrogate omega_r = {best_w:.3f}   analytic = {analytic:.3f}")
    print(f"  same sweep with the simulator would take ~{2001 * sim_time:.0f} s "
          f"({2001 * sim_time / sweep_time:.0f}x slower)")
