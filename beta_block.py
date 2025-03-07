import hashlib
import time

class BetaBlock:
    def __init__(self, alpha_hash, security_hash):
        self.alpha_hash = alpha_hash      # Alpha Block'un hash değeri
        self.security_hash = security_hash  # Security Block'un hash değeri
        self.timestamp = time.time()
        self.block_hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.alpha_hash}{self.security_hash}{self.timestamp}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            'alpha_hash': self.alpha_hash,
            'security_hash': self.security_hash,
            'timestamp': self.timestamp,
            'block_hash': self.block_hash
        }
