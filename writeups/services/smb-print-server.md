# Print Server: identifying SMB behind a forwarded port

## Fingerprint before interacting

A reachable TCP port and a text prompt do not establish that a service is a shell or HTTP. Service detection identified the endpoint as Samba/SMB, so the next step was to use SMB-aware tooling rather than send more raw text.

For a current authorized instance, substitute its temporary values:

```bash
nmap -sV -p <PORT> <HOST>
nmap -Pn -p <PORT> --script smb-protocols,smb2-security-mode <HOST>
```

## Enumerate and connect

Try anonymous share enumeration, specifying the forwarded port:

```bash
smbclient -p <PORT> -L //<HOST> -N
```

Connect to a readable disk share with a negotiated modern dialect:

```bash
smbclient //<HOST>/<SHARE> -p <PORT> -N -m SMB3
```

At the SMB prompt, use `ls`, `get`, or `mget`; these are SMB client commands, not shell commands. The server speaks a structured, stateful protocol with negotiation, session setup, tree connection, and file operations. A plain `nc` session cannot perform those steps.

## Diagnose failures

Authentication failure, access denied, an unknown share, and protocol timeout indicate different problems. A workgroup-listing timeout can occur after the server has already returned share names, so inspect the earlier result before treating the entire command as a failure.

## Takeaway

Service fingerprinting narrows the protocol before choosing a client. A nonstandard forwarded port does not change the SMB protocol, but it must be passed to each tool explicitly. No instance endpoint or retrieved file is stored here.
