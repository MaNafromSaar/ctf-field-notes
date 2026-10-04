#!/usr/bin/env python3
"""Search a local wordlist for a candidate matching a supplied digest."""

import argparse
import hashlib


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("digest", help="expected hexadecimal digest")
    parser.add_argument("wordlist", help="path to a locally available wordlist")
    parser.add_argument("--algorithm", default="sha1", help="hashlib algorithm (default: sha1)")
    args = parser.parse_args()

    try:
        digest_function = hashlib.new(args.algorithm)
    except ValueError as error:
        parser.error(str(error))

    expected = args.digest.lower()
    try:
        with open(args.wordlist, "rb") as candidates:
            for line in candidates:
                candidate = line.rstrip(b"\r\n")
                if hashlib.new(digest_function.name, candidate).hexdigest() == expected:
                    print(candidate.decode("utf-8", errors="replace"))
                    return
    except OSError as error:
        parser.error(str(error))

    raise SystemExit("No matching candidate found")


if __name__ == "__main__":
    main()
