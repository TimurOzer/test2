import os
import ecdsa
import hashlib
import base58
import json

BAKLAVA_TOKEN_ID = "bklvdc38569a110702c2fed1164021f0539df178"

class Wallet:
    def __init__(self, private_key=None):
        if private_key:
            self.private_key = private_key
        else:
            self.private_key = self.generate_private_key()
        
        self.public_key = self.generate_public_key()
        self.address = self.generate_address()
        self.baklava_balance = {BAKLAVA_TOKEN_ID: 0}  # Varsayılan olarak 0 bakiye

    def generate_private_key(self):
        """256-bit rastgele özel anahtar üretir."""
        return os.urandom(32).hex()

    def generate_public_key(self):
        """Özel anahtardan genel anahtar türetir (ECDSA SECP256k1)."""
        private_key_bytes = bytes.fromhex(self.private_key)
        sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
        vk = sk.verifying_key
        return vk.to_string().hex()

    def save_to_server(self):
        """Cüzdanı server'a kaydet"""
        wallet_path = os.path.join(WALLETS_DIR, f"{self.address}.json")
        wallet_data = {
            "address": self.address,
            "baklava_balance": self.baklava_balance
        }
        with open(wallet_path, "w") as f:
            json.dump(wallet_data, f, indent=4)

    def generate_address(self):
        """Genel anahtardan SHA-256 ve Base58 ile cüzdan adresi üretir."""
        public_key_bytes = bytes.fromhex(self.public_key)
        sha256_pubkey = hashlib.sha256(public_key_bytes).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_pubkey)
        hashed_pubkey = ripemd160.digest()

        network_byte = b'\x00' + hashed_pubkey
        checksum = hashlib.sha256(hashlib.sha256(network_byte).digest()).digest()[:4]
        address_bytes = network_byte + checksum
        return base58.b58encode(address_bytes).decode()

    def save_wallet(self, filename="wallet.json"):
        """Cüzdanı JSON dosyasına kaydeder."""
        wallet_data = {
            "private_key": self.private_key,
            "public_key": self.public_key,
            "address": self.address,
            "baklava_balance": self.baklava_balance  # Bakiyeyi kaydet
        }
        with open(filename, "w") as f:
            json.dump(wallet_data, f, indent=4)
        print(f"💾 Cüzdan başarıyla {filename} dosyasına kaydedildi!")

def load_wallet(filename="wallet.json"):
    """JSON dosyasından cüzdanı yükler."""
    if os.path.exists(filename):
        with open(filename, "r") as f:
            wallet_data = json.load(f)
        print(f"🔑 Cüzdan {filename} dosyasından yüklendi!")
        wallet = Wallet(private_key=wallet_data["private_key"])
        wallet.baklava_balance = wallet_data.get("baklava_balance", {BAKLAVA_TOKEN_ID: 0})  # Bakiyeyi yükle
        return wallet
    else:
        print("❌ Cüzdan dosyası bulunamadı, yeni cüzdan oluşturuluyor...")
        return Wallet()

# Yeni cüzdan oluştur ve kaydet
wallet = Wallet()
wallet.save_wallet()

# Kaydedilen cüzdanı tekrar yükle
loaded_wallet = load_wallet()  # load_wallet fonksiyonu tanımlandıktan sonra çağrılıyor

# ✅ Hatalı satır kaldırıldı
print("🏦 Adres:", loaded_wallet.address)
print("🔐 Private Key:", loaded_wallet.private_key)