# Inspecting a runtime password check with LLDB

## Static analysis first

Start with `file`, `strings`, and disassembly to locate the input path, the comparison, and the function that prepares the expected value. Distinguish challenge logic from compiler-generated scaffolding such as stack-canary checks; those are common around functions with local buffers and do not usually participate in the comparison.

In this case, a helper writes a short encoded byte sequence into a caller-owned output buffer and transforms it with a single-byte XOR. This is obfuscation, not a password hash: the value can be recovered by understanding the transformation or by observing the resulting buffer at runtime.

## Inspect the buffer

Set a breakpoint on the decode helper, run the program, and capture the output pointer while stopped in the function. Let the helper return, then inspect the buffer at that saved address as a string or bytes. Reading at function entry is too early because the writes have not happened yet.

Run the authentication flow outside the debugger after analysis. Debugger working directories and environment can differ from the normal challenge process, so an error opening a local flag file under LLDB does not by itself disprove a successful password comparison.

## Takeaway

Follow data from construction to comparison, and use runtime inspection to verify a static hypothesis. Capture caller-owned pointers before returning from the helper; frame-local expressions may no longer be valid after the stack frame exits.
