# Credential reuse and response classification

## Investigation

The challenge presented a login service and a supplied credential list. Before automating anything, identify the input format and determine whether each attempt gets a fresh connection. A small, authorized test establishes the protocol and the service's failure response.

## Avoid the banner false positive

The first response parser treated a generic welcome banner as success, but the banner appeared for both valid and invalid logins. Classify results using a response that is specific to an authenticated state, and reject explicit failure responses first. Authentication success should be verified by a subsequent action that requires the authenticated state, not by a keyword that appears in static text.

The supplied credentials and the original attempt script are intentionally not included. Credential reuse testing belongs only in the challenge environment and should remain within its stated scope.

## Defensive lessons

Use unique passwords, block known-compromised credentials, add appropriate throttling and monitoring, and avoid response behavior that makes authentication outcomes ambiguous. Detection should distinguish repeated failures from normal traffic without exposing account existence unnecessarily.
