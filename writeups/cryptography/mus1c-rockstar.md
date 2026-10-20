# mus1c: recognizing a Rockstar program

## Context

The challenge provides a single text file of song-style lyrics and no other hint about its purpose. The challenge name and the lyrics theme suggest that the text carries a message. This is an archived challenge, so no live instance is involved.

## Observations

- The text does not match any encoding, cipher, or steganography format. It is not Base64, hex, or similar.
- Despite the lyrics, the lines are structured like statements. Some assign values (`put ... into ...`), some adjust values (`build ... up`, `knock ... down`), and some print (`shout ...`).
- Several lines contain odd-looking words and punctuation that serve no purpose in a song, such as repeated letters and trailing commas.

## Hypothesis

The file is source code in an esoteric language designed to read like song lyrics, and the "lyrics" are the program. Running it should produce the hidden data. This would be disproved if no interpreter accepts the file, or if it only produces unrelated output.

## Analysis

[Rockstar](https://codewithrockstar.com/) fits all three observations:

- Variables are named in plain English, and common words such as "my", "the", and "a" act as pronoun-style references.
- Numbers can be written as poetic literals. The length of each word in a phrase gives one digit, so lines that look like prose define numeric values.
- Keywords like `shout` print a value, and `build up` and `knock down` increment and decrement it.

To test the hypothesis, paste the file into the online Rockstar interpreter on the project's site and run it. Treat each `shout` as one output value.

## Resolution

The program prints a list of decimal numbers rather than readable text. Each number lies in the printable ASCII range, so they are character codes. Converting them with a decimal-to-ASCII tool such as [dCode's ASCII decoder](https://www.dcode.fr/ascii-code) gives the answer. No script is needed; both steps are done with existing online tools.

The final text should have the expected flag format. A garbled result would point to a misread poetic literal or a missed increment or decrement, so that is the first thing to recheck.

## Takeaways

Esoteric languages are a recurring CTF theme, and the key step is recognizing one. When text has statement-like structure but fits no encoding, look for a language disguised as prose or art. Other examples include Shakespeare, Piet, Whitespace, and Brainfuck.

For analysis, run unfamiliar code in an isolated interpreter and inspect the output as data. A browser-based interpreter is convenient here, but only paste challenge material into external tools when that is appropriate, as for this archived, public challenge.

## Artifacts intentionally omitted

- The provided lyrics file, which is the program source.
- The program output and the decoded flag.
