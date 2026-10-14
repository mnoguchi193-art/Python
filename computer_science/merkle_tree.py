"""
Merkle Trees — tamper-evident data with logarithmic proofs

A Merkle tree hashes data blocks into leaves, then repeatedly hashes pairs up to
a single root. Any change to any block changes the root, so the root is a compact
fingerprint of the whole dataset — the idea behind Git, blockchains and
Certificate Transparency. Better still, you can prove a single block belongs to
the dataset with only log2(n) sibling hashes (a "Merkle proof"), without
revealing or downloading the rest.
"""

from __future__ import annotations

import hashlib


def _h(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def merkle_root(blocks: list[str]) -> str:
    level = [_h(b) for b in blocks]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])                 # duplicate last if odd
        level = [_h(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
    return level[0]


def merkle_proof(blocks: list[str], index: int) -> list[tuple[str, str]]:
    """Sibling hashes (and their side) needed to prove blocks[index]."""
    level = [_h(b) for b in blocks]
    proof = []
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        sibling = index ^ 1
        side = "right" if index % 2 == 0 else "left"
        proof.append((side, level[sibling]))
        index //= 2
        level = [_h(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
    return proof


def verify_proof(block: str, proof: list[tuple[str, str]], root: str) -> bool:
    h = _h(block)
    for side, sibling in proof:
        h = _h(h + sibling) if side == "right" else _h(sibling + h)
    return h == root


if __name__ == "__main__":
    blocks = ["tx-alice", "tx-bob", "tx-carol", "tx-dave", "tx-eve"]
    root = merkle_root(blocks)
    print("Merkle tree over 5 transactions\n")
    print(f"  root: {root[:32]}...\n")

    proof = merkle_proof(blocks, 2)               # prove "tx-carol"
    print(f"  proof for 'tx-carol': {len(proof)} sibling hashes (log2 n)")
    print(f"  verifies against root? {verify_proof('tx-carol', proof, root)}")
    print(f"  verifies a forged block? "
          f"{verify_proof('tx-mallory', proof, root)}\n")

    tampered = blocks[:]
    tampered[2] = "tx-carol-HACKED"
    print(f"  tampering one block changes the root? "
          f"{merkle_root(tampered) != root}")
    print("\n  One tiny change cascades to the root — and membership is provable")
    print("  with only a handful of hashes, however large the dataset.")
