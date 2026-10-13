# CTF Field Notes

A portfolio of forensic and technical investigations developed through CTF challenges. Each write-up follows evidence from an initial observation to a tested explanation, with emphasis on reproducibility and understanding the underlying behavior rather than publishing a copy-paste answer.

The techniques span artifact analysis, reverse engineering, network services, and application security. Tool choice is driven by the question and the evidence available; scripts are included when automation adds clarity or repeatability, not because every challenge needs one.

## Write-ups

### Binary Exploitation
- [Echo Escape: ret2win with a stack overwrite](writeups/binary-exploitation/echo-escape.md)
- [PIE Time: deriving a runtime function address](writeups/binary-exploitation/pie-time.md)
- [Bytemancy: answering randomized function-address prompts](writeups/binary-exploitation/bytemancy.md)
- [Leaking a flag through a format string](writeups/binary-exploitation/format-string-stack-leak.md)

### Cryptography
- [Known-plaintext recovery against repeating XOR](writeups/cryptography/repeating-xor.md)
- [Reversing an arithmetic character encoding](writeups/cryptography/arithmetic-encoding.md)
- [Recognizing and inspecting a Fernet token](writeups/cryptography/fernet-token.md)

### Forensics
- [Recovering an RSA key from image metadata](writeups/forensics/stego-rsa.md)
- [Image steganography with LSB analysis](writeups/forensics/image-lsb-steganography.md)
- [Finding ROT13 text in a packet capture](writeups/forensics/rot13-in-packet-capture.md)
- [Unpacking nested file formats](writeups/forensics/nested-filetypes.md)

### Reversing
- [Using LLDB to inspect a runtime password check](writeups/reversing/lldb-password-check.md)
- [Tracing an obfuscated hash input through an ELF](writeups/reversing/obfuscated-hash.md)
- [Extension traffic: intent versus executed behavior](writeups/reversing/extension-traffic-analysis.md)

### Web and Services
- [Fool Lockout: a rate-limit window mistaken for a lockout](writeups/web/fool-lockout-rate-limit.md)
- [Session reuse caused by exposed session identifiers](writeups/web/session-reuse.md)
- [Predictable identifiers and an IDOR](writeups/web/md5-idor.md)
- [Inspecting response headers across HTTP methods](writeups/web/response-headers.md)
- [Shell injection in a ping wrapper](writeups/web/ping-command-injection.md)
- [A bounded rate-limit failover condition](writeups/web/rate-limit-failover.md)
- [OTP brute force and session-cookie races](writeups/web/otp-session-race.md)
- [Credential reuse and response classification](writeups/web/credential-stuffing.md)
- [SQL injection through a secret field](writeups/web/secret-box-sql-injection.md)

### Services
- [Identifying SMB behind a forwarded port](writeups/services/smb-print-server.md)

### Infrastructure
- [Using a supplied Kubernetes client configuration](writeups/infrastructure/kubernetes-secret.md)

## Tools and reusable code

- [LLDB field notes](notes/lldb.md)
- [Fernet inspection helper](scripts/decrypt_fernet.py)
- [Bytemancy address-response helper](scripts/solve_bytemancy.py)
- [ELF obfuscated-hash helper](scripts/recover_obfuscated_hash.py)
- [Local wordlist digest search](scripts/search_hash_wordlist.py)
- [Fool Lockout credential tester](scripts/fool_lockout_credential_tester.py)
- [Read-only printf format-string pointer probe with iterative scanning](scripts/format_string_probe.py)

Network helpers require explicit current-instance arguments and make no requests until run. Other helpers operate on local inputs. Use the matching tools and libraries for the challenge environment.

For binary analysis, online decompilation can be a useful way to inspect a program quickly. Preserve the original artifact, record any transformation, and validate important conclusions against runtime behavior or lower-level evidence. Only submit challenge artifacts to external services when their terms and handling are appropriate.

## Publication rules

Challenge-provided binaries, source bundles, databases, captures, images, archives, credentials, keys, and extracted answers do not belong here. Write-ups use placeholders for instance hosts and ports. Notes describe the method and evidence to look for, but intentionally omit flags and other copy-paste answers. Screenshots are exceptional and must be reviewed before being added under a write-up's `assets/screenshots/` directory.

All techniques are documented for authorized CTF environments. Instance-specific services should be treated as temporary and should never be hard-coded into reusable scripts.
