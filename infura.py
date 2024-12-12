from web3 import Web3


INFURA_PROJECT_ID = "b67dc832cece4d53a18dcf9efb74e4cf"  
INFURA_URL = "https://mainnet.infura.io/v3/b67dc832cece4d53a18dcf9efb74e4cf"


web3 = Web3(Web3.HTTPProvider(INFURA_URL))


if web3.is_connected():
    print("Successfully Ethereum  Infura!")
else:
    print("OPS Fail!")
