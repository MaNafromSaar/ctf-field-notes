#!/usr/bin/env python3
"""Reproduce a 64-bit DJB2-style hash from an XOR-obfuscated ELF symbol."""

import argparse

from pwn import ELF

MASK_64 = (1 << 64) - 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("elf", help="path to the locally obtained matching ELF")
    parser.add_argument("--symbol", default="obf_bytes", help="symbol holding encoded bytes")
    parser.add_argument("--xor-key", type=lambda value: int(value, 0), default=0xAA)
    parser.add_argument("--max-length", type=int, default=128)
    args = parser.parse_args()

    if not 1 <= args.max_length <= 1_000_000:
        parser.error("max-length must be between 1 and 1000000")
    if not 0 <= args.xor_key <= 0xFF:
        parser.error("xor-key must be a byte value")

    binary = ELF(args.elf, checksec=False)
    address = binary.symbols.get(args.symbol)
    if address is None:
        parser.error(f"symbol {args.symbol!r} not found; the ELF may be stripped")

    decoded = bytearray()
    for offset in range(args.max_length):
        value = binary.read(address + offset, 1)[0] ^ args.xor_key
        if value == 0:
            break
        decoded.append(value)
    else:
        parser.error("no decoded NUL terminator found within max-length")

    result = 5381
    for byte in decoded:
        result = (result * 33 + byte) & MASK_64

    print(result)


if __name__ == "__main__":
    main()
