import random
import string
from bitcoinlib.wallets import Wallet as wl, WalletError
from bitcoinlib import wallets as wl_del


class Address():

    def __init__(self):
        pass

    def createDummyAddress(self) -> str:
        randlst = [random.choice(string.ascii_letters + string.digits)
                   for i in range(33)]
        return ''.join(randlst)

    def createAddress(self, wallet_name: str, network="bitcoin") -> str:
        w = wl.create(wallet_name, network=network)
        walletkey = w.get_key()
        return walletkey.address

    def deleteAddress(self, wallet_name: str) -> bool:
        try:
            wl_del.wallet_delete(wallet_name)
            return True
        except WalletError:
            print(WalletError)
            return False

    def createAddressTestNet(self):
        pass

    def updateAddress(self):
        pass
