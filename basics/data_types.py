"""
Python Data Types — overview and common operations
"""

# ── Numeric types ──────────────────────────────────────────────────────────
x: int   = 42
y: float = 3.14
z: complex = 1 + 2j
print(f"int={x}  float={y}  complex={z}")
print(f"Division: 7/2={7/2}  Floor div: 7//2={7//2}  Mod: 7%2={7%2}")

# ── Strings ────────────────────────────────────────────────────────────────
s = "Hello, Python!"
print(s.upper(), s.count("l"), s.replace("Python", "World"))
print(f"f-string: {x * 2 = }")   # = syntax prints expression + value

# ── Boolean ───────────────────────────────────────────────────────────────
print(True and False, True or False, not True)
print(bool(0), bool(""), bool([]))   # falsy values

# ── None ──────────────────────────────────────────────────────────────────
val = None
print(val is None)

# ── List ──────────────────────────────────────────────────────────────────
lst = [1, 2, 3, 4, 5]
lst.append(6)
lst.insert(0, 0)
print("list:", lst, "| slice:", lst[2:5])

# ── Tuple (immutable) ─────────────────────────────────────────────────────
coords = (10, 20, 30)
x_coord, y_coord, *rest = coords   # unpacking
print("tuple:", coords, "| rest:", rest)

# ── Dict ──────────────────────────────────────────────────────────────────
person = {"name": "Alice", "age": 30}
person["city"] = "Tokyo"
print({k: v for k, v in person.items()})   # dict comprehension

# ── Set ───────────────────────────────────────────────────────────────────
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}
print("union:", a | b, "| intersection:", a & b, "| difference:", a - b)

# ── Type conversion ───────────────────────────────────────────────────────
print(int("123"), float("3.14"), str(42), list("abc"))
