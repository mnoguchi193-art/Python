"""
Number Theory — the deep structure of the integers

From the Sieve of Eratosthenes to the Prime Number Theorem, number theory studies
the primes and modular arithmetic that underpin modern cryptography. This module
gathers the essentials — prime generation, the extended Euclidean algorithm and
modular inverses, Euler's totient, Fermat's little theorem — and checks the
celebrated estimate pi(x) ~ x / ln(x) for how primes thin out.
"""

from __future__ import annotations

from math import log


def sieve(n: int) -> list[int]:
    """All primes up to n via the Sieve of Eratosthenes."""
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return [i for i, p in enumerate(is_prime) if p]


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Return (g, x, y) with a*x + b*y = g = gcd(a, b)."""
    if b == 0:
        return a, 1, 0
    g, x, y = extended_gcd(b, a % b)
    return g, y, x - (a // b) * y


def mod_inverse(a: int, m: int) -> int:
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError("inverse does not exist")
    return x % m


def euler_totient(n: int) -> int:
    """Count integers in [1, n] coprime to n."""
    result, p, m = n, 2, n
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            result -= result // p
        p += 1
    if m > 1:
        result -= result // m
    return result


if __name__ == "__main__":
    print("Primes up to 50:")
    print(f"  {sieve(50)}\n")

    g, x, y = extended_gcd(240, 46)
    print(f"  extended gcd(240, 46): gcd={g}, 240*{x} + 46*{y} = {240*x + 46*y}")
    print(f"  modular inverse of 3 mod 11: {mod_inverse(3, 11)} "
          f"(3*4 = 12 = 1 mod 11)")
    print(f"  Euler totient phi(36) = {euler_totient(36)}\n")

    print("  Fermat's little theorem (a^(p-1) = 1 mod p for prime p):")
    for a in (2, 3, 5):
        print(f"    {a}^16 mod 17 = {pow(a, 16, 17)}")

    print("\n  Prime Number Theorem: pi(x) vs x/ln(x)")
    print(f"  {'x':>8}  {'pi(x)':>8}  {'x/ln x':>10}  {'ratio':>7}")
    for x in (100, 1000, 10000, 100000):
        pi_x = len(sieve(x))
        approx = x / log(x)
        print(f"  {x:>8}  {pi_x:>8}  {approx:>10.1f}  {pi_x / approx:>7.3f}")
    print("\n  The ratio approaches 1 — primes thin out like 1/ln(x).")
