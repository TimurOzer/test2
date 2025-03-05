import socket
import sys
import os
import hashlib
import shutil
import time

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

def transfer_menu(client_socket):
    while True:
        print("\n--- TRANSFER MENU ---")
        print("1. Test Transfer")
        print("2. Go Back")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            print("\n🔄 Transfer process is under testing...")
            recipient = input("Enter recipient address: ")
            amount = input("Enter transfer amount: ")
            
            # Send a simple test message
            transfer_message = f"TRANSFER|{recipient}|{amount}"
            client_socket.send(transfer_message.encode('utf-8'))
            
            print(f"✉️ Transfer request sent: {transfer_message}")
            input("Press ENTER to continue...")
        
        elif choice == '2':
            return
        
        else:
            print("Invalid choice. Please try again.")

def start_client():
    host = '192.168.1.106'
    port = 5555

    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            print(f"✅ Connected to server: {host}:{port}")

            # Send handshake message
            client_socket.send("HELLO".encode('utf-8'))

            # Receive update status from the server
            update_status = client_socket.recv(1024).decode('utf-8')
            if update_status != "UPDATE_NOT_NEEDED":
                print("Update message:", update_status)
            break

        except ConnectionRefusedError:
            print("❌ Server is currently offline, please try again later.")
            time.sleep(5)
        except Exception as e:
            print(f"❌ Error occurred: {e}")
            time.sleep(5)

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
            print("9. Server Status")  # Yeni seçenek
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
                server_status(client_socket)  # Server Status menüsünü çağırın

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

def balance_menu(client_socket):
    print("\n--- BALANCE MENU ---")
    print("This feature is still under development.")
    input("Press ENTER to continue...")

def wallet_menu(client_socket):
    print("\n--- WALLET MENU ---")
    print("This feature is still under development.")
    input("Press ENTER to continue...")

def airdrop_menu(client_socket):
    print("\n--- AIRDROP MENU ---")
    print("This feature is still under development.")
    input("Press ENTER to continue...")

def mine_menu(client_socket):
    while True:
        print("\n--- MINING MENU ---")
        print("1. Start Mining")
        print("2. Go Back")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            print("\n🚧 Mining is under development.")
            print("This is a demo screen. Real mining operations are not performed yet.")
            input("Press ENTER to continue...")
        
        elif choice == '2':
            return
        
        else:
            print("Invalid choice. Please try again.")

# Check for updates
if __name__ == "__main__":
    updated = safe_update_client()

    if updated:
        print("🔄 Update completed, restarting client...\n")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    print("🚀 Starting client...\n")
    start_client()
