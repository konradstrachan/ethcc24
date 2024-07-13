// SPDX-License-Identifier: BSD-3-Clause-Clear

pragma solidity >=0.8.13 <0.9.0;

import { inEuint32, euint32, ebool, FHE } from "@fhenixprotocol/contracts/FHE.sol";

struct Auction {
    uint256 startTime;
    address winningBidder;
    euint32 amount;
    // TODO track second price for better auction dynamics?
}

contract Auction {

    mapping(bytes32 => Auction) internal auctions;

    uint256 public auctionLength;

    event AuctionEnded(address winner, uint32 bid, bytes sig);

    constructor() {
        // TODO make configurable and better explained
        auctionLength = 2;
    }

    function getAuctionKey(uint256 chainId, uint256 blockNum) public pure returns (bytes32) {
        return keccak256(abi.encodePacked(chainId, blockNum));
    }

    function bidOnBlock(uint256 chainId, uint256 blockNum, inEuint32 calldata amount) external
    {
        bytes32 auctionKey = getAuctionKey(chainId, blockNum);

        Auction memory auction = auctions[auctionKey];

        if (auction.startTime == 0) {
            // new auction, start it now
            auction.startTime = block.timestamp;
            auction.winningBidder = msg.sender;
            auction.amount = FHE.asEuint32(amount);
            auctions[auctionKey] = auction;
            return;
        }

        // else

        require(block.timestamp <= auction.startTime + auctionLength, "Auction ended");

        euint32 updated_value = FHE.asEuint32(amount);

        ebool isHigher = auction.amount.gt(updated_value);
        auction.amount = FHE.select(isHigher, updated_value, auction.amount);
        // TODO for shielded address:
        // auction.winningBidder = FHE.select(isHigher, msg.sender, auction.winningBidder);
        if (FHE.decrypt(isHigher)) {
            auction.winningBidder = msg.sender;
        }

        auctions[auctionKey] = auction;
        
    }

    function fheDecryptAndSign() public pure returns (bytes memory) {
        // Simulate threshold network functionality
        // Mocked signature generated with params:
        // contract_address = '0x7b6aceC5eA36DD5ef5b0639B8C1d0Dab59DdcF03'
        // chain_id = 1
        // block_number = 12345678
        // entity = '0x7b6aceC5eA36DD5ef5b0639B8C1d0Dab59DdcF03'
        // fee_amount = 1000
        return bytes(hex"24987d6292a2ce7fb5b9beac2d53f721e87b6c390a3759ce2b630ed6a75664b93defba6f3a27379c2846063b26bb1f066c0cca009f11d3167e22a2f7524a58291b");
    }

    function resolveAuction(uint256 chainId, uint256 blockNum) external {
        bytes32 auctionKey = getAuctionKey(chainId, blockNum);
        Auction memory auction = auctions[auctionKey];

        require(auction.startTime > 0, "Invalid auction");
        require(block.timestamp > auction.startTime + auctionLength, "Auction ended");

        // mock emitted signature
        bytes memory signature = fheDecryptAndSign();
        emit AuctionEnded(auction.winningBidder, FHE.decrypt(auction.amount), signature);
    }

}
