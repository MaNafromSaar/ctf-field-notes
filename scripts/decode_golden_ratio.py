#!/usr/bin/env python3
"""Decode the slack-space message encoded with powers of the golden ratio."""

from __future__ import annotations

import argparse
import math
from pathlib import Path


FRAME_LENGTH = 15
INTEGER_DIGITS = 11
FRACTION_DIGITS = 3


def decode(text: str) -> str:
    data = text.strip()
    if not data:
        raise ValueError("input is empty")
    if len(data) % FRAME_LENGTH:
        raise ValueError(
            f"input length {len(data)} is not a multiple of {FRAME_LENGTH}"
        )

    phi = (1 + math.sqrt(5)) / 2
    decoded: list[str] = []

    for offset in range(0, len(data), FRAME_LENGTH):
        frame = data[offset : offset + FRAME_LENGTH]
        if frame[INTEGER_DIGITS] != ".":
            raise ValueError(
                f"frame {offset // FRAME_LENGTH} has no radix point at offset 11"
            )

        integer_part = frame[:INTEGER_DIGITS]
        fractional_part = frame[INTEGER_DIGITS + 1 :]
        if len(fractional_part) != FRACTION_DIGITS:
            raise ValueError(f"frame {offset // FRAME_LENGTH} has an invalid length")
        if any(bit not in "01" for bit in integer_part + fractional_part):
            raise ValueError(
                f"frame {offset // FRAME_LENGTH} contains a non-binary digit"
            )

        value = math.fsum(
            phi ** (INTEGER_DIGITS - 1 - index)
            for index, bit in enumerate(integer_part)
            if bit == "1"
        )
        value += math.fsum(
            phi ** -(index + 1)
            for index, bit in enumerate(fractional_part)
            if bit == "1"
        )

        codepoint = math.floor(value + 0.5)
        if not 0 <= codepoint <= 0x7F:
            raise ValueError(
                f"frame {offset // FRAME_LENGTH} rounds outside the ASCII range"
            )
        decoded.append(chr(codepoint))

    return "".join(decoded)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="file containing the encoded bitstream")
    args = parser.parse_args()

    try:
        encoded = args.input.read_text(encoding="ascii")
        message = decode(encoded)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))

    print(message, end="")


if __name__ == "__main__":
    main()
