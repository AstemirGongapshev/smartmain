from web3 import Web3

web3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"))

ABI="@custom:dev-run-script file_path"
contract_address = ABI
contract_abi = [
  
]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def request_loan(account, private_key, amount, repayment_amount, due_date):
    nonce = web3.eth.getTransactionCount(account)
    transaction = contract.functions.requestLoan(amount, repayment_amount, due_date).buildTransaction({
        'chainId': 1,
        'gas': 2000000,
        'gasPrice': web3.toWei('20', 'gwei'),
        'nonce': nonce
    })
    signed_txn = web3.eth.account.signTransaction(transaction, private_key=private_key)
    web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    return web3.toHex(web3.keccak(signed_txn.rawTransaction))

def repay_loan(account, private_key, repayment_amount):
    nonce = web3.eth.getTransactionCount(account)
    transaction = contract.functions.repayLoan().buildTransaction({
        'chainId': 1,
        'gas': 2000000,
        'gasPrice': web3.toWei('20', 'gwei'),
        'nonce': nonce,
        'value': web3.toWei(repayment_amount, 'ether')
    })
    signed_txn = web3.eth.account.signTransaction(transaction, private_key=private_key)
    web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    return web3.toHex(web3.keccak(signed_txn.rawTransaction))
