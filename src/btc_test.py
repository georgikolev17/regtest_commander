import requests
import json

# Your Docker config
RPC_USER = 'bitcoinrpc'
RPC_PASS = 'bitcoinrpcpassword'
RPC_URL = 'http://127.0.0.1:18443'  # The port you exposed

headers = {'content-type': 'application/json'}

def rpc_call(method, params=[]):
    payload = json.dumps({
        "method": method,
        "params": params,
        "jsonrpc": "2.0",
        "id": 0,
    })
    response = requests.post(RPC_URL, headers=headers, data=payload, auth=(RPC_USER, RPC_PASS))
    return response.json()

# 1. Test Connection
print("Attempting to connect to Bitcoin Regtest node...")
result = rpc_call("getblockchaininfo")

if result.get('error'):
    print("Error:", result['error'])
else:
    print("Connection Successful!")
    print(f"Current Block Height: {result['result']['blocks']}")
    print(f"Chain: {result['result']['chain']}")