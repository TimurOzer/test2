import hashlib
import time
import uuid  # transaction_id için

class AlphaBlock:
    def __init__(
        self,
        previous_hash,
        sender,
        recipient,
        amount,
        tag="general",
        transaction_type="transfer",
        status="pending",
        fee="0",
        smart_contract=None,
        signature=None,
        difficulty="100000",
        block_size="1024",
        network="mainnet",
        block_height=0,
        tags=None,
        priority="medium",
        metadata=None
    ):
        self.version = "1.0"  # 1. Blok versiyonu
        self.transaction_id = str(uuid.uuid4())  # 2. İşlem kimliği (UUID)
        self.previous_hash = previous_hash  # Önceki bloğun hash'i
        self.sender = sender  # Gönderen adresi
        self.recipient = recipient  # Alıcı adresi
        self.amount = amount  # Transfer miktarı
        self.tag = tag  # İşlem türü (örn. "transfer", "airdrop")
        self.timestamp = time.time()  # 6. Zaman damgası
        self.nonce = 0
        self.transaction_type = transaction_type  # 3. İşlem türü
        self.status = status  # 4. İşlem durumu
        self.fee = fee  # 5. İşlem ücreti
        self.smart_contract = smart_contract if smart_contract else {}  # 7. Akıllı kontrat bilgisi
        self.signature = signature  # 8. İmza
        self.difficulty = difficulty  # 11. Blok zorluk seviyesi
        self.block_size = block_size  # 13. Blok boyutu
        self.network = network  # 15. Blok zinciri ağı bilgisi
        self.block_height = block_height  # 17. Blok yüksekliği
        self.tags = tags if tags else []  # 18. Özel etiketler
        self.priority = priority  # 19. Blok önceliği
        self.metadata = metadata if metadata else {}  # Metadata
        self.block_hash = self.calculate_hash()

    def calculate_hash(self):
        """Bloğun hash değerini hesaplar."""
        block_data = (
            f"{self.version}{self.transaction_id}{self.previous_hash}{self.sender}"
            f"{self.recipient}{self.amount}{self.tag}{self.timestamp}{self.nonce}"
            f"{self.transaction_type}{self.status}{self.fee}{str(self.smart_contract)}"
            f"{self.signature}{self.difficulty}{self.block_size}{self.network}"
            f"{self.block_height}{str(self.tags)}{self.priority}{str(self.metadata)}"
        )
        return hashlib.sha256(block_data.encode()).hexdigest()

    def to_dict(self):
        """Bloğu sözlük formatına çevirir."""
        return {
            "version": self.version,  # 1. Blok versiyonu
            "transaction_id": self.transaction_id,  # 2. İşlem kimliği
            "previous_hash": self.previous_hash,
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "tag": self.tag,
            "timestamp": self.timestamp,  # 6. Zaman damgası
            "nonce": self.nonce,
            "transaction_type": self.transaction_type,  # 3. İşlem türü
            "status": self.status,  # 4. İşlem durumu
            "fee": self.fee,  # 5. İşlem ücreti
            "smart_contract": self.smart_contract,  # 7. Akıllı kontrat bilgisi
            "signature": self.signature,  # 8. İmza
            "difficulty": self.difficulty,  # 11. Blok zorluk seviyesi
            "block_size": self.block_size,  # 13. Blok boyutu
            "network": self.network,  # 15. Blok zinciri ağı bilgisi
            "block_height": self.block_height,  # 17. Blok yüksekliği
            "tags": self.tags,  # 18. Özel etiketler
            "priority": self.priority,  # 19. Blok önceliği
            "metadata": self.metadata,  # Metadata
            "block_hash": self.block_hash
        }