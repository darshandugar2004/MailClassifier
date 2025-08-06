import streamlit as st
import requests
import json
from datetime import datetime
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
import logging

# child_script.py
import sys
import os

# Get the absolute path of the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the parent directory
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

# Add the parent directory to sys.path
sys.path.append(parent_dir)

from utils import SECRET_KEY, SALT

# Configure logging
logging.basicConfig(
    filename='../logs/ui_logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ClientEncryption:
    def __init__(self):
        self.key = hashlib.pbkdf2_hmac(
            'sha256',
            SECRET_KEY,
            SALT,
            100000
        )
    
    def encrypt_packet(self, user_id: str, query: str) -> str:
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
        enc_data = base64.b64decode(encrypted_data)
        iv = enc_data[:AES.block_size]
        ct = enc_data[AES.block_size:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return json.loads(pt.decode('utf-8'))

# Initialize encryption
comms = ClientEncryption()

# Streamlit UI
st.title("Secure LLM Classification")
st.write("This app securely classifies corporate emails using a fine-tuned model.")

# User session management
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"

# Input form
with st.form("query_form"):
    query = st.text_area("Enter your email text:", height=200)
    submitted = st.form_submit_button("Classify")

if submitted and query:
    try:
        # Encrypt the request
        encrypted_request = comms.encrypt_packet(st.session_state.user_id, query)
        
        # Send to API
        response = requests.post(
            "http://127.0.0.1:8050/predict",
            headers={"Content-Type": "application/json"},
            json={"encrypted_data": encrypted_request}  # Your encrypted payload
        )
        if response.status_code == 200:
            # Decrypt the response
            decrypted = comms.decrypt_packet(response.json()["encrypted_response"])
            result = json.loads(decrypted['query'])
            
            # Display results
            st.success("Classification successful!")
            st.subheader("Results")
            st.write(f"**Category:** {result['label']}")
            st.write(f"**Confidence:** {result['confidence']:.2%}")
            
            # Show probabilities
            st.subheader("Probabilities")
            for cat, prob in result['probabilities'].items():
                st.write(f"{cat}: {prob:.2%}")
                st.progress(prob)
            
            # Log the interaction
            logger.info(f"User {st.session_state.user_id} received response: {result}")
        else:
            st.error(f"Error: {response.text}")
            logger.error(f"API error: {response.text}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        logger.error(f"UI error: {str(e)}")

# Add some info
st.sidebar.markdown("""
### About this App
- Uses a fine-tuned DistilBERT model
- All communications are encrypted
- Runs entirely on your local machine
- No data leaves your environment
""")