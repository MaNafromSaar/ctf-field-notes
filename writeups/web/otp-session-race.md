# OTP brute force and session-cookie races

## Application behavior

The application used a four-digit OTP with a short validity window, but no attempt limit or lockout. That makes the search space small enough to investigate in a challenge. A sequential script can still fail because network and server latency consume much of the OTP lifetime.

## The concurrency trap

The initial parallel search appeared to find a success, yet a follow-up request returned the login page. The important detail was Flask's signed client-side session cookie: concurrent failed requests could return newer cookies containing unauthenticated state. A shared mutable cookie jar allowed those failures to overwrite the cookie from the successful response.

The reliable diagnostic is to inspect the successful OTP response itself, preserve its `Set-Cookie` value, and use that exact session state for a follow-up request. Confirm the authenticated state before treating the guess as successful.

## Takeaway

Concurrency improves throughput, but mutable authentication state introduces races. Isolate per-attempt request state, capture the success response's session explicitly, and budget for server-side expiry. The application-side root cause is the missing attempt control, not the client's search strategy.

## Defensive lessons

Rate-limit OTP verification, enforce attempt limits and lockouts carefully, bind challenges to the correct login session, and avoid allowing parallel attempts to invalidate or replace successful state unpredictably.
