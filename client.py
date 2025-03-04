import socket
import sys
import os
import hashlib
import shutil
import time

def calculate_file_hash(filename):
    """Dosyanın hash'ini hesapla"""
    if not os.path.exists(filename):
        return None
    
    hasher = hashlib.md5()
    with open(filename, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def safe_update_client():
    try:
        host = '192.168.1.106'
        port = 5555

        # Güncelleme için ayrı bir soket oluştur
        update_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        update_socket.connect((host, port))

        # Güncelleme isteğini belirt
        update_socket.send('GET_UPDATE'.encode('utf-8'))

        # Geçerli client.py'nin hash'ini al
        old_hash = calculate_file_hash('client.py')

        # Yeni client dosyasını geçici olarak kaydet
        with open('client_new.py', 'wb') as file:
            while True:
                data = update_socket.recv(1024)
                if not data:
                    break
                file.write(data)

        update_socket.close()

        # Yeni dosyanın hash'ini hesapla
        new_hash = calculate_file_hash('client_new.py')

        # Eğer hash'ler aynıysa güncelleme gereksiz, dosyayı sil
        if old_hash == new_hash:
            os.remove('client_new.py')  # Gereksiz dosyayı sil
            print("✅ Client zaten güncel.")
            return False

        # Önceki güncellemelerden kalan client_old.py varsa sil
        if os.path.exists('client_old.py'):
            os.remove('client_old.py')

        # Eski client.py'yi yedekle
        if os.path.exists('client.py'):
            shutil.move('client.py', 'client_old.py')

        # Yeni dosyayı client.py olarak kaydet
        shutil.move('client_new.py', 'client.py')

        print("✅ Client başarıyla güncellendi!")
        return True  # Güncelleme yapıldı

    except Exception as e:
        print(f"❌ Güncelleme hatası: {e}")
        # Yedeklenen dosyayı geri yükle
        if os.path.exists('client_old.py'):
            shutil.move('client_old.py', 'client.py')
        return False  # Güncelleme başarısız

def transfer_menu(client_socket):
    while True:
        print("\n--- TRANSFER MENÜSÜ ---")
        print("1. Test Transfer İşlemi")
        print("2. Geri Dön")
        
        secim = input("Seçiminizi yapın: ")
        
        if secim == '1':
            print("\n🔄 Transfer işlemi test aşamasında...")
            alici = input("Alıcı adresini girin: ")
            miktar = input("Transfer miktarını girin: ")
            
            # Basit bir test mesajı gönderme
            transfer_mesaji = f"TRANSFER|{alici}|{miktar}"
            client_socket.send(transfer_mesaji.encode('utf-8'))
            
            print(f"✉️ Transfer talebi gönderildi: {transfer_mesaji}")
            input("Devam etmek için ENTER'a basın...")
        
        elif secim == '2':
            return
        
        else:
            print("Geçersiz seçim. Lütfen tekrar deneyin.")

def start_client():
    host = '192.168.1.106'
    port = 5555

    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            print(f"✅ Sunucuya bağlandınız: {host}:{port}")

            # Bağlantı kurulduktan sonra sunucunun gönderdiği ilk mesajı alıyoruz.
            update_status = client_socket.recv(1024).decode('utf-8')
            if update_status != "UPDATE_NOT_NEEDED":
                print("Güncelleme mesajı:", update_status)
            break  # Bağlantı başarılı olunca döngüden çık

        except ConnectionRefusedError:
            print("❌ Sunucu şu anda kapalı, lütfen daha sonra tekrar deneyiniz.")
            time.sleep(5)  # 5 saniye bekleyip tekrar dene
        except Exception as e:
            print(f"❌ Hata oluştu: {e}")
            time.sleep(5)

    # Bağlantıyı sürekli kontrol eden döngü
    try:
        while True:
            print("\n--- ANA MENÜ ---")
            print("1. Mesaj Gönder")
            print("2. Madencilik")
            print("3. Transfer")
            print("4. Çıkış")

            secim = input("Seçiminizi yapın: ")

            if secim == '1':
                while True:
                    message = input("Mesaj gönder (çıkış için 'back'): ")
                    if message.lower() == 'back':
                        break
                    client_socket.send(message.encode('utf-8'))
                    print(f"Mesaj gönderildi: {message}")

            elif secim == '2':
                mine_menu(client_socket)

            elif secim == '3':
                transfer_menu(client_socket)

            elif secim == '4':
                break

            else:
                print("Geçersiz seçim. Lütfen tekrar deneyin.")

            # Sunucunun hâlâ bağlı olup olmadığını kontrol et
            client_socket.send(b'PING')
            time.sleep(2)

    except (ConnectionResetError, BrokenPipeError):
        print("❌ Sunucu bağlantısı kesildi! Sunucu şu an kapalı bulunmakta, lütfen sonra tekrar deneyiniz.")
        time.sleep(5)
        start_client()  # Sunucu yeniden açılınca otomatik bağlan

    finally:
        client_socket.close()

def mine_menu(client_socket):
    while True:
        print("\n--- MADENCİLİK MENÜSÜ ---")
        print("1. Mine İşlemi Başlat")
        print("2. Geri Dön")
        
        secim = input("Seçiminizi yapın: ")
        
        if secim == '1':
            print("\n🚧 Madencilik işlemi henüz geliştirilme aşamasında.")
            print("Bu bir demo ekranıdır. Gerçek madencilik işlemleri yapılmamaktadır.")
            input("Devam etmek için ENTER'a basın...")
        
        elif secim == '2':
            return
        
        else:
            print("Geçersiz seçim. Lütfen tekrar deneyin.")

# Güncelleme kontrolü
if __name__ == "__main__":
    updated = safe_update_client()  # Güncelleme olup olmadığını kontrol et

    if updated:
        print("🔄 Güncelleme tamamlandı, istemci yeniden başlatılıyor...\n")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    print("🚀 Client başlatılıyor...\n")
    start_client()