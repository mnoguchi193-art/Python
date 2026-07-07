"""
Immutability — make invalid states unrepresentable.

Guideline: small VALUES (config, coordinates, IDs, records) should be
immutable; large STATE stays mutable but transitions atomically
(see atomic_refill_demo.py / atomic_file_write_demo.py).
"""

from dataclasses import FrozenInstanceError, dataclass, replace
from types import MappingProxyType

# ── frozen dataclass: a value that cannot change ──────────────────────────
@dataclass(frozen=True)
class Config:
    host: str
    port: int


c1 = Config("example.com", 443)
try:
    c1.port = 8080
except FrozenInstanceError:
    print("Assignment to frozen dataclass: FrozenInstanceError")

c2 = replace(c1, port=8080)        # "modification" = new object
print("replace():", c1, "->", c2)

# Immutable values are hashable → usable as dict keys / set members
routing = {c1: "primary", c2: "fallback"}
print("As dict key:", routing[Config("example.com", 443)])

# ── pitfall: immutability is shallow ──────────────────────────────────────
@dataclass(frozen=True)
class Team:
    name: str
    members: list                  # mutable object inside a frozen shell!


t = Team("Alpha", ["Alice", "Bob"])
t.members.append("Mallory")        # attribute rebinding is blocked, but
print("\nFrozen yet mutated:", t)  # the list's contents are not

# Fix: freeze all the way down (list→tuple, set→frozenset, dict→proxy)
@dataclass(frozen=True)
class SafeTeam:
    name: str
    members: tuple


print("Deep-frozen:", SafeTeam("Alpha", ("Alice", "Bob")))

# ── putting it together: immutable values, atomic state ──────────────────
@dataclass(frozen=True)
class OrderLine:
    sku: str
    qty: int

    def __post_init__(self):
        if self.qty <= 0:          # invalid values cannot even be created
            raise ValueError(f"qty must be positive: {self.qty}")


class Inventory:
    """Mutable state with a single atomic transition path."""

    def __init__(self, stock: dict):
        self._stock = dict(stock)

    @property
    def stock(self):
        return MappingProxyType(self._stock)   # read-only view for outsiders

    def commit_order(self, lines: tuple) -> None:
        """Apply all lines, or none."""
        new = dict(self._stock)                # 1) copy
        for line in lines:                     # 2) validate on the copy
            remaining = new.get(line.sku, 0) - line.qty
            if remaining < 0:
                raise ValueError(f"out of stock: {line.sku}")
            new[line.sku] = remaining
        self._stock = new                      # 3) commit — atomic swap


inv = Inventory({"apple": 10, "banana": 3})
inv.commit_order((OrderLine("apple", 2), OrderLine("banana", 1)))
print("\nOrder committed:", dict(inv.stock))

try:                                           # line 1 fits, line 2 doesn't
    inv.commit_order((OrderLine("apple", 5), OrderLine("banana", 99)))
except ValueError as e:
    print("Order rejected:", e)
print("State after rejection:", dict(inv.stock), "(apple -5 rolled back too)")

try:
    inv.stock["apple"] = 9999                  # no back door
except TypeError:
    print("Direct mutation from outside: TypeError")
