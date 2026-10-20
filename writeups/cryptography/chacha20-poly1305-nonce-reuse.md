# ChaCha20-Poly1305: forging ciphertext after a reused nonce

## Context

A TCP service (`<HOST>:<PORT>`) derives a ChaCha20-Poly1305 key from a
server-side secret and prints two known plaintexts along with their
ciphertexts (each ciphertext followed by its 16-byte Poly1305 tag and the
12-byte nonce used). It then reads one hex-encoded message from the user,
decrypts and verifies it with the same cipher construction, and prints the
flag if the decrypted plaintext's `repr()` contains a specific target
string. The key is never reused across connections, but within a single
connection the nonce is generated once and reused for every call to the
encrypt/decrypt routine.

## Observations

The two printed ciphertexts end in identical trailing bytes. Since each
ciphertext is built as `ciphertext || tag || nonce`, and the tag is fixed at
16 bytes, the last 12 bytes of both outputs are the nonce -- and they match.
That single observation is the whole bug: AEAD constructions require a
unique nonce per (key, nonce) encryption, and this one does not provide it.

## Hypothesis

If the same (key, nonce) pair encrypts two different messages:

- ChaCha20 produces the same keystream both times, so XORing either
  ciphertext with its own known plaintext recovers that keystream, and that
  keystream can be reused to encrypt any new message of equal or shorter
  length (classic two-time-pad confidentiality break).
- Poly1305 also reuses its one-time authenticator key `(r, s)`, which is
  derived once from the keystream's first block. Because `(r, s)` doesn't
  change, the two known (ciphertext, tag) pairs are two independent
  equations in the same two unknowns. That should be enough to solve for
  `(r, s)` directly, rather than only being able to replay or XOR-combine
  the two known messages.

If both hold, nonce reuse breaks not just confidentiality but also
integrity: an attacker can compute a valid tag for an arbitrary chosen
message, not merely for XOR-combinations of the two known plaintexts.

## Analysis

Poly1305 treats the authenticated data as a sequence of 16-byte blocks,
each read as a little-endian integer with an extra set bit appended, and
evaluates a polynomial in a secret value `r` over the field with modulus
`p = 2^130 - 5`:

```text
acc(r) = sum_i block_i * r^(n - i)      (mod p)
tag    = (acc(r) + s) mod 2^128
```

With no associated data, the final block folds in the ciphertext length.
Given two (ciphertext, tag) pairs authenticated under the same `(r, s)`,
subtracting the two `acc(r)` polynomials cancels `s` and leaves a single
polynomial in `r` whose coefficients are known. Any root of that polynomial
modulo `p` is a candidate for `r` (RFC 8439 clamps `r` to a specific bit
pattern before use, which filters out false roots). Because the final
reduction from `acc(r) + s` to a 128-bit tag can wrap, the subtraction is
only correct up to an unknown small multiple of `2^128`; trying a handful of
candidate offsets and factoring the resulting polynomial over `GF(p)` finds
the correct root in practice. Once `r` is fixed, `s` follows directly from
either original tag.

With `(r, s)` and the keystream recovered, forging a message is:

1. XOR the recovered keystream with the desired plaintext (truncated or
   padded to the available keystream length) to get a new ciphertext.
2. Evaluate the Poly1305 polynomial over that new ciphertext with the
   recovered `r`, add `s`, and reduce mod `2^128` to get a valid tag.
3. Append the original (reused) nonce, unchanged.

The forged `ciphertext || tag || nonce` blob decrypts and verifies
successfully against the service's own oracle, because it uses the same
key and nonce the service already derived.

## Resolution

The accompanying helper,
[`scripts/chacha20-Poly1305_nonce_solver.py`](../../scripts/chacha20-Poly1305_nonce_solver.py),
implements the derivation above:

```text
python3 scripts/chacha20-Poly1305_nonce_solver.py
```

Paste the two `Ciphertext (hex):` lines printed by the service (or the
whole transcript -- it extracts the hex automatically) and press Ctrl-D.
The script factors the difference polynomial, recovers `(r, s)`, forges a
ciphertext for the target string, and prints it in a clearly labeled block.
Paste that hex back into the still-open connection's prompt; because each
connection derives its own random key and nonce, the ciphertexts used for
solving must come from that same connection. `--selftest` exercises the
same code path against a freshly keyed local cipher instance, with no
service required.

## Takeaways

- AEAD security depends on the nonce being unique per (key, nonce) pair,
  full stop. A nonce generated once outside the per-message encrypt
  function reuses it for every message encrypted on that connection.
- Nonce reuse against a polynomial-MAC construction like Poly1305 is worse
  than it first looks: it's tempting to assume the damage is limited to a
  two-time pad on the ciphertext (an XOR relationship between the two known
  plaintexts). In fact the one-time authenticator key leaks algebraically,
  which permits forging a tag for an arbitrary chosen message -- a full
  break of the construction's authenticity guarantee, not just its
  confidentiality.
- Treating "the key depends on a secret I can't see" as the end of the
  analysis misses that symmetric AEAD schemes have their own internal,
  per-message state (nonce, and derived one-time MAC keys) that can be
  attacked even while the long-term key stays unknown.

## Artifacts intentionally omitted

- `challenge.py`: the service's source, defining the message/goal strings,
  the encrypt/decrypt wrapper, and the single shared nonce.
- `flag.txt` and any live ciphertext, nonce, or forged-message values from
  an actual instance.
