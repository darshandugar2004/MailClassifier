from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from typing import Dict, Any
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelInference:
    def __init__(self, model_id: str):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Use the provided model_id from Hugging Face Hub
        logger.info(f"Loading model from Hugging Face Hub: {model_id}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_id)
            self.model.to(self.device)
            self.model.eval()
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

        
        # Update these based on your training labels
        self.id_to_label = {0: 'Audit Request', 1: 'Budget Report', 2: 'Employee Feedback', 3: 'Financial Analysis', 4: 'Financial Health', 5: 'Financial Performance', 6: 'Financial Projections', 7: 'Financial Report', 8: 'Merger Announcement', 9: 'Preliminary Financial Report', 10: 'Product Launch', 11: 'Profit Analysis', 12: 'Summary Financial Report', 13: 'Sustainability Initiative'}

    
    def predict(self, text: str) -> Dict[str, Any]:
        """Make prediction on input text"""
        try:
            inputs = self.tokenizer(
                text,
                padding="max_length",
                truncation=True,
                max_length=128,
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1).cpu().numpy()[0]
            predicted_id = np.argmax(probabilities)
            
            return {
                'label': self.id_to_label[predicted_id],
                'confidence': float(probabilities[predicted_id]),
                'probabilities': {k: float(v) for k, v in zip(self.id_to_label.values(), probabilities)}
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise