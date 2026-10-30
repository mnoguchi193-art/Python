"""
Minimal Genome (最小ゲノム) — which genes can a synthetic cell live without?

Projects like JCVI-syn3.0 stripped a bacterium down to the smallest gene
set that still sustains life.  The computational core of such work is a
*gene essentiality* analysis on a metabolic network:

  * each gene encodes an enzyme that catalyses one reaction,
  * nutrients are freely available from the medium,
  * the cell is "viable" if it can still produce every biomass precursor.

Knock out one gene at a time; if the cell can no longer make a required
precursor, that gene is *essential*.  Reachability is computed by forward
propagation to a fixpoint — no external libraries.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Reaction:
    gene: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]


# A toy metabolic network. Precursors "protein" and "lipid" are needed for
# biomass; "atp" powers growth. Some metabolites have two routes (redundancy).
REACTIONS = [
    Reaction("glk",  ("glucose",),            ("g6p",)),
    Reaction("pfk",  ("g6p",),                ("fbp",)),
    Reaction("ald",  ("fbp",),                ("triose",)),
    Reaction("gap",  ("triose",),             ("pyruvate", "atp")),
    Reaction("pps",  ("pyruvate", "atp"),     ("pep",)),        # gluconeogenic backup
    Reaction("pdh",  ("pyruvate",),           ("acetylCoA",)),
    Reaction("fas",  ("acetylCoA", "atp"),    ("lipid",)),
    Reaction("gln",  ("pyruvate", "nh3"),     ("glutamate",)),
    Reaction("asn",  ("glutamate", "nh3"),    ("aminoacid",)),
    Reaction("alt",  ("pep", "glutamate"),    ("aminoacid",)),  # second route to aminoacid
    Reaction("rib",  ("aminoacid", "atp"),    ("protein",)),
]

MEDIUM = {"glucose", "nh3"}
BIOMASS = {"protein", "lipid", "atp"}


# ── Reachability ──────────────────────────────────────────────────────────
def producible(reactions: list[Reaction], medium: set[str]) -> set[str]:
    """All metabolites the network can make from `medium`, to a fixpoint."""
    have = set(medium)
    changed = True
    while changed:
        changed = False
        for r in reactions:
            if all(i in have for i in r.inputs) and not set(r.outputs) <= have:
                have |= set(r.outputs)
                changed = True
    return have


def viable(reactions: list[Reaction]) -> bool:
    return BIOMASS <= producible(reactions, MEDIUM)


# ── Essentiality scan ─────────────────────────────────────────────────────
def essentiality(reactions: list[Reaction]) -> dict[str, bool]:
    result = {}
    for r in reactions:
        knockout = [x for x in reactions if x.gene != r.gene]
        result[r.gene] = not viable(knockout)
    return result


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    genes = [r.gene for r in REACTIONS]
    print(f"Network: {len(REACTIONS)} genes, medium = {sorted(MEDIUM)}, "
          f"biomass = {sorted(BIOMASS)}")
    print(f"Wild-type viable: {viable(REACTIONS)}\n")

    ess = essentiality(REACTIONS)
    essential = [g for g in genes if ess[g]]
    dispensable = [g for g in genes if not ess[g]]
    print("Single-gene knockout scan:")
    for g in genes:
        mark = "ESSENTIAL   " if ess[g] else "dispensable "
        print(f"  {g:5s} {mark}")
    print(f"\n{len(essential)} essential, {len(dispensable)} dispensable.")
    print(f"  Dispensable genes ({', '.join(dispensable)}) have a backup route;")
    print("  removing one still leaves every biomass precursor producible.")

    # Build a minimal genome: drop dispensable genes greedily while viable.
    minimal = list(REACTIONS)
    for g in dispensable:
        trial = [r for r in minimal if r.gene != g]
        if viable(trial):
            minimal = trial
    print(f"\nGreedy minimal genome: {len(minimal)} genes "
          f"({', '.join(r.gene for r in minimal)})")
    print(f"  still viable: {viable(minimal)}")
    print("  (note: greedy order matters when backups share genes — a real")
    print("   minimisation must check combinations, not just single knockouts.)")
