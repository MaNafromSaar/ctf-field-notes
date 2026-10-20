# CTF Field Notes

A portfolio of forensic and technical investigations developed through CTF challenges. Each write-up follows evidence from an initial observation to a tested explanation, with emphasis on reproducibility and understanding the underlying behavior rather than publishing a copy-paste answer.

The techniques span artifact analysis, reverse engineering, network services, and application security. Tool choice is driven by the question and the evidence available; scripts are included when automation adds clarity or repeatability, not because every challenge needs one.

## Start here

If you only read a few, these show the investigative approach best:

| Write-up | Why it is worth reading |
| --- | --- |
| [Unforgotten Bits](writeups/forensics/unforgotten-bits.md) | Multi-layer disk-image investigation in Autopsy: hidden files, slack-space artifacts, steganography, and encodings, with clues connected across mail, chat, and browser history. |
| [Project Orchid](writeups/forensics/disk-image-openssl-enc.md) | Reconstructing an encryption operation from shell history and an encrypted file found on a disk image. |
| [Invisible WORDs](writeups/forensics/invisible-words.md) | Bit-level analysis of pixel data, backed by a reusable bit-lane splitter. |
| [Finding ROT13 text in a packet capture](writeups/forensics/rot13-in-packet-capture.md) | Triage of a capture: separating encrypted traffic from plain text and testing a simple encoding hypothesis. |
| [Extension traffic: intent versus executed behavior](writeups/reversing/extension-traffic-analysis.md) | Reading extension code for what it collects and transmits, and separating apparent intent from what actually executes. |
| [ChaCha20-Poly1305 nonce reuse](writeups/cryptography/chacha20-poly1305-nonce-reuse.md) | Explains why a reused nonce breaks authenticated encryption, with a derivation and a solver. |
| [Fool Lockout](writeups/web/fool-lockout-rate-limit.md) | Source review showing that a nominal lockout was only a rate-limit window, plus a careful credential tester. |

## Write-ups

### Binary Exploitation
- [Echo Escape: ret2win with a stack overwrite](writeups/binary-exploitation/echo-escape.md)
- [PIE Time: deriving a runtime function address](writeups/binary-exploitation/pie-time.md)
- [Bytemancy: answering randomized function-address prompts](writeups/binary-exploitation/bytemancy.md)
- [Bytemancy 1: sending a fixed repeated-byte input](writeups/binary-exploitation/bytemancy1.md)
- [Leaking a flag through a format string](writeups/binary-exploitation/format-string-stack-leak.md)

### Cryptography
- [RSA quiz: key relationships, modular arithmetic, and byte decoding](writeups/cryptography/rsa-quiz-basics.md)
- [Known-plaintext recovery against repeating XOR](writeups/cryptography/repeating-xor.md)
- [Reversing an arithmetic character encoding](writeups/cryptography/arithmetic-encoding.md)
- [mus1c: recognizing a Rockstar program](writeups/cryptography/mus1c-rockstar.md)
- [Recognizing and inspecting a Fernet token](writeups/cryptography/fernet-token.md)
- [Recovering an AES key from a timestamp hint](writeups/cryptography/timestamp-derived-aes.md)
- [ChaCha20-Poly1305: forging ciphertext after a reused nonce](writeups/cryptography/chacha20-poly1305-nonce-reuse.md)

### Forensics
- [Recovering an RSA key from image metadata](writeups/forensics/stego-rsa.md)
- [Image steganography with LSB analysis](writeups/forensics/image-lsb-steganography.md)
- [Invisible WORDs: data in unused pixel bits](writeups/forensics/invisible-words.md)
- [Finding ROT13 text in a packet capture](writeups/forensics/rot13-in-packet-capture.md)
- [Recovering a hidden flag from a TFTP transfer](writeups/forensics/trivial-flag-transfer-protocol.md)
- [Unforgotten Bits: layered image steganography and encodings](writeups/forensics/unforgotten-bits.md)
- [Unpacking nested file formats](writeups/forensics/nested-filetypes.md)
- [Reversing an OpenSSL enc file from a disk image](writeups/forensics/disk-image-openssl-enc.md)

### Reversing
- [Using LLDB to inspect a runtime password check](writeups/reversing/lldb-password-check.md)
- [Tracing an obfuscated hash input through an ELF](writeups/reversing/obfuscated-hash.md)
- [Gatekeeper: probing numeric input formats](writeups/reversing/gatekeeper-numeric-format.md)
- [Investigative Reversing 0: decoding appended PNG data](writeups/reversing/investigative-reversing-0.md)
- [Extension traffic: intent versus executed behavior](writeups/reversing/extension-traffic-analysis.md)

### Web and Services
- [Fool Lockout: a rate-limit window mistaken for a lockout](writeups/web/fool-lockout-rate-limit.md)
- [Session reuse caused by exposed session identifiers](writeups/web/session-reuse.md)
- [Predictable identifiers and an IDOR](writeups/web/md5-idor.md)
- [Inspecting response headers across HTTP methods](writeups/web/response-headers.md)
- [Sockfish: tampering with client-reported evaluation](writeups/web/sockfish-evaluation-tampering.md)
- [Shell injection in a ping wrapper](writeups/web/ping-command-injection.md)
- [A bounded rate-limit failover condition](writeups/web/rate-limit-failover.md)
- [OTP brute force and session-cookie races](writeups/web/otp-session-race.md)
- [Credential reuse and response classification](writeups/web/credential-stuffing.md)
- [SQL injection through a secret field](writeups/web/secret-box-sql-injection.md)
- [IntOverflowBank: triggering a Solidity 0.6 integer wraparound](writeups/web/int-overflow-bank.md)

### Services
- [Identifying SMB behind a forwarded port](writeups/services/smb-print-server.md)

### Infrastructure
- [Using a supplied Kubernetes client configuration](writeups/infrastructure/kubernetes-secret.md)

## Tools and reusable code

- [LLDB field notes](notes/lldb.md)
- [Fernet inspection helper](scripts/decrypt_fernet.py)
- [Timestamp-derived AES decryption helper](scripts/decrypt_timestamped_aes.py)
- [Bytemancy address-response helper](scripts/solve_bytemancy.py)
- [Bytemancy 1 repeated-input sender](scripts/solve_bytemancy1.sh)
- [ELF obfuscated-hash helper](scripts/recover_obfuscated_hash.py)
- [Local wordlist digest search](scripts/search_hash_wordlist.py)
- [Fool Lockout credential tester](scripts/fool_lockout_credential_tester.py)
- [Read-only printf format-string pointer probe with iterative scanning](scripts/format_string_probe.py)
- [Splitter for lower and upper bit lanes in fixed-width word streams](scripts/split_word_stream.py)
- [Unforgotten Bits golden-ratio decoder](scripts/decode_golden_ratio.py)
- [Unforgotten Bits champion passphrase candidate tester](scripts/fuzz_lol_champion_passphrases.py)
- [IntOverflowBank transaction helper using Foundry Cast](scripts/solve_int_overflow_bank.sh)
- [ChaCha20-Poly1305 nonce-reuse forgery solver](scripts/chacha20-Poly1305_nonce_solver.py)

Network helpers require explicit current-instance arguments and make no requests until run. Other helpers operate on local inputs. Use the matching tools and libraries for the challenge environment.

For binary analysis, online decompilation can be a useful way to inspect a program quickly. Preserve the original artifact, record any transformation, and validate important conclusions against runtime behavior or lower-level evidence. Only submit challenge artifacts to external services when their terms and handling are appropriate.

## Publication rules

Challenge-provided binaries, source bundles, databases, captures, images, archives, credentials, keys, and extracted answers do not belong here. Write-ups use placeholders for instance hosts and ports. Notes describe the method and evidence to look for, but intentionally omit flags and other copy-paste answers. Screenshots are exceptional and must be reviewed before being added under a write-up's `assets/screenshots/` directory.

All techniques are documented for authorized CTF environments. Instance-specific services should be treated as temporary and should never be hard-coded into reusable scripts.
