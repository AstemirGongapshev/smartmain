// This setup uses Hardhat Ignition to manage smart contract deployments.
// Learn more about it at https://hardhat.org/ignition

const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

module.exports = buildModule("MfoLoanModule", (m) => {
  // Создаём контракт MFO_Loan
  const mfoLoan = m.contract("MFO_Loan");

  return { mfoLoan };
});
