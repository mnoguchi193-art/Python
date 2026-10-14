"""
Chemical Equation Balancing — stoichiometry as linear algebra

Balancing a reaction is really solving a linear system: every element must be
conserved, so the coefficients form the null space of the element-count matrix.
This module parses chemical formulas (including nested groups like Fe2(SO4)3),
builds that matrix, and solves it with exact rational arithmetic to recover the
smallest whole-number coefficients.
"""

from __future__ import annotations

import re
from collections import Counter
from fractions import Fraction
from math import gcd


def parse_formula(formula: str) -> Counter:
    """Count atoms of each element, handling parentheses and multipliers."""
    tokens = re.findall(r"[A-Z][a-z]?|\(|\)|\d+", formula)
    stack = [Counter()]
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == "(":
            stack.append(Counter())
        elif tok == ")":
            group = stack.pop()
            mult = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                mult = int(tokens[i + 1])
                i += 1
            for el, c in group.items():
                stack[-1][el] += c * mult
        elif not tok.isdigit():
            count = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                count = int(tokens[i + 1])
                i += 1
            stack[-1][tok] += count
        i += 1
    return stack[0]


def balance(reactants: list[str], products: list[str]) -> list[int]:
    """Return integer coefficients for [reactants..., products...]."""
    species = reactants + products
    parsed = [parse_formula(s) for s in species]
    elements = sorted(set().union(*(set(p) for p in parsed)))

    # Element-conservation matrix (products negated), reduced to RREF.
    M = [[Fraction(p.get(el, 0)) * (1 if idx < len(reactants) else -1)
          for idx, p in enumerate(parsed)] for el in elements]
    n = len(species)
    pivots, r = [], 0
    for c in range(n):
        piv = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        M[r] = [x / M[r][c] for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                M[i] = [a - M[i][c] * b for a, b in zip(M[i], M[r])]
        pivots.append(c)
        r += 1

    free = [c for c in range(n) if c not in pivots][0]   # one free coefficient
    x = [Fraction(0)] * n
    x[free] = Fraction(1)
    for ri, pc in enumerate(pivots):
        x[pc] = -M[ri][free]

    lcm = 1
    for v in x:
        lcm = lcm * v.denominator // gcd(lcm, v.denominator)
    ints = [int(v * lcm) for v in x]
    g = 0
    for v in ints:
        g = gcd(g, abs(v))
    ints = [v // g for v in ints]
    return [-v for v in ints] if ints[0] < 0 else ints


def format_equation(reactants, products, coeffs) -> str:
    def side(species, cs):
        return " + ".join((f"{c} " if c != 1 else "") + s
                          for s, c in zip(species, cs))
    nr = len(reactants)
    return f"{side(reactants, coeffs[:nr])} -> {side(products, coeffs[nr:])}"


if __name__ == "__main__":
    reactions = [
        (["H2", "O2"], ["H2O"]),
        (["Fe", "O2"], ["Fe2O3"]),
        (["C3H8", "O2"], ["CO2", "H2O"]),
        (["Ca(OH)2", "H3PO4"], ["Ca3(PO4)2", "H2O"]),
    ]
    print("Balancing chemical equations via linear algebra:\n")
    for reactants, products in reactions:
        coeffs = balance(reactants, products)
        print(f"  {format_equation(reactants, products, coeffs)}")
        print(f"      coefficients: {coeffs}")
