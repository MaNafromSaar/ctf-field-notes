#!/usr/bin/env python3
"""Answer randomized four-byte function-address prompts in an authorized CTF."""

import argparse

from pwn import ELF, context, log, p32, remote


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", help="current challenge host")
    parser.add_argument("port", type=int, help="current challenge port")
    parser.add_argument("elf", help="path to the locally obtained matching ELF")
    parser.add_argument("--rounds", type=int, default=3)
    args = parser.parse_args()

    if args.rounds < 1:
        parser.error("rounds must be positive")

    context.log_level = "info"
    binary = ELF(args.elf, checksec=False)
    connection = remote(args.host, args.port)

    try:
        for _ in range(args.rounds):
            connection.recvuntil(b"procedure '")
            name = connection.recvuntil(b"'", drop=True).decode("ascii")
            connection.recvuntil(b"==> ")
            address = binary.symbols[name]
            log.info("%s = %#x", name, address)
            connection.send(p32(address))

        print(connection.recvall().decode("utf-8", errors="replace"))
    finally:
        connection.close()


if __name__ == "__main__":
    main()
