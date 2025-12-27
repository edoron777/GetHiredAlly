"""Encryption utilities for sensitive data like CVs."""
import os
import logging
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')

_fernet: Optional[Fernet] = None


def get_fernet() -> Optional[Fernet]:
    """Get or create Fernet instance. Returns None if key not configured."""
    global _fernet
    
    if _fernet is not None:
        return _fernet
    
    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        logger.warning("ENCRYPTION_KEY not set - encryption disabled")
        return None
    
    try:
        _fernet = Fernet(key.encode() if isinstance(key, str) else key)
        return _fernet
    except Exception as e:
        logger.error(f"Invalid ENCRYPTION_KEY format: {type(e).__name__}")
        return None


def encrypt_text(plain_text: str) -> str:
    """
    Encrypt plain text string.
    Returns base64-encoded encrypted string.
    Returns original text if encryption is not configured.
    """
    if not plain_text:
        return ""
    
    fernet = get_fernet()
    if not fernet:
        return plain_text
    
    try:
        encrypted_bytes = fernet.encrypt(plain_text.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"Encryption error: {type(e).__name__}")
        return plain_text


def decrypt_text(encrypted_text: str) -> str:
    """
    Decrypt encrypted text string.
    Returns original plain text.
    Returns original text if not encrypted or encryption not configured.
    """
    if not encrypted_text:
        return ""
    
    if not is_encrypted(encrypted_text):
        return encrypted_text
    
    fernet = get_fernet()
    if not fernet:
        return encrypted_text
    
    try:
        decrypted_bytes = fernet.decrypt(encrypted_text.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except InvalidToken:
        logger.error("Decryption failed: Invalid token or wrong key")
        raise ValueError("Failed to decrypt data - invalid key or corrupted data")
    except Exception as e:
        logger.error(f"Decryption error: {type(e).__name__}")
        raise ValueError("Failed to decrypt data")


def is_encrypted(text: str) -> bool:
    """
    Check if text appears to be Fernet encrypted.
    Fernet tokens start with 'gAAAAA'.
    """
    if not text or not isinstance(text, str):
        return False
    return text.startswith('gAAAAA')


def generate_key() -> str:
    """Generate a new Fernet encryption key. Use this once to create ENCRYPTION_KEY."""
    return Fernet.generate_key().decode('utf-8')
