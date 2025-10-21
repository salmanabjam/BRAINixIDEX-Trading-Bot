"""
Security Module Tests
=====================
Test encryption, secret management, and security features.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from src.utils.security import (
    SecureConfig,
    SecretManager,
    generate_api_key_hash,
    validate_api_key_format
)


class TestSecureConfig(unittest.TestCase):
    """Test SecureConfig encryption/decryption."""
    
    def setUp(self):
        """Create temporary directory for tests."""
        self.test_dir = tempfile.mkdtemp()
        self.config = SecureConfig(self.test_dir)
        self.password = "test_password_123"
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test config initialization."""
        self.config.initialize(self.password)
        
        # Check that salt file was created
        salt_path = Path(self.test_dir) / '.salt'
        self.assertTrue(salt_path.exists())
    
    def test_encrypt_decrypt_secret(self):
        """Test encryption and decryption round-trip."""
        self.config.initialize(self.password)
        
        # Encrypt a secret
        test_key = "test_key"
        test_value = "test_secret_value_123"
        self.config.encrypt_secret(test_key, test_value)
        
        # Decrypt and verify
        decrypted = self.config.get_secret(test_key)
        self.assertEqual(decrypted, test_value)
    
    def test_multiple_secrets(self):
        """Test storing multiple secrets."""
        self.config.initialize(self.password)
        
        secrets = {
            'api_key': 'abc123',
            'api_secret': 'xyz789',
            'webhook_url': 'https://example.com/hook'
        }
        
        # Store all secrets
        for key, value in secrets.items():
            self.config.encrypt_secret(key, value)
        
        # Verify all secrets
        for key, expected_value in secrets.items():
            actual_value = self.config.get_secret(key)
            self.assertEqual(actual_value, expected_value)
    
    def test_delete_secret(self):
        """Test secret deletion."""
        self.config.initialize(self.password)
        
        self.config.encrypt_secret('temp_key', 'temp_value')
        self.assertEqual(self.config.get_secret('temp_key'), 'temp_value')
        
        # Delete and verify
        self.config.delete_secret('temp_key')
        self.assertIsNone(self.config.get_secret('temp_key'))
    
    def test_list_keys(self):
        """Test listing secret keys."""
        self.config.initialize(self.password)
        
        keys = ['key1', 'key2', 'key3']
        for key in keys:
            self.config.encrypt_secret(key, f'value_{key}')
        
        stored_keys = self.config.list_keys()
        self.assertEqual(set(stored_keys), set(keys))
    
    def test_wrong_password(self):
        """Test that wrong password fails."""
        self.config.initialize(self.password)
        self.config.encrypt_secret('key', 'value')
        
        # Try to load with wrong password
        wrong_config = SecureConfig(self.test_dir)
        with self.assertRaises(Exception):
            wrong_config._derive_key("wrong_password", self.config.salt)
            wrong_config.get_secret('key')
    
    def test_password_rotation(self):
        """Test rotating encryption password."""
        # Setup with initial password
        self.config.initialize(self.password)
        self.config.encrypt_secret('key', 'value')
        
        # Rotate to new password
        new_password = "new_password_456"
        self.config.rotate_encryption(self.password, new_password)
        
        # Verify with new password
        new_config = SecureConfig(self.test_dir)
        new_config.initialize(new_password)
        self.assertEqual(new_config.get_secret('key'), 'value')
    
    def test_persistence(self):
        """Test that secrets persist across instances."""
        # Create and store secret
        self.config.initialize(self.password)
        self.config.encrypt_secret('persist_key', 'persist_value')
        
        # Create new instance and load
        new_config = SecureConfig(self.test_dir)
        new_config.initialize(self.password)
        
        self.assertEqual(
            new_config.get_secret('persist_key'),
            'persist_value'
        )


class TestSecretManager(unittest.TestCase):
    """Test SecretManager high-level API."""
    
    def setUp(self):
        """Create temporary directory for tests."""
        self.test_dir = tempfile.mkdtemp()
        self.manager = SecretManager(self.test_dir)
        self.password = "manager_password_123"
        self.api_key = "test_api_key_" + "x" * 50  # 64 chars
        self.api_secret = "test_api_secret_" + "y" * 47  # 64 chars
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_setup_and_load(self):
        """Test setup and load workflow."""
        # Setup
        self.manager.setup(
            binance_api_key=self.api_key,
            binance_api_secret=self.api_secret,
            password=self.password
        )
        
        # Load in new instance
        new_manager = SecretManager(self.test_dir)
        new_manager.load(self.password)
        
        # Verify credentials
        creds = new_manager.get_binance_credentials()
        self.assertEqual(creds['api_key'], self.api_key)
        self.assertEqual(creds['api_secret'], self.api_secret)
    
    def test_update_credentials(self):
        """Test updating Binance credentials."""
        # Initial setup
        self.manager.setup(
            binance_api_key=self.api_key,
            binance_api_secret=self.api_secret,
            password=self.password
        )
        
        # Update credentials
        new_key = "new_api_key_" + "a" * 51
        new_secret = "new_api_secret_" + "b" * 48
        
        self.manager.update_credentials(new_key, new_secret)
        
        # Verify update
        creds = self.manager.get_binance_credentials()
        self.assertEqual(creds['api_key'], new_key)
        self.assertEqual(creds['api_secret'], new_secret)
    
    def test_custom_secrets(self):
        """Test adding custom secrets."""
        self.manager.setup(
            binance_api_key=self.api_key,
            binance_api_secret=self.api_secret,
            password=self.password
        )
        
        # Add custom secrets
        self.manager.add_secret('webhook_url', 'https://example.com')
        self.manager.add_secret('api_version', 'v3')
        
        # Verify retrieval
        self.assertEqual(
            self.manager.get_secret('webhook_url'),
            'https://example.com'
        )
        self.assertEqual(self.manager.get_secret('api_version'), 'v3')
    
    def test_password_rotation(self):
        """Test password rotation via manager."""
        # Setup
        self.manager.setup(
            binance_api_key=self.api_key,
            binance_api_secret=self.api_secret,
            password=self.password
        )
        
        # Rotate password
        new_password = "rotated_password_456"
        self.manager.rotate_password(self.password, new_password)
        
        # Load with new password
        new_manager = SecretManager(self.test_dir)
        new_manager.load(new_password)
        
        creds = new_manager.get_binance_credentials()
        self.assertEqual(creds['api_key'], self.api_key)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_generate_api_key_hash(self):
        """Test API key hashing."""
        api_key = "test_api_key_12345"
        hash1 = generate_api_key_hash(api_key)
        hash2 = generate_api_key_hash(api_key)
        
        # Same input should produce same hash
        self.assertEqual(hash1, hash2)
        
        # Hash should be 8 characters (truncated SHA-256)
        self.assertEqual(len(hash1), 8)
        
        # Different input should produce different hash
        hash3 = generate_api_key_hash("different_key")
        self.assertNotEqual(hash1, hash3)
    
    def test_validate_api_key_format_valid(self):
        """Test API key validation with valid keys."""
        # Binance API keys are 64 alphanumeric characters
        valid_key = "a" * 64
        self.assertTrue(validate_api_key_format(valid_key))
        
        # Mixed case and numbers
        valid_key2 = "Abc123" * 10 + "xy12"  # 64 chars
        self.assertTrue(validate_api_key_format(valid_key2))
    
    def test_validate_api_key_format_invalid(self):
        """Test API key validation with invalid keys."""
        # Too short
        self.assertFalse(validate_api_key_format("short"))
        
        # Too long
        self.assertFalse(validate_api_key_format("a" * 65))
        
        # Contains special characters
        self.assertFalse(validate_api_key_format("a" * 63 + "!"))
        
        # Empty
        self.assertFalse(validate_api_key_format(""))


class TestSecurityBestPractices(unittest.TestCase):
    """Test security best practices implementation."""
    
    def setUp(self):
        """Setup test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.config = SecureConfig(self.test_dir)
        self.password = "test_password_123"
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_salt_uniqueness(self):
        """Test that each instance gets unique salt."""
        self.config.initialize(self.password)
        salt1 = self.config._get_or_create_salt()
        
        # New instance in different directory
        test_dir2 = tempfile.mkdtemp()
        config2 = SecureConfig(test_dir2)
        config2.initialize(self.password)
        salt2 = config2._get_or_create_salt()
        
        # Salts should be different
        self.assertNotEqual(salt1, salt2)
        
        shutil.rmtree(test_dir2, ignore_errors=True)
    
    def test_memory_cleanup(self):
        """Test that clear_memory() works."""
        self.config.initialize(self.password)
        self.config.encrypt_secret('key', 'value')
        
        # Clear memory
        self.config.clear_memory()
        
        # Verify secrets are cleared from memory (not from file)
        self.assertEqual(self.config._secrets, {})
        
        # But can still be loaded from file
        self.config.initialize(self.password)
        self.assertEqual(self.config.get_secret('key'), 'value')
    
    def test_file_creation(self):
        """Test that encrypted file is created."""
        self.config.initialize(self.password)
        self.config.encrypt_secret('key', 'value')
        
        secrets_file = Path(self.test_dir) / '.secrets.enc'
        self.assertTrue(secrets_file.exists())
        
        # File should not be empty
        self.assertGreater(secrets_file.stat().st_size, 0)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
