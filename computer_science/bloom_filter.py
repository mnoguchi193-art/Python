"""
Bloom Filter — probabilistic set membership

A space-efficient structure used throughout databases, caches and networks. It
answers "have I seen this?" using a bit array and several hash functions. It can
yield false positives but *never* false negatives — a "no" is always correct.
The trade is dramatic: it stores membership in a few bits per item instead of the
items themselves, with a false-positive rate you tune in advance.
"""

from __future__ import annotations

import hashlib
import math


class BloomFilter:
    def __init__(self, capacity: int, error_rate: float = 0.01):
        self.capacity = capacity
        self.error_rate = error_rate
        # Optimal bit-array size m and number of hash functions k.
        self.m = max(1, int(-capacity * math.log(error_rate) / math.log(2) ** 2))
        self.k = max(1, round(self.m / capacity * math.log(2)))
        self.bits = bytearray((self.m + 7) // 8)

    def _indices(self, item: str) -> list[int]:
        digest = hashlib.sha256(item.encode()).digest()
        h1 = int.from_bytes(digest[:8], "big")
        h2 = int.from_bytes(digest[8:16], "big") | 1   # ensure odd step
        return [(h1 + i * h2) % self.m for i in range(self.k)]

    def add(self, item: str) -> None:
        for idx in self._indices(item):
            self.bits[idx >> 3] |= 1 << (idx & 7)

    def __contains__(self, item: str) -> bool:
        return all(self.bits[idx >> 3] & (1 << (idx & 7))
                   for idx in self._indices(item))


if __name__ == "__main__":
    n = 1000
    bf = BloomFilter(capacity=n, error_rate=0.01)
    members = [f"word{i}" for i in range(n)]
    for w in members:
        bf.add(w)

    print(f"Bloom filter: {n} items, target error {bf.error_rate:.0%}")
    print(f"  bit array: {bf.m} bits ({bf.m / 8 / 1024:.1f} KB), "
          f"{bf.k} hash functions")
    print(f"  ~{bf.m / n:.1f} bits per item\n")

    # No false negatives: every inserted item is reported present.
    print(f"  all members found?  {all(w in bf for w in members)}")

    # Measure the empirical false-positive rate on unseen items.
    trials = 100_000
    false_positives = sum(f"absent{i}" in bf for i in range(trials))
    print(f"  empirical false-positive rate: {false_positives / trials:.3%} "
          f"(target {bf.error_rate:.3%})")
