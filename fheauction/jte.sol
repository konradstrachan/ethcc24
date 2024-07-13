// SPDX-License-Identifier: BSD-3-Clause-Clear

pragma solidity >=0.8.13 <0.9.0;

import { inEuint32, euint32, FHE } from "@fhenixprotocol/contracts/FHE.sol";

struct Auction {
    uint256 startTime;
    address winningBidder;
    euint32 amount;
    // TODO track second price for better auction dynamics?
}

contract Auction {

    mapping(bytes32 => Auction) internal auctions;

    uint256 public auctionLength;

    event AuctionEnded(address winner, uint32 bid);

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

    // TODO - return signature
    function resolveAuction(uint256 chainId, uint256 blockNum) external {
        bytes32 auctionKey = getAuctionKey(chainId, blockNum);
        Auction memory auction = auctions[auctionKey];

        require(auction.startTime > 0, "Invalid auction");

        // TODO mock emitted signature
        emit AuctionEnded(auction.winningBidder, FHE.decrypt(auction.amount));
    }

}