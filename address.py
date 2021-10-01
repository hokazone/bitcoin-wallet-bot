from bitcoinlib import wallets
from bitcoinlib.wallets import (
    Wallet, WalletError, wallet_delete)
import os
import random
import string


class Address():

    def __init__(self):
        self.DB_URI = os.environ["DATABASE_URL3"]

    def create_dummy_address(self) -> str:
        randlst = [random.choice(string.ascii_letters + string.digits)
                   for i in range(33)]
        return ''.join(randlst)

    def create_address(self, wallet_name: str, network="testnet") -> str:
        w = Wallet.create(
            name=wallet_name, network=network, db_uri=self.DB_URI)
        walletkey = w.get_key()
        return walletkey.address

    def scan_wallet(self, wallet_name: str) -> str:
        wallet_open = Wallet(wallet=wallet_name, db_uri=self.DB_URI)
        wallet_open.scan()
        results = wallet_open.info(detail=1)
        return results

    def send_coin(self, wallet_name: str, to_address: str, amount: float):
        wallet_open = Wallet(wallet=wallet_name, db_uri=self.DB_URI)
        try:
            send = wallet_open.send_to(to_address, str(amount) + " TBTC")
            print(send.info())
        except WalletError:
            print(f"Catch WalletError: {WalletError}")

    def delete_address(self, wallet_name: str) -> bool:
        # 削除フラグにて実装予定
        try:
            if wallet_delete(wallet_name, self.DB_URI, True) == 1:
                return True
            else:
                return False
        except Exception:
            return False

    def updateAddress(self):
        pass
