# Challenge: Project Orchid - OpenSSL-encrypted file on a disk image

## Context

The challenge provided a disk image. It was examined in Autopsy. The image and recovered files are not included in this repository.

## Observations

The useful files were in the root directory of the largest partition: an encrypted file and a shell history. The history recorded an `openssl aes256 -salt` encryption of a plaintext file, with the password supplied through `-k`. The encrypted file began with the ASCII header `Salted__`.

## Hypothesis

The history command is the exact encryption operation. Decrypting with the same cipher and the recorded password should restore the plaintext. A wrong password, cipher, or key-derivation setting would fail OpenSSL's padding check or produce non-text output.

## Analysis

`openssl aes256` is the legacy `enc` alias for AES-256-CBC. `-k` does not store an AES key in the file. It supplies a password, and OpenSSL derives the key and IV from that password together with a salt.

With `-salt`, encryption does four things:

1. Generate a random 8-byte salt.
2. Derive a 32-byte AES-256 key and a 16-byte CBC IV from the password and that salt, using the legacy `EVP_BytesToKey` function.
3. Encrypt the plaintext with AES-256-CBC.
4. Write `Salted__`, then the 8-byte salt, then the ciphertext.

The salt is not secret. It is stored so decryption can repeat the same derivation. Its job is to make each encryption unique: the same password and plaintext produce different ciphertext when the salt changes, and a precomputed table for the password alone cannot be reused across files. The password itself is not written into the ciphertext. Anyone who later finds both the password and the `Salted__` header can re-derive the same key and IV.

Decryption is the same command with `-d`, the ciphertext as input, and the password from the history. Do not add `-pbkdf2` unless the recorded command used it; that selects a different derivation and will not reproduce this key.

```sh
openssl aes256 -d -in encrypted-file -out recovered.txt -k 'PASSWORD'
```

OpenSSL 3 prints a warning that this password derivation is deprecated. That warning is not a decryption failure. `bad decrypt` is different: it means the final padding check failed, which usually indicates a mismatched password, digest, or ciphertext. Confirm the output file rather than treating the deprecation warning as failure. If padding fails on a newer OpenSSL than the one that encrypted the file, retry with `-md md5`, the historical default for this legacy derivation. The encrypting command here did not record a message digest, and the matching decrypt restored the plaintext.

## Resolution

Autopsy exposed the encrypted file and the command that created it. Reversing that command with the recorded password recovered the plaintext. The password and recovered answer are omitted.

## Takeaways

A shell history can preserve the exact cryptographic operation, including a password that the ciphertext does not contain. For this OpenSSL format, the salt is public metadata used to derive the key; it is not the key, and it is not a second password. Real secret handling should not place passwords on command lines, where they can be stored in history.

## Artifacts intentionally omitted

- The challenge disk image.
- The shell history and encrypted file recovered from it.
- The password and recovered answer.
