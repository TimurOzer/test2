import socket
import sys
import os
import hashlib
import shutil
import random
import time
import json
from wallet import BAKLAVA_TOKEN_ID  # Bu satırı ekleyin

# Sabit Genesis hash değerleri (uygulamanıza göre güncellenmeli)
GENESIS_NORMAL_HASH = "00002b0487c6a824a33b529bdff43c940c1874e1910a187f85691cdff7a69eda"
GENESIS_SECURITY_HASH = "4a4487b1e40eab0c026f03ea8cdab942ec9d5fe2d1b64ddf666ffc91f5c87f30"

# İlgili blok sınıflarını import ediyoruz
from alpha_block import AlphaBlock
from security_block import SecurityBlock

def get_previous_hashes():
    # Eğer latest_block.json varsa, son Beta Block'un hash'lerini al
    if os.path.exists('latest_block.json'):
        with open('latest_block.json', 'r') as f:
            latest = json.load(f)
        prev_normal_hash = latest.get("alpha_hash")
        prev_security_hash = latest.get("security_hash")
    else:
        prev_normal_hash = GENESIS_NORMAL_HASH
        prev_security_hash = GENESIS_SECURITY_HASH
    return prev_normal_hash, prev_security_hash

def calculate_file_hash(filename):
    """Calculate the hash of a file"""
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

        # Create a separate socket for updates
        update_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        update_socket.connect((host, port))

        # Send update request
        update_socket.send('GET_UPDATE'.encode('utf-8'))

        # Get current client.py hash
        old_hash = calculate_file_hash('client.py')

        # Save the new client file temporarily
        with open('client_new.py', 'wb') as file:
            while True:
                data = update_socket.recv(1024)
                if not data:
                    break
                file.write(data)

        update_socket.close()

        # Calculate new file hash
        new_hash = calculate_file_hash('client_new.py')

        # If hashes match, update is unnecessary, delete the file
        if old_hash == new_hash:
            os.remove('client_new.py')
            print("✅ Client is already up to date.")
            return False

        # Remove previous update backup if exists
        if os.path.exists('client_old.py'):
            os.remove('client_old.py')

        # Backup the old client.py
        if os.path.exists('client.py'):
            shutil.move('client.py', 'client_old.py')

        # Replace with the new client.py
        shutil.move('client_new.py', 'client.py')

        print("✅ Client successfully updated!")
        return True  # Update performed

    except Exception as e:
        print(f"❌ Update error: {e}")
        # Restore backup if update fails
        if os.path.exists('client_old.py'):
            shutil.move('client_old.py', 'client.py')
        return False

# client.py'de transfer_menu fonksiyonunda:
def transfer_menu(client_socket):
    print("\n--- TRANSFER MENU ---")
    recipient = input("Alıcı adresi: ")
    amount = float(input("Miktar: "))

    # Cüzdan bilgilerini yükle
    with open("wallet.json", "r") as f:
        wallet_data = json.load(f)
    
    # Transfer verisini hazırla
    transfer_data = {
        "action": "transfer",
        "sender": wallet_data["address"],
        "recipient": recipient,
        "amount": amount
    }
    
    # Sunucuya gönder
    client_socket.send(json.dumps(transfer_data).encode())
    
    # Yanıtı al
    response = client_socket.recv(4096).decode()
    if not response.strip():
        print("❌ Sunucudan boş yanıt alındı.")
        return
    
    try:
        response_data = json.loads(response)
        if response_data.get("status") == "success":
            print(f"✅ Transfer başarılı! Yeni bakiyeniz: {response_data.get('sender_balance', 0)}")
        else:
            print(f"❌ Transfer başarısız: {response_data.get('message', 'Bilinmeyen hata')}")
    except json.JSONDecodeError:
        print(f"❌ Geçersiz yanıt: {response}")


def start_client():
    host = '192.168.1.106'
    port = 5555

    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            print(f"✅ Connected to server: {host}:{port}")

            # El sıkışma mesajı
            client_socket.send("HELLO".encode('utf-8'))

            # Sunucudan güncelleme durumunu al
            update_status = client_socket.recv(1024).decode('utf-8')
            if update_status != "UPDATE_NOT_NEEDED":
                print("Güncelleme mesajı:", update_status)
            break

        except ConnectionRefusedError:
            print("❌ Sunucu şu anda kapalı, lütfen daha sonra tekrar deneyin.")
            time.sleep(5)
        except Exception as e:
            print(f"❌ Hata oluştu: {e}")
            time.sleep(5)

    # Yeni eklenen cüzdan kontrolü
    if not os.path.exists("wallet.json"):
        print("\n⚠️ Cüzdan bulunamadı!")
        create_choice = input("Yeni cüzdan oluşturmak istiyor musunuz? (E/H): ").strip().lower()
        if create_choice == 'e':
            wallet_menu(client_socket)  # Cüzdan oluşturma menüsüne yönlendir
        else:
            print("❌ Cüzdan olmadan devam edilemez. Çıkılıyor...")
            client_socket.close()
            sys.exit()

    # Continuous connection loop
    try:
        while True:
            print("\n--- MAIN MENU ---")
            print("1. Send Message")
            print("2. Mining")
            print("3. Transfer")
            print("4. Airdrop")
            print("5. Wallet")
            print("6. Balance")
            print("7. Account")
            print("8. Server")
            print("9. Server Status")
            print("10. Exit")

            choice = input("Enter your choice: ")

            if choice == '1':
                while True:
                    message = input("Enter message (type 'back' to exit): ")
                    if message.lower() == 'back':
                        break
                    client_socket.send(message.encode('utf-8'))
                    print(f"Message sent: {message}")

            elif choice == '2':
                mine_menu(client_socket)

            elif choice == '3':
                transfer_menu(client_socket)

            elif choice == '4':
                airdrop_menu(client_socket)

            elif choice == '5':
                wallet_menu(client_socket)

            elif choice == '6':
                balance_menu(client_socket)

            elif choice == '7':
                account_menu(client_socket)

            elif choice == '8':
                server_menu(client_socket)

            elif choice == '9':
                server_status(client_socket)

            elif choice == '10':
                break

            else:
                print("Invalid choice. Please try again.")

            # Check if the connection is still active
            client_socket.send(b'PING')
            time.sleep(2)

    except (ConnectionResetError, BrokenPipeError):
        print("❌ Server connection lost! Please try again later.")
        time.sleep(5)
        start_client()

    finally:
        client_socket.close()


def server_status(client_socket):
    print("\n--- SERVER STATUS ---")
    print("This feature is still under development.")
    input("Press ENTER to continue...")

def server_menu(client_socket):
    print("\n--- SERVER MENU ---")
    print("This feature is still under development.")
    input("Press ENTER to continue...")

def account_menu(client_socket):
    print("\n--- ACCOUNT MENU ---")
    print("This feature is still under development.")
    input("Press ENTER to continue...")

# client.py
# client.py'deki balance_menu fonksiyonunu bu şekilde düzenleyin:

def balance_menu(client_socket):
    # Yerel cüzdanı yükle
    try:
        with open("wallet.json", "r") as f:
            wallet_data = json.load(f)
        client_address = wallet_data["address"]
    except FileNotFoundError:
        print("❌ Cüzdan dosyası bulunamadı. Önce cüzdan oluşturun!")
        input("Devam etmek için ENTER'a basın...")
        return

    # Sunucudan güncel bakiyeyi iste
    client_socket.send(json.dumps({
        "action": "get_balance",
        "address": client_address
    }).encode())

    # Sunucu yanıtını al
    response = client_socket.recv(4096).decode()
    print(f"Sunucudan gelen yanıt: {response}")  # Debug için

    if not response.strip():
        print("❌ Sunucudan boş yanıt alındı.")
        input("Devam etmek için ENTER'a basın...")
        return

    try:
        response_data = json.loads(response)
        
        if response_data.get("status") == "success":
            server_balance = response_data["balance"].get(BAKLAVA_TOKEN_ID, 0)
            
            # Yerel cüzdanı güncelle
            wallet_data["baklava_balance"][BAKLAVA_TOKEN_ID] = server_balance
            with open("wallet.json", "w") as f:
                json.dump(wallet_data, f, indent=4)
            
            print(f"✅ Güncel Bakiye: {server_balance} BAKL")
        
        elif response_data.get("message") == "Cüzdan bulunamadı":
            print("❌ Sunucuda cüzdanınız bulunamadı! Yeni cüzdan oluşturun.")
            if os.path.exists("wallet.json"):
                os.remove("wallet.json")
        
        else:
            print(f"❌ Hata: {response_data.get('message', 'Bilinmeyen hata')}")
    
    except json.JSONDecodeError as e:
        print(f"❌ Geçersiz sunucu yanıtı: {e}")
        print(f"Alınan yanıt: {response}")
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")

    input("Devam etmek için ENTER'a basın...")

def wallet_menu(client_socket):
    # Eğer cüzdan zaten varsa uyarı ver
    if os.path.exists("wallet.json"):
        print("\n⚠️ Zaten bir cüzdanınız var!")
        choice = input("Yeni cüzdan oluşturmak istiyor musunuz? (Eski cüzdan SİLİNECEK!) (E/H): ")
        if choice.lower() != 'e':
            return

    # Mevcut cüzdanı sil (varsa)
    if os.path.exists("wallet.json"):
        os.remove("wallet.json")
    
    # Yeni cüzdan oluştur
    print("\n🔐 Sunucuda yeni cüzdan oluşturuluyor...")
    client_socket.send("CREATE_WALLET".encode('utf-8'))
    wallet_response = client_socket.recv(4096).decode('utf-8')
    
    # Yanıtın boş olup olmadığını kontrol et
    if not wallet_response.strip():
        print("❌ Sunucudan boş yanıt alındı.")
        input("Press ENTER to continue...")
        return
    
    try:
        wallet_data = json.loads(wallet_response)
        # Hata mesajı kontrolü
        if "status" in wallet_data and wallet_data["status"] == "error":
            print(f"❌ {wallet_data['message']}")
            input("Press ENTER to continue...")
            return
            
        with open("wallet.json", "w") as f:
            json.dump(wallet_data, f, indent=4)
        print("🏦 Wallet created and saved as wallet.json")
        print("Address:", wallet_data.get("address"))
    except json.JSONDecodeError as e:
        print(f"❌ Geçersiz yanıt: {e}")
        print("Alınan yanıt:", wallet_response)
    except Exception as e:
        print(f"❌ Hata: {e}")
    input("Press ENTER to continue...")

# client.py'de airdrop_menu fonksiyonunu düzenleyin:

# client.py'de airdrop_menu fonksiyonunu güncelleyin:

def airdrop_menu(client_socket):
    print("\n--- AIRDROP MENU ---")
    print("1. Request Airdrop")
    print("2. Go Back")

    choice = input("Enter your choice: ")

    if choice == '1':
        print("\n🪂 Airdrop requested...")
        # Sunucuya airdrop isteği gönder
        client_socket.send("REQUEST_AIRDROP".encode('utf-8'))

        # Sunucudan gelen yanıtı al
        response = client_socket.recv(4096).decode('utf-8')
        print(f"Sunucudan gelen yanıt: {response}")  # Debug için

        if response == "AIRDROP_RECIPIENT_REQUEST":
            # Sunucuya alıcı adresini gönder (kendi cüzdan adresiniz)
            with open("wallet.json", "r") as f:
                wallet_data = json.load(f)
            client_socket.send(wallet_data["address"].encode('utf-8'))

            # Airdrop başarılı mesajını al
            response = client_socket.recv(4096).decode('utf-8')
            print(f"Sunucudan gelen yanıt: {response}")  # Debug için

            try:
                response_data = json.loads(response)
                if response_data.get("status") == "success":
                    print("🎉 Airdrop successful! 1 Baklava added to your wallet.")
                    # Yerel cüzdanı güncelle (isteğe bağlı, sunucu zaten güncelledi)
                    wallet_data["baklava_balance"][BAKLAVA_TOKEN_ID] += 1
                    with open("wallet.json", "w") as f:
                        json.dump(wallet_data, f, indent=4)
                else:
                    print("❌ Airdrop failed:", response_data.get("message"))
            except json.JSONDecodeError:
                print("❌ Geçersiz sunucu yanıtı.")
        else:
            print("❌ Beklenmeyen sunucu yanıtı:", response)

        input("Press ENTER to continue...")

def mine_menu(client_socket):
    print("\n--- MINING MENU ---")
    client_socket.send("GET_MINING_INFO".encode())
    mining_info = json.loads(client_socket.recv(4096).decode())
    
    # Cüzdanı yükle
    with open("wallet.json", "r") as f:
        wallet = json.load(f)
    
    print(f"🔨 Current Difficulty: {mining_info['difficulty']} (0'lar)")
    print(f"🌍 Global Difficulty: {mining_info['global_difficulty']}")
    print(f"💰 Block Reward: {mining_info['reward']:.2f} BAKL")
    
    if input("Start mining? (y/n): ").lower() != 'y':
        return
    
    print("⛏️ Mining started... (Press CTRL+C to stop)")
    start_time = time.time()
    nonce = random.randint(1, 10**mining_info['difficulty'])  # Rastgele başlangıç
    
    try:
        while True:
            # Hash hesapla
            hash_attempt = hashlib.sha256(f"{nonce}{mining_info['difficulty']}".encode()).hexdigest()
            
            if hash_attempt.startswith('0' * mining_info['difficulty']):
                print(f"✅ Valid nonce found: {nonce} | Hash: {hash_attempt}")
                client_socket.send(f"SUBMIT_MINING|{wallet['address']}|{nonce}".encode())
                result = client_socket.recv(1024).decode()
                print("🏆 Mining successful!" if result == "MINING_SUCCESS" else "❌ Failed")
                return
                
            nonce += 1
            
            # Her 10000 denemede bir ilerleme göster
            if nonce % 10000 == 0:
                elapsed = time.time() - start_time
                print(f"⏳ Hashes: {nonce} | Speed: {nonce/elapsed:.2f} H/s | Elapsed: {elapsed:.1f}s")
                
    except KeyboardInterrupt:
        print("⏹ Mining stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
    except socket.timeout:
        print("❌ Server did not respond in time.")
    except json.JSONDecodeError:
        print("❌ Invalid response from server")

# Check for updates
if __name__ == "__main__":
    updated = safe_update_client()

    if updated:
        print("🔄 Update completed, restarting client...\n")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    print("🚀 Starting client...\n")
    start_client()
