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