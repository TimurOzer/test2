import hashlib
import time
import json

class SecurityBlock:
    def __init__(
        self,
        security_data,
        security_type="data_integrity",
        audit_data=None,
        fraud_detection=None,
        data_integrity_check=None,
        security_signature=None,
        threat_level="low",
        related_blocks=None,
        security_timestamp=None,
        action_taken=None,
        metadata=None
    ):
        self.security_data = security_data  # Temel güvenlik verisi (örneğin, Genesis Block'un security hash'i)
        self.security_type = security_type  # Güvenlik türü
        self.audit_data = audit_data if audit_data else {}  # Denetim verileri
        self.fraud_detection = fraud_detection if fraud_detection else {}  # Sahtecilik tespiti
        self.data_integrity_check = data_integrity_check if data_integrity_check else {}  # Veri bütünlüğü kontrolü
        self.security_signature = security_signature  # Güvenlik imzası
        self.threat_level = threat_level  # Tehdit seviyesi
        self.related_blocks = related_blocks if related_blocks else []  # İlgili bloklar
        self.security_timestamp = security_timestamp if security_timestamp else time.time()  # Güvenlik zaman damgası
        self.action_taken = action_taken  # Alınan aksiyon
        self.metadata = metadata if metadata else {}  # Meta veri
        self.timestamp = time.time()  # Blokun oluşturulma zamanı
        self.block_hash = self.calculate_hash()

    def calculate_hash(self):
        """Bloğun hash değerini hesaplar."""
        block_data = (
            f"{self.security_data}{self.security_type}{json.dumps(self.audit_data)}"
            f"{json.dumps(self.fraud_detection)}{json.dumps(self.data_integrity_check)}"
            f"{self.security_signature}{self.threat_level}{json.dumps(self.related_blocks)}"
            f"{self.security_timestamp}{self.action_taken}{json.dumps(self.metadata)}"
            f"{self.timestamp}"
        )
        return hashlib.sha256(block_data.encode()).hexdigest()

    def to_dict(self):
        """Bloğu sözlük formatına çevirir."""
        return {
            "security_data": self.security_data,
            "security_type": self.security_type,
            "audit_data": self.audit_data,
            "fraud_detection": self.fraud_detection,
            "data_integrity_check": self.data_integrity_check,
            "security_signature": self.security_signature,
            "threat_level": self.threat_level,
            "related_blocks": self.related_blocks,
            "security_timestamp": self.security_timestamp,
            "action_taken": self.action_taken,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "security_hash": self.block_hash  # Güvenlik hash'i
        }

    @property
    def security_hash(self):
        return self.block_hash  # security_hash özelliği olarak block_hash'i döndürüyoruz