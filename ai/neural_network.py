"""
Neural Network from Scratch — backpropagation on XOR

The engine of deep learning, in pure Python. A multilayer perceptron learns the
XOR function — the classic problem a single-layer perceptron *cannot* solve,
which is exactly why hidden layers and backpropagation matter. Forward pass
computes a prediction; backprop sends the error gradient backward to update every
weight by gradient descent.
"""

from __future__ import annotations

import math
import random


def sigmoid(x: float) -> float:
    if x < -60:
        return 0.0
    if x > 60:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


class MLP:
    """One hidden layer, sigmoid activations, trained by backprop."""

    def __init__(self, n_in: int, n_hidden: int, seed: int = 0):
        rng = random.Random(seed)
        rand = lambda: rng.uniform(-1.0, 1.0)
        self.w1 = [[rand() for _ in range(n_in)] for _ in range(n_hidden)]
        self.b1 = [rand() for _ in range(n_hidden)]
        self.w2 = [rand() for _ in range(n_hidden)]
        self.b2 = rand()

    def forward(self, x: list[float]) -> tuple[list[float], float]:
        h = [sigmoid(sum(w * xi for w, xi in zip(row, x)) + b)
             for row, b in zip(self.w1, self.b1)]
        out = sigmoid(sum(w * hi for w, hi in zip(self.w2, h)) + self.b2)
        return h, out

    def train(self, data: list[tuple[list[float], float]],
              epochs: int = 5000, lr: float = 0.5) -> list[float]:
        losses = []
        for _ in range(epochs):
            loss = 0.0
            for x, y in data:
                h, out = self.forward(x)
                loss += (out - y) ** 2
                # Output layer gradient (MSE through sigmoid).
                d_out = (out - y) * out * (1 - out)
                # Hidden layer gradient.
                d_h = [d_out * self.w2[j] * h[j] * (1 - h[j])
                       for j in range(len(h))]
                # Update output weights.
                for j in range(len(h)):
                    self.w2[j] -= lr * d_out * h[j]
                self.b2 -= lr * d_out
                # Update hidden weights.
                for j in range(len(h)):
                    for i in range(len(x)):
                        self.w1[j][i] -= lr * d_h[j] * x[i]
                    self.b1[j] -= lr * d_h[j]
            losses.append(loss / len(data))
        return losses


if __name__ == "__main__":
    xor = [([0, 0], 0), ([0, 1], 1), ([1, 0], 1), ([1, 1], 0)]
    net = MLP(n_in=2, n_hidden=4)
    losses = net.train(xor)

    print("Neural network learning XOR (backpropagation)\n")
    print("  epoch      loss")
    for e in (0, 500, 2000, 4999):
        print(f"  {e:>5}   {losses[e]:.5f}")

    print("\n  input     target  prediction")
    for x, y in xor:
        _, out = net.forward(x)
        print(f"  {x}      {y}       {out:.3f}  -> {round(out)}")
    print("\nThe hidden layer carves the input space so XOR becomes separable.")
