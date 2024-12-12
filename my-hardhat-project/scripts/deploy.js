const hre = require("hardhat");

async function main() {
    // Загружаем фабрику контракта
    const Contract = await hre.ethers.getContractFactory("MFO_Loan");
    // Деплоим контракт
    const contract = await Contract.deploy();

    // Ожидаем завершения деплоя
    await contract.deployed();

    console.log("Contract deployed to:", contract.address);
}

// Запускаем основной процесс
main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
