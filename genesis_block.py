import hashlib
import time
import json

# 🔹 Blockchain Genesis Block için Ayarlar
TOKEN_ADDRESS = "bklvdc38569a110702c2fed1164021f0539df178"
MAX_SUPPLY = 100_000_000  # Maksimum 100 milyon arz
DIFFICULTY = 4  # Proof of Work için zorluk seviyesi (ön eki '0000' olan bir hash bulunacak)

class GenesisBlock:
    def __init__(self, token_address, max_supply):
        self.token_address = token_address
        self.max_supply = max_supply
        self.timestamp = time.time()
        self.prev_hash_1 = "0" * 64  # İlk blok olduğu için önceki hash yok
        self.prev_hash_2 = "0" * 64
        self.nonce = 0  # Madencilik için sayacımız
        self.block_hash = None
        self.security_hash = None  # İkinci güvenlik hash'i olacak

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
            "security_hash": self.security_hash
        }

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

# Genesis blok oluştur ve madenciliği yap
genesis_block = GenesisBlock(TOKEN_ADDRESS, MAX_SUPPLY)
genesis_block.mine_block()

# Genesis bloğu JSON dosyasına kaydet
with open("genesis_block.json", "w") as f:
    json.dump(genesis_block.to_dict(), f, indent=4)

print("📜 Genesis Block saved to 'genesis_block.json'")

