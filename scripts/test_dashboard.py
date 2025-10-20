"""
تست سریع Dashboard برای یافتن خطاها
"""
import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

print("=" * 60)
print("🧪 تست ماژول‌های Dashboard")
print("=" * 60)

# Test 1: Import modules
print("\n1️⃣ تست Import ماژول‌ها...")
try:
    from utils.config import Config
    print("   ✅ Config")
except Exception as e:
    print(f"   ❌ Config: {e}")

try:
    from data.handler import DataHandler
    print("   ✅ DataHandler")
except Exception as e:
    print(f"   ❌ DataHandler: {e}")

try:
    from data.indicators import TechnicalIndicators
    print("   ✅ TechnicalIndicators")
except Exception as e:
    print(f"   ❌ TechnicalIndicators: {e}")

try:
    from core.ml_engine import MLEngine
    print("   ✅ MLEngine")
except Exception as e:
    print(f"   ❌ MLEngine: {e}")

try:
    from core.risk_manager import RiskManager
    print("   ✅ RiskManager")
except Exception as e:
    print(f"   ❌ RiskManager: {e}")

try:
    from core.strategy import SimpleHybridStrategy
    print("   ✅ SimpleHybridStrategy")
except Exception as e:
    print(f"   ❌ SimpleHybridStrategy: {e}")

try:
    from utils.logger import get_logger
    print("   ✅ Logger")
except Exception as e:
    print(f"   ❌ Logger: {e}")

try:
    from analysis.advanced_chart import AdvancedChartAnalysis
    print("   ✅ AdvancedChartAnalysis")
except Exception as e:
    print(f"   ❌ AdvancedChartAnalysis: {e}")

try:
    from analysis.backtester import BacktestEngine
    print("   ✅ BacktestEngine")
except Exception as e:
    print(f"   ⚠️  BacktestEngine: {e}")

try:
    from analysis.live_feed import LiveDataFeed
    print("   ✅ LiveDataFeed")
except Exception as e:
    print(f"   ⚠️  LiveDataFeed: {e}")

# Test 2: Initialize components
print("\n2️⃣ تست اجرای کامپوننت‌ها...")
try:
    handler = DataHandler(use_ccxt=False)
    print("   ✅ DataHandler initialized")
except Exception as e:
    print(f"   ❌ DataHandler init: {e}")

try:
    risk_mgr = RiskManager()
    print("   ✅ RiskManager initialized")
except Exception as e:
    print(f"   ❌ RiskManager init: {e}")

try:
    ml_engine = MLEngine()
    print("   ✅ MLEngine initialized")
except Exception as e:
    print(f"   ❌ MLEngine init: {e}")

# Test 3: Fetch data
print("\n3️⃣ تست دریافت داده...")
try:
    df = handler.fetch_ohlcv(symbol='BTCUSDT', timeframe='1h', limit=100)
    print(f"   ✅ داده دریافت شد: {len(df)} کندل")
    print(f"   📊 ستون‌ها: {list(df.columns)}")
except Exception as e:
    print(f"   ❌ خطا در دریافت داده: {e}")

# Test 4: Calculate indicators
print("\n4️⃣ تست محاسبه اندیکاتورها...")
try:
    from data.indicators import TechnicalIndicators
    indicators = TechnicalIndicators(df)
    df_with_indicators = indicators.calculate_all()
    print(f"   ✅ اندیکاتورها محاسبه شد: {df_with_indicators.shape}")
    print(f"   📊 ستون‌های جدید: {len(df_with_indicators.columns)}")
except Exception as e:
    print(f"   ❌ خطا در محاسبه اندیکاتور: {e}")

print("\n" + "=" * 60)
print("✅ تست‌ها تکمیل شد!")
print("=" * 60)
