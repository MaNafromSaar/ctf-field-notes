#!/usr/bin/env python3
"""Forge a ChaCha20-Poly1305 ciphertext when a nonce has been reused.

Usage:
  python3 chacha20-Poly1305_nonce_solver.py
      # paste the two "Ciphertext (hex):" lines (or the whole transcript),
      # then press Ctrl-D on an empty line
  python3 chacha20-Poly1305_nonce_solver.py CT1_HEX CT2_HEX
      # pass both ciphertexts directly
  python3 chacha20-Poly1305_nonce_solver.py --selftest
      # runs the attack against a local, freshly keyed cipher instance

Solving and connecting stay separate: run this offline against the two
known-plaintext ciphertexts emitted under a reused nonce, then paste the
forged hex this script prints into the live session's decrypt/verify
prompt. No network code lives in this file.

This recovers the Poly1305 one-time authenticator key (r, s) from two
messages authenticated under the same (key, nonce) pair -- it does not
recover the ChaCha20 key itself. See the accompanying write-up for the
derivation: ../writeups/cryptography/chacha20-poly1305-nonce-reuse.md
"""
import re
import secrets
import sys

from sympy import GF, Poly, symbols

P = (1 << 130) - 5
CLAMP = 0x0FFFFFFC0FFFFFFC0FFFFFFC0FFFFFFF

# The two known plaintexts the challenge prints before offering a decrypt
# oracle, and the target string whose presence unlocks the flag. These are
# fixed, public strings from the challenge source, not secrets.
MSG1 = b"Did you know that ChaCha20-Poly1305 is an authenticated encryption algorithm?"
MSG2 = b"That means it protects both the confidentiality and integrity of data!"
GOAL = b"But it's only secure if used correctly!"


def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def mac_blocks(ct):
    # No AAD: pad16(ct) || len(aad) as u64 LE || len(ct) as u64 LE
    data = ct + b"\x00" * (-len(ct) % 16) + (0).to_bytes(8, "little") + len(ct).to_bytes(8, "little")
    return [int.from_bytes(data[i:i + 16] + b"\x01", "little") for i in range(0, len(data), 16)]


def poly_coeffs(ct):
    # acc(r) = sum_i n_i * r^(len-i), lowest degree first
    blocks = mac_blocks(ct)
    n = len(blocks)
    coeffs = [0] * (n + 1)
    for i, b in enumerate(blocks):
        coeffs[n - i] = b
    return coeffs


def poly_eval(coeffs, r):
    return sum(c * pow(r, d, P) for d, c in enumerate(coeffs)) % P


def split(blob):
    return blob[:-28], blob[-28:-12], blob[-12:]


def recover_r_s(ct1, tag1, ct2, tag2):
    x = symbols("x")
    c1, c2 = poly_coeffs(ct1), poly_coeffs(ct2)
    size = max(len(c1), len(c2))
    diff = [((c1[d] if d < len(c1) else 0) - (c2[d] if d < len(c2) else 0)) % P for d in range(size)]
    dt = int.from_bytes(tag1, "little") - int.from_bytes(tag2, "little")
    cands = []
    # tag = ((acc mod P) + s) mod 2^128, so the difference is off by a small multiple of 2^128
    for k in range(-4, 5):
        coeffs = diff[:]
        coeffs[0] = (coeffs[0] - dt - k * (1 << 128)) % P
        poly = Poly(list(reversed(coeffs)), x, domain=GF(P))
        for factor, _ in poly.factor_list()[1]:
            if factor.degree() == 1:
                a, b = [int(c) % P for c in factor.all_coeffs()]
                r = (-b * pow(a, -1, P)) % P
                if r & CLAMP == r:
                    s = (int.from_bytes(tag1, "little") - poly_eval(c1, r)) % (1 << 128)
                    cands.append((r, s))
    return cands


def forge(blob1, blob2, goal=GOAL):
    ct1, tag1, nonce = split(blob1)
    ct2, tag2, _ = split(blob2)
    cands = recover_r_s(ct1, tag1, ct2, tag2)
    if not cands:
        raise SystemExit("no valid Poly1305 key candidate found")
    r, s = cands[0]
    keystream = xor(ct1, MSG1)
    forged_ct = xor(goal, keystream[: len(goal)])
    acc = poly_eval(poly_coeffs(forged_ct), r)
    tag = ((acc + s) % (1 << 128)).to_bytes(16, "little")
    return (forged_ct + tag + nonce).hex(), len(cands)


def selftest():
    from Crypto.Cipher import ChaCha20_Poly1305

    key, nonce = secrets.token_bytes(32), secrets.token_bytes(12)

    def enc(m):
        ct, tag = ChaCha20_Poly1305.new(key=key, nonce=nonce).encrypt_and_digest(m)
        return ct + tag + nonce

    forged, n = forge(enc(MSG1), enc(MSG2))
    blob = bytes.fromhex(forged)
    pt = ChaCha20_Poly1305.new(key=key, nonce=blob[-12:]).decrypt_and_verify(blob[:-28], blob[-28:-12])
    print("candidates:", n, "decrypted:", pt)
    assert pt == GOAL


def extract_ciphertexts(text):
    hexes = re.findall(r"Ciphertext \(hex\):\s*([0-9a-fA-F]+)", text)
    if len(hexes) < 2:
        hexes = re.findall(r"\b[0-9a-fA-F]{40,}\b", text)
    if len(hexes) < 2:
        raise SystemExit(f"found only {len(hexes)} hex ciphertext(s), need 2")
    return hexes[0], hexes[1]


def print_result(forged_hex):
    banner = "=" * 70
    print()
    print(banner)
    print("FORGED MESSAGE -- paste this at the live session's")
    print("decrypt/verify prompt:")
    print()
    print(forged_hex)
    print(banner)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        args = sys.argv[1:]
        if len(args) == 2:
            ct1_hex, ct2_hex = args
        else:
            print("Paste the two 'Ciphertext (hex):' lines (or the whole")
            print("transcript), then press Ctrl-D on an empty line:")
            ct1_hex, ct2_hex = extract_ciphertexts(sys.stdin.read())
        forged_hex, _ = forge(bytes.fromhex(ct1_hex), bytes.fromhex(ct2_hex))
        print_result(forged_hex)
