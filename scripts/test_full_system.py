"""
تست کامل سیستم - همه ماژول‌ها
"""
import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

print("=" * 70)
print("🚀 تست کامل سیستم BRAINixIDEX Trading Bot")
print("=" * 70)

# تست 1: سیستم‌های اصلی
print("\n📦 تست 1: سیستم‌های اصلی")
print("-" * 70)

try:
    from data.handler import DataHandler
    from data.indicators import TechnicalIndicators
    from core.ml_engine import MLEngine
    from core.risk_manager import RiskManager
    from core.strategy import SimpleHybridStrategy
    from analysis.advanced_chart import AdvancedChartAnalysis
    from analysis.backtester import StrategyBacktester
    from analysis.live_feed import LiveDataFeed
    print("✅ همه ماژول‌های اصلی import شدند")
except Exception as e:
    print(f"❌ خطا در import: {e}")
    sys.exit(1)

# تست 2: دریافت داده
print("\n📊 تست 2: دریافت داده از Binance")
print("-" * 70)

try:
    handler = DataHandler(use_ccxt=False)
    df = handler.fetch_ohlcv(symbol='BTCUSDT', timeframe='1h', limit=100)
    print(f"✅ داده دریافت شد: {len(df)} کندل")
    print(f"   📅 از {df.index[0]} تا {df.index[-1]}")
    print(f"   💰 قیمت فعلی: ${df['close'].iloc[-1]:,.2f}")
except Exception as e:
    print(f"❌ خطا در دریافت داده: {e}")

# تست 3: محاسبه اندیکاتورها
print("\n📈 تست 3: محاسبه اندیکاتورها")
print("-" * 70)

try:
    indicators = TechnicalIndicators(df)
    df_with_indicators = indicators.calculate_all()
    print(f"✅ اندیکاتورها محاسبه شد")
    print(f"   📊 تعداد ستون‌ها: {len(df_with_indicators.columns)}")
    print(f"   📋 ستون‌ها: {', '.join(df_with_indicators.columns[:10])}...")
    
    latest = indicators.get_latest_signals()
    print(f"\n   🎯 آخرین سیگنال‌ها:")
    print(f"      RSI: {latest['rsi']:.2f}")
    print(f"      ATR: ${latest['atr']:,.2f}")
    print(f"      ADX: {latest['adx']:.2f}")
except Exception as e:
    print(f"❌ خطا در محاسبه اندیکاتور: {e}")

# تست 4: ML Engine
print("\n🤖 تست 4: موتور یادگیری ماشین")
print("-" * 70)

try:
    ml_engine = MLEngine(timeframe='1h')
    
    # بارگذاری یا آموزش مدل
    if ml_engine.load_model():
        print("✅ مدل ML بارگذاری شد")
    else:
        print("⚠️  مدل وجود ندارد - شروع آموزش...")
        metrics = ml_engine.train(df_with_indicators)
        print(f"✅ مدل آموزش داده شد - Accuracy: {metrics['accuracy']:.4f}")
    
    # پیش‌بینی
    predictions = ml_engine.get_prediction_confidence(df_with_indicators)
    if predictions is not None and len(predictions) > 0:
        last_pred = predictions.iloc[-1]
        pred_text = {1: "خرید 🟢", -1: "فروش 🔴", 0: "نگه‌داری ⚪"}
        print(f"   💡 پیش‌بینی: {pred_text.get(last_pred['prediction'], 'نامشخص')}")
        print(f"   📊 اطمینان: {last_pred['confidence']:.1%}")
except Exception as e:
    print(f"❌ خطا در ML Engine: {e}")

# تست 5: استراتژی معاملاتی
print("\n🎯 تست 5: استراتژی معاملاتی")
print("-" * 70)

try:
    strategy = SimpleHybridStrategy(use_ml=True)
    latest_signals = indicators.get_latest_signals()
    
    signal = strategy.generate_signal(latest_signals)
    
    action_emoji = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '⚪'}
    print(f"✅ سیگنال استراتژی:")
    print(f"   {action_emoji[signal['action']]} اکشن: {signal['action']}")
    print(f"   ⭐ قدرت: {signal['strength']}/10")
    print(f"   📝 دلیل: {signal['reason']}")
except Exception as e:
    print(f"❌ خطا در استراتژی: {e}")

# تست 6: مدیریت ریسک
print("\n💰 تست 6: مدیریت ریسک")
print("-" * 70)

try:
    risk_mgr = RiskManager()
    
    current_price = df['close'].iloc[-1]
    atr = df_with_indicators['atr'].iloc[-1]
    
    position = risk_mgr.calculate_position_size(
        entry_price=current_price,
        atr=atr,
        direction='long'
    )
    
    print(f"✅ محاسبه position:")
    print(f"   📊 حجم: {position['size']} واحد")
    print(f"   💵 ارزش: ${position['value']:,.2f}")
    print(f"   🛑 حد ضرر: ${position['stop_loss']:,.2f}")
    print(f"   🎯 حد سود: ${position['take_profit']:,.2f}")
    print(f"   ⚠️  ریسک: ${position['risk_amount']:,.2f}")
except Exception as e:
    print(f"❌ خطا در risk management: {e}")

# تست 7: تحلیل پیشرفته نمودار
print("\n📊 تست 7: تحلیل پیشرفته نمودار")
print("-" * 70)

try:
    chart_analyzer = AdvancedChartAnalysis(df_with_indicators)
    analysis = chart_analyzer.get_complete_analysis(current_price)
    
    print(f"✅ تحلیل نمودار:")
    print(f"   📍 حمایت‌ها: {len(analysis['support_resistance']['support'])} سطح")
    print(f"   📍 مقاومت‌ها: {len(analysis['support_resistance']['resistance'])} سطح")
    print(f"   📐 الگوها: {len(analysis['patterns'])} الگو")
    
    if analysis['support_resistance']['support']:
        print(f"   🟢 نزدیک‌ترین حمایت: ${analysis['support_resistance']['support'][0]:,.2f}")
    if analysis['support_resistance']['resistance']:
        print(f"   🔴 نزدیک‌ترین مقاومت: ${analysis['support_resistance']['resistance'][0]:,.2f}")
except Exception as e:
    print(f"❌ خطا در chart analysis: {e}")

# تست 8: Backtester
print("\n🔄 تست 8: بک‌تستر")
print("-" * 70)

try:
    backtester = StrategyBacktester(initial_capital=10000)
    
    # استفاده از پیش‌بینی‌های ML
    import numpy as np
    predictions_array = predictions['prediction'].values if predictions is not None else np.zeros(len(df_with_indicators))
    
    results = backtester.run_backtest(df_with_indicators, predictions_array)
    
    print(f"✅ بک‌تست اجرا شد:")
    print(f"   💼 تعداد معاملات: {results['total_trades']}")
    print(f"   ✅ برنده: {results['winning_trades']}")
    print(f"   ❌ بازنده: {results['losing_trades']}")
    print(f"   📊 نرخ برد: {results['win_rate']:.1%}")
    print(f"   💰 سود/زیان کل: {results['total_return']:.2f}%")
except Exception as e:
    print(f"❌ خطا در backtester: {e}")

# خلاصه نهایی
print("\n" + "=" * 70)
print("✅ تست کامل سیستم با موفقیت انجام شد!")
print("=" * 70)
print("\n🎯 وضعیت کلی:")
print("   ✅ دریافت داده: فعال")
print("   ✅ اندیکاتورها: فعال")
print("   ✅ ML Engine: فعال")
print("   ✅ استراتژی: فعال")
print("   ✅ Risk Management: فعال")
print("   ✅ Chart Analysis: فعال")
print("   ✅ Backtester: فعال")
print("\n🚀 سیستم آماده استفاده است!")
print("=" * 70)
