# Session reuse caused by exposed session identifiers

## Observation

After creating an ordinary account, a secondary application page exposed active session identifiers and associated account names, including a privileged account. A session identifier is a bearer credential: the server maps it to authenticated state, so possession can be sufficient to act as that user.

## Verify the trust boundary

In an authorized instance, compare the current browser's session cookie with the values exposed by the application. Replacing only the cookie value with a listed identifier tests whether the server validates the session's ownership or simply trusts the identifier. Avoid recording or publishing any live token.

## Why it works

The flaw is disclosure of a valid credential combined with server-side trust in that credential. Cookie flags can reduce some client-side exposure, but they cannot make a token safe after the application itself discloses it.

## Defensive lessons

- Never render active session identifiers or other bearer tokens in public pages or diagnostics.
- Enforce idle and absolute expiry server-side; a persistent browser cookie is not a timeout policy.
- Rotate identifiers after login and privilege changes, and support session revocation.
- Use `Secure`, `HttpOnly`, and an appropriate `SameSite` policy as defense in depth.
