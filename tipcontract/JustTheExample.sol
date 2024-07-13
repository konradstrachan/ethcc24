// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./JustTheEnforcement.sol";

contract JustTheExample is JustTheEnforcement {

    event Executed (uint256 order);
    event Paid (uint256 amount);

    modifier correctlyOrdered {
        require(verifyOrderingRight(), "ordering mmismatch");
        _;
    }

    function testLogic() public correctlyOrdered {
        // Show what index this (this will now have been incremented)
        emit Executed(executionCounter[block.number]);
    }

    function testPriorityLogic(uint256 feeAmount, bytes memory sig) public payable {
        require(
            claimPriorityOrdering(address(this), block.chainid, block.number, msg.sender, feeAmount, sig),
            "failed to set ordering");
        testLogic();
    }

    receive() external payable  { 
        emit Paid(msg.value);
    }

    fallback() external payable {
        emit Paid(msg.value);
    }
}
