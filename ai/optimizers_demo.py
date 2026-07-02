"""
Gradient-descent optimizers compared: SGD vs momentum vs Adam
（勾配降下法の最適化アルゴリズム比較: SGD・モーメンタム・Adam）

Every neural network — up to and including large language models — is
trained by some variant of the same update: nudge each parameter against
its gradient. The variants differ in how they *shape* that nudge:

  SGD        p -= lr * g                      raw gradient, one global step
  Momentum   v = β·v + g;  p -= lr * v        a heavy ball: past gradients
                                              accumulate, damping zig-zags
  Adam       m = β1·m + (1-β1)·g              momentum, plus a per-parameter
             s = β2·s + (1-β2)·g²             step size scaled by 1/√s —
             p -= lr * m̂ / (√ŝ + ε)           steep directions get small
                                              steps, flat ones get large

Two experiments below:

1. the Rosenbrock valley — a curved ravine that is the classic stress test:
   the gradient points across the valley, not along it
2. training an XOR network — the same task as ai/agi_demo.py, but with the
   gradient computation separated from the update rule so the three
   optimizers can be swapped in fairly (identical initial weights)
"""

from __future__ import annotations

import math
import random
from typing import Callable, Sequence

# ── Optimizers (shared interface: update params in place) ─────────────────


class SGD:
    """Plain stochastic gradient descent: the baseline."""

    def __init__(self, lr: float) -> None:
        self.lr = lr

    def step(self, params: list[float], grads: Sequence[float]) -> None:
        for i, g in enumerate(grads):
            params[i] -= self.lr * g


class Momentum:
    """SGD plus velocity: past gradients accumulate and smooth the path."""

    def __init__(self, lr: float, beta: float = 0.9) -> None:
        self.lr = lr
        self.beta = beta
        self.velocity: list[float] = []

    def step(self, params: list[float], grads: Sequence[float]) -> None:
        if not self.velocity:
            self.velocity = [0.0] * len(params)
        for i, g in enumerate(grads):
            self.velocity[i] = self.beta * self.velocity[i] + g
            params[i] -= self.lr * self.velocity[i]


class Adam:
    """Adaptive moments (Kingma & Ba, 2015): the de-facto default today.

    Tracks a running mean (m) and a running magnitude (s) of each gradient,
    then steps by m/√s — so every parameter gets its own step size. The
    m̂, ŝ 'bias corrections' undo the zero-initialization of the averages.
    """

    def __init__(
        self,
        lr: float,
        beta1: float = 0.9,
        beta2: float = 0.999,
        eps: float = 1e-8,
    ) -> None:
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps
        self.m: list[float] = []
        self.s: list[float] = []
        self.t = 0

    def step(self, params: list[float], grads: Sequence[float]) -> None:
        if not self.m:
            self.m = [0.0] * len(params)
            self.s = [0.0] * len(params)
        self.t += 1
        for i, g in enumerate(grads):
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * g
            self.s[i] = self.beta2 * self.s[i] + (1 - self.beta2) * g * g
            m_hat = self.m[i] / (1 - self.beta1 ** self.t)
            s_hat = self.s[i] / (1 - self.beta2 ** self.t)
            params[i] -= self.lr * m_hat / (math.sqrt(s_hat) + self.eps)


# ── Experiment 1: the Rosenbrock valley ───────────────────────────────────


def rosenbrock(x: float, y: float) -> float:
    return (1 - x) ** 2 + 100 * (y - x * x) ** 2


def rosenbrock_grad(x: float, y: float) -> tuple[float, float]:
    dx = -2 * (1 - x) - 400 * x * (y - x * x)
    dy = 200 * (y - x * x)
    return dx, dy


def race_on_rosenbrock(optimizers: dict[str, object], iterations: int) -> None:
    """Run each optimizer from the same start; print f(x, y) checkpoints."""
    start = [-1.5, 1.5]
    runs = {name: list(start) for name in optimizers}
    checkpoints = [0, 100, 500, 1000, 2000, 5000, iterations]
    header = "    iteration" + "".join(f"{name:>12}" for name in optimizers)
    print(header)
    for it in range(iterations + 1):
        if it in checkpoints:
            row = f"    {it:>9}"
            for name in optimizers:
                x, y = runs[name]
                row += f"{rosenbrock(x, y):>12.5f}"
            print(row)
        for name, opt in optimizers.items():
            params = runs[name]
            opt.step(params, rosenbrock_grad(*params))  # type: ignore[attr-defined]
    for name in optimizers:
        x, y = runs[name]
        print(f"    {name} finished at ({x:.3f}, {y:.3f})  [minimum is (1, 1)]")


# ── Experiment 2: training an XOR network ─────────────────────────────────

XOR_DATA: list[tuple[list[float], float]] = [
    ([0.0, 0.0], 0.0),
    ([0.0, 1.0], 1.0),
    ([1.0, 0.0], 1.0),
    ([1.0, 1.0], 0.0),
]


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


class XorNet:
    """A 2-4-1 sigmoid network with the gradient computation split out,
    so any optimizer can be plugged in. Parameter layout (17 floats):
    W1 (4x2), b1 (4), W2 (4), b2 (1).
    """

    HIDDEN = 4

    @staticmethod
    def initial_params(seed: int) -> list[float]:
        rng = random.Random(seed)
        return [rng.uniform(-1, 1) for _ in range(4 * 2 + 4 + 4 + 1)]

    @staticmethod
    def loss_and_grad(params: list[float]) -> tuple[float, list[float]]:
        """Mean squared error over the four XOR cases, and its gradient."""
        h_n = XorNet.HIDDEN
        w1 = params[: 2 * h_n]
        b1 = params[2 * h_n : 3 * h_n]
        w2 = params[3 * h_n : 4 * h_n]
        b2 = params[4 * h_n]

        grads = [0.0] * len(params)
        loss = 0.0
        for inputs, target in XOR_DATA:
            hidden = [
                _sigmoid(w1[2 * j] * inputs[0] + w1[2 * j + 1] * inputs[1] + b1[j])
                for j in range(h_n)
            ]
            output = _sigmoid(sum(w2[j] * hidden[j] for j in range(h_n)) + b2)
            loss += (output - target) ** 2

            d_out = 2 * (output - target) * output * (1 - output)
            for j in range(h_n):
                grads[3 * h_n + j] += d_out * hidden[j]           # W2
                d_hidden = d_out * w2[j] * hidden[j] * (1 - hidden[j])
                grads[2 * j] += d_hidden * inputs[0]              # W1
                grads[2 * j + 1] += d_hidden * inputs[1]
                grads[2 * h_n + j] += d_hidden                    # b1
            grads[4 * h_n] += d_out                               # b2

        n = len(XOR_DATA)
        return loss / n, [g / n for g in grads]


def race_on_xor(
    optimizer_factories: dict[str, Callable[[], object]],
    epochs: int,
    seed: int = 5,
) -> None:
    """Train identical networks with each optimizer; print loss checkpoints."""
    initial = XorNet.initial_params(seed)
    checkpoints = [1, 50, 100, 200, 500, 1000, 2000, epochs]
    histories: dict[str, list[float]] = {}
    solved_at: dict[str, int | None] = {}

    for name, factory in optimizer_factories.items():
        params = list(initial)  # every optimizer starts from the same weights
        opt = factory()
        losses = []
        solved = None
        for epoch in range(1, epochs + 1):
            loss, grads = XorNet.loss_and_grad(params)
            losses.append(loss)
            if solved is None and loss < 0.01:
                solved = epoch
            opt.step(params, grads)  # type: ignore[attr-defined]
        histories[name] = losses
        solved_at[name] = solved

    print("        epoch" + "".join(f"{name:>12}" for name in histories))
    for cp in checkpoints:
        row = f"    {cp:>9}"
        for losses in histories.values():
            row += f"{losses[cp - 1]:>12.5f}"
        print(row)
    for name, solved in solved_at.items():
        reached = f"epoch {solved}" if solved else f"not within {epochs} epochs"
        print(f"    {name}: loss < 0.01 at {reached}")


# ── Demo ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("── 1. Rosenbrock valley: f(x,y) = (1-x)² + 100(y-x²)², min 0 at (1,1) ──")
    print("   the gradient points across the curved ravine, not along it\n")
    # Each optimizer gets a reasonable, individually tuned learning rate —
    # SGD diverges on this ravine with anything much larger.
    race_on_rosenbrock(
        {
            "SGD": SGD(lr=0.0005),
            "momentum": Momentum(lr=0.0005),
            "Adam": Adam(lr=0.05),
        },
        iterations=10000,
    )

    print("\n── 2. XOR network (2-4-1): same initial weights, three optimizers ──\n")
    race_on_xor(
        {
            "SGD": lambda: SGD(lr=0.5),
            "momentum": lambda: Momentum(lr=0.5),
            "Adam": lambda: Adam(lr=0.05),
        },
        epochs=3000,
    )
