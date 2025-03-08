import hashlib
import time

class SecurityBlock:
    def __init__(self, security_data):
        self.security_data = security_data  # Genellikle Genesis Block'un security hash'i gibi bir veri kullanılır
        self.timestamp = time.time()
        self.block_hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.security_data}{self.timestamp}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            'security_data': self.security_data,
            'timestamp': self.timestamp,
            'security_hash': self.block_hash  # Burada 'security_hash' olarak döndürüyoruz
        }

    @property
    def security_hash(self):
        return self.block_hash  # security_hash özelliği olarak block_hash'i döndürüyoruz