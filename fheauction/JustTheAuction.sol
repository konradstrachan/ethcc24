// SPDX-License-Identifier: BSD-3-Clause-Clear

pragma solidity >=0.8.13 <0.9.0;

import { inEuint32, euint32, ebool, FHE } from "@fhenixprotocol/contracts/FHE.sol";

// Confidential addresses module from
// https://github.com/FhenixProtocol/blind-auction-example/blob/main/contracts/
import "./ConfAddress.sol";

struct Auction {
    uint256 startTime;
    Eaddress winningBidder;
    euint32 amount;
    // TODO track second price for better auction dynamics?
}

contract JustTheAuction {

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

    function bidOnBlockInternal(uint256 chainId, uint256 blockNum, euint32 amount) internal
    {
        bytes32 auctionKey = getAuctionKey(chainId, blockNum);
        Eaddress memory eaddress = ConfAddress.toEaddress(msg.sender);

        Auction memory auction = auctions[auctionKey];

        if (auction.startTime == 0) {
            // new auction, start it now
            auction.startTime = block.timestamp;
            auction.winningBidder = eaddress;
            auction.amount = amount;
            auctions[auctionKey] = auction;
            return;
        }

        // else

        require(block.timestamp <= auction.startTime + auctionLength, "Auction ended");

        euint32 updated_value = amount;

        ebool isHigher = auction.amount.gt(updated_value);
        auction.amount = FHE.select(isHigher, updated_value, auction.amount);
        auction.winningBidder = ConfAddress.conditionalUpdate(isHigher, eaddress, auction.winningBidder);

        auctions[auctionKey] = auction;
    }

    function bidOnBlock(uint256 chainId, uint256 blockNum, inEuint32 calldata amount) external
    {
        euint32 eamount = FHE.asEuint32(amount);
        bidOnBlockInternal(chainId, blockNum, eamount);
    }

    function bidOnBlockRaw(uint256 chainId, uint256 blockNum, uint32 amount) external
    {
        euint32 eamount = FHE.asEuint32(amount);
        bidOnBlockInternal(chainId, blockNum, eamount);
    }

    function fheDecryptAndSign() public pure returns (bytes memory) {
        // Simulate threshold network functionality
        // Mocked signature generated with params:
        // contract_address = '0x7b6aceC5eA36DD5ef5b0639B8C1d0Dab59DdcF03'
        // chain_id = 100
        // block_number = 100
        // entity = '0x7b6aceC5eA36DD5ef5b0639B8C1d0Dab59DdcF03'
        // fee_amount = 100
        return bytes(hex"65919b7aa0413abcd42dd723148448be69461418acc9df58a8dfa6cb7558ef1477d5e6c7edfe482e95c5e28c58bb04d4392f5716439a3937c6984f068529814c1c");
    }

    function resolveAuction(uint256 chainId, uint256 blockNum) external {
        bytes32 auctionKey = getAuctionKey(chainId, blockNum);
        Auction memory auction = auctions[auctionKey];

        require(auction.startTime > 0, "Invalid auction");
        require(block.timestamp > auction.startTime + auctionLength, "Auction ended");

        // mock emitted signature
        bytes memory signature = fheDecryptAndSign();

        emit AuctionEnded(
            ConfAddress.unsafeToAddress(auction.winningBidder),
            FHE.decrypt(auction.amount),
            signature);
    }

}
