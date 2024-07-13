from web3 import Web3

contract_address_example_contract = '0x5FbDB2315678afecb367f032d93F642f64180aa3'
contract_abi_example_contract = [{"anonymous": False,"inputs": [{"indexed": False,"internalType": "uint256","name": "order","type": "uint256"}],"name": "Executed","type": "event"},{"anonymous": False,"inputs": [{"indexed": False,"internalType": "bytes32","name": "dig","type": "bytes32"},{"indexed": False,"internalType": "address","name": "signer","type": "address"}],"name": "Signer","type": "event"},{"inputs": [{"internalType": "address","name": "contractAddress","type": "address"},{"internalType": "uint256","name": "chainId","type": "uint256"},{"internalType": "uint256","name": "blockNumber","type": "uint256"},{"internalType": "address","name": "entity","type": "address"},{"internalType": "uint256","name": "feeAmount","type": "uint256"},{"internalType": "bytes","name": "sig","type": "bytes"}],"name": "claimPriorityOrdering","outputs": [{"internalType": "bool","name": "","type": "bool"}],"stateMutability": "payable","type": "function"},{"inputs": [{"internalType": "address","name": "contractAddress","type": "address"},{"internalType": "uint256","name": "chainId","type": "uint256"},{"internalType": "uint256","name": "blockNumber","type": "uint256"},{"internalType": "address","name": "entity","type": "address"},{"internalType": "uint256","name": "feeAmount","type": "uint256"}],"name": "createPCDigest","outputs": [{"internalType": "bytes32","name": "","type": "bytes32"}],"stateMutability": "pure","type": "function"},{"inputs": [{"internalType": "uint256","name": "","type": "uint256"}],"name": "executionCounter","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "expectedSigner","outputs": [{"internalType": "address","name": "","type": "address"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "uint256","name": "blockNumber","type": "uint256"}],"name": "getOrderingHint","outputs": [{"internalType": "address","name": "","type": "address"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "uint256","name": "","type": "uint256"}],"name": "priority","outputs": [{"internalType": "address","name": "","type": "address"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "bytes32","name": "ethSignedMessageHash","type": "bytes32"},{"internalType": "bytes","name": "signature","type": "bytes"}],"name": "recoverSigner","outputs": [{"internalType": "address","name": "","type": "address"}],"stateMutability": "pure","type": "function"},{"inputs": [{"internalType": "bytes","name": "sig","type": "bytes"}],"name": "splitSignature","outputs": [{"internalType": "bytes32","name": "r","type": "bytes32"},{"internalType": "bytes32","name": "s","type": "bytes32"},{"internalType": "uint8","name": "v","type": "uint8"}],"stateMutability": "pure","type": "function"},{"inputs": [],"name": "testLogic","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint256","name": "feeAmount","type": "uint256"},{"internalType": "bytes","name": "sig","type": "bytes"}],"name": "testPriorityLogic","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "address","name": "contractAddress","type": "address"},{"internalType": "uint256","name": "chainId","type": "uint256"},{"internalType": "uint256","name": "blockNumber","type": "uint256"},{"internalType": "address","name": "entity","type": "address"},{"internalType": "uint256","name": "feeAmount","type": "uint256"},{"internalType": "bytes","name": "sig","type": "bytes"}],"name": "testSigLogic","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [],"name": "verifyOrderingRight","outputs": [{"internalType": "bool","name": "","type": "bool"}],"stateMutability": "nonpayable","type": "function"}]

rpc_url = 'http://127.0.0.1:8545/'
web3 = Web3(Web3.HTTPProvider(rpc_url))

def hexbytes_to_string(hexbytes):
    return (hexbytes).hex()

def send_custom_rpc(method, params):
    return web3.provider.make_request(method, params)

def get_and_print_logs(tx_hash):
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    logs = contract.events.Executed().process_receipt(receipt)

    for log in logs:
        output = f"tx_hash {hexbytes_to_string(log['transactionHash'])} : event [{log['event']}] arg order [{log['args']['order']}]"
        print(output)


# Check if the connection is successful
if web3.is_connected():
    print("Connected to Hardhat node")
else:
    print("Failed to connect")
    exit(0)

# Import account from private key, this is taken from the default hardhat config from ScaffoldETH
private_key = 'ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'

# Create account from private key
account = web3.eth.account.from_key(private_key)
contract = web3.eth.contract(address=contract_address_example_contract, abi=contract_abi_example_contract)

### test functions below ###

send_custom_rpc('evm_setAutomine', [False])
print("Auto-mining turned off (no new blocks produced)")
# Set mining interval to 0 (disables automatic interval mining)
send_custom_rpc('evm_setIntervalMining', [0])
print("Interval mining set to 0")

print("Sending Tx1..")
tx_hash1 = contract.functions.testLogic().transact({
    'from': web3.eth.accounts[0]
})

print("Sending Tx2..")
tx_hash2 = contract.functions.testLogic().transact({
    'from': web3.eth.accounts[0]
})

send_custom_rpc('evm_mine', [])
print("Block mined manually.")

# Get the receipt to see the logs
print("Tx1 logs:")
get_and_print_logs(tx_hash1)
print("Tx2 logs:")
get_and_print_logs(tx_hash2)
