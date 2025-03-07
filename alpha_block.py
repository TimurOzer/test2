import hashlib
import time

class AlphaBlock:
    def __init__(self, previous_hash, recipient, amount, tag='transaction'):
        self.previous_hash = previous_hash  # Genesis veya önceki alpha block'un normal hash'i
        self.recipient = recipient          # Transferin gönderileceği cüzdan adresi
        self.amount = amount                # Transfer miktarı
        self.tag = tag                      # İşlem tipi (ör. 'transaction' veya 'mining')
        self.timestamp = time.time()
        self.block_hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.previous_hash}{self.recipient}{self.amount}{self.tag}{self.timestamp}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            'previous_hash': self.previous_hash,
            'recipient': self.recipient,
            'amount': self.amount,
            'tag': self.tag,
            'timestamp': self.timestamp,
            'block_hash': self.block_hash
        }
