"""
素数定理 (Prime Number Theorem) — π(x) の近似アルゴリズム

PNT:    π(x) ~ x / ln(x)         (基本形)
        π(x) ~ Li(x) = ∫₂ˣ dt/ln(t)   (より精度の高い近似)

stdlib のみ使用。
"""

from __future__ import annotations

import math


# ── π(x): 素数計数関数 (エラトステネスの篩で厳密に求める) ───────────────────
def sieve_of_eratosthenes(n: int) -> list[int]:
    """n 以下の素数を昇順で返す。"""
    if n < 2:
        return []
    is_prime = bytearray(b"\x01") * (n + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, math.isqrt(n) + 1):
        if is_prime[i]:
            is_prime[i * i :: i] = bytearray(len(is_prime[i * i :: i]))
    return [i for i, p in enumerate(is_prime) if p]


def prime_pi(n: int) -> int:
    """π(n): n 以下の素数の個数 (厳密値)。"""
    return len(sieve_of_eratosthenes(n))


# ── 近似 1: x / ln(x) ────────────────────────────────────────────────────
def pnt_basic(x: float) -> float:
    """素数定理の基本形 x / ln(x)。"""
    if x < 2:
        return 0.0
    return x / math.log(x)


# ── 近似 2: 対数積分 Li(x) ───────────────────────────────────────────────
def logarithmic_integral(x: float, steps: int = 10_000) -> float:
    """
    Li(x) = ∫₂ˣ dt / ln(t)
    シンプソン則による数値積分 (steps は偶数化して使用)。
    """
    if x <= 2:
        return 0.0
    if steps % 2:
        steps += 1
    a, b = 2.0, float(x)
    h = (b - a) / steps
    total = 1.0 / math.log(a) + 1.0 / math.log(b)
    for k in range(1, steps):
        t = a + k * h
        total += (4.0 if k % 2 else 2.0) / math.log(t)
    return total * h / 3.0


# ── 表示 ─────────────────────────────────────────────────────────────────
def relative_error(approx: float, exact: int) -> float:
    return (approx - exact) / exact * 100.0 if exact else float("nan")


def compare(upper_bounds: list[int]) -> None:
    """π(x), x/ln(x), Li(x) を表で比較する。"""
    header = f"{'x':>10} | {'π(x)':>10} | {'x/ln(x)':>14} | {'err%':>7} | {'Li(x)':>14} | {'err%':>7}"
    print(header)
    print("-" * len(header))
    for x in upper_bounds:
        pi_x = prime_pi(x)
        basic = pnt_basic(x)
        li = logarithmic_integral(x)
        print(
            f"{x:>10} | {pi_x:>10} | {basic:>14.2f} | "
            f"{relative_error(basic, pi_x):>6.2f}% | "
            f"{li:>14.2f} | {relative_error(li, pi_x):>6.2f}%"
        )


if __name__ == "__main__":
    print("素数定理 (Prime Number Theorem) — 近似精度の比較\n")
    compare([10, 100, 1_000, 10_000, 100_000, 1_000_000])

    print("\n参考: 100 以下の素数")
    print(sieve_of_eratosthenes(100))
