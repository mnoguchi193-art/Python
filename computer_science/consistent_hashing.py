"""
Consistent Hashing — the backbone of distributed systems

How do distributed caches and databases (Memcached, Cassandra, DynamoDB) spread
keys across servers so that adding or removing a server moves as *few* keys as
possible? Naive `hash(key) % N` reshuffles almost everything when N changes.
Consistent hashing places servers and keys on a ring; a key belongs to the next
server clockwise, so only ~1/N of keys move when the cluster resizes.

Virtual nodes (replicas) smooth out the load across servers.
"""

from __future__ import annotations

import bisect
import hashlib


class ConsistentHashRing:
    def __init__(self, nodes: list[str] | None = None, vnodes: int = 150):
        self.vnodes = vnodes
        self._ring: dict[int, str] = {}
        self._sorted: list[int] = []
        for node in nodes or []:
            self.add_node(node)

    @staticmethod
    def _hash(key: str) -> int:
        return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")

    def add_node(self, node: str) -> None:
        for v in range(self.vnodes):
            h = self._hash(f"{node}#{v}")
            self._ring[h] = node
            bisect.insort(self._sorted, h)

    def remove_node(self, node: str) -> None:
        for v in range(self.vnodes):
            h = self._hash(f"{node}#{v}")
            del self._ring[h]
            self._sorted.remove(h)

    def get_node(self, key: str) -> str:
        h = self._hash(key)
        i = bisect.bisect(self._sorted, h) % len(self._sorted)
        return self._ring[self._sorted[i]]


if __name__ == "__main__":
    keys = [f"key{i}" for i in range(10_000)]
    ring = ConsistentHashRing(["A", "B", "C", "D"])

    before = {k: ring.get_node(k) for k in keys}
    counts: dict[str, int] = {}
    for node in before.values():
        counts[node] = counts.get(node, 0) + 1
    print("Consistent hashing — 10,000 keys over 4 nodes")
    print(f"  load per node: {dict(sorted(counts.items()))}\n")

    ring.add_node("E")
    after = {k: ring.get_node(k) for k in keys}
    moved = sum(before[k] != after[k] for k in keys)
    print(f"  added node E: {moved:,} keys moved "
          f"({moved / len(keys):.1%}, ideal ~1/5 = 20%)")

    # Contrast with naive modulo hashing.
    def modulo_node(key, n):
        return ring._hash(key) % n

    moved_mod = sum(modulo_node(k, 4) != modulo_node(k, 5) for k in keys)
    print(f"  naive hash % N: {moved_mod:,} keys moved "
          f"({moved_mod / len(keys):.1%}) — almost everything reshuffles")
