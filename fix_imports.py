"""
Fix imports in restructured files
"""
import os
import re
from pathlib import Path

def fix_imports_in_file(filepath):
    """Fix import statements in a Python file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Mapping of old imports to new imports
    replacements = {
        'from config import': 'from utils.config import',
        'from data_handler import': 'from data.handler import',
        'from indicators import': 'from data.indicators import',
        'from fundamental_news import': 'from data.news import',
        'from ml_engine import': 'from core.ml_engine import',
        'from strategy import': 'from core.strategy import',
        'from risk_manager import': 'from core.risk_manager import',
        'from ai_predictor import': 'from ai.predictor import',
        'from ai_models_config import': 'from ai.models_config import',
        'from backtest import': 'from analysis.backtest import',
        'from live_data_feed import': 'from analysis.live_feed import',
        'import config': 'from utils import config',
    }
    
    modified = False
    for old, new in replacements.items():
        if old in content:
            content = content.replace(old, new)
            modified = True
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    src_dir = Path('src')
    scripts_dir = Path('scripts')
    tests_dir = Path('tests')
    
    count = 0
    for directory in [src_dir, scripts_dir, tests_dir]:
        if directory.exists():
            for py_file in directory.rglob('*.py'):
                if fix_imports_in_file(py_file):
                    print(f"✅ Fixed: {py_file}")
                    count += 1
    
    print(f"\n✅ Fixed {count} files")

if __name__ == '__main__':
    main()
