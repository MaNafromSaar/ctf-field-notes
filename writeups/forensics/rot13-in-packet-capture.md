# Challenge: Wireshark Doo Dooo Doo Do Doo ROT13 in a packet capture

## Context

The challenge provided a PCAPNG capture for analysis in Wireshark. The capture itself is intentionally omitted from this repository.

## Observations

Searching packet bytes for ASCII flag fragments found nothing. Wireshark's protocol statistics showed that much of the traffic was encrypted, while only a small amount of line-based text data was present. That text contained a value with an obvious flag-like structure, but its contents were not readable as-is.

## Hypothesis

The flag-shaped text is encoded with a simple substitution rather than encrypted by the captured network protocol. Decoding it with ROT13 should produce readable text while preserving the recognizable structure.

## Analysis

Start with **Statistics → Protocol Hierarchy** to understand which protocols dominate the capture and avoid spending time inspecting encrypted payloads as though they were plaintext. Then filter for Wireshark's line-based text data dissector with `data-text-lines` and inspect the few matching packets. For text carried over TCP, **Follow → TCP Stream** reconstructs the conversation and avoids the clutter of ACK-only packets in the packet list.

Apply ROT13 to the candidate text and check whether the result is readable and consistent with the challenge's flag format. ROT13 is a Caesar rotation by 13 letters; it is a reversible encoding, not encryption that requires a key.

## Resolution

The line-based text packets exposed a flag-shaped candidate. ROT13 decoding made the contents readable and confirmed the result. The decoded answer is intentionally omitted.

## Takeaways

Protocol statistics helped prioritize the small amount of useful plaintext among mostly encrypted traffic. Display filters and stream reconstruction made the relevant data easier to inspect; recognizing ROT13 avoided unnecessary cryptanalysis. This also highlighted the need of building stronger Wireshark fluency through focused training for me personally.

## Artifacts intentionally omitted

- The challenge-provided PCAPNG capture.
- The captured text and decoded answer.
