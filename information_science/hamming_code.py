"""
Hamming(7,4) Code — error correction (channel coding)

Shannon proved reliable communication over a noisy channel is possible; Hamming
codes are a concrete, elegant way to do it. Four data bits are encoded into seven
by adding three parity bits. The receiver computes a 3-bit "syndrome" that is
literally the binary position of the flipped bit — so any single-bit error is not
just detected but pinpointed and corrected. This is the math inside ECC memory,
deep-space links and more.
"""

from __future__ import annotations


def encode(data: list[int]) -> list[int]:
    """Encode 4 data bits into a 7-bit codeword (parity at positions 1, 2, 4)."""
    d1, d2, d3, d4 = data
    c = [0] * 8                       # 1-indexed; c[0] unused
    c[3], c[5], c[6], c[7] = d1, d2, d3, d4
    c[1] = c[3] ^ c[5] ^ c[7]
    c[2] = c[3] ^ c[6] ^ c[7]
    c[4] = c[5] ^ c[6] ^ c[7]
    return c[1:]


def decode(codeword: list[int]) -> tuple[list[int], int]:
    """Correct a single-bit error. Returns (data bits, error position or 0)."""
    c = [0] + list(codeword)         # back to 1-indexed
    s1 = c[1] ^ c[3] ^ c[5] ^ c[7]
    s2 = c[2] ^ c[3] ^ c[6] ^ c[7]
    s4 = c[4] ^ c[5] ^ c[6] ^ c[7]
    syndrome = s1 + 2 * s2 + 4 * s4
    if syndrome:
        c[syndrome] ^= 1             # the syndrome IS the error's position
    return [c[3], c[5], c[6], c[7]], syndrome


if __name__ == "__main__":
    data = [1, 0, 1, 1]
    codeword = encode(data)
    print(f"Hamming(7,4) — data {data} encodes to codeword {codeword}\n")

    print("Corrupting each bit in turn and decoding:")
    print(f"  {'flipped pos':>11}  {'received':>14}  {'detected':>8}  {'recovered':>11}")
    for pos in range(7):
        corrupted = codeword[:]
        corrupted[pos] ^= 1
        recovered, syndrome = decode(corrupted)
        ok = "OK" if recovered == data else "FAIL"
        print(f"  {pos + 1:>11}  {str(corrupted):>14}  {syndrome:>8}  "
              f"{str(recovered):>11} {ok}")

    clean, syndrome = decode(codeword)
    print(f"\n  No error: syndrome {syndrome}, data {clean} "
          f"(every single-bit error is corrected).")
