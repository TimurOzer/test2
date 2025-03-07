import socket
import threading
import os
import json
from genesis_block import GenesisBlock, TOKEN_ADDRESS, MAX_SUPPLY  # Genesis Block sınıfı ve sabitler

# Yeni blok sınıflarını import ediyoruz
from alpha_block import AlphaBlock
from security_block import SecurityBlock
from beta_block import BetaBlock

DATA_DIR = "data"  # Veri klasörü
GENESIS_BLOCK_FILE = os.path.join(DATA_DIR, "genesis_block.json")  # Dosya yolu

def ensure_data_dir():
    """Eğer data klasörü yoksa, oluşturur."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"📁 '{DATA_DIR}' klasörü oluşturuldu.")

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

def send_prev_hashes(client_socket):
    # Beta blok sayısını kontrol edelim
    beta_num = get_next_block_number("beta") - 1
    if beta_num < 1:
        # Henüz beta yoksa, Genesis'den al
        with open(GENESIS_BLOCK_FILE, "r") as f:
            genesis_data = json.load(f)
        prev_normal = genesis_data.get("block_hash")
        prev_security = genesis_data.get("security_hash")
    else:
        # En son beta blok dosyasını oku
        beta_filename = os.path.join(DATA_DIR, f"beta{beta_num}.json")
        with open(beta_filename, "r") as f:
            beta_data = json.load(f)
        prev_normal = beta_data.get("alpha_hash")
        prev_security = beta_data.get("security_hash")
    
    response = {
        "prev_normal_hash": prev_normal,
        "prev_security_hash": prev_security
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
            if message == "GET_PREV_HASHES":
                send_prev_hashes(client_socket)
                continue  # veya döngüden çıkmadan diğer mesajları bekleyin
            if not message:
                break

            # Transfer işlemi kontrolü
            try:
                data = json.loads(message)
                if data.get("action") == "transfer":
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
                    alpha_hash = alpha_data.get("block_hash")
                    security_hash = security_data.get("security_hash")
                    beta_block = BetaBlock(alpha_hash, security_hash)
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
                # Gelen mesaj JSON değilse, eski yöntemle kontrol edilebilir
                if message.startswith('TRANSFER|'):
                    print(f"💸 Transfer talebi alındı: {message}")
                else:
                    print(f"📩 {client_address} mesaj gönderdi: {message}")
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        print(f"❌ {client_address} bağlantısı kesildi.")
        client_socket.close()

def start_server():
    host = '192.168.1.106'  # Sunucunun IP adresi
    port = 5555             # Sunucunun portu

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"🌐 Sunucu {host}:{port} üzerinde çalışıyor...")

    ensure_data_dir()
    create_genesis_block()

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()
