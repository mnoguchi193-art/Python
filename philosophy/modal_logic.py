"""
Modal Logic — Kripke semantics and frame correspondence

Modal logic adds "necessarily" (box) and "possibly" (dia) to propositional
logic, interpreted over *possible worlds*. A formula's truth depends on the
world you evaluate it in and on which worlds are *accessible* from it:

  box f  is true at w  iff  f is true at EVERY world accessible from w
  dia f  is true at w  iff  f is true at SOME world accessible from w

The deep result (frame correspondence) is that structural properties of the
accessibility relation validate specific axioms:
  reflexive   <-> axiom T : box p -> p           ("the necessary is actual")
  transitive  <-> axiom 4 : box p -> box box p   (positive introspection)

A model is (worlds, accessibility pairs, valuation: world -> set of true atoms).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Model:
    worlds: set[str]
    access: set[tuple[str, str]]          # (w, v): v is accessible from w
    valuation: dict[str, set[str]]         # world -> atoms true there

    def successors(self, w: str) -> set[str]:
        return {v for (x, v) in self.access if x == w}


def holds(model: Model, world: str, f) -> bool:
    if isinstance(f, str):
        return f in model.valuation.get(world, set())
    op = f[0]
    if op == "not":
        return not holds(model, world, f[1])
    if op == "box":
        return all(holds(model, v, f[1]) for v in model.successors(world))
    if op == "dia":
        return any(holds(model, v, f[1]) for v in model.successors(world))
    a = holds(model, world, f[1])
    b = holds(model, world, f[2])
    return {"and": a and b, "or": a or b, "imp": (not a) or b}[op]


def valid_in(model: Model, f) -> bool:
    """Is the formula true at every world of the model?"""
    return all(holds(model, w, f) for w in model.worlds)


if __name__ == "__main__":
    p = "p"
    T = ("imp", ("box", p), p)               # box p -> p

    # Frame WITHOUT reflexivity: w1 sees only w2 (where p holds), but not itself.
    non_reflexive = Model(
        worlds={"w1", "w2"},
        access={("w1", "w2")},
        valuation={"w2": {"p"}},             # p false at w1, true at w2
    )
    print("Non-reflexive frame:")
    print(f"  box p at w1 : {holds(non_reflexive, 'w1', ('box', p))}")
    print(f"  p     at w1 : {holds(non_reflexive, 'w1', p)}")
    print(f"  axiom T (box p -> p) valid? {valid_in(non_reflexive, T)}  "
          f"(fails: the necessary need not be actual)\n")

    # Same frame made reflexive: every world can see itself.
    reflexive = Model(
        worlds={"w1", "w2"},
        access={("w1", "w2"), ("w1", "w1"), ("w2", "w2")},
        valuation={"w2": {"p"}},
    )
    print("Reflexive frame:")
    print(f"  axiom T (box p -> p) valid? {valid_in(reflexive, T)}  "
          f"(reflexivity validates T)")

    # Axiom 4 and transitivity.
    ax4 = ("imp", ("box", p), ("box", ("box", p)))
    transitive = Model(
        worlds={"a", "b", "c"},
        access={("a", "b"), ("b", "c"), ("a", "c"),   # transitive closure
                ("a", "a"), ("b", "b"), ("c", "c")},
        valuation={"a": {"p"}, "b": {"p"}, "c": {"p"}},
    )
    print(f"\nTransitive frame: axiom 4 (box p -> box box p) valid? "
          f"{valid_in(transitive, ax4)}")
