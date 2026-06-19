"""
HyperLogLog — counting millions of distinct items in kilobytes

How many *unique* users visited today? Storing every id is infeasible at scale,
so systems like Redis and analytics databases use HyperLogLog: a probabilistic
cardinality estimator. It hashes each item, uses the first bits to pick a
register and the run of leading zeros in the rest as evidence of how many
distinct values have been seen, and combines the registers with a harmonic mean.
The result estimates cardinality within ~1% using a few KB, regardless of stream
size.
"""

from __future__ import annotations

import hashlib
import math


class HyperLogLog:
    def __init__(self, precision: int = 14):
        self.p = precision
        self.m = 1 << precision
        self.registers = [0] * self.m
        if self.m == 16:
            self.alpha = 0.673
        elif self.m == 32:
            self.alpha = 0.697
        elif self.m == 64:
            self.alpha = 0.709
        else:
            self.alpha = 0.7213 / (1 + 1.079 / self.m)

    def add(self, item) -> None:
        h = int.from_bytes(
            hashlib.blake2b(str(item).encode(), digest_size=8).digest(), "big")
        index = h >> (64 - self.p)
        w = h & ((1 << (64 - self.p)) - 1)
        bits = 64 - self.p
        rank = bits + 1 if w == 0 else bits - w.bit_length() + 1
        self.registers[index] = max(self.registers[index], rank)

    def count(self) -> int:
        inv_sum = sum(2.0 ** -r for r in self.registers)
        estimate = self.alpha * self.m ** 2 / inv_sum
        if estimate <= 2.5 * self.m:                       # small-range correction
            zeros = self.registers.count(0)
            if zeros:
                estimate = self.m * math.log(self.m / zeros)
        return round(estimate)


if __name__ == "__main__":
    hll = HyperLogLog(precision=14)
    true_count = 200_000
    for i in range(true_count):
        hll.add(f"user-{i}")
        hll.add(f"user-{i}")        # duplicates must not inflate the count

    estimate = hll.count()
    error = abs(estimate - true_count) / true_count
    print("HyperLogLog cardinality estimation\n")
    print(f"  true distinct items : {true_count:,}")
    print(f"  estimated           : {estimate:,}")
    print(f"  error               : {error:.2%}")
    print(f"  registers           : {hll.m:,} bytes (~{hll.m / 1024:.0f} KB)")
    print(f"  exact storage would need ~{true_count * 12 / 1024:.0f} KB of ids\n")
    print("  A near-exact unique count in a fixed few KB — independent of how")
    print("  many billions of items stream through.")
