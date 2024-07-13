// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract jtt {
    // Address expected to be the signer
    address public constant expectedSigner = 0x7b6aceC5eA36DD5ef5b0639B8C1d0Dab59DdcF03;

    struct PreConf {
        address contractAddress;
        uint256 chainId;
        uint256 blockNumber;
        address entity;
        uint256 feeAmount;
    }

    mapping(uint256 => address) public priority;
    mapping(uint256 => uint256) public executionCounter;

    function verifyOrderingRight() public returns (bool) {
        address blockPriorityOwner = priority[block.number];

        // No one (yet?) has block priority
        if (blockPriorityOwner == address(0)) {
            // increment counter anyway
            ++executionCounter[block.number];
            return true;
        }

        // Someone has priority in this block

        uint256 execCounterCurrent = executionCounter[block.number];

        // Someone has priority, check it is this caller for the first slot
        if (execCounterCurrent == 0){ 
            if (blockPriorityOwner == msg.sender) {
                // increment counter
                ++executionCounter[block.number];
                return true;
            } else {
                // Only the priority owner can be the first to execute
                return false;
            }
        }

        // Ordering after the first execution is unrestrained
        ++executionCounter[block.number];
        return true;
    }

    function claimPriorityOrdering(
        address contractAddress,
        uint256 chainId,
        uint256 blockNumber,
        address entity,
        uint256 feeAmount,
        bytes memory sig) public payable returns (bool) {

        require(contractAddress == address(this), "Invalid contract");
        require(blockNumber == block.number, "Invalid block");
        require(msg.sender == entity, "Invalid entity");

        bytes32 bidDigest = createPCDigest(
            contractAddress,
            chainId,
            blockNumber,
            entity,
            msg.value);

        require(recoverSigner(bidDigest, sig) == expectedSigner, "Attestor address mismatch");

        // Check if the sent amount of ETH is at least the fee amount
        require(msg.value >= feeAmount, "Insufficient fee amount");

        // Split the received ETH
        uint256 halfFee = msg.value / 2;
        payable(address(this)).transfer(halfFee);
        payable(block.coinbase).transfer(msg.value - halfFee);

        // If ok, then set ordering priority
        priority[blockNumber] = entity;
        return true;
    }

    function createPCDigest(
        address contractAddress,
        uint256 chainId, 
        uint256 blockNumber,
        address entity,
        uint256 feeAmount) public pure returns (bytes32) {
        PreConf memory pc = PreConf(contractAddress, chainId, blockNumber, entity, feeAmount);
        return keccak256(abi.encode(pc));
    }

    function recoverSigner(bytes32 ethSignedMessageHash, bytes memory signature) public pure returns (address) {
        (bytes32 r, bytes32 s, uint8 v) = splitSignature(signature);
        return ecrecover(ethSignedMessageHash, v, r, s);
    }

    function splitSignature(bytes memory sig) public pure returns (bytes32 r, bytes32 s, uint8 v) {
        require(sig.length == 65, "invalid signature length");
        assembly {
            r := mload(add(sig, 32))
            s := mload(add(sig, 64))
            v := byte(0, mload(add(sig, 96)))
        }
        if (v < 27) {
            v += 27;
        }
    }

    function testLogic() public {
        require(verifyOrderingRight());
    }

    function testPriorityLogic(uint256 feeAmount, bytes memory sig) public {
        require(claimPriorityOrdering(address(this), block.chainid, block.number, msg.sender, feeAmount, sig));
        testLogic();
    }
}
