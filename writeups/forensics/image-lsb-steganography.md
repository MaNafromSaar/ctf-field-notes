# Challenge: Image steganography with LSB analysis

## Context

The challenge provided an image and required recovering content concealed within it. The original image is not included in this repository.

## Observations

Initial inspection in IrfanView covered visually suspicious areas, image metadata, and the file's hex data. None of these checks exposed the hidden content directly.

## Hypothesis

The image may contain data encoded in its pixel values, such as through least-significant-bit (LSB) steganography. A plausible extraction from an appropriate image channel or bit plane would support this; noise or arbitrary output would not.

## Analysis

Rather than writing a new LSB extraction script, I used StegSolve Online to inspect the image with its existing steganography analysis and extraction features. The tool returned a coherent result consistent with the challenge. The important check was that the output made sense as challenge data, not merely that a tool produced bytes.

## Resolution

The hidden content was recovered using StegoToolkit's existing analysis. No custom extractor was needed. The result itself is omitted so the write-up documents the method without publishing the answer.

## Takeaways

Recognizing when to use a known tool is part of effective analysis: it avoids rebuilding common functionality and leaves more time to validate the evidence. StegSolve Online's official description says processing happens in the browser and the image is not uploaded; a Java desktop version is also available. The useful lesson for real forensic work is to verify how a tool handles data and follow organizational policy, rather than assuming that every online interface uploads its inputs.

## Artifacts intentionally omitted

- The challenge-provided image.
- The extracted content and answer.
