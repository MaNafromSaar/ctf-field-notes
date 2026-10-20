# Recovering an AES key from a timestamp hint

## Identify the construction

The encryption routine hashes the decimal timestamp string with SHA-256 and uses the first 16 digest bytes as an AES key. It encrypts padded plaintext with AES in ECB mode. The timestamp is therefore the key input; it is not itself the AES key.

The exact representation matters: hash the Unix timestamp in seconds as decimal text, then take the first 16 raw digest bytes. In hexadecimal, those key bytes appear as 32 characters.

## Derive the key and decrypt

The helper in [`scripts/decrypt_timestamped_aes.py`](../../scripts/decrypt_timestamped_aes.py) accepts the timestamp and ciphertext as command-line arguments, so it contains no challenge-specific timestamp or ciphertext:

```text
python scripts/decrypt_timestamped_aes.py <unix_timestamp> <ciphertext_hex>
```

The helper derives the key, decrypts with AES-ECB, and removes PKCS#7 padding. It also prints the derived key in hexadecimal for inspection.

## Confirm with CyberChef

I repeated the key derivation and decryption in CyberChef as a second confirmation and to practice the recipe. Use the timestamp-derived key in hexadecimal with AES Decrypt, ECB mode, hexadecimal input, and PKCS#7 padding. The decrypted output should agree with the local helper.

## Takeaway

A timestamp-derived key is reproducible when the timestamp is known, but a timestamp is usually a low-entropy key source. AES-ECB also provides no authentication and can reveal repeated block patterns. This is useful for understanding the challenge, not a secure design for real data.
