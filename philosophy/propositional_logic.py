"""
Propositional Logic — validity, entailment and truth tables

Formal logic mechanized: build propositional formulas, evaluate them under every
assignment, and decide the questions philosophers care about — is an argument
*valid* (do the premises entail the conclusion?), is a sentence a tautology,
is it satisfiable?

Formulas are nested tuples:
  "p"                      an atom
  ("not", f)               negation
  ("and", f, g)            conjunction
  ("or",  f, g)            disjunction
  ("imp", f, g)            material implication  (f -> g)
  ("iff", f, g)            biconditional         (f <-> g)
"""

from __future__ import annotations

from itertools import product
from typing import Union


Formula = Union[str, tuple]


def variables(f: Formula) -> set[str]:
    if isinstance(f, str):
        return {f}
    return set().union(*(variables(arg) for arg in f[1:]))


def evaluate(f: Formula, assignment: dict[str, bool]) -> bool:
    if isinstance(f, str):
        return assignment[f]
    op = f[0]
    if op == "not":
        return not evaluate(f[1], assignment)
    a = evaluate(f[1], assignment)
    b = evaluate(f[2], assignment)
    return {
        "and": a and b,
        "or": a or b,
        "imp": (not a) or b,
        "iff": a == b,
    }[op]


def _assignments(varnames: list[str]):
    for values in product([False, True], repeat=len(varnames)):
        yield dict(zip(varnames, values))


def is_tautology(f: Formula) -> bool:
    return all(evaluate(f, a) for a in _assignments(sorted(variables(f))))


def is_satisfiable(f: Formula) -> bool:
    return any(evaluate(f, a) for a in _assignments(sorted(variables(f))))


def entails(premises: list[Formula], conclusion: Formula
            ) -> tuple[bool, dict[str, bool] | None]:
    """Do the premises logically entail the conclusion?

    Returns (valid, counterexample). The counterexample is an assignment that
    makes every premise true but the conclusion false.
    """
    varnames = sorted(set().union(variables(conclusion),
                                  *(variables(p) for p in premises)))
    for a in _assignments(varnames):
        if all(evaluate(p, a) for p in premises) and not evaluate(conclusion, a):
            return False, a
    return True, None


def show(f: Formula) -> str:
    if isinstance(f, str):
        return f
    if f[0] == "not":
        return f"¬{show(f[1])}"
    sym = {"and": "∧", "or": "∨", "imp": "→", "iff": "↔"}[f[0]]
    return f"({show(f[1])} {sym} {show(f[2])})"


if __name__ == "__main__":
    p, q = "p", "q"

    # Modus ponens: from p and (p -> q), infer q.  VALID.
    valid, _ = entails([p, ("imp", p, q)], q)
    print(f"Modus ponens  {{p, p→q}} ⊨ q : {valid}")

    # Affirming the consequent: from (p -> q) and q, infer p.  INVALID.
    valid, counter = entails([("imp", p, q), q], p)
    print(f"Aff. consequent {{p→q, q}} ⊨ p : {valid}  counterexample: {counter}")

    # De Morgan is a tautology.
    de_morgan = ("iff", ("not", ("and", p, q)), ("or", ("not", p), ("not", q)))
    print(f"\nDe Morgan {show(de_morgan)}")
    print(f"  tautology? {is_tautology(de_morgan)}")

    # Truth table for implication.
    imp = ("imp", p, q)
    print(f"\nTruth table for {show(imp)}:")
    for a in _assignments(["p", "q"]):
        print(f"  p={a['p']!s:<5} q={a['q']!s:<5} -> {evaluate(imp, a)}")
