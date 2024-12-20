// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title MFO_Loan
 * @dev Пример микрофинансового контракта, позволяющего брать микрокредит на фиксированных условиях.
 *      Заёмщик запрашивает кредит, получает фиксированную сумму, а к моменту срока погашения должен 
 *      вернуть фиксированную сумму погашения. Владелец контракта может забрать накопленные средства.
 */
contract MFO_Loan {
    // Структура, описывающая условия кредита конкретного заёмщика
    struct Loan {
        uint256 amount;           // Сумма выданного кредита
        uint256 repaymentAmount;  // Сумма погашения
        uint256 dueDate;          // Крайний срок погашения (в виде unix-времени)
        bool isRepaid;            // Статус кредита (погашен или нет)
    }

    // Маппинг хранит состояние кредитов для каждого заёмщика (адреса)
    mapping(address => Loan) public loans;

    // Адрес владельца контракта (обычно — MFO)
    address public owner;

    // События для отслеживания выдачи и погашения кредита
    event LoanRequested(address indexed borrower, uint256 amount, uint256 repaymentAmount, uint256 dueDate);
    event LoanRepaid(address indexed borrower, uint256 amount);

    // Модификатор, разрешающий доступ только владельцу
    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can perform this action");
        _;
    }

    // Модификатор, проверяющий отсутствие активного кредита у вызывающего
    modifier hasNoActiveLoan() {
        // Активный кредит: dueDate еще не истёк и кредит не погашен
        // Если dueDate = 0, значит кредит не брался, или 
        // если isRepaid = true, значит предыдущий кредит погашен
        require(loans[msg.sender].dueDate == 0 || loans[msg.sender].isRepaid, "Active loan exists");
        _;
    }

    // Конструктор контракта: устанавливаем владельца при деплое
    constructor() {
        owner = msg.sender;
    }

    // Фиксированные параметры кредита - синтетические данные для примера
    uint256 public fixedLoanAmount = 50000 wei;     // сумма кредита (пример: 50.000 wei)
    uint256 public fixedRepaymentAmount = 1500 wei; // сумма, которую нужно вернуть (пример: 1.500 wei)
    uint256 public fixedLoanDuration = 30 days;     // срок кредита (пример: 30 дней)

    /**
     * @dev Метод для запроса кредита. 
     * Вызывается заёмщиком, у которого нет активного кредита.
     * После вызова - ему "виртуально" предоставляется кредит с фиксированными условиями.
     */
    function requestLoan() external hasNoActiveLoan {
        uint256 dueDate = block.timestamp + fixedLoanDuration;

        loans[msg.sender] = Loan({
            amount: fixedLoanAmount,
            repaymentAmount: fixedRepaymentAmount,
            dueDate: dueDate,
            isRepaid: false
        });

        emit LoanRequested(msg.sender, fixedLoanAmount, fixedRepaymentAmount, dueDate);
    }

    /**
     * @dev Метод для погашения кредита.
     * Заёмщик отправляет ровно repaymentAmount средств, погашая свою задолженность.
     */
    function repayLoan() external payable {
        Loan storage loan = loans[msg.sender];
        require(loan.dueDate != 0, "No active loan");
        require(!loan.isRepaid, "Loan already repaid");
        require(msg.value == loan.repaymentAmount, "Incorrect repayment amount");

        loan.isRepaid = true;
        emit LoanRepaid(msg.sender, msg.value);
    }

    /**
     * @dev Метод для вывода собранных средств владельцем контракта.
     * Разрешён только владельцу.
     */
    function withdrawFunds() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }

    /**
     * @dev Вспомогательный метод для получения деталей кредита заёмщика.
     */
    function getLoanDetails(address borrower) external view returns (Loan memory) {
        return loans[borrower];
    }
}
