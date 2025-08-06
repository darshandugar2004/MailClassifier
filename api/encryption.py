import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
import json
from datetime import datetime
import os
import sys

# Get the absolute path of the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the parent directory
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

# Add the parent directory to sys.path
sys.path.append(parent_dir)

from utils import SECRET_KEY, SALT

class SecureComms:
    def __init__(self):
        # Derive a consistent key using PBKDF2
        self.key = hashlib.pbkdf2_hmac(
            'sha256',
            SECRET_KEY,
            SALT,
            100000  # Number of iterations
        )
    
    def encrypt_packet(self, user_id: str, query: str) -> str:
        """Create and encrypt a data packet"""
        packet = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'query': query
        }
        packet_str = json.dumps(packet)
        
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(packet_str.encode(), AES.block_size))
        iv = cipher.iv
        return base64.b64encode(iv + ct_bytes).decode('utf-8')
    
    def decrypt_packet(self, encrypted_data: str) -> dict:
        """Decrypt a data packet"""
        enc_data = base64.b64decode(encrypted_data)
        iv = enc_data[:AES.block_size]
        ct = enc_data[AES.block_size:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return json.loads(pt.decode('utf-8'))