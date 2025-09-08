"""Cryptographic utilities for encrypting/decrypting sensitive data."""

from cryptography.fernet import Fernet
from app.core.config import get_settings
import base64


def _get_fernet() -> Fernet:
    """Get Fernet instance using SECRET_KEY."""
    settings = get_settings()
    # Use first 32 chars of secret key and pad/truncate as needed
    key = settings.SECRET_KEY.encode()[:32]
    key = key.ljust(32, b'0')[:32]  # Pad with zeros if too short, truncate if too long
    # Encode as base64url for Fernet
    key_b64 = base64.urlsafe_b64encode(key)
    return Fernet(key_b64)


def encrypt_text(plaintext: str) -> str:
    """Encrypt plaintext string and return base64 encoded ciphertext."""
    fernet = _get_fernet()
    encrypted = fernet.encrypt(plaintext.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_text(ciphertext: str) -> str:
    """Decrypt base64 encoded ciphertext and return plaintext string."""
    fernet = _get_fernet()
    encrypted = base64.urlsafe_b64decode(ciphertext.encode())
    decrypted = fernet.decrypt(encrypted)
    return decrypted.decode()
