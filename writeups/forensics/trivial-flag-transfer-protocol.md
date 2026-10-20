# Recovering a hidden flag from a TFTP transfer

## Follow the transfer

The capture contained UDP/TFTP traffic. ROT13-decoded plan messages pointed to a concealed transfer and suggested examining the photos. Exporting the complete TFTP object revealed a Debian package; its `data.tar.xz` contained three BMP images and the `steghide` utility.

## Extract from a photo

The plan's decoded wording contained a single word that served as the passphrase (omitted here; note its exact case and spacing). Use it with `steghide` on the photos; only one contained the hidden content:

```text
steghide extract -sf <picture.bmp> -p <PASSPHRASE>
```

## Takeaway

Reassemble binary transfers as objects rather than saving an ASCII rendering, and preserve exact case and spacing when testing a passphrase. The flag and challenge artifacts are intentionally omitted.
