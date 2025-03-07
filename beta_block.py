import hashlib
import time

class BetaBlock:
    def __init__(self, prev_alpha_hash, prev_security_hash):
        self.prev_alpha_hash = prev_alpha_hash      # Önceki alpha block'un hash'i
        self.prev_security_hash = prev_security_hash  # Önceki security block'un hash'i
        self.timestamp = time.time()
        self.block_hash = self.calculate_block_hash()
        self.security_hash = self.calculate_security_hash()

    def calculate_block_hash(self):
        block_string = f"{self.prev_alpha_hash}{self.prev_security_hash}{self.timestamp}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def calculate_security_hash(self):
        # Örneğin, block hash'e ek bir sabit değer ekleyerek yeni bir hash oluşturabilirsiniz.
        salt = "beta_salt_value"
        return hashlib.sha256((self.block_hash + salt).encode()).hexdigest()

    def to_dict(self):
        return {
            "prev_alpha_hash": self.prev_alpha_hash,
            "prev_security_hash": self.prev_security_hash,
            "timestamp": self.timestamp,
            "block_hash": self.block_hash,
            "security_hash": self.security_hash
        }
