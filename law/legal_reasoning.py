"""
Legal Reasoning — defeasible (non-monotonic) rule engine

Real law is not classical logic: rules have exceptions, and conclusions can be
*withdrawn* when a more authoritative rule applies. This is the core problem of
AI & Law. This engine does defeasible reasoning with priorities that encode the
classic conflict-resolution canons:

  lex specialis  — the specific rule beats the general one
  lex posterior  — the later rule beats the earlier one

Literals are strings; a leading '-' marks negation ("-may_be_served").
"""

from __future__ import annotations

from dataclasses import dataclass


def neg(literal: str) -> str:
    """Logical negation of a literal."""
    return literal[1:] if literal.startswith("-") else "-" + literal


@dataclass(frozen=True)
class Rule:
    name: str
    body: frozenset[str]   # all must hold for the rule to fire
    head: str              # the literal it concludes
    priority: int = 0      # higher beats lower on conflict


def rule(name: str, body: set[str], head: str, priority: int = 0) -> Rule:
    return Rule(name, frozenset(body), head, priority)


def derive(facts: set[str], rules: list[Rule], max_iter: int = 100) -> set[str]:
    """Compute the defeasible conclusions from facts under the rule set.

    Each pass: a rule fires only if its body is currently supported AND no
    *applicable* rule with the opposite head has greater-or-equal priority
    (ambiguity blocking). Iterating to a fixpoint lets defeated conclusions
    drop back out as stronger rules become applicable.
    """
    conclusions = set(facts)
    for _ in range(max_iter):
        applicable = [r for r in rules if r.body <= conclusions]
        winners = set(facts)
        for r in applicable:
            challengers = [c for c in applicable if c.head == neg(r.head)]
            if all(r.priority > c.priority for c in challengers):
                winners.add(r.head)
        if winners == conclusions:
            return conclusions
        conclusions = winners
    return conclusions


if __name__ == "__main__":
    # ── Lex specialis: a minor cannot be served, despite the general rule ──
    rules = [
        rule("definition", {"minor"}, "customer", priority=100),  # ~ strict
        rule("general", {"customer"}, "may_be_served", priority=1),
        rule("exception", {"minor"}, "-may_be_served", priority=5),
    ]
    result = derive({"minor"}, rules)
    print("Case 1 — minor at a bar (lex specialis):")
    print(f"  derived: {sorted(result)}")
    print(f"  may_be_served? {'may_be_served' in result}  "
          f"(specific exception overrides general rule)\n")

    # ── Lex posterior: the 2020 statute overrides the 1990 statute ──
    rules = [
        rule("statute_1990", {"imported_good"}, "tariff_applies", priority=1),
        rule("statute_2020", {"imported_good"}, "-tariff_applies", priority=2),
    ]
    result = derive({"imported_good"}, rules)
    print("Case 2 — conflicting statutes (lex posterior):")
    print(f"  derived: {sorted(result)}")
    print(f"  tariff_applies? {'tariff_applies' in result}  "
          f"(later statute prevails)")
