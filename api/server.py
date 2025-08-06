# server/server.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from model_loader import ModelInference
from encryption import SecureComms
import logging
import logging.config
from datetime import datetime
from pydantic import BaseModel
import os
import json
import yaml

# Load logging configuration from YAML file
with open(os.path.join(os.path.dirname(__file__), "logging.yaml"), 'r') as f:
    log_config = yaml.safe_load(f.read())
logging.config.dictConfig(log_config)

logger = logging.getLogger(__name__)

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_id = "darshandugar/MailClassifier-DistilBERT"
model = ModelInference(model_id=model_id)

comms = SecureComms()

class EncryptedRequest(BaseModel):
    encrypted_data: str

@app.post("/predict")
async def predict(request: EncryptedRequest):
    try:
        # Decrypt the request
        decrypted = comms.decrypt_packet(request.encrypted_data)
        logger.info(f"Received request from user: {decrypted['user_id']}")
        
        # Make prediction
        result = model.predict(decrypted['query'])
        
        # Log the interaction
        log_entry = {
            'timestamp': decrypted['timestamp'],
            'user_id': decrypted['user_id'],
            'query': decrypted['query'],
            'response': result
        }
        logger.info(f"Interaction: {log_entry}")
        
        # Encrypt the response
        encrypted_response = comms.encrypt_packet(
            user_id=decrypted['user_id'],
            query=json.dumps(result)
        )
        
        return {"encrypted_response": encrypted_response}
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8050)