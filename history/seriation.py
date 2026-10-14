"""
Seriation — recovering chronological order from artifact frequencies

The original computational method in archaeology (Flinders Petrie, 1899). Without
any absolute dates, assemblages can be ordered in time because each artifact
style waxes and wanes: its frequency over the true sequence forms a single peak —
the "battleship curve". Seriation searches for the ordering that makes every
style's frequency curve unimodal.

Input: {assemblage: {artifact_type: count}}.
"""

from __future__ import annotations

from itertools import permutations


Data = dict[str, dict[str, float]]


def proportions(data: Data) -> Data:
    """Normalize each assemblage's counts to sum to 1."""
    out: Data = {}
    for name, counts in data.items():
        total = sum(counts.values()) or 1.0
        out[name] = {t: counts.get(t, 0) / total for t in counts}
    return out


def _penalty(order: tuple[str, ...], data: Data, types: list[str],
             tol: float = 1e-9) -> int:
    """Count unimodality violations: a frequency rising again after falling."""
    total = 0
    for t in types:
        series = [data[name].get(t, 0.0) for name in order]
        signs = []
        for i in range(len(series) - 1):
            d = series[i + 1] - series[i]
            if d > tol:
                signs.append(1)
            elif d < -tol:
                signs.append(-1)
        total += sum(1 for i in range(1, len(signs))
                     if signs[i - 1] == -1 and signs[i] == 1)
    return total


def seriate(data: Data) -> tuple[list[str], int]:
    """Return the assemblage ordering minimizing unimodality violations."""
    props = proportions(data)
    types = sorted({t for counts in props.values() for t in counts})
    names = list(props)
    best_order, best_penalty = names, None
    for perm in permutations(names):
        score = _penalty(perm, props, types)
        if best_penalty is None or score < best_penalty:
            best_order, best_penalty = list(perm), score
            if score == 0:
                break
    return best_order, best_penalty


def battleship(order: list[str], data: Data, width: int = 30) -> str:
    """ASCII 'battleship curve' chart of each type along the ordering."""
    props = proportions(data)
    types = sorted({t for c in props.values() for t in c})
    lines = []
    for t in types:
        lines.append(f"  type {t}:")
        for name in order:
            bar = "#" * round(props[name].get(t, 0.0) * width)
            lines.append(f"    {name:<8} {bar}")
    return "\n".join(lines)


if __name__ == "__main__":
    # Six graves; each pottery style A-F peaks in a different (unknown) period.
    # We hand them to the algorithm in SCRAMBLED order.
    scrambled: Data = {
        "grave_3": {"A": 1, "B": 4, "C": 9, "D": 4, "E": 1, "F": 0},
        "grave_5": {"A": 0, "B": 0, "C": 1, "D": 4, "E": 9, "F": 4},
        "grave_1": {"A": 9, "B": 4, "C": 1, "D": 0, "E": 0, "F": 0},
        "grave_6": {"A": 0, "B": 0, "C": 0, "D": 1, "E": 4, "F": 9},
        "grave_2": {"A": 4, "B": 9, "C": 4, "D": 1, "E": 0, "F": 0},
        "grave_4": {"A": 1, "B": 4, "C": 4, "D": 9, "E": 4, "F": 1},
    }

    order, penalty = seriate(scrambled)
    print("Frequency seriation (Petrie)\n")
    print(f"  input order    : {list(scrambled)}")
    print(f"  recovered order: {order}")
    print(f"  unimodality violations: {penalty} "
          f"(0 = every style forms a battleship curve)\n")
    print(battleship(order, scrambled))
    print("\nWith zero violations, the recovered sequence is the chronological")
    print("order (determined only up to overall direction).")
