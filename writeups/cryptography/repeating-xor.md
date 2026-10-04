# Known-plaintext recovery against repeating XOR

## Observation

A local challenge program produced a known test ciphertext and a corresponding non-secret test plaintext. A second ciphertext began with the same bytes, suggesting the same deterministic key and keystream were reused.

## Recover the repeating key

For XOR encryption, each ciphertext byte is the plaintext byte XORed with a key byte. XORing a known plaintext with its ciphertext recovers the corresponding key-stream bytes:

```text
key_stream[i] = ciphertext[i] XOR plaintext[i]
```

Compare the recovered bytes for repetition. If the repeating pattern is shorter than the known plaintext, the key is likely that pattern; verify it against the full known pair before applying it elsewhere.

Decrypt each ciphertext byte with the key byte at the same position modulo the key length:

```text
plaintext[i] = ciphertext[i] XOR key[i mod key_length]
```

## Validation

Check that decryption reproduces the entire known test plaintext, not just its prefix. For a separate ciphertext, inspect whether the result has plausible structure and expected encoding before treating it as valid.

## Takeaway

XOR is reversible, and reusing a short repeating key leaks a predictable keystream. A known-plaintext sample can expose the key without brute force; the core failure is key/keystream reuse, not a weakness in hexadecimal encoding.
