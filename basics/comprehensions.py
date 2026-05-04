"""
Python Comprehensions — list, dict, set, generator expressions
"""

import sys

# ── List comprehension ────────────────────────────────────────────────────
squares = [x ** 2 for x in range(10)]
evens   = [x for x in range(20) if x % 2 == 0]
print("Squares:", squares)
print("Evens:  ", evens)

# ── Dict comprehension ────────────────────────────────────────────────────
word_lengths = {word: len(word) for word in ["apple", "banana", "cherry"]}
inverted     = {v: k for k, v in word_lengths.items()}
print("Lengths:", word_lengths)
print("Inverted:", inverted)

# ── Set comprehension ─────────────────────────────────────────────────────
letters = {ch.lower() for ch in "Hello World" if ch.isalpha()}
print("Unique letters:", sorted(letters))

# ── Nested comprehension — matrix transpose ───────────────────────────────
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
transposed = [[row[i] for row in matrix] for i in range(3)]
print("Original:   ", matrix)
print("Transposed: ", transposed)

# ── Conditional comprehension ─────────────────────────────────────────────
categorized = ["even" if x % 2 == 0 else "odd" for x in range(6)]
print("Categories:", categorized)

# ── Generator expression vs list — memory comparison ─────────────────────
n = 1_000_000
list_size = sys.getsizeof([x ** 2 for x in range(n)])
gen_size  = sys.getsizeof(x ** 2 for x in range(n))
print(f"List ({n} elements): {list_size:,} bytes")
print(f"Generator expression: {gen_size} bytes")
