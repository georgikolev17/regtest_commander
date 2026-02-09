import requests
import json
import argparse
import sys

# --- CONFIG ---
RPC_USER = 'bitcoinrpc'
RPC_PASS = 'bitcoinrpcpassword'
RPC_URL = 'http://127.0.0.1:18443'

def rpc(method, params=[], wallet_name=None):
    """
    Sends a JSON-RPC request to Bitcoin Core.
    If wallet_name is provided, it routes to that specific wallet.
    """
    url = RPC_URL
    if wallet_name:
        # Route to the specific wallet endpoint
        url = f"{RPC_URL}/wallet/{wallet_name}"
    
    payload = json.dumps({
        "method": method,
        "params": params,
        "jsonrpc": "1.0",
        "id": "sob_app"
    })

    try:
        response = requests.post(
            url, 
            data=payload, 
            headers={'content-type': 'application/json'},
            auth=(RPC_USER, RPC_PASS)
        )
        # Check for HTTP errors
        response.raise_for_status()
        return response.json()['result']
    except requests.exceptions.HTTPError as err:
        print(f"RPC Error: {err}")
        print(f"   Server said: {response.text}")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("CRITICAL: Could not connect to Bitcoin Node.")
        print("   -> Is your Docker container running?")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="My Bitcoin Regtest Controller")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 1. getinfo
    subparsers.add_parser("getinfo", help="Show blockchain info")

    # 2. createwallet <name>
    wallet_parser = subparsers.add_parser("createwallet", help="Create or load a wallet")
    wallet_parser.add_argument("name", type=str, help="Name of the wallet")

    # 3. getnewaddress <wallet_name>
    addr_parser = subparsers.add_parser("getnewaddress", help="Generate a new address")
    addr_parser.add_argument("wallet_name", type=str, help="Wallet to generate address for")

    # 4. mine <blocks> <address>
    mine_parser = subparsers.add_parser("mine", help="Mine blocks")
    mine_parser.add_argument("blocks", type=int, help="Number of blocks")
    mine_parser.add_argument("address", type=str, help="Address to receive rewards")

    # 5. getbalance <wallet_name>
    bal_parser = subparsers.add_parser("getbalance", help="Get wallet balance")
    bal_parser.add_argument("wallet_name", type=str, help="Wallet to check")

    # 6. send <amount> <address> <wallet_name>
    send_parser = subparsers.add_parser("send", help="Send BTC to an address")
    send_parser.add_argument("amount", type=float, help="Amount of BTC to send")
    send_parser.add_argument("address", type=str, help="Recipient address")
    send_parser.add_argument("wallet_name", type=str, help="Wallet to send FROM")

    args = parser.parse_args()

    # --- COMMAND LOGIC ---

    if args.command == "getinfo":
        info = rpc("getblockchaininfo")
        print(f"Chain: {info['chain']}")
        print(f"Blocks: {info['blocks']}")

    elif args.command == "createwallet":
        print(f"Attempting to create wallet '{args.name}'...")
        try:
            rpc("createwallet", [args.name])
            print(f"Wallet '{args.name}' created!")
        except:
            print(f"Wallet might exist. Loading...")
            rpc("loadwallet", [args.name])
            print(f"Wallet '{args.name}' loaded.")

    elif args.command == "getnewaddress":
        # Note: We pass wallet_name to the rpc function!
        addr = rpc("getnewaddress", [], wallet_name=args.wallet_name)
        print(f"New Address ({args.wallet_name}): {addr}")

    elif args.command == "mine":
        print(f"Mining {args.blocks} blocks...")
        hashes = rpc("generatetoaddress", [args.blocks, args.address])
        print(f"Mined {len(hashes)} blocks.")
        print(f"   Last Hash: {hashes[-1]}")

    elif args.command == "getbalance":
        bal = rpc("getbalance", [], wallet_name=args.wallet_name)
        print(f"Balance ({args.wallet_name}): {bal} BTC")

    elif args.command == "send":
        print(f"Sending {args.amount} BTC from '{args.wallet_name}' to {args.address}...")
        try:
            # RPC: sendtoaddress <address> <amount>
            # Note: The 'wallet_name' argument routes the request to the SENDER's wallet
            txid = rpc("sendtoaddress", [args.address, args.amount], wallet_name=args.wallet_name)
            print(f"Sent! Transaction ID: {txid}")
            print("Don't forget to mine a block to confirm this!")
        except Exception as e:
            print(f"Send failed: {e}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()