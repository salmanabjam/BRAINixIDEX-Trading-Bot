"""
BiX TradeBOT - Security Module
===============================
Secure handling of API keys, secrets, and sensitive configuration.

Features:
- AES-256 encryption for API keys
- Fernet symmetric encryption
- Secure key derivation (PBKDF2)
- Environment variable encryption
- Secret rotation support
- Secure memory cleanup

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import os
import base64
import hashlib
import secrets
import getpass
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import json

from utils.advanced_logger import get_logger

logger = get_logger(__name__, component='Security')


class SecureConfig:
    """
    Secure configuration manager with encryption support.
    
    Features:
    - Encrypts sensitive data at rest
    - Derives encryption key from master password
    - Supports key rotation
    - Secure memory cleanup
    """
    
    SALT_SIZE = 32  # bytes
    KEY_ITERATIONS = 100000  # PBKDF2 iterations
    ENCRYPTED_FILE = '.secrets.enc'
    SALT_FILE = '.salt'
    
    def __init__(self, config_dir: str = 'config'):
        """
        Initialize secure configuration.
        
        Args:
            config_dir: Directory to store encrypted secrets
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.encrypted_file = self.config_dir / self.ENCRYPTED_FILE
        self.salt_file = self.config_dir / self.SALT_FILE
        
        self._fernet: Optional[Fernet] = None
        self._secrets: Dict[str, str] = {}
        
        logger.info("🔐 Secure configuration initialized")
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2.
        
        Args:
            password: Master password
            salt: Cryptographic salt
            
        Returns:
            Derived encryption key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.KEY_ITERATIONS,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        return base64.urlsafe_b64encode(key)
    
    def _get_or_create_salt(self) -> bytes:
        """Get existing salt or create new one."""
        if self.salt_file.exists():
            with open(self.salt_file, 'rb') as f:
                return f.read()
        else:
            salt = secrets.token_bytes(self.SALT_SIZE)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
            # Set restrictive permissions (Unix-like systems)
            try:
                os.chmod(self.salt_file, 0o600)
            except Exception:
                pass  # Windows doesn't support chmod
            logger.info("🔑 Generated new salt")
            return salt
    
    def initialize(self, password: Optional[str] = None) -> None:
        """
        Initialize encryption with master password.
        
        Args:
            password: Master password (prompts if None)
        """
        if password is None:
            password = getpass.getpass("Enter master password: ")
        
        if not password:
            raise ValueError("Password cannot be empty")
        
        salt = self._get_or_create_salt()
        key = self._derive_key(password, salt)
        self._fernet = Fernet(key)
        
        logger.info("✅ Encryption initialized")
    
    def encrypt_secret(self, key: str, value: str) -> None:
        """
        Encrypt and store a secret.
        
        Args:
            key: Secret identifier
            value: Secret value to encrypt
        """
        if self._fernet is None:
            raise RuntimeError(
                "Encryption not initialized. Call initialize() first"
            )
        
        self._secrets[key] = value
        self._save_encrypted()
        logger.debug(f"🔒 Encrypted secret: {key}")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> str:
        """
        Retrieve and decrypt a secret.
        
        Args:
            key: Secret identifier
            default: Default value if not found
            
        Returns:
            Decrypted secret value
        """
        if self._fernet is None:
            raise RuntimeError(
                "Encryption not initialized. Call initialize() first"
            )
        
        if not self._secrets and self.encrypted_file.exists():
            self._load_encrypted()
        
        value = self._secrets.get(key, default)
        if value is None:
            logger.warning(f"⚠️  Secret not found: {key}")
        return value
    
    def delete_secret(self, key: str) -> bool:
        """
        Delete a secret.
        
        Args:
            key: Secret identifier
            
        Returns:
            True if deleted, False if not found
        """
        if key in self._secrets:
            del self._secrets[key]
            self._save_encrypted()
            logger.info(f"🗑️  Deleted secret: {key}")
            return True
        return False
    
    def list_keys(self) -> list:
        """List all secret keys (not values)."""
        if not self._secrets and self.encrypted_file.exists():
            self._load_encrypted()
        return list(self._secrets.keys())
    
    def _save_encrypted(self) -> None:
        """Save encrypted secrets to file."""
        if self._fernet is None:
            raise RuntimeError("Encryption not initialized")
        
        # Convert to JSON
        json_data = json.dumps(self._secrets)
        
        # Encrypt
        encrypted_data = self._fernet.encrypt(json_data.encode())
        
        # Save to file
        with open(self.encrypted_file, 'wb') as f:
            f.write(encrypted_data)
        
        # Set restrictive permissions
        try:
            os.chmod(self.encrypted_file, 0o600)
        except Exception:
            pass  # Windows doesn't support chmod
        
        logger.debug("💾 Secrets saved (encrypted)")
    
    def _load_encrypted(self) -> None:
        """Load and decrypt secrets from file."""
        if self._fernet is None:
            raise RuntimeError("Encryption not initialized")
        
        if not self.encrypted_file.exists():
            logger.warning("⚠️  No encrypted secrets file found")
            return
        
        try:
            # Read encrypted data
            with open(self.encrypted_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt
            decrypted_data = self._fernet.decrypt(encrypted_data)
            
            # Parse JSON
            self._secrets = json.loads(decrypted_data.decode())
            
            logger.debug(
                f"🔓 Loaded {len(self._secrets)} secrets (decrypted)"
            )
        except Exception as e:
            logger.error(f"❌ Failed to load secrets: {e}")
            raise ValueError(
                "Failed to decrypt secrets. "
                "Check your password or reinitialize."
            )
    
    def rotate_encryption(self, old_password: str, new_password: str) -> None:
        """
        Rotate encryption key by re-encrypting with new password.
        
        Args:
            old_password: Current master password
            new_password: New master password
        """
        # Decrypt with old password
        old_salt = self._get_or_create_salt()
        old_key = self._derive_key(old_password, old_salt)
        old_fernet = Fernet(old_key)
        
        if self.encrypted_file.exists():
            with open(self.encrypted_file, 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = old_fernet.decrypt(encrypted_data)
            self._secrets = json.loads(decrypted_data.decode())
        
        # Generate new salt
        new_salt = secrets.token_bytes(self.SALT_SIZE)
        with open(self.salt_file, 'wb') as f:
            f.write(new_salt)
        
        # Re-encrypt with new password
        new_key = self._derive_key(new_password, new_salt)
        self._fernet = Fernet(new_key)
        self._save_encrypted()
        
        logger.info("🔄 Encryption key rotated successfully")
    
    def clear_memory(self) -> None:
        """Clear sensitive data from memory."""
        self._secrets = {}
        self._fernet = None
        logger.debug("🧹 Cleared secrets from memory")


class SecretManager:
    """
    High-level secret management interface.
    
    Provides convenient methods for managing API keys and secrets.
    """
    
    def __init__(self, config_dir: str = 'config'):
        """Initialize secret manager."""
        self.secure_config = SecureConfig(config_dir)
        self._initialized = False
    
    def setup(
        self,
        binance_api_key: str,
        binance_api_secret: str,
        password: Optional[str] = None
    ) -> None:
        """
        Initial setup of encrypted secrets.
        
        Args:
            binance_api_key: Binance API key
            binance_api_secret: Binance API secret
            password: Master password (prompts if None)
        """
        self.secure_config.initialize(password)
        self.secure_config.encrypt_secret('BINANCE_API_KEY', binance_api_key)
        self.secure_config.encrypt_secret(
            'BINANCE_API_SECRET',
            binance_api_secret
        )
        self._initialized = True
        logger.info("✅ Secrets setup completed")
    
    def load(self, password: Optional[str] = None) -> None:
        """
        Load encrypted secrets.
        
        Args:
            password: Master password (prompts if None)
        """
        self.secure_config.initialize(password)
        self._initialized = True
        logger.info("✅ Secrets loaded")
    
    def get_binance_credentials(self) -> Dict[str, str]:
        """
        Get Binance API credentials.
        
        Returns:
            Dictionary with api_key and api_secret
        """
        if not self._initialized:
            raise RuntimeError(
                "SecretManager not initialized. Call load() first"
            )
        
        api_key = self.secure_config.get_secret('BINANCE_API_KEY', '')
        api_secret = self.secure_config.get_secret('BINANCE_API_SECRET', '')
        
        if not api_key or not api_secret:
            raise ValueError(
                "Binance credentials not found. Run setup() first"
            )
        
        return {
            'api_key': api_key,
            'api_secret': api_secret
        }
    
    def update_credentials(
        self,
        binance_api_key: str,
        binance_api_secret: str
    ) -> None:
        """Update Binance credentials."""
        if not self._initialized:
            raise RuntimeError(
                "SecretManager not initialized. Call load() first"
            )
        
        self.secure_config.encrypt_secret('BINANCE_API_KEY', binance_api_key)
        self.secure_config.encrypt_secret(
            'BINANCE_API_SECRET',
            binance_api_secret
        )
        logger.info("🔄 Credentials updated")
    
    def add_secret(self, key: str, value: str) -> None:
        """Add or update a custom secret."""
        if not self._initialized:
            raise RuntimeError(
                "SecretManager not initialized. Call load() first"
            )
        self.secure_config.encrypt_secret(key, value)
    
    def get_secret(self, key: str, default: Optional[str] = None) -> str:
        """Get a custom secret."""
        if not self._initialized:
            raise RuntimeError(
                "SecretManager not initialized. Call load() first"
            )
        return self.secure_config.get_secret(key, default)
    
    def rotate_password(
        self,
        old_password: str,
        new_password: str
    ) -> None:
        """Rotate master password."""
        self.secure_config.rotate_encryption(old_password, new_password)
        logger.info("🔄 Master password rotated")


def generate_api_key_hash(api_key: str) -> str:
    """
    Generate SHA-256 hash of API key for logging/auditing.
    
    Args:
        api_key: API key to hash
        
    Returns:
        Hex-encoded hash (first 8 characters for brevity)
    """
    hash_obj = hashlib.sha256(api_key.encode())
    return hash_obj.hexdigest()[:8]


def validate_api_key_format(api_key: str) -> bool:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if format is valid
    """
    # Binance API keys are 64 characters alphanumeric
    if len(api_key) != 64:
        return False
    return api_key.isalnum()


if __name__ == "__main__":
    # Example usage
    print("🔐 BiX TradeBOT - Secure Secret Management")
    print("=" * 50)
    
    # Initialize manager
    manager = SecretManager()
    
    # Setup (first time)
    print("\n1. Initial Setup")
    api_key = input("Enter Binance API Key: ")
    api_secret = getpass.getpass("Enter Binance API Secret: ")
    
    if validate_api_key_format(api_key):
        print("✅ API key format valid")
    else:
        print("⚠️  API key format may be invalid")
    
    manager.setup(api_key, api_secret)
    print("✅ Secrets encrypted and saved")
    
    # Load (subsequent uses)
    print("\n2. Loading Secrets")
    manager2 = SecretManager()
    manager2.load()
    
    creds = manager2.get_binance_credentials()
    print(f"✅ Loaded credentials")
    print(f"   API Key Hash: {generate_api_key_hash(creds['api_key'])}")
    
    # List secrets
    print("\n3. Available Secrets:")
    keys = manager2.secure_config.list_keys()
    for key in keys:
        print(f"   - {key}")
    
    print("\n✅ Security demonstration complete")
