"""
Abstract Argumentation — Dung's framework

A landmark of computational philosophy and AI: reasoning about *conflicting*
arguments without looking inside them. An argumentation framework is just a
directed graph of attacks; the question is which sets of arguments can be
rationally accepted together.

Key notions (Dung 1995):
  conflict-free : the set contains no argument attacking another in it
  defends a     : every attacker of a is itself attacked by the set
  admissible    : conflict-free and defends all its own members
  grounded      : the least complete extension (skeptical consensus)
  preferred     : maximal admissible sets (credulous positions)
  stable        : conflict-free and attacks every argument left out

Attacks are (attacker, target) pairs.
"""

from __future__ import annotations

from itertools import combinations


Attacks = set
Args = set


def attackers(arg: str, attacks: Attacks) -> set[str]:
    return {x for (x, y) in attacks if y == arg}


def conflict_free(s: set[str], attacks: Attacks) -> bool:
    return not any((a, b) in attacks for a in s for b in s)


def defends(s: set[str], arg: str, attacks: Attacks) -> bool:
    """Does s defend arg — is every attacker of arg attacked by some s-member?"""
    return all(any((d, b) in attacks for d in s)
               for b in attackers(arg, attacks))


def is_admissible(s: set[str], attacks: Attacks) -> bool:
    return conflict_free(s, attacks) and all(defends(s, a, attacks) for a in s)


def grounded_extension(args: Args, attacks: Attacks) -> set[str]:
    """Least fixpoint of the characteristic function, from the empty set."""
    s: set[str] = set()
    while True:
        nxt = {a for a in args if defends(s, a, attacks)}
        if nxt == s:
            return s
        s = nxt


def _subsets(args: Args):
    items = list(args)
    for r in range(len(items) + 1):
        for combo in combinations(items, r):
            yield set(combo)


def preferred_extensions(args: Args, attacks: Attacks) -> list[set[str]]:
    admissible = [s for s in _subsets(args) if is_admissible(s, attacks)]
    return [s for s in admissible
            if not any(s < t for t in admissible)]   # maximal ones


def stable_extensions(args: Args, attacks: Attacks) -> list[set[str]]:
    result = []
    for s in _subsets(args):
        if not conflict_free(s, attacks):
            continue
        outside = args - s
        if all(any((a, b) in attacks for a in s) for b in outside):
            result.append(s)
    return result


if __name__ == "__main__":
    # a defeats b; c and d attack each other; c also attacks b.
    args = {"a", "b", "c", "d"}
    attacks = {("a", "b"), ("c", "b"), ("c", "d"), ("d", "c")}

    print("Arguments:", sorted(args))
    print("Attacks  :", sorted(attacks), "\n")

    print(f"Grounded extension (skeptical): "
          f"{sorted(grounded_extension(args, attacks))}")
    print(f"Preferred extensions (credulous): "
          f"{[sorted(s) for s in preferred_extensions(args, attacks)]}")
    print(f"Stable extensions: "
          f"{[sorted(s) for s in stable_extensions(args, attacks)]}")

    print("\n'a' is in every extension (it is unattacked); the c/d conflict has")
    print("no skeptical resolution, so the grounded view stays agnostic on them.")
