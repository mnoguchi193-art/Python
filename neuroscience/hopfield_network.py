"""
Hopfield Network — associative memory as attractor dynamics

John Hopfield's 1982 model (Nobel Prize in Physics, 2024) stores patterns as the
stable states of a recurrent network. Each stored memory becomes the bottom of an
energy valley; presenting a corrupted version, the network rolls downhill and
settles into the nearest memory — content-addressable recall and error
correction, the way biological memory retrieves a whole from a fragment.

Patterns are vectors of +1/-1 (here, 5x5 pixel glyphs).
"""

from __future__ import annotations


def to_vector(rows: list[str]) -> list[int]:
    return [1 if ch == "#" else -1 for row in rows for ch in row]


def train(patterns: list[list[int]]) -> list[list[float]]:
    """Hebbian outer-product weights with a zero diagonal."""
    n = len(patterns[0])
    w = [[0.0] * n for _ in range(n)]
    for p in patterns:
        for i in range(n):
            for j in range(n):
                if i != j:
                    w[i][j] += p[i] * p[j] / n
    return w


def energy(w: list[list[float]], state: list[int]) -> float:
    return -0.5 * sum(w[i][j] * state[i] * state[j]
                      for i in range(len(state)) for j in range(len(state)))


def recall(w: list[list[float]], state: list[int], max_sweeps: int = 20
           ) -> tuple[list[int], int]:
    """Asynchronous updates until the network reaches a fixed point."""
    state = state[:]
    n = len(state)
    for sweep in range(1, max_sweeps + 1):
        changed = False
        for i in range(n):
            total = sum(w[i][j] * state[j] for j in range(n))
            new = 1 if total >= 0 else -1
            if new != state[i]:
                state[i] = new
                changed = True
        if not changed:
            return state, sweep
    return state, max_sweeps


def render(vector: list[int], width: int = 5) -> str:
    return "\n".join(
        "".join("#" if vector[r * width + c] == 1 else "." for c in range(width))
        for r in range(len(vector) // width)
    )


if __name__ == "__main__":
    glyphs = {
        "X": ["#...#", ".#.#.", "..#..", ".#.#.", "#...#"],
        "O": [".###.", "#...#", "#...#", "#...#", ".###."],
        "T": ["#####", "..#..", "..#..", "..#..", "..#.."],
    }
    patterns = [to_vector(g) for g in glyphs.values()]
    w = train(patterns)

    # Corrupt the 'X' by flipping 4 pixels.
    corrupted = to_vector(["#...#", ".#.#.", "#.#.#", ".....", "#...#"])

    print("Hopfield associative memory (3 stored 5x5 glyphs)\n")
    print("Corrupted input (energy {:.2f}):".format(energy(w, corrupted)))
    print(render(corrupted))

    recovered, sweeps = recall(w, corrupted)
    print(f"\nRecalled after {sweeps} sweeps (energy {energy(w, recovered):.2f}):")
    print(render(recovered))

    match = recovered == patterns[0]
    print(f"\nMatches the stored 'X'? {match}  "
          f"(memory rolled downhill to the nearest attractor)")
