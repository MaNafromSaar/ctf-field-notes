# Sockfish: tampering with client-reported evaluation

## Observation

The browser runs Stockfish in a worker and forwards its evaluation through the challenge's message flow. The challenge trusted that reported score.

## Intercept

Using Burp Suite, intercept the evaluation messages and replace the score with a sufficiently negative value. The challenge then treated Stockfish as having lost and triggered its resignation condition, without requiring a winning chess line.

## Takeaway

The weakness was trusting a client-controlled evaluation as authoritative game state. A client-reported score should not decide a server-side outcome.
