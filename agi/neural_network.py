"""
Neural Network from Scratch (ニューラルネットワークと誤差逆伝播法)

外部ライブラリなしで実装する多層パーセプトロン (MLP)。
現代の AI (深層学習・大規模言語モデル) の中核となる仕組み。

- 順伝播 (forward): 入力 -> 隠れ層 (sigmoid) -> 出力
- 逆伝播 (backpropagation): 誤差の勾配を連鎖律で逆向きに伝える
- 勾配降下法 (gradient descent) で重みを更新

デモでは線形分離不可能な XOR 問題を学習する。
"""

from __future__ import annotations

import math
import random
from typing import List

Vector = List[float]
Matrix = List[List[float]]


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def sigmoid_derivative(y: float) -> float:
    # y = sigmoid(x) を受け取る形の導関数: σ'(x) = σ(x)(1 - σ(x))
    return y * (1.0 - y)


class NeuralNetwork:
    """1隠れ層の全結合ニューラルネットワーク。"""

    def __init__(self, n_input: int, n_hidden: int, n_output: int, seed: int = 0):
        rng = random.Random(seed)
        # 重みは小さな乱数で初期化 (全て0だと対称性が壊れず学習できない)
        self.w_hidden: Matrix = [
            [rng.uniform(-1, 1) for _ in range(n_input)] for _ in range(n_hidden)
        ]
        self.b_hidden: Vector = [0.0] * n_hidden
        self.w_output: Matrix = [
            [rng.uniform(-1, 1) for _ in range(n_hidden)] for _ in range(n_output)
        ]
        self.b_output: Vector = [0.0] * n_output

    def forward(self, inputs: Vector) -> Vector:
        self.inputs = inputs
        self.hidden = [
            sigmoid(sum(w * x for w, x in zip(ws, inputs)) + b)
            for ws, b in zip(self.w_hidden, self.b_hidden)
        ]
        self.outputs = [
            sigmoid(sum(w * h for w, h in zip(ws, self.hidden)) + b)
            for ws, b in zip(self.w_output, self.b_output)
        ]
        return self.outputs

    def backward(self, targets: Vector, lr: float) -> float:
        """逆伝播で勾配を計算し、重みを更新。二乗誤差を返す。"""
        # 出力層の誤差信号 δ = (y - t) * σ'(y)
        delta_out = [
            (o - t) * sigmoid_derivative(o) for o, t in zip(self.outputs, targets)
        ]
        # 隠れ層の誤差信号 (出力層の δ を重みで逆向きに配分)
        delta_hidden = [
            sigmoid_derivative(h)
            * sum(d * self.w_output[k][j] for k, d in enumerate(delta_out))
            for j, h in enumerate(self.hidden)
        ]
        # 出力層の重み更新
        for k, d in enumerate(delta_out):
            for j, h in enumerate(self.hidden):
                self.w_output[k][j] -= lr * d * h
            self.b_output[k] -= lr * d
        # 隠れ層の重み更新
        for j, d in enumerate(delta_hidden):
            for i, x in enumerate(self.inputs):
                self.w_hidden[j][i] -= lr * d * x
            self.b_hidden[j] -= lr * d
        return sum((o - t) ** 2 for o, t in zip(self.outputs, targets)) / 2

    def train(self, dataset: List[tuple], epochs: int = 5000, lr: float = 0.5) -> None:
        for epoch in range(1, epochs + 1):
            loss = 0.0
            for inputs, targets in dataset:
                self.forward(inputs)
                loss += self.backward(targets, lr)
            if epoch % 1000 == 0:
                print(f"epoch {epoch:5d}  loss = {loss:.6f}")


if __name__ == "__main__":
    # XOR: 単純パーセプトロンでは解けない古典的問題
    xor_data = [
        ([0.0, 0.0], [0.0]),
        ([0.0, 1.0], [1.0]),
        ([1.0, 0.0], [1.0]),
        ([1.0, 1.0], [0.0]),
    ]

    nn = NeuralNetwork(n_input=2, n_hidden=4, n_output=1)
    print("=== XOR を学習 ===")
    nn.train(xor_data)

    print("\n=== 予測結果 ===")
    for inputs, targets in xor_data:
        pred = nn.forward(inputs)[0]
        print(f"{inputs} -> {pred:.4f} (expected {targets[0]:.0f})")
