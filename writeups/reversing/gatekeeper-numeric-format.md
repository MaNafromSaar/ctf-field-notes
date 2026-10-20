# Gatekeeper: probing numeric input formats

## Test the boundaries

The prompt asks for a value above a threshold, but the program also requires a three-character input. Decimal input cannot satisfy both conditions, so test alternative representations rather than trying ever-larger decimal strings. Roman-numeral-looking input was rejected; hexadecimal input worked.

## Recognize the output

The accepted value revealed flag text with a repeated noise marker and reversed character order. Removing the repeated marker and reversing the remaining text recovered the flag format.

## Takeaway

Even in a reversing challenge, simple boundary tests and educated guesses about input formats can reveal the intended path before deep binary analysis is needed.
