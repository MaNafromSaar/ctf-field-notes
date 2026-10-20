# Challenge: RSA Quiz — From Key Math to Plaintext

## Context

The quiz presents different combinations of RSA values and asks for derived values, such as the modulus, totient, private exponent, ciphertext, or plaintext. Some prompts also ask whether a requested operation is possible and feasible.

## Observations

The variables recur across the questions: `p` and `q` are prime factors, `n` is their product, `e` is the public exponent, and `d` is the private exponent. A recovered plaintext is returned as a decimal integer, suggesting that it may need to be decoded as bytes afterward.

## Hypothesis

The prompts use textbook RSA arithmetic. The values can be derived from the standard RSA relationships; when the plaintext is presented as an integer, converting it to bytes may reveal readable text.

## Analysis

### Variables and general formulas

- `p`, `q`: distinct prime numbers.
- `n = p × q`: the RSA modulus, included in the public key.
- `φ(n) = (p − 1)(q − 1)`: Euler's totient when the prime factors are known.
- `e`: the public exponent, chosen so that `gcd(e, φ(n)) = 1`.
- `d`: the private exponent, satisfying `e × d ≡ 1 (mod φ(n))`.
- `m`: the plaintext represented as an integer, with `0 ≤ m < n`.
- `c`: the ciphertext integer.

Textbook RSA encryption and decryption are:

```text
c = m^e mod n
m = c^d mod n
```

For example, choose the small toy values `p = 11`, `q = 17`, and `e = 3`:

```text
n   = 11 × 17 = 187
φ(n) = 10 × 16 = 160
d   = 3^(-1) mod 160 = 107
```

If the one-byte plaintext is `A`, its byte value is `m = 65`. Encrypting and decrypting gives:

```text
c = 65^3 mod 187 = 109
m = 109^107 mod 187 = 65
```

The integer `65` is hexadecimal `41`, which is the ASCII byte for `A`. In general, convert the decrypted integer to an even-length hexadecimal byte sequence, then decode those bytes using the expected text encoding.

### Applying the formulas to the quiz

- When `p` and `q` are supplied and `n` is requested, calculate `n = p × q`.
- When `p` and `q` are supplied and the totient is requested, calculate `φ(n) = (p − 1)(q − 1)`.
- When `e`, `p`, and `q` are supplied and `d` is requested, compute the modular inverse `d = e^(-1) mod φ(n)`.
- When `e`, plaintext `m`, and `n` are supplied and ciphertext is requested, calculate `c = m^e mod n`.
- When one factor `p` and `n` are supplied, calculate `q = n / p`, then derive `φ(n)` and `d`; decrypt with `m = c^d mod n`. Finally, convert `m` from an integer to bytes and decode the text.
- When only `n`, `e`, and `c` are supplied, decryption generally requires factoring `n`. A small exponent can permit a direct integer-root attack only in special cases, such as an unpadded message whose power did not wrap modulo `n`; check whether `c` is an exact `e`th power before assuming that shortcut applies.

These questions use unpadded textbook RSA to make the arithmetic visible. The relationships explain the quiz, but textbook RSA is not a safe way to encrypt real messages.

## Resolution

Identify which RSA variables each prompt supplies and requests, then apply the matching relationship above. Use arbitrary-precision integer arithmetic for large values, and verify encryption by checking that `m^e mod n` reproduces the supplied ciphertext. Decode the resulting integer only after the RSA calculation is complete.

## Takeaways

RSA's formulas are simple, but the security relies on keeping the factors of a suitably large modulus secret and using a secure padding scheme. The public exponent alone does not reveal the private exponent; knowing a prime factor of `n`, however, is enough to derive it.

## Artifacts intentionally omitted

Challenge-specific numbers, ciphertexts, plaintexts, and recovered flag text are omitted.
