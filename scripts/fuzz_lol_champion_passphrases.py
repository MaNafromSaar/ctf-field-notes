#!/usr/bin/env python3
"""Generate and test steghide passphrases formed from a prefix and two champions."""

from __future__ import annotations

import argparse
import itertools
import shutil
import subprocess
import sys
from pathlib import Path


def load_champions(path: Path) -> list[str]:
    names = [
        line.strip().lower()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not names:
        raise ValueError("champion list is empty")
    if any(not name.isascii() or not name.isalnum() for name in names):
        raise ValueError("champion names must contain only ASCII letters and digits")
    return list(dict.fromkeys(names))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="BMP image containing the steghide payload")
    parser.add_argument(
        "--prefix",
        required=True,
        help="known passphrase prefix",
    )
    parser.add_argument(
        "--champions",
        type=Path,
        required=True,
        help="file containing one normalized champion name per line",
    )
    parser.add_argument(
        "--wordlist-out",
        type=Path,
        required=True,
        help="new file where all generated candidates will be saved",
    )
    parser.add_argument(
        "--extract-to",
        type=Path,
        required=True,
        help="new file path for the extracted payload if a passphrase matches",
    )
    args = parser.parse_args()

    if not args.image.is_file():
        parser.error(f"image file does not exist: {args.image}")
    if args.wordlist_out.resolve() == args.image.resolve():
        parser.error("wordlist output must not overwrite the image")
    if args.extract_to.resolve() in (args.image.resolve(), args.wordlist_out.resolve()):
        parser.error("extraction output must be a different path from the image and wordlist")
    if args.wordlist_out.exists():
        parser.error(f"refusing to overwrite wordlist: {args.wordlist_out}")
    if args.extract_to.exists():
        parser.error(f"refusing to overwrite extraction output: {args.extract_to}")

    steghide = shutil.which("steghide")
    if steghide is None:
        parser.error("steghide was not found on PATH")

    try:
        champions = load_champions(args.champions)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))

    candidates = (
        args.prefix + first + second
        for first, second in itertools.product(champions, repeat=2)
    )
    try:
        with args.wordlist_out.open("x", encoding="ascii", newline="\n") as wordlist:
            for candidate in candidates:
                wordlist.write(candidate + "\n")
    except OSError as exc:
        parser.error(f"cannot write candidate wordlist: {exc}")

    total = len(champions) ** 2
    print(f"Wrote {total} ordered two-champion suffixes to {args.wordlist_out}.")
    print(f"Testing candidates against {args.image}...")

    with args.wordlist_out.open(encoding="ascii") as wordlist:
        for candidate in wordlist:
            passphrase = candidate.rstrip("\n")
            try:
                result = subprocess.run(
                    [
                        steghide,
                        "extract",
                        "-sf",
                        str(args.image),
                        "-p",
                        passphrase,
                        "-xf",
                        str(args.extract_to),
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
            except OSError as exc:
                parser.error(f"could not run steghide: {exc}")
            if result.returncode == 0:
                print(f"Passphrase matched: {passphrase}")
                print(f"Extracted payload: {args.extract_to}")
                return

    print(f"No match after {total} candidates.", file=sys.stderr)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
