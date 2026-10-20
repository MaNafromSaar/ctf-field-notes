#!/usr/bin/env python3
"""Split a raw byte stream into lower and upper bit lanes of fixed-width words."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import BinaryIO


class BitWriter:
    """Pack successive bits least-significant-bit first into output bytes."""

    def __init__(self, stream: BinaryIO) -> None:
        self.stream = stream
        self.buffer = 0
        self.buffered_bits = 0
        self.bits_written = 0

    def write(self, value: int, bit_count: int) -> None:
        self.buffer |= value << self.buffered_bits
        self.buffered_bits += bit_count
        self.bits_written += bit_count

        while self.buffered_bits >= 8:
            self.stream.write(bytes((self.buffer & 0xFF,)))
            self.buffer >>= 8
            self.buffered_bits -= 8

    def finish(self) -> None:
        if self.buffered_bits:
            self.stream.write(bytes((self.buffer & 0xFF,)))
            self.buffer = 0
            self.buffered_bits = 0


def prompt_for_int(label: str) -> int:
    while True:
        try:
            return int(input(f"{label}: "))
        except ValueError:
            print("Enter an integer.", file=sys.stderr)


def split_stream(
    input_path: Path,
    lower_path: Path,
    upper_path: Path,
    skipped_path: Path | None,
    word_bits: int,
    split_bit: int,
    byteorder: str,
    skip_bytes: int,
) -> tuple[int, int, int]:
    if word_bits <= 0 or word_bits % 8:
        raise ValueError("word width must be a positive multiple of 8 bits")
    if not 0 < split_bit < word_bits:
        raise ValueError("split bit must be between 1 and word width - 1")
    if byteorder not in ("little", "big"):
        raise ValueError("byte order must be 'little' or 'big'")
    if skip_bytes < 0:
        raise ValueError("skip byte count must not be negative")

    word_bytes = word_bits // 8
    input_size = input_path.stat().st_size - skip_bytes
    if input_size < 0:
        raise ValueError("skip byte count exceeds input size")
    if input_size == 0:
        raise ValueError("input stream is empty after skipping the requested bytes")
    if input_size % word_bytes:
        raise ValueError(
            f"input size ({input_size} bytes) is not divisible by "
            f"the {word_bytes}-byte word width"
        )
    output_paths = [lower_path.resolve(), upper_path.resolve()]
    if skipped_path is not None:
        output_paths.append(skipped_path.resolve())
    if input_path.resolve() in output_paths:
        raise ValueError("output paths must not overwrite the input")
    if len(set(output_paths)) != len(output_paths):
        raise ValueError("all output paths must be different")

    word_count = input_size // word_bytes
    lower_mask = (1 << split_bit) - 1
    upper_bits = word_bits - split_bit

    with input_path.open("rb") as source, lower_path.open("wb") as lower_file, upper_path.open("wb") as upper_file:
        skipped_file = skipped_path.open("wb") if skipped_path is not None else None
        try:
            if skipped_file is not None:
                remaining = skip_bytes
                while remaining:
                    chunk = source.read(min(65536, remaining))
                    if not chunk:
                        raise OSError("input ended while copying skipped bytes")
                    skipped_file.write(chunk)
                    remaining -= len(chunk)
            else:
                source.seek(skip_bytes)

            lower_writer = BitWriter(lower_file)
            upper_writer = BitWriter(upper_file)

            while word := source.read(word_bytes):
                if len(word) != word_bytes:
                    raise OSError("input changed or ended unexpectedly while reading")
                value = int.from_bytes(word, byteorder=byteorder)
                lower_writer.write(value & lower_mask, split_bit)
                upper_writer.write(value >> split_bit, upper_bits)

            lower_writer.finish()
            upper_writer.finish()
        finally:
            if skipped_file is not None:
                skipped_file.close()

    return word_count, lower_writer.bits_written, upper_writer.bits_written


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Split each fixed-width word in a raw binary file at a bit position. "
            "Words are byte-aligned; split positions need not be."
        )
    )
    parser.add_argument("input", type=Path, help="input raw binary file")
    parser.add_argument(
        "--word-bits",
        type=int,
        help="declared width of each input word in bits (prompts if omitted)",
    )
    parser.add_argument(
        "--split-bit",
        type=int,
        help=(
            "number of low-order bits for the lower stream "
            "(prompts if omitted; range: 1 to word width - 1)"
        ),
    )
    parser.add_argument(
        "--byteorder",
        choices=("little", "big"),
        default="little",
        help="byte order used to interpret each word (default: little)",
    )
    parser.add_argument(
        "--skip-bytes",
        type=int,
        default=0,
        help="number of leading input bytes to skip before reading words (default: 0)",
    )
    parser.add_argument(
        "--save-skipped-bytes",
        action="store_true",
        help="save skipped leading bytes as <output-prefix>.header.bin",
    )
    parser.add_argument(
        "--output-prefix",
        type=Path,
        help="output path prefix (default: input path)",
    )
    args = parser.parse_args()

    if (args.word_bits is None or args.split_bit is None) and not sys.stdin.isatty():
        parser.error("--word-bits and --split-bit are required when stdin is not interactive")

    word_bits = args.word_bits if args.word_bits is not None else prompt_for_int("Word width in bits")
    split_bit = args.split_bit if args.split_bit is not None else prompt_for_int("Split position from LSB")
    if word_bits <= 0 or word_bits % 8:
        parser.error("--word-bits must be a positive multiple of 8")
    if not 0 < split_bit < word_bits:
        parser.error("--split-bit must be between 1 and word width - 1")
    if args.save_skipped_bytes and args.skip_bytes == 0:
        parser.error("--save-skipped-bytes requires --skip-bytes greater than zero")

    prefix = args.output_prefix or args.input
    lower_path = Path(f"{prefix}.lower.bin")
    upper_path = Path(f"{prefix}.upper.bin")
    skipped_path = Path(f"{prefix}.header.bin") if args.save_skipped_bytes else None
    try:
        word_count, lower_total_bits, upper_total_bits = split_stream(
            args.input,
            lower_path,
            upper_path,
            skipped_path,
            word_bits,
            split_bit,
            args.byteorder,
            args.skip_bytes,
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    print(f"Processed {word_count} {word_bits}-bit words ({args.byteorder}-endian).")
    print(f"Lower stream (bits {split_bit - 1}:0): {lower_path} ({lower_total_bits} bits)")
    print(f"Upper stream (bits {word_bits - 1}:{split_bit}): {upper_path} ({upper_total_bits} bits)")
    if skipped_path is not None:
        print(f"Skipped prefix: {skipped_path} ({args.skip_bytes} bytes)")
    print("Bits are packed LSB-first; zero padding may fill the last output byte.")


if __name__ == "__main__":
    main()
