"""
Python Functions — defaults, *args/**kwargs, closures, decorators, generators
"""

import time
import functools


# ── Default args, *args, **kwargs ─────────────────────────────────────────
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

def summarize(*args: float, label: str = "values") -> str:
    return f"{label}: sum={sum(args):.1f}, count={len(args)}"

def build_profile(**kwargs: str) -> dict:
    return dict(kwargs)

print(greet("Alice"))
print(summarize(1.0, 2.5, 3.0, label="scores"))
print(build_profile(name="Bob", city="Osaka"))


# ── First-class functions ─────────────────────────────────────────────────
def apply(func, values: list) -> list:
    return [func(v) for v in values]

print(apply(str.upper, ["hello", "world"]))


# ── Closures ──────────────────────────────────────────────────────────────
def make_multiplier(factor: int):
    def multiply(x):
        return x * factor   # closes over `factor`
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5), triple(5))


# ── Decorators ────────────────────────────────────────────────────────────
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.perf_counter() - t0:.6f}s")
        return result
    return wrapper

def retry(max_attempts: int = 3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"Attempt {attempt} failed: {e}, retrying...")
        return wrapper
    return decorator

@timer
def slow_sum(n: int) -> int:
    return sum(range(n))

slow_sum(100_000)


# ── Generator functions ───────────────────────────────────────────────────
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

gen = fibonacci()
print("First 10 Fibonacci:", [next(gen) for _ in range(10)])
