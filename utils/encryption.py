import asyncio
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hashlib
from typing import Tuple
from logger_config import logger

class EncryptionManager:
    """Handles encryption/decryption for Free Fire protocol"""
    
    def __init__(self, key: bytes = None, iv: bytes = None):
        self.key = key or get_random_bytes(16)
        self.iv = iv or get_random_bytes(16)
    
    @staticmethod
    def encrypt_aes(data: bytes, key: bytes, iv: bytes) -> bytes:
        """Encrypt data using AES-128-CBC"""
        try:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            # Add PKCS7 padding
            padding_length = 16 - (len(data) % 16)
            padded_data = data + bytes([padding_length] * padding_length)
            encrypted = cipher.encrypt(padded_data)
            return encrypted
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return b''
    
    @staticmethod
    def decrypt_aes(data: bytes, key: bytes, iv: bytes) -> bytes:
        """Decrypt data using AES-128-CBC"""
        try:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(data)
            # Remove PKCS7 padding
            padding_length = decrypted[-1]
            return decrypted[:-padding_length]
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return b''
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def generate_session_key() -> Tuple[bytes, bytes]:
        """Generate random session key and IV"""
        return get_random_bytes(16), get_random_bytes(16)

encryption_manager = EncryptionManager()
