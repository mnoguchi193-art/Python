"""
Big-data streaming algorithms / ビッグデータ向けストリーミングアルゴリズム

When data is too large to fit in memory, we process it in a single pass using
sublinear space. These sketches trade a little accuracy for huge memory
savings — the workhorses behind large-scale social-data analytics.

    reservoir_sample   uniform sample of fixed size from an unbounded stream
    MisraGries         heavy hitters (frequent items)
    BloomFilter        approximate set membership (no false negatives)
    HyperLogLog        count distinct elements in tiny space
"""

import hashlib
import math
import random


def reservoir_sample(stream, k: int, seed: int | None = None) -> list:
    """Algorithm R: a uniform sample of k items in O(k) space, one pass."""
    rng = random.Random(seed)
    reservoir: list = []
    for i, item in enumerate(stream):
        if i < k:
            reservoir.append(item)
        else:
            j = rng.randint(0, i)
            if j < k:
                reservoir[j] = item
    return reservoir


class MisraGries:
    """Find items occurring more than n/(k+1) times using k counters."""

    def __init__(self, k: int = 8) -> None:
        self.k = k
        self.counters: dict = {}

    def add(self, item) -> None:
        if item in self.counters:
            self.counters[item] += 1
        elif len(self.counters) < self.k:
            self.counters[item] = 1
        else:
            for key in list(self.counters):
                self.counters[key] -= 1
                if self.counters[key] == 0:
                    del self.counters[key]

    def candidates(self) -> dict:
        return dict(self.counters)


class BloomFilter:
    """Approximate membership: no false negatives, tunable false positives."""

    def __init__(self, capacity: int, error_rate: float = 0.01) -> None:
        self.size = max(1, int(-capacity * math.log(error_rate) / math.log(2) ** 2))
        self.hashes = max(1, round(self.size / capacity * math.log(2)))
        self.bits = bytearray((self.size + 7) // 8)

    def _positions(self, item) -> list[int]:
        data = str(item).encode()
        h1 = int.from_bytes(hashlib.sha1(data).digest()[:8], "big")
        h2 = int.from_bytes(hashlib.md5(data).digest()[:8], "big") | 1
        return [(h1 + i * h2) % self.size for i in range(self.hashes)]

    def add(self, item) -> None:
        for pos in self._positions(item):
            self.bits[pos // 8] |= 1 << (pos % 8)

    def __contains__(self, item) -> bool:
        return all(
            self.bits[pos // 8] & (1 << (pos % 8)) for pos in self._positions(item)
        )


class HyperLogLog:
    """Estimate the number of distinct items in O(2^b) registers."""

    def __init__(self, b: int = 10) -> None:
        self.b = b
        self.m = 1 << b
        self.registers = [0] * self.m

    def add(self, item) -> None:
        h = int.from_bytes(hashlib.sha1(str(item).encode()).digest()[:8], "big")
        index = h >> (64 - self.b)              # top b bits choose a register
        w = h & ((1 << (64 - self.b)) - 1)      # remaining bits
        rho = (64 - self.b) - w.bit_length() + 1  # position of leftmost 1-bit
        self.registers[index] = max(self.registers[index], rho)

    def count(self) -> float:
        if self.m >= 128:
            alpha = 0.7213 / (1 + 1.079 / self.m)
        else:
            alpha = {16: 0.673, 32: 0.697, 64: 0.709}.get(self.m, 0.7213)
        raw = alpha * self.m**2 / sum(2.0**-r for r in self.registers)
        zeros = self.registers.count(0)
        if raw <= 2.5 * self.m and zeros:
            return self.m * math.log(self.m / zeros)  # linear counting
        return raw


if __name__ == "__main__":
    stream = list(range(1000))
    print("Reservoir sample (k=5):", reservoir_sample(stream, 5, seed=1))

    mg = MisraGries(k=3)
    for item in ["a"] * 50 + ["b"] * 30 + ["c", "d", "e"] * 5:
        mg.add(item)
    print("Heavy hitters:", mg.candidates())

    bf = BloomFilter(capacity=1000)
    for x in range(500):
        bf.add(x)
    print(f"42 in filter:   {42 in bf}")
    print(f"9999 in filter: {9999 in bf}  (expected False)")

    hll = HyperLogLog(b=10)
    for x in range(10000):
        hll.add(x)
    estimate = hll.count()
    print(f"HLL distinct estimate: {estimate:.0f}  (true 10000, "
          f"error {abs(estimate - 10000) / 10000 * 100:.1f}%)")
