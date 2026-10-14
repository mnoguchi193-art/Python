"""
Atomic container refill — replace contents in place without breaking shared
references, and without corrupting state on failure.

Principle: build the new contents FIRST, then commit with an operation that
cannot fail ("prepare, then commit").
"""

from collections import deque

# ── rebinding vs in-place replacement ─────────────────────────────────────
history = [1, 2, 3]
alias = history                # another module holds this reference

history = [10, 20]             # rebinding: alias is left behind
print("After rebinding, alias:", alias)

history = alias
history[:] = [10, 20]          # slice assignment: same object, new contents
print("After slice assignment, alias:", alias)
print("Same object?", history is alias)

# deque/dict/set have no slice assignment — use clear + refill instead:
#   d.clear(); d.extend(new_items)     (deque)
#   m.clear(); m.update(new_mapping)   (dict)

# ── pitfall: lazy generator reading the container being refilled ──────────
nums = [1, 2, 3, 4, 5, 6]
gen = (n for n in nums if n % 2 == 0)  # lazy — nothing read yet
nums.clear()                           # emptied BEFORE gen runs
nums.extend(gen)                       # gen now sees an empty list
print("\nclear-then-extend from own generator:", nums, "(silently empty!)")

# deque at least detects the bug instead of silently losing data
nums_dq = deque([1, 2, 3, 4, 5, 6])
gen = (n for n in nums_dq if n % 2 == 0)
nums_dq.clear()
try:
    nums_dq.extend(gen)
except RuntimeError as e:
    print("deque raises:", e)

# ── pitfall: exception mid-refill leaves half-filled state ────────────────
def risky_source():
    yield 1
    yield 2
    raise ValueError("boom")

target = deque([100, 200, 300])
try:
    target.clear()                     # original data destroyed first...
    target.extend(risky_source())      # ...then refill fails halfway
except ValueError:
    pass
print("\nclear-first ordering after failure:", list(target))

# ── fix: prepare, then commit ─────────────────────────────────────────────
target = deque([100, 200, 300])
try:
    new_items = list(risky_source())   # 1) prepare — may fail, target untouched
    target.clear()                     # 2) commit — cannot fail
    target.extend(new_items)
except ValueError:
    pass
print("prepare-first ordering after failure:", list(target), "(intact)")

# list slice assignment does prepare-then-commit internally, so even a
# self-referencing generator is safe:
lst = [1, 2, 3, 4, 5, 6]
lst[:] = (n for n in lst if n % 2 == 0)
print("slice assignment from own generator:", lst)
