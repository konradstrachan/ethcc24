from web3 import Web3

#0xC19642f7f878d781865e6d45047A444708c24dF4 from https://privatekeys.pw/keys/ethereum/random
private_key = 'XXXXXXX'
rpc_url = 'XXXXXXX'

def create_pc_digest(contract_address, chain_id, block_number, entity, fee_amount):
    web3 = Web3(Web3.HTTPProvider(rpc_url))

    # Ensure the connection is successful
    if not web3.is_connected():
        raise Exception("Unable to connect to the node")

    # Pack and hash the parameters similar to Solidity's abi.encodePacked
    pc_digest = Web3.solidity_keccak(
        ['address', 'uint256', 'uint256', 'address', 'uint256'],
        [contract_address, chain_id, block_number, entity, fee_amount]
    )

    return pc_digest

def sign_message(private_key, message_digest):
    # Sign the message digest
    web3 = Web3(Web3.HTTPProvider('YOUR_INFURA_URL'))
    signed_message = web3.eth.account.signHash(message_digest, private_key)

    return signed_message

# Example usage
contract_address = '0x7b6aceC5eA36DD5ef5b0639B8C1d0Dab59DdcF03'
chain_id = 1
block_number = 12345678
entity = '0x7b6aceC5eA36DD5ef5b0639B8C1d0Dab59DdcF03'
fee_amount = 1000

pc_digest = create_pc_digest(contract_address, chain_id, block_number, entity, fee_amount)
signed_message = sign_message(private_key, pc_digest)

print(f'Message Digest: {pc_digest.hex()}')
print(f'Signature: {signed_message.signature.hex()}')
