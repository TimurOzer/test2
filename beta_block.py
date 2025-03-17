import hashlib
import time
import json

class BetaBlock:
    def __init__(
        self,
        prev_alpha_hash,
        prev_security_hash,
        block_type="bridge",
        consensus_data=None,
        linked_blocks=None,
        integrity_check=None,
        metadata=None,
        security_level="medium",
        transaction_summary=None,
        checkpoint_data=None,
        signature=None
    ):
        self.prev_alpha_hash = prev_alpha_hash  # Önceki alpha block'un hash'i
        self.prev_security_hash = prev_security_hash  # Önceki security block'un hash'i
        self.block_type = block_type  # Blok türü
        self.consensus_data = consensus_data if consensus_data else {}  # Konsensüs verileri
        self.linked_blocks = linked_blocks if linked_blocks else []  # Bağlantılı bloklar
        self.integrity_check = integrity_check if integrity_check else {}  # Bütünlük kontrolü
        self.metadata = metadata if metadata else {}  # Meta veri
        self.security_level = security_level  # Güvenlik seviyesi
        self.transaction_summary = transaction_summary if transaction_summary else {}  # İşlem özeti
        self.checkpoint_data = checkpoint_data if checkpoint_data else {}  # Kontrol noktası verileri
        self.signature = signature  # İmza
        self.timestamp = time.time()  # Zaman damgası
        self.block_hash = self.calculate_block_hash()
        self.security_hash = self.calculate_security_hash()

    def calculate_block_hash(self):
        """Bloğun hash değerini hesaplar."""
        block_data = (
            f"{self.prev_alpha_hash}{self.prev_security_hash}{self.block_type}"
            f"{json.dumps(self.consensus_data)}{json.dumps(self.linked_blocks)}"
            f"{json.dumps(self.integrity_check)}{json.dumps(self.metadata)}"
            f"{self.security_level}{json.dumps(self.transaction_summary)}"
            f"{json.dumps(self.checkpoint_data)}{self.signature}{self.timestamp}"
        )
        return hashlib.sha256(block_data.encode()).hexdigest()

    def calculate_security_hash(self):
        """Güvenlik hash'ini hesaplar."""
        salt = "beta_salt_value"
        return hashlib.sha256((self.block_hash + salt).encode()).hexdigest()

    def to_dict(self):
        """Bloğu sözlük formatına çevirir."""
        return {
            "prev_alpha_hash": self.prev_alpha_hash,
            "prev_security_hash": self.prev_security_hash,
            "block_type": self.block_type,
            "consensus_data": self.consensus_data,
            "linked_blocks": self.linked_blocks,
            "integrity_check": self.integrity_check,
            "metadata": self.metadata,
            "security_level": self.security_level,
            "transaction_summary": self.transaction_summary,
            "checkpoint_data": self.checkpoint_data,
            "signature": self.signature,
            "timestamp": self.timestamp,
            "block_hash": self.block_hash,
            "security_hash": self.security_hash
        }