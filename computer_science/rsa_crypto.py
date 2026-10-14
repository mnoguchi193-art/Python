"""
RSA Public-Key Cryptography — from scratch

The algorithm that secures the internet. Its security rests on a simple
asymmetry: multiplying two large primes is easy, but factoring their product is
(believed to be) infeasible. A public key (n, e) encrypts; only the private key d
decrypts. Run in reverse, the same math produces unforgeable digital signatures.

Built on Miller-Rabin primality testing and Python's fast modular exponentiation.
"""

from __future__ import annotations

import hashlib
import secrets


def is_probable_prime(n: int, rounds: int = 40) -> bool:
    """Miller-Rabin probabilistic primality test."""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_prime(bits: int) -> int:
    while True:
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(candidate):
            return candidate


def generate_keypair(bits: int = 512) -> tuple[tuple[int, int], tuple[int, int]]:
    """Returns (public (n, e), private (n, d))."""
    e = 65537
    while True:
        p, q = generate_prime(bits // 2), generate_prime(bits // 2)
        if p == q:
            continue
        n, phi = p * q, (p - 1) * (q - 1)
        if phi % e != 0:
            break
    d = pow(e, -1, phi)               # modular inverse (Python 3.8+)
    return (n, e), (n, d)


def encrypt(message: str, public: tuple[int, int]) -> int:
    n, e = public
    m = int.from_bytes(message.encode(), "big")
    if m >= n:
        raise ValueError("message too long for key size")
    return pow(m, e, n)


def decrypt(cipher: int, private: tuple[int, int]) -> str:
    n, d = private
    m = pow(cipher, d, n)
    return m.to_bytes((m.bit_length() + 7) // 8, "big").decode()


def sign(message: str, private: tuple[int, int]) -> int:
    n, d = private
    h = int.from_bytes(hashlib.sha256(message.encode()).digest(), "big") % n
    return pow(h, d, n)


def verify(message: str, signature: int, public: tuple[int, int]) -> bool:
    n, e = public
    h = int.from_bytes(hashlib.sha256(message.encode()).digest(), "big") % n
    return pow(signature, e, n) == h


if __name__ == "__main__":
    print("RSA — generating a 512-bit key pair...")
    public, private = generate_keypair(512)
    print(f"  modulus n has {public[0].bit_length()} bits\n")

    message = "Attack at dawn"
    cipher = encrypt(message, public)
    recovered = decrypt(cipher, private)
    print(f"  plaintext : {message!r}")
    print(f"  ciphertext: {str(cipher)[:50]}...")
    print(f"  decrypted : {recovered!r}  (match: {recovered == message})\n")

    signature = sign(message, private)
    print(f"  signature verifies on the original message? "
          f"{verify(message, signature, public)}")
    print(f"  signature verifies on a tampered message?  "
          f"{verify('Attack at dusk', signature, public)}")
    print("\nOnly the private key can sign; anyone with the public key can check.")
