// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./JustTheEnforcement.sol";

contract JustTheExample is JustTheEnforcement {

    event Executed (uint256 order);

    modifier correctlyOrdered {
        require(verifyOrderingRight());
        _;
    }

    function testLogic() public correctlyOrdered {
        // Show what index this (this will now have been incremented)
        emit Executed(executionCounter[block.number]);
    }

    function testPriorityLogic(uint256 feeAmount, bytes memory sig) public {
        require(claimPriorityOrdering(address(this), block.chainid, block.number, msg.sender, feeAmount, sig));
        testLogic();
    }
}
