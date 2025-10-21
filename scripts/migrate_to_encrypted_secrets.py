"""
Migration Script: .env → Encrypted Secrets
===========================================
Safely migrate API credentials from .env file to encrypted storage.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import os
import sys
import shutil
from pathlib import Path
from getpass import getpass
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.security import SecretManager, validate_api_key_format
from dotenv import load_dotenv


def backup_env_file(env_path: Path) -> Path:
    """Create timestamped backup of .env file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = env_path.parent / f'.env.backup_{timestamp}'
    
    if env_path.exists():
        shutil.copy2(env_path, backup_path)
        print(f"✅ Created backup: {backup_path}")
        return backup_path
    else:
        print("⚠️  No .env file found to backup")
        return None


def load_env_credentials(env_path: Path) -> dict:
    """Load credentials from .env file."""
    load_dotenv(env_path)
    
    api_key = os.getenv('BINANCE_API_KEY', '').strip()
    api_secret = os.getenv('BINANCE_API_SECRET', '').strip()
    
    return {
        'api_key': api_key,
        'api_secret': api_secret
    }


def validate_credentials(creds: dict) -> bool:
    """Validate that credentials are present and properly formatted."""
    if not creds['api_key'] or not creds['api_secret']:
        print("❌ API credentials not found in .env file")
        return False
    
    # Validate API key format (Binance keys are 64 chars)
    if not validate_api_key_format(creds['api_key']):
        print("⚠️  Warning: API key format doesn't match Binance standard (64 chars)")
        response = input("Continue anyway? (yes/no): ").strip().lower()
        if response != 'yes':
            return False
    
    return True


def confirm_migration(creds: dict) -> bool:
    """Show preview and confirm migration."""
    print("\n" + "="*60)
    print("🔒 MIGRATION PREVIEW")
    print("="*60)
    print(f"\nAPI Key: {creds['api_key'][:8]}...{creds['api_key'][-4:]}")
    print(f"Secret:  {'*' * 20}")
    print("\nThese credentials will be:")
    print("  ✓ Encrypted with AES-256")
    print("  ✓ Protected by your master password")
    print("  ✓ Stored in config/.secrets.enc")
    print("\nYour .env file will:")
    print("  ✓ Be backed up with timestamp")
    print("  ✓ Remain unchanged (you can delete it manually later)")
    print("\n" + "="*60)
    
    response = input("\nProceed with migration? (yes/no): ").strip().lower()
    return response == 'yes'


def get_master_password() -> str:
    """Prompt for and confirm master password."""
    print("\n🔑 Master Password Setup")
    print("-" * 40)
    print("Requirements:")
    print("  • Minimum 12 characters recommended")
    print("  • Mix of letters, numbers, symbols")
    print("  • You'll need this password to start the bot")
    print("  • CANNOT BE RECOVERED if lost!")
    print()
    
    while True:
        password = getpass("Enter master password: ")
        
        if len(password) < 8:
            print("❌ Password too short (minimum 8 characters)")
            continue
        
        if len(password) < 12:
            print("⚠️  Warning: Password shorter than 12 characters (not recommended)")
            response = input("Continue anyway? (yes/no): ").strip().lower()
            if response != 'yes':
                continue
        
        confirm = getpass("Confirm master password: ")
        
        if password != confirm:
            print("❌ Passwords don't match. Try again.\n")
            continue
        
        return password


def migrate_secrets(
    creds: dict,
    password: str,
    config_dir: str = 'config'
) -> bool:
    """Migrate credentials to encrypted storage."""
    try:
        # Initialize SecretManager
        manager = SecretManager(config_dir)
        
        # Setup with credentials
        print("\n🔐 Encrypting credentials...")
        manager.setup(
            api_key=creds['api_key'],
            api_secret=creds['api_secret'],
            password=password
        )
        
        # Verify by loading
        print("✓ Verifying encrypted secrets...")
        manager = SecretManager(config_dir)
        manager.load(password)
        stored_creds = manager.get_binance_credentials()
        
        if (stored_creds['api_key'] == creds['api_key'] and 
            stored_creds['api_secret'] == creds['api_secret']):
            print("✅ Verification successful!")
            return True
        else:
            print("❌ Verification failed: credentials don't match")
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def create_env_example(project_root: Path):
    """Create .env.example template."""
    example_content = """# BiX TradeBOT - Environment Variables Template
# ================================================

# Binance API Credentials
# Note: For production, use encrypted secrets instead
# Run: python scripts/migrate_to_encrypted_secrets.py
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here

# Use Binance Testnet (True/False)
BINANCE_TESTNET=True

# Security Settings
USE_ENCRYPTED_SECRETS=True
SECRETS_CONFIG_DIR=config
"""
    
    example_path = project_root / '.env.example'
    with open(example_path, 'w') as f:
        f.write(example_content)
    
    print(f"✅ Created .env.example template")


def update_gitignore(project_root: Path):
    """Ensure sensitive files are in .gitignore."""
    gitignore_path = project_root / '.gitignore'
    
    sensitive_files = [
        '.env',
        '.env.backup_*',
        'config/.secrets.enc',
        'config/.salt'
    ]
    
    existing_lines = set()
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            existing_lines = set(line.strip() for line in f)
    
    new_lines = [f for f in sensitive_files if f not in existing_lines]
    
    if new_lines:
        with open(gitignore_path, 'a') as f:
            f.write("\n# Encrypted secrets and credentials\n")
            for line in new_lines:
                f.write(f"{line}\n")
        print(f"✅ Updated .gitignore ({len(new_lines)} entries added)")
    else:
        print("✓ .gitignore already up to date")


def show_next_steps():
    """Display post-migration instructions."""
    print("\n" + "="*60)
    print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("\n1. Update your .env file:")
    print("   Add this line:")
    print("   USE_ENCRYPTED_SECRETS=True")
    print("\n2. Test the bot with encrypted secrets:")
    print("   python run.py")
    print("   (You'll be prompted for your master password)")
    print("\n3. Optional - Remove old .env credentials:")
    print("   After confirming everything works, you can remove")
    print("   BINANCE_API_KEY and BINANCE_API_SECRET from .env")
    print("   (Keep the backup file safe!)")
    print("\n4. Password Management:")
    print("   • NEVER commit your master password to git")
    print("   • Store it in a password manager")
    print("   • To rotate password: use SecretManager.rotate_password()")
    print("\n" + "="*60)


def main():
    """Run migration process."""
    print("🔄 BiX TradeBOT - Credentials Migration")
    print("=" * 60)
    print("This script will migrate your API credentials from .env")
    print("to encrypted storage using AES-256 encryption.")
    print("=" * 60)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    env_path = project_root / '.env'
    config_dir = project_root / 'config'
    
    # Create config directory if needed
    config_dir.mkdir(exist_ok=True)
    
    # Step 1: Check if already migrated
    secrets_path = config_dir / '.secrets.enc'
    if secrets_path.exists():
        print("\n⚠️  Encrypted secrets already exist!")
        response = input("Overwrite existing secrets? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Migration cancelled.")
            return
    
    # Step 2: Backup .env file
    print("\n📦 Step 1: Backing up .env file...")
    backup_path = backup_env_file(env_path)
    
    # Step 3: Load credentials
    print("\n📥 Step 2: Loading credentials from .env...")
    creds = load_env_credentials(env_path)
    
    # Step 4: Validate credentials
    print("\n🔍 Step 3: Validating credentials...")
    if not validate_credentials(creds):
        print("\n❌ Migration aborted.")
        return
    
    # Step 5: Confirm migration
    if not confirm_migration(creds):
        print("\n❌ Migration cancelled by user.")
        return
    
    # Step 6: Get master password
    print("\n🔑 Step 4: Setting up master password...")
    password = get_master_password()
    
    # Step 7: Migrate secrets
    print("\n🔒 Step 5: Encrypting and storing credentials...")
    success = migrate_secrets(creds, password, str(config_dir))
    
    if not success:
        print("\n❌ Migration failed. Your .env file remains unchanged.")
        return
    
    # Step 8: Create .env.example
    print("\n📝 Step 6: Creating .env.example template...")
    create_env_example(project_root)
    
    # Step 9: Update .gitignore
    print("\n🔒 Step 7: Updating .gitignore...")
    update_gitignore(project_root)
    
    # Step 10: Show next steps
    show_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
