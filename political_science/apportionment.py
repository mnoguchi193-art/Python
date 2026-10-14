"""
Apportionment — turning populations into seats (and its paradoxes)

How many legislative seats does each state (or party) get? There is no perfect
method. Highest-averages rules (D'Hondt favors large states, Sainte-Lague is more
proportional) avoid paradoxes but can over-reward big players; the largest-
remainder (Hamilton) method matches quotas closely but suffers the *Alabama
paradox*, where adding a seat to the whole house can cost a state one of its seats.
"""

from __future__ import annotations


def highest_averages(pops: dict[str, int], seats: int, divisor) -> dict[str, int]:
    alloc = {k: 0 for k in pops}
    for _ in range(seats):
        winner = max(pops, key=lambda k: pops[k] / divisor(alloc[k]))
        alloc[winner] += 1
    return alloc


def dhondt(pops, seats):
    return highest_averages(pops, seats, lambda s: s + 1)


def sainte_lague(pops, seats):
    return highest_averages(pops, seats, lambda s: 2 * s + 1)


def hamilton(pops: dict[str, int], seats: int) -> dict[str, int]:
    """Largest-remainder method."""
    total = sum(pops.values())
    quotas = {k: pops[k] / total * seats for k in pops}
    alloc = {k: int(q) for k, q in quotas.items()}
    leftover = seats - sum(alloc.values())
    order = sorted(pops, key=lambda k: quotas[k] - alloc[k], reverse=True)
    for k in order[:leftover]:
        alloc[k] += 1
    return alloc


if __name__ == "__main__":
    parties = {"A": 100_000, "B": 80_000, "C": 30_000, "D": 21_000}
    seats = 10
    print(f"Allocating {seats} seats among parties {parties}\n")
    print(f"  {'method':<16}" + "".join(f"{k:>4}" for k in parties))
    for name, fn in (("D'Hondt", dhondt), ("Sainte-Lague", sainte_lague),
                     ("Hamilton", hamilton)):
        a = fn(parties, seats)
        print(f"  {name:<16}" + "".join(f"{a[k]:>4}" for k in parties))
    print("  (D'Hondt rounds toward big parties; Sainte-Lague is more even.)\n")

    # The Alabama paradox under Hamilton's method.
    states = {"A": 6, "B": 6, "C": 2}
    print(f"Alabama paradox (Hamilton), states {states}:")
    for house in (10, 11):
        a = hamilton(states, house)
        print(f"  house size {house}: {a}")
    print("  Enlarging the house from 10 to 11 seats DROPS state C from 2 to 1 —")
    print("  more total seats, fewer for C. That is the Alabama paradox.")
