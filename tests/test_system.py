"""
BiX TradeBOT - تست سریع سیستم کامل
======================================
تست یکپارچه تمام قابلیت‌های سیستم

Author: SALMAN ThinkTank AI Core
Version: 2.0.0
"""

import logging
from datetime import datetime

# تنظیم لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_data_fetching():
    """تست دریافت داده"""
    print("\n" + "="*70)
    print("📊 TEST 1: Data Fetching")
    print("="*70)
    
    try:
        from data.handler import DataHandler
        
        handler = DataHandler()
        df = handler.fetch_ohlcv(symbol="BTCUSDT", timeframe="1h", limit=100)
        
        print(f"✅ داده دریافت شد: {len(df)} کندل")
        print(f"   از تاریخ: {df.index[0]}")
        print(f"   تا تاریخ: {df.index[-1]}")
        return True
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False


def test_indicators():
    """تست محاسبه اندیکاتورها"""
    print("\n" + "="*70)
    print("📈 TEST 2: Technical Indicators")
    print("="*70)
    
    try:
        from data.handler import DataHandler
        from data.indicators import TechnicalIndicators
        
        handler = DataHandler()
        df = handler.fetch_ohlcv(symbol="BTCUSDT", timeframe="1h", limit=200)
        
        indicators = TechnicalIndicators(df)
        df_with_indicators = indicators.calculate_all()
        
        indicator_cols = [col for col in df_with_indicators.columns 
                         if col not in ['open', 'high', 'low', 'close', 'volume']]
        
        print(f"✅ اندیکاتورها محاسبه شدند: {len(indicator_cols)} مورد")
        print(f"   لیست: {', '.join(indicator_cols[:5])}...")
        return True
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False


def test_ml_engine():
    """تست موتور ML"""
    print("\n" + "="*70)
    print("🤖 TEST 3: ML Engine (Auto Load/Train)")
    print("="*70)
    
    try:
        from data.handler import DataHandler
        from data.indicators import TechnicalIndicators
        from core.ml_engine import MLEngine
        
        # دریافت داده
        handler = DataHandler()
        df = handler.fetch_ohlcv(symbol="BTCUSDT", timeframe="1h", limit=500)
        
        # اندیکاتورها
        indicators = TechnicalIndicators(df)
        df = indicators.calculate_all()
        
        # ML Engine با بارگذاری یا آموزش خودکار
        ml_engine = MLEngine(timeframe="1h")
        
        # تست بارگذاری خودکار
        ready = ml_engine.auto_load_or_train(df)
        
        if ready:
            print(f"✅ مدل آماده است")
            
            # تست پیش‌بینی
            predictions = ml_engine.predict(df)
            
            if predictions is not None:
                last_signal = predictions[-1]
                signal_name = {-1: "SELL", 0: "HOLD", 1: "BUY"}[last_signal]
                print(f"   آخرین پیش‌بینی: {signal_name}")
                return True
            else:
                print("⚠️ پیش‌بینی خالی است")
                return False
        else:
            print("❌ مدل آماده نشد")
            return False
            
    except Exception as e:
        print(f"❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fundamental_news():
    """تست سیستم اخبار فاندامنتال"""
    print("\n" + "="*70)
    print("📰 TEST 4: Fundamental News Analysis")
    print("="*70)
    
    try:
        from data.news import FundamentalNewsAnalyzer
        
        # تحلیل Bitcoin
        analyzer = FundamentalNewsAnalyzer("BTCUSDT")
        report = analyzer.generate_comprehensive_report()
        
        # ذخیره
        filepath = analyzer.save_report_to_json(report)
        
        # نمایش نتایج
        print(f"✅ گزارش تولید شد")
        print(f"   📊 تعداد اخبار: {report['statistics']['total_news']}")
        print(f"   💡 تعداد ایده‌ها: {report['statistics']['total_ideas']}")
        print(f"   🎯 سنتیمنت: {report['overall_analysis']['sentiment'].upper()}")
        print(f"   📈 توصیه: {report['overall_analysis']['recommendation']}")
        print(f"   💾 فایل: {filepath}")
        
        return True
    except Exception as e:
        print(f"❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_combined_analysis():
    """تست ترکیب سیگنال‌های تکنیکال + فاندامنتال"""
    print("\n" + "="*70)
    print("🎯 TEST 5: Combined Analysis (Technical + Fundamental)")
    print("="*70)
    
    try:
        from data.handler import DataHandler
        from data.indicators import TechnicalIndicators
        from core.ml_engine import MLEngine
        from data.news import FundamentalNewsAnalyzer
        
        symbol = "BTCUSDT"
        
        # 1. تحلیل تکنیکال
        print("   🔧 در حال تحلیل تکنیکال...")
        handler = DataHandler()
        df = handler.fetch_ohlcv(symbol=symbol, timeframe="1h", limit=500)
        
        indicators = TechnicalIndicators(df)
        df = indicators.calculate_all()
        
        ml_engine = MLEngine(timeframe="1h")
        ml_engine.auto_load_or_train(df)
        predictions = ml_engine.predict(df)
        
        tech_signal = predictions[-1] if predictions is not None else 0
        tech_name = {-1: "SELL", 0: "HOLD", 1: "BUY"}[tech_signal]
        
        print(f"   ✅ سیگنال تکنیکال: {tech_name} ({tech_signal})")
        
        # 2. تحلیل فاندامنتال
        print("   📰 در حال تحلیل اخبار...")
        news_analyzer = FundamentalNewsAnalyzer(symbol)
        report = news_analyzer.generate_comprehensive_report()
        
        sentiment = report['overall_analysis']['sentiment']
        fund_signal = 1 if sentiment == 'bullish' else (
            -1 if sentiment == 'bearish' else 0
        )
        
        print(f"   ✅ سیگنال فاندامنتال: {sentiment.upper()} ({fund_signal})")
        
        # 3. ترکیب سیگنال‌ها
        print("\n   🎯 ترکیب سیگنال‌ها (60% تکنیکال + 40% فاندامنتال)...")
        
        combined_score = (0.6 * tech_signal) + (0.4 * fund_signal)
        
        if combined_score > 0.3:
            final_signal = "BUY 🟢"
        elif combined_score < -0.3:
            final_signal = "SELL 🔴"
        else:
            final_signal = "HOLD ⚪"
        
        print(f"\n   📊 نتیجه نهایی:")
        print(f"      امتیاز ترکیبی: {combined_score:.2f}")
        print(f"      سیگنال نهایی: {final_signal}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """اجرای تمام تست‌ها"""
    
    print("\n" + "="*70)
    print("🚀 BiX TradeBOT - تست کامل سیستم v2.0")
    print("="*70)
    print(f"⏰ زمان شروع: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # اجرای تست‌ها
    results['data'] = test_data_fetching()
    results['indicators'] = test_indicators()
    results['ml_engine'] = test_ml_engine()
    results['news'] = test_fundamental_news()
    results['combined'] = test_combined_analysis()
    
    # خلاصه نتایج
    print("\n" + "="*70)
    print("📊 خلاصه نتایج تست‌ها")
    print("="*70)
    
    test_names = {
        'data': 'دریافت داده',
        'indicators': 'اندیکاتورهای تکنیکال',
        'ml_engine': 'موتور ML',
        'news': 'تحلیل اخبار',
        'combined': 'ترکیب سیگنال‌ها'
    }
    
    passed = 0
    total = len(results)
    
    for key, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_names[key]:.<50} {status}")
        if result:
            passed += 1
    
    print("\n" + "="*70)
    print(f"📈 نتیجه کلی: {passed}/{total} تست موفق ({passed/total*100:.0f}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 تمام تست‌ها موفق بودند! سیستم آماده است.")
    else:
        print(f"\n⚠️ {total-passed} تست ناموفق. لطفاً خطاها را بررسی کنید.")
    
    print(f"\n⏰ زمان پایان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
