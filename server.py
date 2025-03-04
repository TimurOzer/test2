import socket
import threading
import os

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

    while True:
        client_socket, client_address = server_socket.accept()
        
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()