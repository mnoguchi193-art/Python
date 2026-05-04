"""
itertools module — chain, islice, groupby, combinations, accumulate, etc.
"""

import itertools

# ── chain — flatten nested iterables ─────────────────────────────────────
flat = list(itertools.chain([1, 2], [3, 4], [5]))
print("chain:", flat)

# ── islice — lazy slicing ─────────────────────────────────────────────────
naturals = itertools.count(1)
first_10 = list(itertools.islice(naturals, 10))
print("islice (first 10 naturals):", first_10)

# ── cycle — round-robin assignments ──────────────────────────────────────
teams = ["Team A", "Team B", "Team C"]
assignments = list(zip(range(7), itertools.cycle(teams)))
print("Cycle assignments:", assignments)

# ── groupby — group sorted data ───────────────────────────────────────────
employees = [
    ("Alice", "Engineering"), ("Bob", "Engineering"),
    ("Carol", "Marketing"),   ("Dave", "Marketing"),
    ("Eve",   "Engineering"),
]
by_dept = sorted(employees, key=lambda e: e[1])
print("\nBy department:")
for dept, group in itertools.groupby(by_dept, key=lambda e: e[1]):
    print(f"  {dept}: {[e[0] for e in group]}")

# ── combinations / permutations / product ────────────────────────────────
items = ["A", "B", "C"]
print("\nCombinations(2):", list(itertools.combinations(items, 2)))
print("Permutations(2):", list(itertools.permutations(items, 2)))
print("Product(2):     ", list(itertools.product([0, 1], repeat=2)))

# ── accumulate — running total ────────────────────────────────────────────
monthly_sales = [120, 85, 130, 95, 110]
cumulative = list(itertools.accumulate(monthly_sales))
print("\nMonthly sales:    ", monthly_sales)
print("Cumulative total: ", cumulative)
