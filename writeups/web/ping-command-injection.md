# Shell injection in a ping wrapper

## Observation

A network service claimed to restrict a ping target, but accepted an arbitrary loopback address. This suggested that the validation was weaker than the message implied, and raised the question of how the input was used to construct the command.

## Test safely

In the authorized challenge only, send a harmless local address followed by a shell command separator and a benign command that reveals whether shell interpretation occurs. If the second command runs, the input is being interpreted by a shell rather than passed as one validated argument. Do not test this technique against systems outside the assigned instance.

The likely unsafe construction is conceptually:

```text
shell("ping ... " + user_input)
```

A separator changes the shell's parse tree and starts a second command. The issue is not that ping accepts unusual address syntax; it is that untrusted text crosses a shell boundary.

## Defensive lesson

Avoid shell command construction. Call the process with an argument vector and validate the target as an IP address using a standard parser. If a shell is unavoidable, strict allowlisting and correct argument escaping are essential, but still less robust than avoiding the shell.
