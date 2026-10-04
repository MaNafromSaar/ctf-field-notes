#!/usr/bin/env python3
"""Decrypt a Fernet token supplied by the analyst; makes no network requests."""

import argparse

from cryptography.fernet import Fernet, InvalidToken


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("key", help="URL-safe Base64 Fernet key")
    parser.add_argument("token", help="Fernet token")
    args = parser.parse_args()

    try:
        plaintext = Fernet(args.key.encode("ascii")).decrypt(args.token.encode("ascii"))
    except (UnicodeEncodeError, ValueError, InvalidToken) as error:
        parser.error(f"could not decrypt token: {error}")

    print(plaintext.decode("utf-8", errors="replace"))


if __name__ == "__main__":
    main()
