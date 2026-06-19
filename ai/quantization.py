"""
Neural Network Quantization — how an AI PC runs models on its NPU

Intel's "AI PC" (Core Ultra) pairs the CPU and GPU with an NPU dedicated to
neural inference. To run efficiently on that hardware, models are *quantized*:
their 32-bit floating-point weights are mapped to 8-bit integers. This cuts
memory and bandwidth 4x and lets the NPU use fast integer arithmetic — the
on-device inference can even be done entirely in integers and still reconstruct
the floating-point result closely.

This module shows symmetric INT8 quantization and an integer-only layer.
"""

from __future__ import annotations


def quantize(values: list[float]) -> tuple[list[int], float]:
    """Symmetric per-tensor INT8 quantization. Returns (int8 codes, scale)."""
    scale = max((abs(v) for v in values), default=1.0) / 127 or 1.0
    codes = [max(-127, min(127, round(v / scale))) for v in values]
    return codes, scale


def dequantize(codes: list[int], scale: float) -> list[float]:
    return [c * scale for c in codes]


def quantized_matvec(weights: list[list[float]], x: list[float]) -> list[float]:
    """A linear layer y = W x computed via integer (INT8) arithmetic.

    Weights and inputs are quantized; the dot products are pure integer
    multiply-accumulate (what an NPU does), then rescaled back to float.
    """
    qx, sx = quantize(x)
    out = []
    for row in weights:
        qw, sw = quantize(row)
        acc = sum(a * b for a, b in zip(qw, qx))   # integer MAC
        out.append(acc * sw * sx)
    return out


if __name__ == "__main__":
    weights = [0.12, -0.87, 0.45, -0.03, 0.99, -0.51, 0.07, -0.64]
    codes, scale = quantize(weights)
    recon = dequantize(codes, scale)

    print("INT8 weight quantization\n")
    print(f"  float32 weights : {weights}")
    print(f"  int8 codes      : {codes}")
    print(f"  scale           : {scale:.5f}")
    print(f"  dequantized     : {[round(v, 3) for v in recon]}")
    max_err = max(abs(a - b) for a, b in zip(weights, recon))
    print(f"  max reconstruction error: {max_err:.4f}")
    print(f"  memory: 32-bit -> 8-bit  = 4x smaller "
          f"({len(weights) * 4} B -> {len(weights)} B)\n")

    # An integer-only linear layer reproduces the float result.
    W = [[0.5, -0.2, 0.1, 0.8],
         [-0.3, 0.9, -0.6, 0.2],
         [0.7, 0.4, -0.8, -0.1]]
    x = [1.0, -2.0, 0.5, 1.5]
    y_float = [sum(w * xi for w, xi in zip(row, x)) for row in W]
    y_int = quantized_matvec(W, x)

    print("Linear layer: full-precision vs INT8 (integer MAC on the NPU)")
    print(f"  {'float32':>10}  {'int8':>10}  {'abs error':>10}")
    for f, q in zip(y_float, y_int):
        print(f"  {f:>10.4f}  {q:>10.4f}  {abs(f - q):>10.4f}")
    print("\n  Integer inference matches float closely at a quarter the memory —")
    print("  the trade that lets an AI PC's NPU run models fast and efficiently.")
