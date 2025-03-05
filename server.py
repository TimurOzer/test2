import socket
import threading
import os
import json
from genesis_block import GenesisBlock  # Genesis Block sınıfını içe aktar

GENESIS_BLOCK_FILE = "genesis_block.json"

def create_genesis_block():
    """Eğer genesis_block.json yoksa, yeni bir Genesis Block oluşturur."""
    if not os.path.exists(GENESIS_BLOCK_FILE):
        print("🔧 Genesis Block bulunamadı, oluşturuluyor...")
        TOKEN_ADDRESS = "bklvdc38569a110702c2fed1164021f0539df178"
        MAX_SUPPLY = 100_000_000

        genesis_block = GenesisBlock(TOKEN_ADDRESS, MAX_SUPPLY)
        genesis_block.mine_block()

        # Genesis bloğunu kaydet
        with open(GENESIS_BLOCK_FILE, "w") as f:
            json.dump(genesis_block.to_dict(), f, indent=4)

        print("✅ Genesis Block başarıyla oluşturuldu ve kaydedildi!")
    else:
        print("📜 Genesis Block zaten mevcut, yeniden oluşturulmadı.")

def handle_client(client_socket, client_address):
    print(f"🔗 {client_address} bağlandı.")
    
    try:
        # Güncelleme isteği kontrolü
        update_request = client_socket.recv(1024).decode('utf-8')
        
        if update_request == 'GET_UPDATE':
            # Client.py dosyasını gönder
            with open('client.py', 'rb') as file:
                client_socket.sendfile(file)
            print(f"📦 {client_address} için client.py güncellendi.")
            client_socket.close()
            return
        
        client_socket.send('UPDATE_NOT_NEEDED'.encode('utf-8'))
        
        # Normal mesaj alışverişi
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            
            if not message:
                break
            
            # Transfer işlemi kontrolü
            if message.startswith('TRANSFER|'):
                print(f"💸 Transfer talebi alındı: {message}")
                # Burada transfer işlemleri için gerekli mantık eklenecek
            else:
                print(f"📩 {client_address} mesaj gönderdi: {message}")
                # Sunucuya gelen mesaj anında işlenir ve ekrana yazılır.
    
    except Exception as e:
        print(f"❌ Hata: {e}")
    
    finally:
        print(f"❌ {client_address} bağlantısı kesildi.")
        client_socket.close()

def start_server():
    host = '192.168.1.106'
    port = 5555

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"🌐 Sunucu {host}:{port} üzerinde çalışıyor...")

    # Genesis Block'un ilk çalıştırmada oluşturulmasını sağla
    create_genesis_block()

    while True:
        client_socket, client_address = server_socket.accept()
        
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()
