"""
The Roofline Model — compute vs memory bandwidth in accelerated computing

Modern CPU+GPU "superchips" like NVIDIA's Vera Rubin pair a CPU (Vera) with a GPU
(Rubin) over a coherent high-bandwidth link (NVLink-C2C). Whether a kernel runs
fast then depends on its *arithmetic intensity* — FLOPs performed per byte moved:

    attainable FLOP/s = min( peak compute,  intensity x memory bandwidth )

Low-intensity kernels (vector add, SpMV) are *memory-bound* — limited by
bandwidth, which is exactly why these systems invest so heavily in HBM and
coherent interconnect. High-intensity kernels (dense matmul) are *compute-bound*.
The crossover is the "ridge point".
"""

from __future__ import annotations


def attainable(intensity: float, peak_flops: float, bandwidth: float) -> float:
    """Peak achievable FLOP/s for a given arithmetic intensity (FLOP/byte)."""
    return min(peak_flops, intensity * bandwidth)


def ridge_point(peak_flops: float, bandwidth: float) -> float:
    """Arithmetic intensity where a kernel stops being memory-bound."""
    return peak_flops / bandwidth


def is_memory_bound(intensity: float, peak_flops: float, bandwidth: float) -> bool:
    return intensity < ridge_point(peak_flops, bandwidth)


if __name__ == "__main__":
    peak = 50e12       # 50 TFLOP/s peak compute
    bw = 8e12          # 8 TB/s memory bandwidth
    ridge = ridge_point(peak, bw)

    print(f"Accelerator: {peak/1e12:.0f} TFLOP/s compute, {bw/1e12:.0f} TB/s "
          f"bandwidth")
    print(f"Ridge point: {ridge:.2f} FLOP/byte "
          f"(below = memory-bound, above = compute-bound)\n")

    kernels = [("vector add (AXPY)", 0.083), ("SpMV", 0.25),
               ("stencil", 0.5), ("FFT", 2.0), ("dense matmul (GEMM)", 16.0)]
    print(f"  {'kernel':<20}{'intensity':>10}{'GFLOP/s':>10}{'% peak':>8}  bound")
    for name, ai in kernels:
        perf = attainable(ai, peak, bw)
        bound = "memory" if is_memory_bound(ai, peak, bw) else "compute"
        print(f"  {name:<20}{ai:>10.3f}{perf/1e9:>10.0f}{perf/peak:>7.0%}  {bound}")

    # Why bandwidth matters: doubling it (more HBM / NVLink-C2C) only helps the
    # memory-bound kernels.
    print("\nEffect of doubling memory bandwidth (8 -> 16 TB/s):")
    for name, ai in [("vector add (AXPY)", 0.083), ("dense matmul (GEMM)", 16.0)]:
        before = attainable(ai, peak, bw)
        after = attainable(ai, peak, 2 * bw)
        print(f"  {name:<20}: {before/1e9:>8.0f} -> {after/1e9:>8.0f} GFLOP/s "
              f"({after/before:.1f}x)")
    print("\n  Memory-bound work scales with bandwidth; compute-bound work does")
    print("  not — the trade-off that shapes CPU+GPU superchip design.")
