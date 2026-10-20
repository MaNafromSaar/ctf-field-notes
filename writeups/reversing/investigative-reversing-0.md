# Investigative Reversing 0: decoding appended PNG data

## Find the trailing bytes

The PNG had 26 bytes after its `IEND` chunk. Rather than guess from the partly non-text bytes, inspect the companion ELF to learn how it produced them.

## Trace the writer

The binary opens `flag.txt` for reading and `mystery.png` in append mode. It reads one 26-byte item (`0x1A`) and appends it to the image:

- Offsets 0–5 and 16–25 are copied unchanged.
- Offsets 6–14 have 5 added; subtract 5 to recover them.
- Offset 15 has 3 subtracted; add 3 to recover it.

This explains why the program expects server-side files and need not be run to decode the existing PNG. Stack-canary operations in the decompilation are compiler protection, unrelated to the transform.

## Takeaway

When a binary is provided, trace the code that writes the suspicious bytes. A small, reversible transform can be easier to understand statically than by trying to recreate the original runtime environment. The flag and challenge artifacts are omitted.
