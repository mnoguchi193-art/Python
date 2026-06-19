"""
CRDTs — distributed data that merges without coordination

How can replicas of the same data (a shared counter, a collaborative document)
accept edits offline and on different servers, then reconcile to one consistent
state with no locks or consensus? Conflict-free Replicated Data Types guarantee
it: their merge operation is commutative, associative and idempotent, so replicas
that have seen the same updates converge regardless of order or duplication.

Shown here: a grow-only counter (G-Counter) and a grow-only set (G-Set).
"""

from __future__ import annotations


class GCounter:
    """A counter that each node increments in its own slot; value = total."""

    def __init__(self, node: str):
        self.node = node
        self.counts: dict[str, int] = {}

    def increment(self, amount: int = 1) -> None:
        self.counts[self.node] = self.counts.get(self.node, 0) + amount

    def value(self) -> int:
        return sum(self.counts.values())

    def merge(self, other: "GCounter") -> None:
        for node, count in other.counts.items():
            self.counts[node] = max(self.counts.get(node, 0), count)


class GSet:
    """A set that only grows; merge is union."""

    def __init__(self):
        self.items: set = set()

    def add(self, item) -> None:
        self.items.add(item)

    def merge(self, other: "GSet") -> None:
        self.items |= other.items


if __name__ == "__main__":
    # Three replicas of a "likes" counter increment independently while offline.
    a, b, c = GCounter("A"), GCounter("B"), GCounter("C")
    a.increment(3)
    b.increment(5)
    c.increment(2)

    print("G-Counter: three replicas increment offline (3, 5, 2)\n")
    # Reconcile in arbitrary, even repeated, order — all converge to 10.
    a.merge(b); a.merge(c)
    c.merge(a); c.merge(a)          # duplicate merges are harmless (idempotent)
    b.merge(c); b.merge(a)
    print(f"  replica A: {a.value()}")
    print(f"  replica B: {b.value()}")
    print(f"  replica C: {c.value()}")
    print(f"  all equal? {a.value() == b.value() == c.value()} (converged to 10)\n")

    # A collaborative tag set edited on two replicas.
    x, y = GSet(), GSet()
    x.add("urgent"); x.add("bug")
    y.add("bug"); y.add("feature")
    x.merge(y); y.merge(x)
    print("G-Set: two replicas add tags, then merge")
    print(f"  replica X: {sorted(x.items)}")
    print(f"  replica Y: {sorted(y.items)}")
    print(f"  converged? {x.items == y.items}")
    print("\n  No locks, no central server — eventual consistency by construction.")
