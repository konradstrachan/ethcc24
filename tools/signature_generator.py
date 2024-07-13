from web3 import Web3

#0xC19642f7f878d781865e6d45047A444708c24dF4 from https://privatekeys.pw/keys/ethereum/random
private_key = 'XXXXXXX'
rpc_url = 'XXXXXXX'

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

# Example usage
contract_address = Web3.to_checksum_address('0xccfd90303b75c910c027716b2c43b21eac633c4f')
chain_id = 100
block_number = 100
entity = '0x7b6aceC5eA36DD5ef5b0639B8C1d0Dab59DdcF03'
fee_amount = 100

pc_digest = create_pc_digest(contract_address, chain_id, block_number, entity, fee_amount)
signed_message = sign_message(private_key, pc_digest)

print(f'Message Digest: {pc_digest.hex()}')
print(f'Signature: {signed_message.signature.hex()}')
