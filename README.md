# JustTheTip 

An application layer preconfirmations framework relying on Block builder tips to land transactions at the tip of the block.

Built during ETH Global Brussels 2024 hackathon.

![image](https://github.com/user-attachments/assets/6697d8ba-1cde-46ab-b249-851c577a656b)

## Introduction

### tl;dr what is this?

Smart contracts that provides soft block space inclusion and execution guarantees through incentive distribution using fully homomorphic encryption shielded auctions to allow fair blind auctions.

### Problem description

Block space is not created equal with significant premium being placed to being able to include transactions before others to achieve execution advantage. The so-called top of block is both a practical (being in the first few transactions) and abstract notion (landing a transaction before any other interaction with the same smart contract / subset of functionality within a contract like a specific AMM pool). Regardless on exact definition, being able to gain advantage over ordering through guarantees around execution is the object of the current preconfirmation design space. 

This hackathon project explores how a purely application layer preconfirmation system could work through the use of a fair blind auction run on Fhenix to allow for the permissionless bidding on any block space.

### Design limitations

#### incentive driven inclusion

Block builders are a beneficiary of the preconfirmation auction and are therefore incentivised to include transactions containing a preconf payment. There is no further mechanism at the application layer that can compel timely inclusion.

Ideally this logic should reside lower within the stack at a sequencing / block production level to provide harder guarantees.

#### verification of bid amounts

The Fhenix auction does not check the bidder of the preconf has the funds to actually execute the preconfirmation on chain leading to malicious actors being able to deny preconf service to others by providing absurdly high bids. There are a few mechanisms to prevent against this, but this was not the primary focus of this project.

## Mechanism

![image](https://github.com/user-attachments/assets/4b6e7405-c03d-4997-aea4-46590eb531bf)

JTT has two main components:

* Shielded auction module
* Execution guarantees module

### Shielded auction module

Found within the [fheauction folder](https://github.com/konradstrachan/ethcc24/tree/main/fheauction) of the repo.

This Solidity smart contract is designed to handle a sealed-bid auction using fully homomorphic encryption (FHE) to ensure confidentiality and integrity of bids. The contract is implemented on [Fhenix](https://www.fhenix.io/) and utilisied their FHE and additional libraries for encryption and shielding operations.

#### Auction functions

getAuctionKey: Generates a unique key for each auction based on the chain ID and block number.

bidOnBlockInternal:

Handles the internal logic for making a bid. It checks if a new auction should start or if an existing bid should be updated based on the received encrypted bid (euint32 amount).

bidOnBlock and bidOnBlockRaw:

External functions that users call to place bids. They convert the bid amount into an encrypted format and delegate to bidOnBlockInternal.

resolveAuction:

Finalizes the auction when the specified time has elapsed. It decrypts the highest bid and reveals the winner. The function emits an AuctionEnded event with the decrypted highest bid and a mock signature.
Encryption and Signature:

#### Operational Flow

Each auction is associated with a specific blockchain block and chain ID.

Bids are placed within the confines of the auction's duration and are encrypted to preserve bidder privacy.

Auctions can be run at any time prior to block creation and the result of which is revealed at the end of the auction period. Along with the auction result, an attestation is provided by the Fhenix threshold network that can be taken and supplied to any contract ahead of time or just in time to guarantee transaction ordering.

NOTE: the attestation is mocked due to the Threshold layer of Fhenix currently not supporting signing of decrypted data.

### Execution guarantees module

Found within the [tipcontract folder](https://github.com/konradstrachan/ethcc24/tree/main/tipcontract) of the repo.

* JustTheEnforcement.sol - enforcement logic designed to be inherited
* JustTheExample.sol - example contract showing use of JustTheEnforcement features

The logic within the JustTheEnforcement contract is compatible with all EVM chains and is designed to manage block-level transaction ordering allowing functions to support normal and pre-confirmed transactions with the correct ordering at block construction time.

#### Core logic

Methods that inheriting contracts and block builders should use to guarantee functionality.

getOrderingHint: 

Allows querying of which address, if any, has priority for a specific block. This function helps anticipate and manage ordering collisions and is a helper function designed to be called by block builders at any time during block simulations.

verifyOrderingRight:

Checks if the caller has the right to execute at the current transaction index in the current block. Where a preconfirmation exists for a particular block and contract, the first transaction is only permitted from the pre-confirmation holder. Subsequent transactions are allowed from any address. Where no preconf is known, any address can execute the first transaction within the block.

All functions within a smart contract that wish to enforce preconf ordering should begin with a call to this method. For simplicity it can be wrapped in a modifer as below.

```
    modifier correctlyOrdered {
        require(verifyOrderingRight(), "ordering mmismatch");
        _;
    }
```

claimPriorityOrdering:

This function allows an address to claim priority for transactions in the current block by proving their identity and providing a signature.

For each function in a contract that has the ability to be executed preferentially, the following pattern is recommended:

```
    // usual logic called by non-preconf holders directly
    function testLogic() public correctlyOrdered {
        
        ...
    }

    // specialisation function of functions that guarantee preconf ordering with additional params
    function testPriorityLogic(uint256 feeAmount, bytes memory sig) public payable {
        require(
            claimPriorityOrdering(address(this), block.chainid, block.number, msg.sender, feeAmount, sig),
            "failed to set ordering");
        
        testLogic();
    }
```

The claimPriorityOrdering validates the attestation against multiple checks like eexecution rights, contract address, block number, entity, and minimum fee. The fee should be send in the native token to this method as part of the call. If successful, it sets the calling address as having priority for the block.

The fee collected is split, with half going to the contract and half to the miner incentivising inclusion.

#### Implementation

A minimum viable implementation of the logic is shown within the JustTheExample contract. Any contract and any logic can be wrapped by preconf guarantees based on the inclusion of verifyOrderingRight checks.

## Testing

Since proving functionality requires control over block times and creation, for simplicity the project was fully tested on a local hardhat environment using the script found in tools. The contracts have also been deployed and tested on Fhenix and other chains.

![image](https://github.com/user-attachments/assets/b66d12a1-7816-4a00-a8c5-02dd08178a09)

## Deployed contracts

Fhenix

* https://explorer.helium.fhenix.zone/address/0x35461b3ba63Aa1764b46778570D8E369Ea3CFF86

Sepolia

* https://sepolia.etherscan.io/address/0x354a50252bde407efccfe4fa605498e5db68aef6

Zircuit

* https://explorer.zircuit.com/address/0x4DC36FCc192c042fC49Fe934D86E8942D79c4e93

Rootstock

* https://explorer.testnet.rootstock.io/address/0x35461b3ba63aa1764b46778570d8e369ea3cff86
