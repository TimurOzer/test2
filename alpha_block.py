import hashlib
import time

class AlphaBlock:
    def __init__(self, previous_hash, recipient, amount, tag):
        self.previous_hash = previous_hash  # Buraya Beta Block'un hash'i gelmeli
        self.recipient = recipient
        self.amount = amount
        self.tag = tag
        self.timestamp = time.time()
        self.block_hash = self.calculate_block_hash()

    def calculate_block_hash(self):
        block_string = f"{self.previous_hash}{self.recipient}{self.amount}{self.tag}{self.timestamp}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            "previous_hash": self.previous_hash,  # Buraya Beta Block'un hash'i gelmeli!
            "recipient": self.recipient,
            "amount": self.amount,
            "tag": self.tag,
            "timestamp": self.timestamp,
            "block_hash": self.block_hash
        }

