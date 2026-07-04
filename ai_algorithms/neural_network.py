"""
Neural Network from Scratch (誤差逆伝播法)

外部ライブラリなしの純Python実装。2層のフィードフォワードネットワークを
勾配降下法で学習し、線形分離不可能な XOR 問題を解く。
"""

from __future__ import annotations
import math
import random


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def sigmoid_derivative(y: float) -> float:
    """y = sigmoid(x) を受け取る形の導関数: σ'(x) = σ(x)(1 − σ(x))"""
    return y * (1.0 - y)


class NeuralNetwork:
    """入力層 → 隠れ層 (sigmoid) → 出力層 (sigmoid) の全結合ネットワーク。"""

    def __init__(self, n_inputs: int, n_hidden: int, n_outputs: int, seed: int = 0):
        rng = random.Random(seed)
        # weights[i][j]: ニューロン i の入力 j に対する重み
        self.w_hidden = [[rng.uniform(-1, 1) for _ in range(n_inputs)] for _ in range(n_hidden)]
        self.b_hidden = [0.0] * n_hidden
        self.w_output = [[rng.uniform(-1, 1) for _ in range(n_hidden)] for _ in range(n_outputs)]
        self.b_output = [0.0] * n_outputs

    def forward(self, inputs: list[float]) -> tuple[list[float], list[float]]:
        """Return (hidden_activations, output_activations)."""
        hidden = [
            sigmoid(sum(w * x for w, x in zip(weights, inputs)) + b)
            for weights, b in zip(self.w_hidden, self.b_hidden)
        ]
        output = [
            sigmoid(sum(w * h for w, h in zip(weights, hidden)) + b)
            for weights, b in zip(self.w_output, self.b_output)
        ]
        return hidden, output

    def train_step(self, inputs: list[float], targets: list[float], lr: float) -> float:
        """1サンプルで順伝播 → 逆伝播 → 重み更新。二乗誤差を返す。"""
        hidden, output = self.forward(inputs)

        # 出力層の誤差信号 δ = (y − t) * σ'(y)
        delta_out = [
            (o - t) * sigmoid_derivative(o) for o, t in zip(output, targets)
        ]
        # 隠れ層の誤差信号: 出力層の δ を重みで逆伝播
        delta_hidden = [
            sigmoid_derivative(h) * sum(d * self.w_output[k][j] for k, d in enumerate(delta_out))
            for j, h in enumerate(hidden)
        ]

        # 勾配降下で更新 (w ← w − lr * δ * 入力)
        for k, d in enumerate(delta_out):
            for j, h in enumerate(hidden):
                self.w_output[k][j] -= lr * d * h
            self.b_output[k] -= lr * d
        for j, d in enumerate(delta_hidden):
            for i, x in enumerate(inputs):
                self.w_hidden[j][i] -= lr * d * x
            self.b_hidden[j] -= lr * d

        return sum((o - t) ** 2 for o, t in zip(output, targets)) / len(output)

    def predict(self, inputs: list[float]) -> list[float]:
        return self.forward(inputs)[1]


if __name__ == "__main__":
    # XOR: 単層パーセプトロンでは解けない古典的な非線形問題
    dataset = [
        ([0.0, 0.0], [0.0]),
        ([0.0, 1.0], [1.0]),
        ([1.0, 0.0], [1.0]),
        ([1.0, 1.0], [0.0]),
    ]
    net = NeuralNetwork(n_inputs=2, n_hidden=4, n_outputs=1)

    for epoch in range(5000):
        loss = sum(net.train_step(x, t, lr=0.5) for x, t in dataset) / len(dataset)
        if epoch % 1000 == 0:
            print(f"epoch {epoch:4d}  loss = {loss:.4f}")

    print("\nXOR predictions:")
    for x, t in dataset:
        y = net.predict(x)[0]
        print(f"  {x} -> {y:.3f} (expected {t[0]:.0f}, predicted {round(y)})")
