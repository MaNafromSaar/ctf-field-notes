# Challenge:  file types - nested archives and more

## Context

The challenge provided a file named `Flag.pdf`. Despite its extension, its contents were a shell archive. The challenge artifact and extracted layers are not included in this repository.

## Observations

The `file` command identified the input as a shell archive. Running the inspected archive script produced a file that `file` identified as an `ar` archive. Each extraction or decompression revealed another format, and the final text was hexadecimal rather than directly readable.

## Hypothesis

The challenge is a sequence of nested containers and compression formats, not a single encrypted file. Identifying each layer by its content signature should reveal the next appropriate listing or decompression tool.

## Analysis

Work in a fresh directory and inspect the shell archive before running it: a shar file is executable shell code. Running it with `sh` extracts the first payload, an `ar` archive. List archive contents before extracting, and use a separate directory for each extraction so that files with the same name do not overwrite earlier layers.

The observed chain was:

| Layer | What it is | How it was handled |
|---|---|---|
| SHAR | A shell archive: shell commands that reconstruct embedded files. | Inspect, then run with `sh` in an isolated directory. |
| `ar` | A Unix archive format, often used for libraries. | List with `ar t`, then extract with `ar x`. |
| CPIO | A Unix archive format for storing files and metadata. | List with `cpio -it < archive`; extract in a separate directory with `cpio -id < archive`. |
| bzip2 | A compressed stream using the Burrows–Wheeler transform. | `bzip2 -dc input > output` |
| gzip | A DEFLATE-compressed stream. | `gzip -dc input > output` |
| lzip | An LZMA-based compression format. | `lzip -dc input > output` |
| LZMA | A standalone LZMA-compressed stream. | `lzma -dc input > output` |
| LZ4 | A fast compression format. | `lz4 -d -c input > output` |
| LZOP | A compression format using the LZO algorithm. | `lzop -d -c input > output` |
| lzip | Another lzip-compressed layer. | `lzip -dc input > output` |
| XZ | A container format that commonly uses LZMA2 compression. | `xz -dc input > output` |
| Hex | Text encoding in which each pair of hex digits represents one byte. | `xxd -r -p input > output` |

After each operation, `file output` verified the next layer. Writing decompressor output to a new file with `-c` avoided relying on filename extensions and preserved the input for inspection. The final hex decoding produced the challenge answer; the answer is omitted here.

## Resolution

The archive was unpacked one layer at a time, using each detected file signature to choose the next extraction or decompression tool. The terminal layer was hex-decoded with `xxd`; no cryptographic decryption was required.

## Takeaways

File extensions are hints, not evidence: `file` and content signatures guided the investigation. Archives contain files, compression formats encode data, and hex is an encoding rather than encryption. Listing archive contents and using isolated directories makes a long extraction chain safer and easier to follow.
Along the way you are exposed to more exotic filetypes and archives, which can broaden your understanding of different compression and packaging methods used in various computing environments.
The Matroschka structure of the nesting is a fun component and piques curiosity about where the iteration will stop. Once you see that the extracted type is just ASCII, you go on to read and see... yet another layer.

## Artifacts intentionally omitted

- The challenge-provided shell archive.
- All extracted intermediate files.
- The recovered answer.
