# Recovering an RSA key from image metadata

## Observation

The image itself appears ordinary, but metadata inspection reveals a long hexadecimal value. The challenge also supplies an encrypted output. This suggests the metadata may contain key material rather than the plaintext answer.

## Restore and validate the key

Inspect metadata with a tool such as `exiftool`, then copy only the hex digits from the relevant field into a local working file. Convert the plain hexadecimal bytes back to a binary PEM file with:

```bash
xxd -r -p metadata.hex recovered.pem
```

Validate the result before using it:

```bash
head recovered.pem
openssl pkey -in recovered.pem -check -noout
```

The PEM header and OpenSSL's key check distinguish a correctly reconstructed private key from malformed metadata or copied formatting characters.

## Decrypt

Use the recovered private key with the matching OpenSSL decryption operation and the challenge-provided ciphertext. Keep both artifacts local; neither is part of this portfolio repository. If decryption fails, verify the key format and the challenge's padding/mode assumptions rather than repeatedly altering the input.

## Takeaway

Metadata can carry structured data that is invisible in the image view. The hidden hex is only an encoding layer: restore the original bytes, validate their format, and then apply the cryptographic operation indicated by the other artifact.
