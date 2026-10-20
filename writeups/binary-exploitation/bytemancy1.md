# Bytemancy1

## Context

The challenge provides host and port along with the python source code for the challenge itself.

## Observations

It says explicitly and straightforward to enter ASCII 101 1751 times. 

## Analysis

The prompt asks for ASCII decimal 101 repeated 1,751 times. Decimal 101 is the lowercase letter e; the Python escape \x65 is hexadecimal 65, which is also decimal 101. So the required input is e repeated 1,751 times, followed by a newline for input().

A short Bash script can generate and send it through netcat. Preparing the payload manually is possible but certainly not recommended.

```bash
#!/usr/bin/env bash

if (( $# < 1 || $# > 2 )); then
  echo "Usage: $0 HOST [PORT]" >&2
  exit 2
fi

host=$1
port=$2

{
  python3 -c 'import sys; sys.stdout.write("e" * 1751 + "\n")'
  sleep 1
} | nc "$host" "$port"
```

## Takeaways

A script or programmatic approach is recommended to generate and send the repeated 'e' characters, as manual preparation is error-prone and tedious.

Error-handling is not thorough here and in this case not needed.

## Artifacts intentionally omitted

The challenge source bundle and supplied host and port are not included.