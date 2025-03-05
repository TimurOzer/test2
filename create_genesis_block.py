import hashlib
import time
import json
import os

class Block:
    def __init__(self, index, timestamp, data, prev_hash, proof, security_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data  # Token adresi (bklv ile başlayan)
        self.prev_hash = prev_hash
        self.proof = proof  # Proof of Work
        self.security_hash = security_hash  # İkinci hash değeri
        self.hash = self.calculate_hash()  # Normal hash (SHA-256)
    
    def calculate_hash(self):
        """Calculate SHA-256 hash of the block's content"""
        block_string = f"{self.index}{self.timestamp}{self.data}{self.prev_hash}{self.proof}{self.security_hash}"
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()

def proof_of_work(block, difficulty):
    """Perform Proof of Work mining for the block"""
    target = '0' * difficulty
    while True:
        block_hash = block.calculate_hash()
        if block_hash[:difficulty] == target:
            return block_hash  # Proof of Work complete
        block.proof += 1  # Increase the proof of work value to try again

def generate_bklv_address(start_nonce=0):
    """Generate an address starting with 'bklv' and 40 characters in total"""
    nonce = start_nonce
    while True:
        # Hash a string of 'bklv' combined with the nonce
        address_candidate = f"bklv{nonce}"
        address_hash = hashlib.sha256(address_candidate.encode('utf-8')).hexdigest()
        
        # We only need the first 36 characters from the hash to make the address 40 characters long
        full_address = f"bklv{address_hash[:36]}"  # bklv + first 36 characters of the hash
        
        # Check if the address is 40 characters long and starts with 'bklv'
        if len(full_address) == 40 and full_address.startswith("bklv"):
            print(f"✅ Address found: {full_address}")
            return full_address, nonce
        
        nonce += 1  # Increment the nonce to try the next possibility
        
        # Every 10,000 tries, print an update
        if nonce % 10000 == 0:
            print(f"⏳ Searching... {nonce} attempts made, address still not found.")

def load_nonce():
    """Load the last nonce used from a file to continue from where we left off"""
    if os.path.exists("nonce_state.txt"):
        with open("nonce_state.txt", "r") as file:
            return int(file.read().strip())
    return 0  # If no file exists, start from 0

def save_nonce(nonce):
    """Save the current nonce to a file to resume later"""
    with open("nonce_state.txt", "w") as file:
        file.write(str(nonce))

def create_private_key(address):
    """Generate a private key based on the address using SHA-256"""
    # Private key generation based on the address using SHA-256
    private_key = hashlib.sha256(address.encode('utf-8')).hexdigest()
    return private_key

def save_token_data(address, private_key):
    """Save the address and private key to a JSON file"""
    token_data = {
        "address": address,
        "private_key": private_key
    }
    
    with open("token.json", "w") as json_file:
        json.dump(token_data, json_file, indent=4)
    
    print("📄 Token data saved to 'token.json'.")

def create_genesis_block():
    """Create the Genesis block"""
    print("🔧 Creating Genesis Block...")

    # Load the last nonce used
    start_nonce = load_nonce()
    
    # Generate the "bklv" address by mining
    data, next_nonce = generate_bklv_address(start_nonce)  # This will generate an address starting with 'bklv' and 40 characters long
    
    # Save the next nonce to continue from where we left off
    save_nonce(next_nonce)
    
    # Generate the private key for the address
    private_key = create_private_key(data)
    
    # Save the token data (address and private key) to a JSON file
    save_token_data(data, private_key)
    
    prev_hash = "0" * 64  # Previous block hash (0's for the first block)
    proof = 0  # Start mining from 0
    security_hash = "0" * 64  # Initially set the security hash to zeros

    # Create Genesis Block
    genesis_block = Block(0, int(time.time()), data, prev_hash, proof, security_hash)

    # Perform Proof of Work
    difficulty = 4  # Example difficulty (you can adjust this)
    block_hash = proof_of_work(genesis_block, difficulty)
    
    # Generate security hash (similarly)
    security_hash = hashlib.sha256(block_hash.encode('utf-8')).hexdigest()[:64]  # Example security hash generation
    
    # Set the security hash for the genesis block
    genesis_block.security_hash = security_hash

    # Print the token address
    print(f"📍 Genesis Block Address: {genesis_block.data}")
    print(f"📍 Genesis Block Security Hash: {genesis_block.security_hash}")

    print(f"✅ Genesis Block Created! Proof of Work: {block_hash}")

    return genesis_block, block_hash

# Create the Genesis block and get the hash
genesis_block, genesis_block_hash = create_genesis_block()
print(f"Genesis Block Hash: {genesis_block_hash}")
