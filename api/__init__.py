"""
Secure API package for LLM deployment

This package provides:
- Model loading and inference
- Secure encrypted communication
- API endpoints for predictions
"""

from .server import app  # Import the FastAPI app for easy access
from .model_loader import ModelInference
from .encryption import SecureComms

__all__ = ['app', 'ModelInference', 'SecureComms']
__version__ = '0.1.0'

# Initialize package-level logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)