import socket
import threading
import os
import shutil
import json
import hashlib
import time
from genesis_block import GenesisBlock, TOKEN_ADDRESS, MAX_SUPPLY  # Genesis Block sınıfı ve sabitler
from wallet import Wallet, load_wallet  # load_wallet fonksiyonunu da import edin
from baklava_foundation import calculate_transfer_fee, transfer_fee_to_foundation, BaklavaFoundationWallet
from wallet_block import WalletBlock
from wallet import BAKLAVA_TOKEN_ID

# Yeni blok sınıflarını import ediyoruz
from alpha_block import AlphaBlock
from security_block import SecurityBlock
from beta_block import BetaBlock

DATA_DIR = "data"  # Veri klasörü
GENESIS_BLOCK_FILE = os.path.join(DATA_DIR, "genesis_block.json")  # Dosya yolu
WALLETS_DIR = os.path.join(DATA_DIR, "wallets")  # Yeni eklendi
BAKLAVA_TOKEN_ID = "bklvdc38569a110702c2fed1164021f0539df178"
beta_blocks_today = len([f for f in os.listdir(DATA_DIR) if f.startswith("beta")])
# Global zorluk değişkeni
GLOBAL_MINING_DIFFICULTY = 4  # Başlangıç zorluğu
DAILY_BETA_BLOCKS = 0  # Bugün üretilen beta blok sayısı
LAST_BLOCK_TIMESTAMP = time.time()  # Son blok zamanı

# Yeni sabitler
STATE_FILE = os.path.join(DATA_DIR, "server_state.json")

def save_server_state():
    """Sunucu durumunu dosyaya kaydeder."""
    state = {
        "global_mining_difficulty": GLOBAL_MINING_DIFFICULTY,
        "daily_beta_blocks": DAILY_BETA_BLOCKS,
        "last_block_timestamp": LAST_BLOCK_TIMESTAMP
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def load_server_state():
    """Sunucu durumunu dosyadan yükler."""
    global GLOBAL_MINING_DIFFICULTY, DAILY_BETA_BLOCKS, LAST_BLOCK_TIMESTAMP
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
        GLOBAL_MINING_DIFFICULTY = state.get("global_mining_difficulty", 4)
        DAILY_BETA_BLOCKS = state.get("daily_beta_blocks", 0)
        LAST_BLOCK_TIMESTAMP = state.get("last_block_timestamp", time.time())
    else:
        # İlk başlatmada varsayılan değerler
        GLOBAL_MINING_DIFFICULTY = 4
        DAILY_BETA_BLOCKS = 0
        LAST_BLOCK_TIMESTAMP = time.time()
        save_server_state()  # İlk durumu kaydet
        
def ensure_data_dir():
    """Klasörleri oluştur"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(WALLETS_DIR):  # Yeni eklendi
        os.makedirs(WALLETS_DIR)

def ensure_data_dir():
    """Eğer data klasörü yoksa, oluşturur."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"📁 '{DATA_DIR}' klasörü oluşturuldu.")
    
def calculate_difficulty():
    global GLOBAL_MINING_DIFFICULTY, DAILY_BETA_BLOCKS, LAST_BLOCK_TIMESTAMP

    # Günlük beta blok sayısını kontrol et
    current_time = time.time()
    if current_time - LAST_BLOCK_TIMESTAMP > 86400:  # 1 gün geçtiyse
        DAILY_BETA_BLOCKS = 0  # Günlük beta blok sayısını sıfırla
        LAST_BLOCK_TIMESTAMP = current_time  # Zamanı güncelle
        save_server_state()  # Durumu kaydet

    # Zorluğu hesapla
    difficulty = GLOBAL_MINING_DIFFICULTY + int(DAILY_BETA_BLOCKS ** 0.5)
    return max(4, difficulty)  # Minimum zorluk 4
    
def is_valid_nonce(nonce, difficulty):
    """Nonce değerinin geçerli olup olmadığını kontrol eder."""
    try:
        nonce = int(nonce)  # Nonce'u integer'a çevir
        hash_result = hashlib.sha256(f"{nonce}{difficulty}".encode()).hexdigest()
        return hash_result.startswith('0' * difficulty)
    except (ValueError, TypeError):
        return False  # Nonce geçersizse False döndür
    
def calculate_mining_reward(client_socket):
    global GLOBAL_MINING_DIFFICULTY
    with open(GENESIS_BLOCK_FILE, "r") as f:
        genesis_data = json.load(f)
    
    mining_reserve = genesis_data["mining_reserve"]
    
    # Ödül formülü: (Base Reward) / (1 + Difficulty^1.5)
    base_reward = 100  # Temel ödül
    reward = base_reward / (1 + (GLOBAL_MINING_DIFFICULTY ** 1.5))
    
    return {
        "difficulty": GLOBAL_MINING_DIFFICULTY + int(DAILY_BETA_BLOCKS ** 0.5),
        "reward": round(reward, 2),
        "global_difficulty": GLOBAL_MINING_DIFFICULTY
    }

def update_mining_difficulty():
    global GLOBAL_MINING_DIFFICULTY, DAILY_BETA_BLOCKS
    DAILY_BETA_BLOCKS += 1
    GLOBAL_MINING_DIFFICULTY += 1  # Her başarılı madencilikte zorluğu +1 artır
    save_server_state()  # Durumu kaydet
    print(f"🔼 Global mining difficulty increased to: {GLOBAL_MINING_DIFFICULTY}")
    
def update_mining_reserve(reward):
    with open(GENESIS_BLOCK_FILE, "r+") as f:
        genesis_data = json.load(f)
        genesis_data["mining_reserve"] -= reward
        f.seek(0)
        json.dump(genesis_data, f, indent=4)
        f.truncate()

def create_genesis_block():
    """Eğer genesis_block.json yoksa veya geçersizse, yeni bir Genesis Block oluşturur."""
    if not os.path.exists(GENESIS_BLOCK_FILE):
        print("🔧 Genesis Block bulunamadı, oluşturuluyor...")
        genesis_block = GenesisBlock(TOKEN_ADDRESS, MAX_SUPPLY)
        genesis_block.mine_block()
        try:
            with open(GENESIS_BLOCK_FILE, "w") as f:
                json.dump(genesis_block.to_dict(), f, indent=4)
            print("✅ Genesis Block başarıyla oluşturuldu ve kaydedildi!")
        except Exception as e:
            print(f"❌ Genesis Block kaydedilirken hata oluştu: {e}")
    else:
        try:
            with open(GENESIS_BLOCK_FILE, "r") as f:
                genesis_data = json.load(f)
            if not genesis_data:
                raise ValueError("Dosya boş veya geçersiz JSON içeriyor.")
            genesis_block = GenesisBlock.from_dict(genesis_data)
            print("📜 Genesis Block zaten mevcut, yeniden oluşturulmadı.")
            print(f"🔹 Mevcut Block Hash: {genesis_block.block_hash}")
        except Exception as e:
            print(f"❌ Genesis Block okunurken hata oluştu: {e}")
            print("🔧 Genesis Block geçersiz, yeniden oluşturuluyor...")
            genesis_block = GenesisBlock(TOKEN_ADDRESS, MAX_SUPPLY)
            genesis_block.mine_block()
            try:
                with open(GENESIS_BLOCK_FILE, "w") as f:
                    json.dump(genesis_block.to_dict(), f, indent=4)
                print("✅ Genesis Block başarıyla oluşturuldu ve kaydedildi!")
            except Exception as e:
                print(f"❌ Genesis Block kaydedilirken hata oluştu: {e}")

def get_next_block_number(prefix):
    """
    DATA klasöründeki ilgili prefix'e sahip (örn. 'alpha', 'security', 'beta') dosyaların numarasını
    tespit eder ve bir sonraki numarayı döner.
    """
    files = [f for f in os.listdir(DATA_DIR) if f.startswith(prefix) and f.endswith('.json')]
    max_num = 0
    for filename in files:
        try:
            # Örneğin 'alpha1.json' dosyasından numarayı çıkarır
            num = int(filename[len(prefix):-5])
            if num > max_num:
                max_num = num
        except Exception:
            pass
    return max_num + 1

def get_previous_hashes():
    beta_num = get_next_block_number("beta") - 1
    if beta_num < 1:
        with open(GENESIS_BLOCK_FILE, "r") as f:
            genesis_data = json.load(f)
        prev_normal = genesis_data.get("block_hash")
        prev_security = genesis_data.get("security_hash")
    else:
        beta_filename = os.path.join(DATA_DIR, f"beta{beta_num}.json")
        with open(beta_filename, "r") as f:
            beta_data = json.load(f)
        prev_normal = beta_data.get("block_hash")
        prev_security = beta_data.get("security_hash")
    return prev_normal, prev_security

def send_prev_hashes(client_socket):
    beta_num = get_next_block_number("beta") - 1
    if beta_num < 1:
        with open(GENESIS_BLOCK_FILE, "r") as f:
            genesis_data = json.load(f)
        prev_normal = genesis_data.get("block_hash")
        prev_security = genesis_data.get("security_hash")
        beta_hash = None
    else:
        beta_filename = os.path.join(DATA_DIR, f"beta{beta_num}.json")
        with open(beta_filename, "r") as f:
            beta_data = json.load(f)
        # Dikkat: Burada eski input değeri olan "prev_security_hash" yerine
        # Beta blokun computed security hash'ini kullanmalıyız.
        prev_normal = beta_data.get("block_hash")  # Alpha için, yeni transferde Beta'nin block_hash kullanılabilir.
        prev_security = beta_data.get("security_hash")  # Computed security hash
        beta_hash = beta_data.get("block_hash")
    
    response = {
        "prev_normal_hash": prev_normal,
        "prev_security_hash": prev_security,
        "last_beta_hash": beta_hash
    }
    client_socket.send(json.dumps(response).encode('utf-8'))

def handle_client(client_socket, client_address):
    print(f"🔗 {client_address} bağlandı.")
    try:
        # Güncelleme isteği kontrolü
        update_request = client_socket.recv(1024).decode('utf-8')
        if update_request == 'GET_UPDATE':
            with open('client.py', 'rb') as file:
                client_socket.sendfile(file)
            print(f"📦 {client_address} için client.py güncellendi.")
            client_socket.close()
            return

        client_socket.send('UPDATE_NOT_NEEDED'.encode('utf-8'))

        while True:
            message = client_socket.recv(4096).decode('utf-8')
            if not message:
                break
                
            if message == "GET_PREV_HASHES":
                send_prev_hashes(client_socket)
                continue  # veya döngüyü kesmeden diğer mesajları bekleyin  
            # server.py'de "CREATE_WALLET" işlemi sırasında:           
            if message == "GET_MINING_INFO":
                print("🔍 Mining info requested by client")
                mining_info = calculate_mining_reward(client_socket)
                print(f"📤 Sending mining info: {mining_info}")
                client_socket.send(json.dumps(mining_info).encode())
                continue
            # SUBMIT_MINING mesajını ana döngüye ekleyin
            if message.startswith("SUBMIT_MINING"):
                print(f"⛏️ Mining submission received: {message}")
                try:
                    _, address, nonce = message.split("|")
                    mining_info = calculate_mining_reward(client_socket)
                    
                    # Nonce kontrolü
                    if is_valid_nonce(nonce, mining_info["difficulty"]):
                        update_mining_reserve(mining_info["reward"])
                        update_mining_difficulty()  # Zorluğu güncelle
                        
                        # Ödülü cüzdana ekle
                        wallet_path = os.path.join(WALLETS_DIR, f"{address}.json")
                        if os.path.exists(wallet_path):
                            with open(wallet_path, "r+") as f:
                                wallet_data = json.load(f)
                                wallet_data["baklava_balance"][BAKLAVA_TOKEN_ID] += mining_info["reward"]
                                f.seek(0)
                                json.dump(wallet_data, f, indent=4)
                                f.truncate()
                            print(f"💰 Mining reward added to {address}")
                        else:
                            print(f"❌ Wallet not found: {address}")
                            client_socket.send("WALLET_NOT_FOUND".encode())
                            continue
                        
                        # Blokları oluştur
                        prev_hashes = get_previous_hashes()
                        alpha_block = AlphaBlock(
                            previous_hash=prev_hashes[0],
                            sender="MINING_SYSTEM",
                            recipient=address,
                            amount=mining_info["reward"],
                            tag="mining"
                        )
                        security_block = SecurityBlock(prev_hashes[1])
                        beta_block = BetaBlock(
                            prev_alpha_hash=alpha_block.block_hash,
                            prev_security_hash=security_block.security_hash
                        )
                        
                        save_block(alpha_block, "alpha")
                        save_block(security_block, "security")
                        save_block(beta_block, "beta")
                        
                        client_socket.send("MINING_SUCCESS".encode())
                        print(f"✅ Mining successful for {address}")
                    else:
                        client_socket.send("INVALID_NONCE".encode())
                        print(f"❌ Invalid nonce: {nonce}")
                except Exception as e:
                    print(f"❌ Mining submission error: {e}")
                    client_socket.send("ERROR".encode())
                continue
            if message == "CREATE_WALLET":
                print("🏦 Cüzdan oluşturma talebi alındı.")
                new_wallet = Wallet()
                wallet_data = {
                    "private_key": new_wallet.private_key,
                    "public_key": new_wallet.public_key,
                    "address": new_wallet.address,
                    "baklava_balance": new_wallet.baklava_balance  # Bakiyeyi ekleyin
                }

                # Cüzdanı wallets klasörüne kaydet
                os.makedirs(WALLETS_DIR, exist_ok=True)
                wallet_path = os.path.join(WALLETS_DIR, f"{new_wallet.address}.json")
                with open(wallet_path, "w") as f:
                    json.dump(wallet_data, f, indent=4)
                print(f"✅ Cüzdan {new_wallet.address}.json olarak kaydedildi.")

                # İstemciye cüzdan bilgilerini gönder
                client_socket.send(json.dumps(wallet_data).encode('utf-8'))

                # Alpha Block oluşturma
                prev_normal_hash, prev_security_hash = get_previous_hashes()  # Önceki hash'leri al
                alpha_block = AlphaBlock(
                    previous_hash=prev_normal_hash,  # Beta Block'un hash'i
                    sender="SYSTEM",  # Cüzdan oluşturma işlemi sistem tarafından yapıldı
                    recipient=new_wallet.address,    # Cüzdan adresi
                    amount="0",                      # Cüzdan oluşturma işlemi için amount=0
                    tag="wallet"                     # Tag="wallet"
                )

                # Alpha Block'u kaydet
                alpha_num = get_next_block_number("alpha")
                alpha_filename = os.path.join(DATA_DIR, f"alpha{alpha_num}.json")
                with open(alpha_filename, "w") as f:
                    json.dump(alpha_block.to_dict(), f, indent=4)
                print(f"✅ Alpha Block kaydedildi: {alpha_filename}")

                # Security Block oluşturma
                security_block = SecurityBlock(prev_security_hash)
                security_num = get_next_block_number("security")
                security_filename = os.path.join(DATA_DIR, f"security{security_num}.json")
                with open(security_filename, "w") as f:
                    json.dump(security_block.to_dict(), f, indent=4)
                print(f"✅ Security Block kaydedildi: {security_filename}")

                # Beta Block oluşturma
                beta_block = BetaBlock(
                    prev_alpha_hash=alpha_block.block_hash,
                    prev_security_hash=security_block.security_hash
                )
                beta_num = get_next_block_number("beta")
                beta_filename = os.path.join(DATA_DIR, f"beta{beta_num}.json")
                with open(beta_filename, "w") as f:
                    json.dump(beta_block.to_dict(), f, indent=4)
                print(f"✅ Beta Block oluşturuldu ve kaydedildi: {beta_filename}")
                continue
                
            # server.py'de "REQUEST_AIRDROP" işlemi içine ekleyin:
            if message == "REQUEST_AIRDROP":
                print("🪂 Airdrop talebi alındı.")
                
                # Genesis Block'dan airdrop rezervini al
                with open(GENESIS_BLOCK_FILE, "r") as f:
                    genesis_data = json.load(f)
                airdrop_reserve = genesis_data.get("airdrop_reserve", 0)  # Varsayılan değer 0

                if airdrop_reserve >= 1:
                    # Airdrop rezervini güncelle
                    genesis_data["airdrop_reserve"] -= 1
                    with open(GENESIS_BLOCK_FILE, "w") as f:
                        json.dump(genesis_data, f, indent=4)

                    # Alıcının adresini istemciden al (örneğin, airdrop isteği yapanın adresi)
                    client_socket.send("AIRDROP_RECIPIENT_REQUEST".encode('utf-8'))
                    recipient_address = client_socket.recv(1024).decode('utf-8')  # Client'ın yanıtını bekleyin

                    # Alıcının cüzdanını güncelle
                    recipient_path = os.path.join(WALLETS_DIR, f"{recipient_address}.json")
                    if os.path.exists(recipient_path):
                        with open(recipient_path, "r") as f:
                            recipient_data = json.load(f)
                        recipient_data["baklava_balance"][BAKLAVA_TOKEN_ID] += 1
                    else:
                        recipient_data = {
                            "address": recipient_address,
                            "baklava_balance": {BAKLAVA_TOKEN_ID: 1}
                        }

                    with open(recipient_path, "w") as f:
                        json.dump(recipient_data, f, indent=4)

                    # Blokları oluştur ve kaydet
                    prev_normal_hash, prev_security_hash = get_previous_hashes()
                    alpha_block = AlphaBlock(
                        previous_hash=prev_normal_hash,  # Önceki bloğun hash'i
                        sender="AIRDROP_SYSTEM",  # Airdrop sistem tarafından yapıldı
                        recipient=recipient_address,  # Alıcı adresi
                        amount="1",  # Airdrop miktarı
                        tag="airdrop"  # İşlem türü
                    )
                    security_block = SecurityBlock(prev_security_hash)

                    # Alpha ve Security Block'ları kaydet
                    alpha_num = get_next_block_number("alpha")
                    security_num = get_next_block_number("security")

                    alpha_filename = os.path.join(DATA_DIR, f"alpha{alpha_num}.json")
                    security_filename = os.path.join(DATA_DIR, f"security{security_num}.json")

                    with open(alpha_filename, "w") as f:
                        json.dump(alpha_block.to_dict(), f, indent=4)
                    with open(security_filename, "w") as f:
                        json.dump(security_block.to_dict(), f, indent=4)

                    print(f"✅ Alpha Block kaydedildi: {alpha_filename}")
                    print(f"✅ Security Block kaydedildi: {security_filename}")

                    # Düzeltilmiş hali:
                    beta_block = BetaBlock(
                        prev_alpha_hash=alpha_block.block_hash,
                        prev_security_hash=security_block.security_hash
                    )
                    beta_num = get_next_block_number("beta")
                    beta_filename = os.path.join(DATA_DIR, f"beta{beta_num}.json")
                    with open(beta_filename, "w") as f:
                        json.dump(beta_block.to_dict(), f, indent=4)

                    print(f"✅ Beta Block oluşturuldu ve kaydedildi: {beta_filename}")

                    # İstemciye başarılı yanıt gönder
                    response = {
                        "status": "success",
                        "message": "Airdrop successful! 1 Baklava added to your wallet."
                    }
                    client_socket.send(json.dumps(response).encode('utf-8'))
                else:
                    # Airdrop rezervi yetersiz
                    response = {
                        "status": "error",
                        "message": "Insufficient airdrop reserve."
                    }
                    client_socket.send(json.dumps(response).encode('utf-8'))
                continue

            try:
                data = json.loads(message)
                
                # server.py'de transfer işlemi sırasında:

                if data.get("action") == "transfer":
                    sender = data["sender"]
                    recipient = data["recipient"]
                    amount = data["amount"]
                    tag = data.get("tag", "transfer")  # Default tag is "transfer"

                    sender_path = os.path.join(WALLETS_DIR, f"{sender}.json")
                    with open(sender_path, "r") as f:
                        sender_data = json.load(f)
                    
                    # Check if sender has enough balance for the amount
                    if sender_data["baklava_balance"].get(BAKLAVA_TOKEN_ID, 0) < amount:
                        client_socket.send(json.dumps({"status": "error", "message": "Yetersiz bakiye"}).encode())
                        continue

                    transfer_fee = 0
                    recipient_receives = amount

                    # Calculate fee if tag is "transfer"
                    if tag == "transfer":
                        current_beta_blocks = len([f for f in os.listdir(DATA_DIR) if f.startswith("beta")])
                        transfer_fee = calculate_transfer_fee(current_beta_blocks)
                        
                        if amount < transfer_fee:
                            client_socket.send(json.dumps({"status": "error", "message": "Transfer miktarı ücretten küçük"}).encode())
                            continue
                        
                        recipient_receives = amount - transfer_fee

                    # Deduct the full amount from sender
                    sender_data["baklava_balance"][BAKLAVA_TOKEN_ID] -= amount
                    with open(sender_path, "w") as f:
                        json.dump(sender_data, f, indent=4)

                    # Update recipient's balance
                    recipient_path = os.path.join(WALLETS_DIR, f"{recipient}.json")
                    if os.path.exists(recipient_path):
                        with open(recipient_path, "r") as f:
                            recipient_data = json.load(f)
                        recipient_data["baklava_balance"][BAKLAVA_TOKEN_ID] = recipient_data["baklava_balance"].get(BAKLAVA_TOKEN_ID, 0) + recipient_receives
                    else:
                        recipient_data = {
                            "address": recipient,
                            "baklava_balance": {BAKLAVA_TOKEN_ID: recipient_receives}
                        }

                    with open(recipient_path, "w") as f:
                        json.dump(recipient_data, f, indent=4)

                    # Transfer fee to foundation if applicable
                    if transfer_fee > 0:
                        transfer_fee_to_foundation(transfer_fee)
                        print(f"💸 Transfer ücreti ({transfer_fee}) Baklava Foundation cüzdanına aktarıldı.")

                    # Alıcının bakiyesini güncelle
                    recipient_path = os.path.join(WALLETS_DIR, f"{recipient}.json")
                    if os.path.exists(recipient_path):
                        with open(recipient_path, "r") as f:
                            recipient_data = json.load(f)
                        recipient_data["baklava_balance"][BAKLAVA_TOKEN_ID] = recipient_data["baklava_balance"].get(BAKLAVA_TOKEN_ID, 0) + amount
                    else:
                        recipient_data = {
                            "address": recipient,
                            "baklava_balance": {BAKLAVA_TOKEN_ID: amount}
                        }

                    with open(recipient_path, "w") as f:
                        json.dump(recipient_data, f, indent=4)
                                        
                    # Blokları oluştur ve kaydet
                    prev_hashes = get_previous_hashes()
                    alpha_block = AlphaBlock(
                        previous_hash=prev_hashes[0],  # Önceki bloğun hash'i
                        sender=sender,  # Gönderen adresi
                        recipient=recipient,  # Alıcı adresi
                        amount=amount,  # Transfer miktarı
                        tag=tag  # İşlem türü
                    )
                    security_block = SecurityBlock(prev_hashes[1])
                    
                    # Düzeltilmiş hali:
                    beta_block = BetaBlock(
                        prev_alpha_hash=alpha_block.block_hash,
                        prev_security_hash=security_block.security_hash
                    )
                    
                    # Blokları kaydet
                    save_block(alpha_block, "alpha")
                    save_block(security_block, "security")
                    save_block(beta_block, "beta")
                    
                    response = {
                        "status": "success",
                        "message": "Transfer başarılı",
                        "sender_balance": sender_data["baklava_balance"].get(BAKLAVA_TOKEN_ID, 0),
                        "recipient_balance": recipient_data["baklava_balance"].get(BAKLAVA_TOKEN_ID, 0),
                        "transfer_fee": transfer_fee if tag == "transfer" else 0  # Ücret bilgisini ekle
                    }
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    continue
                    
                # server.py'deki "get_balance" işlemini bu şekilde güncelleyin:

                elif data.get("action") == "get_balance":
                    address = data["address"]
                    wallet_path = os.path.join(WALLETS_DIR, f"{address}.json")
                    
                    if not os.path.exists(wallet_path):
                        # Eğer wallet.json ana dizinde varsa onu kullan
                        main_wallet_path = os.path.join(os.getcwd(), "wallet.json")
                        if os.path.exists(main_wallet_path):
                            shutil.copy(main_wallet_path, wallet_path)  # Sunucuya kopyala
                    
                    if os.path.exists(wallet_path):
                        try:
                            with open(wallet_path, "r") as f:
                                wallet_data = json.load(f)
                            client_socket.send(json.dumps({"status": "success", "balance": wallet_data["baklava_balance"]}).encode())
                        except Exception as e:
                            client_socket.send(json.dumps({"status": "error", "message": f"Cüzdan okunurken hata: {e}"}).encode())
                    else:
                        client_socket.send(json.dumps({"status": "error", "message": "Cüzdan bulunamadı"}).encode())
                    continue
                                   
                # Alpha ve Security bloklarını içeren transfer işlemi kontrolü
                elif data.get("action") == "transfer":
                    print("💸 Transfer talebi alındı.")
                    alpha_data = data.get("alpha")
                    security_data = data.get("security")
                    if not alpha_data or not security_data:
                        client_socket.send("Eksik blok verisi".encode('utf-8'))
                        continue

                    # Alpha ve Security bloklarını DATA klasörüne kaydet
                    alpha_num = get_next_block_number("alpha")
                    security_num = get_next_block_number("security")

                    alpha_filename = os.path.join(DATA_DIR, f"alpha{alpha_num}.json")
                    security_filename = os.path.join(DATA_DIR, f"security{security_num}.json")

                    with open(alpha_filename, "w") as f:
                        json.dump(alpha_data, f, indent=4)
                    with open(security_filename, "w") as f:
                        json.dump(security_data, f, indent=4)

                    print(f"✅ Alpha Block kaydedildi: {alpha_filename}")
                    print(f"✅ Security Block kaydedildi: {security_filename}")

                    # Beta Block oluşturma
                    prev_alpha_hash = alpha_data.get("block_hash")
                    prev_security_hash = security_data.get("security_hash")
                    beta_block = BetaBlock(prev_alpha_hash, prev_security_hash)
                    beta_data = beta_block.to_dict()

                    beta_num = get_next_block_number("beta")
                    beta_filename = os.path.join(DATA_DIR, f"beta{beta_num}.json")
                    with open(beta_filename, "w") as f:
                        json.dump(beta_data, f, indent=4)

                    print(f"✅ Beta Block oluşturuldu ve kaydedildi: {beta_filename}")
                    client_socket.send(json.dumps(beta_data).encode('utf-8'))
                    continue
                else:
                    print(f"📩 {client_address} mesaj gönderdi: {message}")
            except json.JSONDecodeError:
                if message.startswith('TRANSFER|'):
                    print(f"💸 Transfer talebi alındı: {message}")
                else:
                    print(f"📩 {client_address} mesaj gönderdi: {message}")
                
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        print(f"❌ {client_address} bağlantısı kesildi.")
        client_socket.close()

def save_block(block, prefix):
    block_num = get_next_block_number(prefix)
    filename = os.path.join(DATA_DIR, f"{prefix}{block_num}.json")
    with open(filename, "w") as f:
        json.dump(block.to_dict(), f, indent=4)

def start_server():
    host = '192.168.1.106'  # Sunucunun IP adresi
    port = 5555             # Sunucunun portu
    
    # Sunucu durumunu yükle
    load_server_state()
    print(f"🌍 Loaded server state: Global Difficulty={GLOBAL_MINING_DIFFICULTY}, Daily Blocks={DAILY_BETA_BLOCKS}")
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"🌐 Sunucu {host}:{port} üzerinde çalışıyor...")

    ensure_data_dir()
    create_genesis_block()

    # Baklava Foundation cüzdanını kontrol et ve yoksa oluştur
    foundation_wallet = BaklavaFoundationWallet.load_wallet()
    if not os.path.exists("baklava_foundation_wallet.json"):
        foundation_wallet.save_wallet()
        print("✅ Baklava Foundation cüzdanı oluşturuldu ve kaydedildi.")

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()
