# Predictable identifiers and an IDOR

## Observation

An authenticated profile request used a hash-like path component. The value corresponded to MD5 of the account's small numeric identifier, making it possible to test the mapping locally. The hash did not provide authorization; it only obscured a predictable object reference.

## Test the mapping

Given an account identifier, compute its MD5 digest and compare it with the profile path observed in the browser. If the relationship holds, nearby candidate identifiers can be tested against the profile endpoint using the same authenticated session. Use only the assigned challenge instance, keep the range bounded, and avoid saving session cookies or returned private data in this repository.

A generic local check of the transform is:

```bash
printf '%s' '<USER_ID>' | md5sum
```

## Root cause

The server accepted a user-controlled reference without checking that the requested profile belonged to the authenticated account. This is an insecure direct object reference (IDOR). Hashing or encoding an identifier does not fix missing authorization, especially when the input space is enumerable.

## Defensive lessons

Authorize each object access on the server. Prefer opaque identifiers only as defense in depth; they do not replace an ownership or permission check. Rate limits can slow enumeration but do not correct the access-control flaw.
