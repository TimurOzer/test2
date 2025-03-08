# wallet_block.py
import hashlib
import time

class WalletBlock:
    def __init__(self, wallet_address):
        self.wallet_address = wallet_address
        self.timestamp = time.time()
        self.tag = "wallet"
        self.block_hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.wallet_address}{self.timestamp}{self.tag}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            "wallet_address": self.wallet_address,
            "timestamp": self.timestamp,
            "tag": self.tag,
            "block_hash": self.block_hash
        }
