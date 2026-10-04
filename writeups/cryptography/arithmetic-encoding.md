# Reversing an arithmetic character encoding

## Observe controlled runs

The program asks an arithmetic question and emits a sequence of integers. Local runs with different answers show that each encoded integer scales with the submitted result. This is evidence for a simple per-byte multiplication, not a cryptographic cipher.

Model one output as:

```text
encoded[i] = byte[i] * answer
```

Use multiple controlled inputs to test whether dividing each output by the answer yields the same byte sequence. For an online run, solve the prompt, divide the corresponding values, and verify the quotients form plausible bytes before decoding them as text.

## Avoid false certainty

One readable-looking output is not enough to establish the transform. Confirm the same rule across multiple positions and at least two local runs, and check for non-integral quotients or values outside the byte range.

## Takeaway

Controlled experiments expose simple transformations quickly. The interesting work is identifying what changes between runs and validating a model, not guessing the encoded answer.
