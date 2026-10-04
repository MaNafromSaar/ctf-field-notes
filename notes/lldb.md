# LLDB field notes

## Control execution

| Command | Use |
|---|---|
| `b <function>` | Break at a named function |
| `b <file>:<line>` | Break at a source line |
| `run` | Start or restart the process |
| `continue` | Resume execution |
| `step` / `next` | Step into / over a source line |
| `stepi` / `nexti` | Step into / over one machine instruction |
| `finish` | Run until the current function returns |

## Inspect state

| Command | Use |
|---|---|
| `register read` | Display registers |
| `frame variable` | Display current-frame variables (when symbols exist) |
| `p (char*)$rdi` | Interpret the first argument register as a C string on common x86-64 ABIs |
| `memory read --format x --count 16 <address>` | Inspect bytes at an address |
| `memory read --format s --count 1 <address>` | Read a C string at an address |
| `disassemble --name <function>` | Disassemble a named function |

## Practical cautions

- At a function-entry breakpoint, its output buffer may not have been initialized yet.
- Capture pointers to caller-owned buffers before stepping out of the function.
- Prefer symbol or source breakpoints over raw addresses. PIE and ASLR can change addresses between runs.
- A stack-canary check and an `endbr64` landing instruction are often compiler/runtime scaffolding, not the challenge's core logic.
- If a debugger run has a process stopped, `continue` resumes it; `run` may ask whether to terminate and restart it.
