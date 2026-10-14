"""
Threshold Models of Collective Behavior — Granovetter cascades

Why do riots, fads, and protests sometimes explode and sometimes fizzle from
almost identical crowds? Mark Granovetter's answer: each person has a *threshold*
— the number (or fraction) of others who must already act before they join. The
outcome depends on the whole distribution of thresholds, not on averages.

Two variants here: a global crowd model, and a network (complex-contagion)
model — the basis of modern influence-maximization research.
"""

from __future__ import annotations


def granovetter_cascade(thresholds: list[int]) -> tuple[int, list[int]]:
    """Global model: an agent joins once the number active reaches its threshold.

    Returns (final number active, the round-by-round count).
    """
    active = 0
    timeline = [0]
    while True:
        new_active = sum(1 for t in thresholds if t <= active)
        timeline.append(new_active)
        if new_active == active:
            return active, timeline
        active = new_active


def network_cascade(graph: dict[str, list[str]],
                    thresholds: dict[str, float],
                    seeds: set[str]) -> set[str]:
    """Linear threshold model: a node activates when the *fraction* of its
    neighbors that are active reaches its threshold (complex contagion)."""
    active = set(seeds)
    changed = True
    while changed:
        changed = False
        for v in graph:
            if v in active or not graph[v]:
                continue
            share = sum(1 for u in graph[v] if u in active) / len(graph[v])
            if share >= thresholds[v]:
                active.add(v)
                changed = True
    return active


if __name__ == "__main__":
    # A "uniform crowd" of 100 with thresholds 0,1,2,...,99 -> everyone riots.
    stable_crowd = list(range(100))
    final, _ = granovetter_cascade(stable_crowd)
    print(f"Crowd with thresholds 0..99 -> {final}/100 riot (full cascade)")

    # Remove the single instigator-of-one: the person with threshold 1 now
    # needs 2. The chain reaction never gets past the first domino.
    fragile_crowd = [0] + [2] + list(range(2, 100))
    final, timeline = granovetter_cascade(fragile_crowd)
    print(f"Change ONE threshold (1 -> 2) -> {final}/100 riot (cascade collapses)")
    print(f"  timeline: {timeline}")
    print("  => identical 'average' radicalism, opposite outcomes.\n")

    # Complex contagion on a network: adoption needs 50% of one's neighbors.
    # A dense triangle {a,b,c} is joined to a second cluster {d,e,f} by a
    # single bridge edge c-d.
    graph = {
        "a": ["b", "c"], "b": ["a", "c"], "c": ["a", "b", "d"],
        "d": ["c", "e", "f"], "e": ["d", "f"], "f": ["d", "e"],
    }
    thresholds = {v: 0.5 for v in graph}
    activated = network_cascade(graph, thresholds, seeds={"a", "b"})
    print(f"Network cascade from seeds {{a, b}} (50% rule): "
          f"{sorted(activated)}")
    print("The contagion stalls at the bridge: d needs half its 3 neighbors "
          "active,\nbut only c is, so the second cluster is never reached "
          "(complex contagion\nneeds reinforcement, unlike a simple virus).")
