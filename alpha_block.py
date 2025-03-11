import hashlib
import time

class AlphaBlock:
    def __init__(self, previous_hash, sender, recipient, amount, tag="general"):
        self.previous_hash = previous_hash  # Önceki bloğun hash'i
        self.sender = sender  # Gönderen adresi
        self.recipient = recipient  # Alıcı adresi
        self.amount = amount  # Transfer miktarı
        self.tag = tag  # İşlem türü (örn. "transfer", "airdrop")
        self.timestamp = time.time()
        self.nonce = 0
        self.block_hash = self.calculate_hash()

    def calculate_hash(self):
        """Bloğun hash değerini hesaplar."""
        block_data = f"{self.previous_hash}{self.sender}{self.recipient}{self.amount}{self.tag}{self.timestamp}{self.nonce}"
        return hashlib.sha256(block_data.encode()).hexdigest()

    def to_dict(self):
        """Bloğu sözlük formatına çevirir."""
        return {
            "previous_hash": self.previous_hash,
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "tag": self.tag,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "block_hash": self.block_hash
        }
