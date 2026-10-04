# Recognizing and inspecting a Fernet token

## Recognition

The source labels a key as URL-safe Base64 representing 32 bytes. That format is characteristic of Fernet, the authenticated symmetric encryption recipe in Python's `cryptography` package. A Fernet token commonly has a recognizable version byte when Base64-decoded, but its content is still authenticated ciphertext, not plain Base64 text.

## Decrypt locally

Use the provided key and token with `cryptography.fernet.Fernet`. The helper in [`scripts/decrypt_fernet.py`](../../scripts/decrypt_fernet.py) accepts both values as command-line arguments and prints the authenticated plaintext. It contains no challenge key, ciphertext, or destination. Inspect the plaintext as data; do not automatically make a network request to a recovered URL.

A successful decryption confirms that the key and token are compatible and that the token's authentication tag verifies. A failure can mean the wrong key, a truncated or altered token, or a different encryption format.

## Takeaway

The key's encoding and length identify a likely library, while authenticated decryption is the test. Encoding is not encryption, and a hidden service destination should be analyzed as text rather than contacted automatically.
