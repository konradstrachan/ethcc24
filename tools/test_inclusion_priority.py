from web3 import Web3
from web3.logs import DISCARD

contract_address_example_contract = '0x0DCd1Bf9A1b36cE34237eEaFef220932846BCD82'
contract_abi_example_contract = [{"anonymous": False,"inputs": [{"indexed": False,"internalType": "uint256","name": "order","type": "uint256"}],"name": "Executed","type": "event"},{"anonymous": False,"inputs": [{"indexed": False,"internalType": "uint256","name": "amount","type": "uint256"}],"name": "Paid","type": "event"},{"anonymous": False,"inputs": [{"indexed": False,"internalType": "bytes32","name": "dig","type": "bytes32"},{"indexed": False,"internalType": "address","name": "signer","type": "address"}],"name": "Signer","type": "event"},{"stateMutability": "payable","type": "fallback"},{"inputs": [{"internalType": "address","name": "contractAddress","type": "address"},{"internalType": "uint256","name": "chainId","type": "uint256"},{"internalType": "uint256","name": "blockNumber","type": "uint256"},{"internalType": "address","name": "entity","type": "address"},{"internalType": "uint256","name": "feeAmount","type": "uint256"},{"internalType": "bytes","name": "sig","type": "bytes"}],"name": "claimPriorityOrdering","outputs": [{"internalType": "bool","name": "","type": "bool"}],"stateMutability": "payable","type": "function"},{"inputs": [{"internalType": "address","name": "contractAddress","type": "address"},{"internalType": "uint256","name": "chainId","type": "uint256"},{"internalType": "uint256","name": "blockNumber","type": "uint256"},{"internalType": "address","name": "entity","type": "address"},{"internalType": "uint256","name": "feeAmount","type": "uint256"}],"name": "createPCDigest","outputs": [{"internalType": "bytes32","name": "","type": "bytes32"}],"stateMutability": "pure","type": "function"},{"inputs": [{"internalType": "uint256","name": "","type": "uint256"}],"name": "executionCounter","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "expectedSigner","outputs": [{"internalType": "address","name": "","type": "address"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "uint256","name": "blockNumber","type": "uint256"}],"name": "getOrderingHint","outputs": [{"internalType": "address","name": "","type": "address"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "uint256","name": "","type": "uint256"}],"name": "priority","outputs": [{"internalType": "address","name": "","type": "address"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "bytes32","name": "ethSignedMessageHash","type": "bytes32"},{"internalType": "bytes","name": "signature","type": "bytes"}],"name": "recoverSigner","outputs": [{"internalType": "address","name": "","type": "address"}],"stateMutability": "pure","type": "function"},{"inputs": [{"internalType": "bytes","name": "sig","type": "bytes"}],"name": "splitSignature","outputs": [{"internalType": "bytes32","name": "r","type": "bytes32"},{"internalType": "bytes32","name": "s","type": "bytes32"},{"internalType": "uint8","name": "v","type": "uint8"}],"stateMutability": "pure","type": "function"},{"inputs": [],"name": "testLogic","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint256","name": "feeAmount","type": "uint256"},{"internalType": "bytes","name": "sig","type": "bytes"}],"name": "testPriorityLogic","outputs": [],"stateMutability": "payable","type": "function"},{"inputs": [{"internalType": "address","name": "contractAddress","type": "address"},{"internalType": "uint256","name": "chainId","type": "uint256"},{"internalType": "uint256","name": "blockNumber","type": "uint256"},{"internalType": "address","name": "entity","type": "address"},{"internalType": "uint256","name": "feeAmount","type": "uint256"},{"internalType": "bytes","name": "sig","type": "bytes"}],"name": "testSigLogic","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [],"name": "verifyOrderingRight","outputs": [{"internalType": "bool","name": "","type": "bool"}],"stateMutability": "nonpayable","type": "function"},{"stateMutability": "payable","type": "receive"}]

rpc_url = 'http://127.0.0.1:8545/'
web3 = Web3(Web3.HTTPProvider(rpc_url))

# Check if the connection is successful
if web3.is_connected():
    print("Connected to Hardhat node")
else:
    print("Failed to connect")
    exit(0)

# Import account from private key, this is taken from the default hardhat config from ScaffoldETH
# Relates to address 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 
private_key = 'ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'

def create_pc_digest(contract_address, chain_id, block_number, entity, fee_amount):
    web3 = Web3(Web3.HTTPProvider(rpc_url))

    # Ensure the connection is successful
    if not web3.is_connected():
        raise Exception("Unable to connect to the Ethereum node")

    # Convert hex address to bytes and ensure 20-byte addresses
    contract_address_bytes = Web3.to_bytes(hexstr=contract_address)
    entity_bytes = Web3.to_bytes(hexstr=entity)

    # Prepare other values with proper byte order and size, padding left to fill up to 32 bytes
    chain_id_bytes = chain_id.to_bytes(32, byteorder='big')
    block_number_bytes = block_number.to_bytes(32, byteorder='big')
    fee_amount_bytes = fee_amount.to_bytes(32, byteorder='big')

    # Concatenate all byte values in order, simulating abi.encode() with full 32-byte alignment
    packed_data = (
        contract_address_bytes.rjust(32, b'\0') +  # Pad left
        chain_id_bytes +
        block_number_bytes +
        entity_bytes.rjust(32, b'\0') +  # Pad left
        fee_amount_bytes
    )
    return Web3.keccak(packed_data)

def sign_message(private_key, message_digest):
    # Sign the message digest
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    signed_message = web3.eth.account.signHash(message_digest, private_key)

    return signed_message

def generate_digest_and_signature(contract_address, chain_id, block_number, entity, fee_amount):
    contract_address = Web3.to_checksum_address(contract_address)
    pc_digest = create_pc_digest(contract_address, chain_id, block_number, entity, fee_amount)
    signed_message = sign_message(private_key, pc_digest)
    return (pc_digest, signed_message.signature)

def hexbytes_to_string(hexbytes):
    return (hexbytes).hex()

def send_custom_rpc(method, params):
    return web3.provider.make_request(method, params)

def get_latest_block_number():
    return int(send_custom_rpc('eth_blockNumber', {})['result'], 16)

def get_and_print_logs(tx_hash):
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    logs = contract.events.Paid().process_receipt(receipt, errors=DISCARD)

    for log in logs:
        output = f"tx_hash {hexbytes_to_string(log['transactionHash'])} : event [{log['event']}] arg paid [{log['args']['amount']}]"
        print(output)

    logs = contract.events.Executed().process_receipt(receipt, errors=DISCARD)

    for log in logs:
        output = f"tx_hash {hexbytes_to_string(log['transactionHash'])} : event [{log['event']}] arg order [{log['args']['order']}]"
        print(output)

# Create account from private key
account = web3.eth.account.from_key(private_key)
contract = web3.eth.contract(address=contract_address_example_contract, abi=contract_abi_example_contract)

### test functions below ###
print("########################################")
print("🗃️  Set up of environment..")

send_custom_rpc('evm_setAutomine', [False])
print("Auto-mining turned off (no new blocks produced)")
# Set mining interval to 0 (disables automatic interval mining)
send_custom_rpc('evm_setIntervalMining', [0])
print("Interval mining disabled")
print("")

print("########################################")
print("🏷️  Test 1: inclusion without preconf based ordering")

print("📤 Sending Tx1..")
tx_hash1 = contract.functions.testLogic().transact({
    'from': web3.eth.accounts[0]
})

print("📤 Sending Tx2..")
tx_hash2 = contract.functions.testLogic().transact({
    'from': web3.eth.accounts[0]
})

send_custom_rpc('evm_mine', [])
print("🧾 Block mined")

# Get the receipt to see the logs
print("📩 Tx1 logs:")
get_and_print_logs(tx_hash1)
print("📩 Tx2 logs:")
get_and_print_logs(tx_hash2)

print("")
print("########################################")
print("🏷️  Test 2: inclusion WITH preconf based ordering")

print("⚙️ Getting latest block number..")
block_number = get_latest_block_number()
print(f"Latest block number is [{block_number}]")
print("🏗️ Simulating execution of Fhenix auction")
print("Started auction..")
print(".. auction ended")

# Auction for next block
block_number = block_number + 1

contract_address = contract_address_example_contract
chain_id = 31337 # Hardhat default
executing_entity = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'
fee_amount = 100
digest, signature = generate_digest_and_signature(contract_address, chain_id, block_number, executing_entity, fee_amount)

print(f"🤖 FHE digest of winning bid: [{digest.hex()}]")
print(f"🤖 FHE signed attestation of winning bid: [{signature.hex()}]")

print("--------------------------------------------")

print("📤 Sending Tx1 (setting preconf expectation)..")
tx_hash1 = contract.functions.claimPriorityOrdering(
    contract_address,
    chain_id,
    block_number,
    executing_entity,
    fee_amount,
    signature).transact({
    'from': web3.eth.accounts[0],
    'value': 100
})

print("📤 Sending Tx2 (tx which is not allowed to be first)..")

try:
    tx_hash2 = contract.functions.testLogic().transact({
        'from': web3.eth.accounts[1]
    })
except Exception as e:
    print(f"Failed with {e}")

print("📤 Sending Tx3 (tx which has the preconf)..")
tx_hash2 = contract.functions.testLogic().transact({
    'from': web3.eth.accounts[0]
})

print("📤 Sending Tx4 (resending Tx2)..")
tx_hash3 = contract.functions.testLogic().transact({
    'from': web3.eth.accounts[1]
})

send_custom_rpc('evm_mine', [])
print("🧾 Block mined")

# Get the receipt to see the logs
print("📩 Tx1 logs:")
get_and_print_logs(tx_hash1)
print("📩 Tx2 logs:")
get_and_print_logs(tx_hash2)
print("📩 Tx3 logs:")
get_and_print_logs(tx_hash3)

print("")
print("Done")