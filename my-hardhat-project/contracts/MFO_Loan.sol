// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract MFO_Loan {
    struct Loan {
        uint256 amount;
        uint256 repaymentAmount;
        uint256 dueDate;
        bool isRepaid;
    }

    mapping(address => Loan) public loans;

    address public owner;

    event LoanRequested(address indexed borrower, uint256 amount, uint256 repaymentAmount, uint256 dueDate);
    event LoanRepaid(address indexed borrower, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can perform this action");
        _;
    }

    modifier hasNoActiveLoan() {
        require(loans[msg.sender].dueDate == 0 || loans[msg.sender].isRepaid, "Active loan exists");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function requestLoan(uint256 _amount, uint256 _repaymentAmount, uint256 _dueDate) external hasNoActiveLoan {
        require(_amount > 0, "Loan amount must be greater than 0");
        require(_repaymentAmount > _amount, "Repayment amount must be greater than the loan amount");
        require(_dueDate > block.timestamp, "Due date must be in the future");

        loans[msg.sender] = Loan({
            amount: _amount,
            repaymentAmount: _repaymentAmount,
            dueDate: _dueDate,
            isRepaid: false
        });

        emit LoanRequested(msg.sender, _amount, _repaymentAmount, _dueDate);
    }

    function repayLoan() external payable {
        Loan storage loan = loans[msg.sender];
        require(loan.dueDate != 0, "No active loan");
        require(!loan.isRepaid, "Loan already repaid");
        require(msg.value == loan.repaymentAmount, "Incorrect repayment amount");

        loan.isRepaid = true;
        emit LoanRepaid(msg.sender, msg.value);
    }

    function withdrawFunds() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }

    function getLoanDetails(address borrower) external view returns (Loan memory) {
        return loans[borrower];
    }
}
