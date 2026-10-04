# DAB Hash: separating the prompt from the hashed input

## Trace the data flow

The program asks for a password and later asks for a number, which can suggest the password is hashed and compared with that number. Disassembly shows a different data flow: a helper decodes a constant byte array, hashes that fixed string, and compares the result with the numeric input. The password prompt is a separate part of the program.

Follow the value reaching the hash function rather than inferring behavior from prompt wording. Inspect the helper and hash routine in the matching ELF, then confirm the secret's location and transform from the program's own output or memory behavior.

## Reproduce the expected numeric value

The binary stores an obfuscated NUL-terminated byte sequence. The helper applies a one-byte XOR, then the hash routine uses a 64-bit DJB2-style recurrence:

```text
h = (h * 33 + byte) modulo 2^64
```

[`scripts/recover_obfuscated_hash.py`](../../scripts/recover_obfuscated_hash.py) reproduces this calculation from a local matching ELF and prints the numeric result only. It does not include the challenge binary or decoded secret.

## Takeaway

Names and prompts are not a substitute for data-flow analysis. Trace the actual value passed into a comparison; otherwise, a password prompt can send the investigation toward an unrelated hash algorithm.
