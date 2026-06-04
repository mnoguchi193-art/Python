"""
Molecular similarity — Tanimoto fingerprints / 分子類似性(谷本係数)

Virtual screening ranks a compound library by similarity to a known active.
Each molecule is encoded as a fingerprint — a set of structural features
(bits) — and similarity is the Tanimoto (Jaccard) coefficient:

    T(A, B) = |A ∩ B| / |A ∪ B|

Standard library only.
"""


def tanimoto(fp_a: set, fp_b: set) -> float:
    """Tanimoto/Jaccard similarity of two fingerprints (in [0, 1])."""
    if not fp_a and not fp_b:
        return 1.0
    intersection = len(fp_a & fp_b)
    union = len(fp_a | fp_b)
    return intersection / union


def screen_library(
    query: set, library: dict[str, set], threshold: float = 0.0
) -> list[tuple[str, float]]:
    """Rank library compounds by Tanimoto similarity to the query."""
    scored = [
        (name, tanimoto(query, fp))
        for name, fp in library.items()
    ]
    scored = [(n, s) for n, s in scored if s >= threshold]
    return sorted(scored, key=lambda kv: kv[1], reverse=True)


if __name__ == "__main__":
    # Fingerprints as sets of structural-feature ids.
    query = {1, 2, 5, 8, 13, 21}
    library = {
        "compound_A": {1, 2, 5, 8, 13, 21},   # identical
        "compound_B": {1, 2, 5, 8, 34},        # similar core
        "compound_C": {3, 4, 6, 7, 9},         # unrelated
        "compound_D": {1, 2, 5, 13, 21, 55, 89},
    }
    print("Virtual screening results:")
    for name, score in screen_library(query, library, threshold=0.1):
        print(f"  {name}: Tanimoto = {score:.3f}")
