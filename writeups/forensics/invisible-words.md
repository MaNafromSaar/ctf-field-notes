# Challenge: Invisible WORDs

## Context

The challenge provided a BMP image. The challenge title emphasized “WORDs,”
suggesting a look at the representation of the pixel data rather than only
the rendered image. The original image is not included in this repository.

## Observations

File identification reported a 32-bit, 960 × 540 BMP. IrfanView showed
`original colors: 32bit` and `current colors: 24bit`, a prompt to compare the
stored pixel width with the color information used to display the image.

The BMP header supplied the more precise clue: the red, green, and blue masks
were `0x00007c00`, `0x000003e0`, and `0x0000001f`. Those masks occupy bits 0
through 14 of each 32-bit pixel word. No declared color mask uses bits 15
through 31.

## Hypothesis

The higher-order bits of each stored pixel word may contain data that does
not contribute to the visible color. The hypothesis is testable by separating
the upper and lower bit lanes and checking whether either produces a
recognizable file format.

## Analysis

The key distinction is between a pixel's stored width and the bits assigned
to its color channels. Although each pixel occupies 32 bits, the stated RGB
masks use only 15 bits in total. The title's “WORD” points to examining the
upper 16-bit portion separately,  the word-width is actually 16, not 32 as claimed.

The reusable helper [`split_word_stream.py`](../../scripts/split_word_stream.py)
splits a byte stream into lower and upper bit lanes. For this BMP, the pixel
array starts at byte offset 138; skip the BMP header, then treat each pixel as
a 32-bit little-endian word and split at bit 16:

```bash
python3 scripts/split_word_stream.py output.bmp \
  --skip-bytes 138 --save-skipped-bytes \
  --word-bits 32 --split-bit 16 --byteorder little
file output.bmp.lower.bin output.bmp.upper.bin
```

The helper accepts a split at any bit position and an optional leading-byte
skip for container headers. Add `--save-skipped-bytes` to retain the skipped
prefix separately as `output.bmp.header.bin`. Each lane is packed
least-significant-bit first; if a lane's total length is not byte-aligned, its
last output byte is zero-padded. The default byte order is little-endian, and
it can be changed with `--byteorder big`. If either numeric option is omitted
in an interactive terminal, the helper prompts for it. Word widths must be a
positive multiple of eight, since input words are read from a byte stream.

The upper-lane output begins with a ZIP local-file signature. A normal
`unzip` attempt reports that it cannot find an end-of-central-directory
record. The stream contains extensive trailing padding after the embedded
archive records, so the end record is not near the end of the extracted lane
where ordinary ZIP readers expect to find it. The archive can be salvaged
into a new file with Info-ZIP:

```bash
cp output.bmp.upper.bin found.zip
zip -FF found.zip --out restore.zip
unzip restore.zip
```

This repair step scans and rebuilds archive directory/end records; it does
not require appending a literal `/EOF` string to the extracted data. The
recovered ZIP entry has a Base64-encoded filename. Decoding the name and
searching the extracted Project Gutenberg text (The Masterpiece of Mary Shelley, 
"Frankenstein" - although H.G. Wells' "Invisible Man" would have been an even better fit) 
led to the challenge answer, which is intentionally omitted.

### Curiosity test: rebuild the lower stream as a BMP

The lower stream contains each pixel's original low 16 bits. Because the RGB
masks occupy bits 0 through 14, those bits still contain the full 5:5:5 color
values. For a visual check, reuse the saved 138-byte BMP prefix, adjust its
header to describe 16-bit pixels, and append the lower stream:

```bash
python3 - <<'PY'
from pathlib import Path
import struct

header = bytearray(Path("output.bmp.header.bin").read_bytes())
pixels = Path("output.bmp.lower.bin").read_bytes()
width, height = struct.unpack_from("<ii", header, 18)
assert width == 960 and height == 540
assert len(pixels) == width * abs(height) * 2
struct.pack_into("<I", header, 2, len(header) + len(pixels))
struct.pack_into("<H", header, 28, 16)
struct.pack_into("<I", header, 34, len(pixels))
Path("remainder_reconstructed.bmp").write_bytes(header + pixels)
PY
```

The resulting 16-bit BMP opens and renders the same central image. The raw
lower stream remains unchanged; the original 32-bit header must be adjusted
because it no longer describes the 16-bit-per-pixel data. Conversely, if the
splitter is run without skipping the BMP prefix, those header bytes become
part of the word stream and the split no longer aligns with pixel boundaries.

## Resolution

The data was concealed in the upper portion of the per-pixel words, not in a
different document format. The useful path was to inspect the image's actual
bit masks, split each 32-bit pixel at bit 16, identify the ZIP data, and
repair the archive directory so it could be extracted and searched.

## Takeaways

Do not infer a file's internal structure from its extension or displayed
color depth alone. Compare the declared pixel size with the channel masks,
then inspect unused bits as a separate data stream. When carving embedded
archives, trailing data can prevent standard readers from finding an
otherwise present ZIP directory; recovery tools can rebuild it without
altering the original evidence.

## Artifacts intentionally omitted

- The challenge-provided BMP image and extracted archive/text.
- The challenge answer and other copy-paste answer tokens.
