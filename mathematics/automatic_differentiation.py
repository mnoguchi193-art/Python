"""
Automatic Differentiation — exact derivatives by dual numbers

The mathematical engine inside every deep-learning framework. Forward-mode
autodiff augments each number with an infinitesimal part (a "dual number"
a + b*eps where eps^2 = 0). Pushing x + 1*eps through any computation makes the
dual part come out as the exact derivative — no finite-difference error, no
hand-derived formulas. Here it is in a few lines of operator overloading, then
used to drive Newton's method.
"""

from __future__ import annotations

import math


class Dual:
    def __init__(self, value: float, deriv: float = 0.0):
        self.value = value
        self.deriv = deriv

    @staticmethod
    def _coerce(x):
        return x if isinstance(x, Dual) else Dual(x, 0.0)

    def __add__(self, o):
        o = self._coerce(o)
        return Dual(self.value + o.value, self.deriv + o.deriv)
    __radd__ = __add__

    def __sub__(self, o):
        o = self._coerce(o)
        return Dual(self.value - o.value, self.deriv - o.deriv)

    def __rsub__(self, o):
        return self._coerce(o).__sub__(self)

    def __mul__(self, o):
        o = self._coerce(o)
        return Dual(self.value * o.value,
                    self.deriv * o.value + self.value * o.deriv)
    __rmul__ = __mul__

    def __truediv__(self, o):
        o = self._coerce(o)
        return Dual(self.value / o.value,
                    (self.deriv * o.value - self.value * o.deriv) / o.value ** 2)

    def __pow__(self, n: float):
        return Dual(self.value ** n, n * self.value ** (n - 1) * self.deriv)

    def __neg__(self):
        return Dual(-self.value, -self.deriv)


def sin(d: Dual) -> Dual:
    return Dual(math.sin(d.value), math.cos(d.value) * d.deriv)


def cos(d: Dual) -> Dual:
    return Dual(math.cos(d.value), -math.sin(d.value) * d.deriv)


def exp(d: Dual) -> Dual:
    return Dual(math.exp(d.value), math.exp(d.value) * d.deriv)


def derivative(f, x: float) -> float:
    return f(Dual(x, 1.0)).deriv


def newton(f, x0: float, iterations: int = 12) -> float:
    """Find a root of f using derivatives supplied automatically by autodiff."""
    x = x0
    for _ in range(iterations):
        d = f(Dual(x, 1.0))
        x = x - d.value / d.deriv
    return x


if __name__ == "__main__":
    print("Automatic differentiation via dual numbers\n")

    f = lambda x: x ** 3 + 2 * x ** 2 + 1
    print(f"  f(x) = x^3 + 2x^2 + 1")
    print(f"    f'(2)  autodiff = {derivative(f, 2.0):.6f}   "
          f"analytic 3x^2+4x = {3 * 4 + 4 * 2}")

    g = lambda x: sin(x ** 2)
    print(f"\n  g(x) = sin(x^2)")
    print(f"    g'(1)  autodiff = {derivative(g, 1.0):.6f}   "
          f"analytic 2x*cos(x^2) = {2 * math.cos(1):.6f}")

    print("\n  Newton's method for sqrt(2) (root of x^2 - 2), derivative by AD:")
    root = newton(lambda x: x ** 2 - 2, x0=1.0)
    print(f"    result = {root:.12f}   (math.sqrt(2) = {math.sqrt(2):.12f})")
    print("\n  Exact to machine precision — the same trick scales to the millions")
    print("  of parameters in a neural network (reverse-mode backprop).")
