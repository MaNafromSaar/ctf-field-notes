#!/usr/bin/env python3
"""Decrypt AES-ECB ciphertext using a timestamp-derived key."""

import argparse
from hashlib import sha256

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("timestamp", type=int, help="Unix timestamp in seconds")
    parser.add_argument("ciphertext_hex", help="AES ciphertext encoded as hexadecimal")
    args = parser.parse_args()

    try:
        ciphertext = bytes.fromhex(args.ciphertext_hex)
        key = sha256(str(args.timestamp).encode("ascii")).digest()[:16]
        plaintext = unpad(
            AES.new(key, AES.MODE_ECB).decrypt(ciphertext),
            AES.block_size,
        ).decode("utf-8")
    except ValueError as error:
        parser.error(f"could not decrypt ciphertext: {error}")

    print(f"Key (hex): {key.hex()}")
    print(plaintext)


if __name__ == "__main__":
    main()
