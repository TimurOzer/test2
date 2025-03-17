import hashlib
import time
import uuid  # transaction_id için

# 🔹 Blockchain Genesis Block için Ayarlar
TOKEN_ADDRESS = "bklvdc38569a110702c2fed1164021f0539df178"
MAX_SUPPLY = 100_000_000  # Maksimum 100 milyon arz
DIFFICULTY = 4  # Proof of Work için zorluk seviyesi (ön eki '0000' olan bir hash bulunacak)

class GenesisBlock:
    def __init__(
        self,
        token_address,
        max_supply,
        timestamp=None,
        prev_hash_1="0" * 64,
        prev_hash_2="0" * 64,
        nonce=0,
        block_hash=None,
        security_hash=None,
        version="1.0",  # 1. Blok versiyonu
        transaction_id=None,  # 2. İşlem kimliği
        transaction_type="genesis",  # 3. İşlem türü
        status="confirmed",  # 4. İşlem durumu
        fee="0",  # 5. İşlem ücreti
        smart_contract=None,  # 7. Akıllı kontrat bilgisi
        signature=None,  # 8. İmza
        block_size="1024",  # 13. Blok boyutu
        network="mainnet",  # 15. Blok zinciri ağı bilgisi
        block_height=0,  # 17. Blok yüksekliği
        tags=None,  # 18. Özel etiketler
        priority="high",  # 19. Blok önceliği
        metadata=None,  # Metadata
        airdrop_reserve=50000000,
        mining_reserve=50000000
    ):
        self.version = version
        self.transaction_id = transaction_id if transaction_id else str(uuid.uuid4())
        self.token_address = token_address
        self.max_supply = max_supply
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.prev_hash_1 = prev_hash_1
        self.prev_hash_2 = prev_hash_2
        self.nonce = nonce
        self.block_hash = block_hash
        self.security_hash = security_hash
        self.transaction_type = transaction_type
        self.status = status
        self.fee = fee
        self.smart_contract = smart_contract if smart_contract else {}
        self.signature = signature
        self.block_size = block_size
        self.network = network
        self.block_height = block_height
        self.tags = tags if tags else ["genesis"]
        self.priority = priority
        self.metadata = metadata if metadata else {}
        self.airdrop_reserve = airdrop_reserve
        self.mining_reserve = mining_reserve

    def to_dict(self):
        """Genesis blok verilerini sözlük formatına çevirir."""
        return {
            "version": self.version,
            "transaction_id": self.transaction_id,
            "token_address": self.token_address,
            "max_supply": self.max_supply,
            "timestamp": self.timestamp,
            "prev_hash_1": self.prev_hash_1,
            "prev_hash_2": self.prev_hash_2,
            "nonce": self.nonce,
            "block_hash": self.block_hash,
            "security_hash": self.security_hash,
            "transaction_type": self.transaction_type,
            "status": self.status,
            "fee": self.fee,
            "smart_contract": self.smart_contract,
            "signature": self.signature,
            "block_size": self.block_size,
            "network": self.network,
            "block_height": self.block_height,
            "tags": self.tags,
            "priority": self.priority,
            "metadata": self.metadata,
            "airdrop_reserve": self.airdrop_reserve,
            "mining_reserve": self.mining_reserve
        }

    @classmethod
    def from_dict(cls, data):
        """Sözlük formatındaki verileri kullanarak GenesisBlock nesnesi oluşturur."""
        return cls(
            version=data.get("version", "1.0"),
            transaction_id=data.get("transaction_id", str(uuid.uuid4())),
            token_address=data["token_address"],
            max_supply=data["max_supply"],
            timestamp=data["timestamp"],
            prev_hash_1=data["prev_hash_1"],
            prev_hash_2=data["prev_hash_2"],
            nonce=data["nonce"],
            block_hash=data["block_hash"],
            security_hash=data["security_hash"],
            transaction_type=data.get("transaction_type", "genesis"),
            status=data.get("status", "confirmed"),
            fee=data.get("fee", "0"),
            smart_contract=data.get("smart_contract", {}),
            signature=data.get("signature", None),
            block_size=data.get("block_size", "1024"),
            network=data.get("network", "mainnet"),
            block_height=data.get("block_height", 0),
            tags=data.get("tags", ["genesis"]),
            priority=data.get("priority", "high"),
            metadata=data.get("metadata", {}),
            airdrop_reserve=data.get("airdrop_reserve", 50000000),
            mining_reserve=data.get("mining_reserve", 50000000)
        )

    def mine_block(self):
        """Proof of Work (PoW) madencilik işlemi ile uygun hash değerini bulur."""
        print("⛏️ Mining Genesis Block...")
        while True:
            block_data = (
                f"{self.version}{self.transaction_id}{self.token_address}{self.max_supply}"
                f"{self.timestamp}{self.prev_hash_1}{self.prev_hash_2}{self.nonce}"
                f"{self.transaction_type}{self.status}{self.fee}{str(self.smart_contract)}"
                f"{self.signature}{self.block_size}{self.network}{self.block_height}"
                f"{str(self.tags)}{self.priority}{str(self.metadata)}"
            )
            block_hash = hashlib.sha256(block_data.encode()).hexdigest()

            # Eğer hash DIFFICULTY seviyesini sağlıyorsa (örn. '0000' ile başlıyorsa) madencilik tamam
            if block_hash.startswith("0" * DIFFICULTY):
                self.block_hash = block_hash
                self.security_hash = hashlib.sha256(block_hash.encode()).hexdigest()  # Security hash üretildi
                print(f"✅ Genesis Block Mined!")
                print(f"🔹 Block Hash: {self.block_hash}")
                print(f"🔹 Security Hash: {self.security_hash}")
                break
            
            # 10.000 adımda bir durumu bildir
            if self.nonce % 10_000 == 0:
                print(f"⏳ Still mining... Nonce: {self.nonce}")

            self.nonce += 1