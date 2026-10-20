# Challenge: IntOverflowBank

## Context

The challenge provides a Solidity 0.6.12 bank contract and a temporary instance. The `deposit` function updates an internal `uint256` balance; it does not accept or transfer ETH.

## Observations

After adding the requested amount to the caller's balance, `deposit` checks whether the resulting balance is less than the amount. The contract reveals the flag when that condition is true.

## Hypothesis

In Solidity 0.6.12, unsigned integer addition wraps modulo \(2^{256}\). A sufficiently large deposit can therefore make the updated balance smaller than the amount.

## Analysis

Starting from a zero internal balance, call `deposit(2)` and then `deposit(2^256 - 2)` from the same account. The second addition computes:

```text
2 + (2^256 - 2) = 2^256 ≡ 0 (mod 2^256)
```

The new balance is zero, which is less than the second deposit amount, so the reveal condition is satisfied. The deposit calls send no ETH; the account needs ETH only to pay transaction gas.

## Resolution

The [CLI helper](../../scripts/solve_int_overflow_bank.sh) submits both calls using Foundry's `cast`, prompting for the current RPC endpoint, private key, bank address, and account address. This avoids needing to configure a browser wallet. Install Foundry first, then run the script and accept the default second-deposit amount. No separate manual deposit is needed. Confirm both transactions succeeded, then read the revealed state or flag through the challenge interface.

## Takeaways

Solidity versions before 0.8 do not automatically revert on integer overflow. Use checked arithmetic or Solidity 0.8+ defaults, and avoid using an overflow comparison as a security condition.

## Artifacts intentionally omitted

The challenge contract source, temporary RPC endpoint, addresses, and private key are not reproduced here.
