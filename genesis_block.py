import hashlib
import time
import json

# 🔹 Blockchain Genesis Block için Ayarlar
TOKEN_ADDRESS = "bklvdc38569a110702c2fed1164021f0539df178"
MAX_SUPPLY = 100_000_000  # Maksimum 100 milyon arz
DIFFICULTY = 4  # Proof of Work için zorluk seviyesi (ön eki '0000' olan bir hash bulunacak)

class GenesisBlock:
    def __init__(self, token_address, max_supply, timestamp=None, prev_hash_1="0" * 64, prev_hash_2="0" * 64, nonce=0, block_hash=None, security_hash=None):
        self.token_address = token_address
        self.max_supply = max_supply
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.prev_hash_1 = prev_hash_1
        self.prev_hash_2 = prev_hash_2
        self.nonce = nonce
        self.block_hash = block_hash
        self.security_hash = security_hash
        self.airdrop_reserve = 50000000
        self.mining_reserve = 50000000  # Yeni eklenen kısım

    def to_dict(self):
        """Genesis blok verilerini sözlük formatına çevirir."""
        return {
            "token_address": self.token_address,
            "max_supply": self.max_supply,
            "timestamp": self.timestamp,
            "prev_hash_1": self.prev_hash_1,
            "prev_hash_2": self.prev_hash_2,
            "nonce": self.nonce,
            "block_hash": self.block_hash,
            "security_hash": self.security_hash,
            "airdrop_reserve": self.airdrop_reserve,
            "mining_reserve": self.mining_reserve  # Yeni eklenen kısım
        }

    @classmethod
    def from_dict(cls, data):
        """Sözlük formatındaki verileri kullanarak GenesisBlock nesnesi oluşturur."""
        return cls(
            token_address=data["token_address"],
            max_supply=data["max_supply"],
            timestamp=data["timestamp"],
            prev_hash_1=data["prev_hash_1"],
            prev_hash_2=data["prev_hash_2"],
            nonce=data["nonce"],
            block_hash=data["block_hash"],
            security_hash=data["security_hash"]
        )
        genesis.mining_reserve = data.get("mining_reserve", 50000000)
        return genesis

    def mine_block(self):
        """Proof of Work (PoW) madencilik işlemi ile uygun hash değerini bulur."""
        print("⛏️ Mining Genesis Block...")
        while True:
            block_data = f"{self.token_address}{self.max_supply}{self.timestamp}{self.prev_hash_1}{self.prev_hash_2}{self.nonce}"
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