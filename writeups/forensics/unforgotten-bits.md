# Challenge: Unforgotten Bits

## Context

The challenge provided a four-partition filesystem image. Only one partition
contained the user artifacts relevant to the investigation; that filesystem
looked ordinary. Its root and user home contained notes, mail, chat logs,
browser history, and references to a gallery of four BMP images. No challenge
artifacts are included in this repository.

## Artifact examination

I loaded the image into Autopsy and began by comparing its partitions rather
than assuming the first one was the target. Three partitions did not contain
relevant user evidence; the remaining partition held a normal-looking
filesystem. In a CTF, the root directory and suspected user's home are often
productive starting points, so I prioritized those while still checking the
broader filesystem for overlooked artifacts.

That approach surfaced the notes, mail, shell history, and image references.
The browser-history directory was hidden, and the slack-space artifacts were
not visible in the standard file view. I had to inspect hidden items and use
Autopsy's slack-artifact view to find the otherwise easy-to-miss stream of
`0`, `1`, and `.`. Finding and interpreting that artifact was a major part of
the challenge, not just a decoding step. It also gave me practical experience
with Autopsy's partition navigation and artifact views. I then tested the
hypotheses from those artifacts with focused decoding and decryption steps.

## Observations

The root shell history contained a directory listing (`ls -la`) and shutdown
commands. Together with repeated L/A hints elsewhere, this drew my attention
to deleted data and to enabling slack-space artifacts in Autopsy's view. The
slack remnants were not visible in the standard file view. Separately,
home-directory notes contained names I recognized as League of Legends
references. That cultural context made the champion-name interpretation—and
later the passphrase-candidate strategy—plausible; without it, the names
could have looked unrelated. A suspicious email urged the user to remove
mail and clean the trash. The gallery and chat logs connected these clues to
the images.

One chat log gave a layered extraction procedure: use steghide on the BMPs,
then decrypt the extracted payloads with OpenSSL AES-CBC using parameters
provided in the chat. The actual passphrase, key, IV, and salt are omitted
here.

The first, second, and fourth images yielded payloads that decrypted into
the first 1,000 lines of Project Gutenberg copies of *Dracula*,
*Frankenstein*, and *Les Misérables*. Comparing them against Gutenberg
editions did not reveal the answer; the texts were a training lead toward a
different encoding, not the final payload.

### Hidden hints

The browser history contained three useful references: Church encoding, a
general overview of numeric encodings, and golden-ratio base notation. The
first two broaden the search for possible representations; the golden-ratio
reference points directly to the remaining slack-space message. The root
`.ash-history` entry `ls -al` also emphasizes checking hidden files when
exploring the challenge filesystem.

An attached slack-space remnant contained a stream of `0`, `1`, and `.`. The
periods initially made the data look like dot-separated numerals, but they
fall every 14 bits after an initial 11-bit prefix. In the continuous bitstream,
each decoded character is a 14-bit base-\(\phi\) numeral with 11 digits before
the radix point and 3 after it. The periods therefore do not delimit
characters; the character frames cross them.

## Hypothesis

The four BMPs contain separate steghide payloads, with encryption or another
encoding applied afterward. The notes' known passphrase prefix plus the
League-of-Legends context may constrain the remaining image's steghide
password. The browser-history searches may point to a further transformation
of that image's extracted payload.

## Analysis

### Extract and decrypt the first three identified payloads

For each gallery BMP, extract the embedded payload with steghide, supplying
the passphrase from the chat log:

```bash
steghide extract -sf <image.bmp> -p "$STEG_PASSPHRASE" -xf <payload.bin>
```

Decrypt the payloads for images 1, 2, and 4 with the AES-256-CBC key and IV
from that same chat. Keep the values out of shared notes and command history:

```bash
openssl enc -d -aes-256-cbc \
  -K "$AES_KEY_HEX" -iv "$AES_IV_HEX" \
  -in <payload.bin> -out <plaintext.txt>
```

The resulting Gutenberg headers identify the three books. Comparing those
texts to Gutenberg editions was tested, but did not expose the answer.

### Recover the remaining steghide payload

The notes supplied the beginning of a passphrase, and the browser history
showed that the user researched number encodings. Separately, the champion
context suggested testing a four-name concatenation: the known two-name
prefix followed by two more champion names, with no separators.

A wordlist of 173 normalized champion IDs from Riot's Data Dragon 16.20.1 was
used to generate every ordered pair after the known prefix (173² = 29,929
candidates). Testing those candidates against the remaining BMP with
steghide succeeded and recovered a 560-byte payload. The exact passphrase and
payload are intentionally omitted.

The candidate generator for this challenge is available as
[fuzz_lol_champion_passphrases.py](../../scripts/fuzz_lol_champion_passphrases.py).
It tested the complete ordered-pair space, including names already present in
the known prefix.

### Decode the slack-space message

Applying the chat's AES key and IV directly to the 560-byte payload failed
OpenSSL's CBC padding check. Rather than treating the failed attempt as
evidence of corruption, the other artifact—the bitstream found in slack
space—provided a route to the missing parameters.

Treat each 14-bit frame as a positional numeral in base
\(\phi=(1+\sqrt{5})/2\): the 11 integer digits have weights
\(\phi^{10},\ldots,\phi^0\), and the 3 fractional digits have weights
\(\phi^{-1},\ldots,\phi^{-3}\). The periods appear every 14 bits after an
initial 11-bit prefix, so they are not character delimiters. Each character
frame crosses a period; concatenating the bit groups and grouping into
11-bit integer parts plus 3-bit fractional parts recovers the framing.

For example, the first frame is `01010010100.010`. Its set digits contribute
\(\phi^9+\phi^7+\phi^4+\phi^2+\phi^{-2}\), approximately 114.90, which rounds
to ASCII `s`. The complete sequence decodes to 127 characters containing
`salt`, `key`, and `iv` fields. This is a base-\(\phi\) positional expansion,
not a direct Zeckendorf conversion using integer Fibonacci weights. The
decoder is available as
[decode_golden_ratio.py](../../scripts/decode_golden_ratio.py). Run it with
the slack-space text file as its input:

```bash
python3 scripts/decode_golden_ratio.py /path/to/1.txt
```

The decoded salt, key, and IV are then used to decrypt the recovered payload
with AES-256-CBC.

```bash
openssl enc -d -aes-256-cbc \
  -K "$RECOVERED_KEY_HEX" -iv "$RECOVERED_IV_HEX" \
  -in pic3-payload.bin -out pic3_decrypted.bin
```

The output is a text file containing the flag. Its value is intentionally
omitted from this write-up.

The browsing-history links are useful context in their own right:

- [Church encoding](https://en.wikipedia.org/wiki/Church_encoding) describes
  representing data and operations as functions in lambda calculus. It was a
  plausible lead from the history, but not the encoding used here.
- [Numeric Encoding](https://cs.lmu.edu/~ray/notes/numenc/) surveys numeral
  systems, including positional notation, and helps frame the question of
  how a sequence of digits can represent numbers.
- [Golden ratio base](https://www.wikiwand.com/en/Golden_ratio_base) explains
  positional notation using powers of \(\phi\), which matches the slack-space
  data.

Links were accessed on 2026-10-15.

## Resolution

The filesystem clues lead to the chat instructions; steghide extracts data
from the BMPs; AES-CBC reveals three Gutenberg excerpts; a focused
champion-name wordlist recovers the remaining image's payload; and the
slack-space remnant decodes as base-\(\phi\) ASCII containing the salt, key,
and IV needed for its decryption. That final decryption reveals a text file
containing the flag. The flag and cryptographic values are intentionally
omitted.

## Takeaways

This was a deliberately layered investigation with useful dead ends. The
Gutenberg excerpts looked promising, but comparisons did not yield the flag.
The failed AES attempt prompted a return to the slack-space data and the
browser-history hints. Separating extraction, encoding, and decryption made
it possible to validate each stage: base-\(\phi\) values rounded cleanly to
ASCII fields, and those recovered parameters decrypted the remaining
payload. A golden-ratio hint can indicate powers of \(\phi\), not only
Fibonacci-number weights; delimiter spacing helps infer framing, while
readable output validates the interpretation.

## Artifacts intentionally omitted

- The challenge filesystem, BMP images, mail, chat logs, and browser history.
- Extracted payloads and Gutenberg texts.
- Passphrases, cryptographic parameters, the final answer, and other
  copy-paste secrets.
