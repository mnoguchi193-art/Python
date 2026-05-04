"""
Python Control Flow — if/elif/else, loops, match/case, exceptions
"""

# ── if / elif / else ──────────────────────────────────────────────────────
score = 75
if score >= 90:
    grade = "A"
elif score >= 75:
    grade = "B"
elif score >= 60:
    grade = "C"
else:
    grade = "F"
print(f"Score {score} → Grade {grade}")

# Walrus operator := (Python 3.8+)
data = [1, 3, 5, 7, 9]
if (n := len(data)) > 4:
    print(f"Long list: {n} elements")

# ── for / while ───────────────────────────────────────────────────────────
for i in range(5):
    if i == 3:
        continue
    print(i, end=" ")
print()

# for...else — else runs when loop finishes without break
for num in [2, 4, 6, 8]:
    if num % 2 != 0:
        print("Odd found!")
        break
else:
    print("All even")

# ── match / case (Python 3.10+) ───────────────────────────────────────────
command = "quit"
match command:
    case "start":
        print("Starting...")
    case "stop" | "quit":
        print("Stopping...")
    case _:
        print(f"Unknown command: {command}")

# ── Exception handling ────────────────────────────────────────────────────
class NegativeValueError(ValueError):
    pass

def safe_sqrt(n: float) -> float:
    if n < 0:
        raise NegativeValueError(f"Cannot take sqrt of {n}")
    return n ** 0.5

for val in [4.0, -1.0, "text"]:
    try:
        result = safe_sqrt(val)  # type: ignore
    except NegativeValueError as e:
        print(f"Domain error: {e}")
    except TypeError as e:
        print(f"Type error: {e}")
    else:
        print(f"sqrt({val}) = {result:.4f}")
    finally:
        pass  # cleanup would go here
