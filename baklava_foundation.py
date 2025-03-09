import os
import ecdsa
import hashlib
import base58
import json
import math

# Sabitler
F_MIN = 0.0001  # Minimum transfer ücreti
ALPHA = 0.00005  # Ücretin blok sayısına duyarlılık katsayısı

class BaklavaFoundationWallet:
    def __init__(self, private_key=None):
        if private_key:
            self.private_key = private_key
        else:
            self.private_key = self.generate_private_key()
        
        self.public_key = self.generate_public_key()
        self.address = self.generate_address()
        self.balance = 0  # Baklava Foundation cüzdanının başlangıç bakiyesi

    def generate_private_key(self):
        """256-bit rastgele özel anahtar üretir."""
        return os.urandom(32).hex()

    def generate_public_key(self):
        """Özel anahtardan genel anahtar türetir (ECDSA SECP256k1)."""
        private_key_bytes = bytes.fromhex(self.private_key)
        sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
        vk = sk.verifying_key
        return vk.to_string().hex()

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

    def save_wallet(self, filename="baklava_foundation_wallet.json"):
        """Cüzdanı JSON dosyasına kaydeder."""
        wallet_data = {
            "private_key": self.private_key,
            "public_key": self.public_key,
            "address": self.address,
            "balance": self.balance
        }
        with open(filename, "w") as f:
            json.dump(wallet_data, f, indent=4)
        print(f"💾 Baklava Foundation cüzdanı başarıyla {filename} dosyasına kaydedildi!")

    @staticmethod
    def load_wallet(filename="baklava_foundation_wallet.json"):
        """JSON dosyasından cüzdanı yükler."""
        if os.path.exists(filename):
            with open(filename, "r") as f:
                wallet_data = json.load(f)
            print(f"🔑 Baklava Foundation cüzdanı {filename} dosyasından yüklendi!")
            wallet = BaklavaFoundationWallet(private_key=wallet_data["private_key"])
            wallet.balance = wallet_data.get("balance", 0)  # Bakiyeyi yükle
            return wallet
        else:
            print("❌ Baklava Foundation cüzdan dosyası bulunamadı, yeni cüzdan oluşturuluyor...")
            return BaklavaFoundationWallet()

def calculate_transfer_fee(blocks_produced_today):
    """
    Transfer ücretini hesaplar.
    Formül: F = F_MIN + ALPHA * log(1 + B)
    F: Transfer ücreti
    B: O gün üretilen Beta blok sayısı
    """
    return F_MIN + ALPHA * math.log(1 + blocks_produced_today)

def transfer_fee_to_foundation(amount):
    """
    Transfer ücretini Baklava Foundation cüzdanına aktarır.
    """
    foundation_wallet = BaklavaFoundationWallet.load_wallet()
    foundation_wallet.balance += amount
    foundation_wallet.save_wallet()
    print(f"💸 {amount} transfer ücreti Baklava Foundation cüzdanına aktarıldı. Yeni bakiye: {foundation_wallet.balance}")