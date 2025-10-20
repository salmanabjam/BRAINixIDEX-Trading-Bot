# 📰 راهنمای سیستم تحلیل اخبار فاندامنتال - BiX TradeBOT
## دریافت و تحلیل اخبار از TradingView

---

## 🎯 امکانات سیستم

✅ **دریافت خودکار اخبار** از TradingView برای هر ارز دیجیتال  
✅ **تحلیل سنتیمنت** (مثبت/منفی/خنثی) با هوش مصنوعی  
✅ **دریافت ایده‌های تحلیلی** کاربران TradingView  
✅ **بررسی گفتگوهای عمومی** و نظرات معامله‌گران  
✅ **ذخیره ساختاریافته** در فایل JSON  
✅ **پشتیبانی از تمام ارزهای Binance** (BTC, ETH, ADA, SOL, ...)  

---

## 🚀 نحوه استفاده

### روش 1: استفاده از دستور ساده

```python
from fundamental_news import FundamentalNewsAnalyzer

# برای تحلیل ADA
analyzer = FundamentalNewsAnalyzer("ADAUSDT")
report = analyzer.generate_comprehensive_report()
filepath = analyzer.save_report_to_json(report)

print(f"گزارش ذخیره شد: {filepath}")
print(f"سیگنال: {report['overall_analysis']['recommendation']}")
```

### روش 2: تست چندین ارز

```python
# لیست ارزهای مورد نظر
symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "BNBUSDT"]

for symbol in symbols:
    analyzer = FundamentalNewsAnalyzer(symbol)
    report = analyzer.generate_comprehensive_report()
    filepath = analyzer.save_report_to_json(report)
    
    print(f"\n{'='*60}")
    print(f"📊 {symbol}")
    print(f"✅ فایل: {filepath}")
    print(f"📈 سنتیمنت: {report['overall_analysis']['sentiment']}")
    print(f"🎯 توصیه: {report['overall_analysis']['recommendation']}")
    print(f"💯 اطمینان: {report['overall_analysis']['confidence']*100:.1f}%")
```

### روش 3: بارگذاری آخرین گزارش

```python
analyzer = FundamentalNewsAnalyzer("ADAUSDT")

# بارگذاری آخرین گزارش ذخیره‌شده
latest_report = analyzer.get_latest_report()

if latest_report:
    print("📊 آخرین تحلیل:")
    print(f"زمان: {latest_report['metadata']['generated_at']}")
    print(f"سیگنال: {latest_report['overall_analysis']['recommendation']}")
else:
    print("⚠️ هنوز گزارشی ذخیره نشده")
```

---

## 📁 ساختار فایل JSON خروجی

```json
{
  "metadata": {
    "symbol": "ADAUSDT",           // نماد ارز
    "exchange": "BINANCE",         // صرافی
    "base_currency": "ADA",        // ارز پایه
    "generated_at": "2025-10-20...", // زمان تولید
    "timezone": "UTC"              // منطقه زمانی
  },
  
  "news_headlines": {
    "total_count": 25,             // تعداد اخبار
    "items": [                     // لیست اخبار
      {
        "id": "...",
        "title": "...",            // عنوان خبر
        "published": "...",        // تاریخ انتشار
        "source": "CoinDesk",      // منبع خبر
        "link": "https://...",     // لینک خبر
        "sentiment": "bullish",    // سنتیمنت (bullish/bearish/neutral)
        "tags": ["defi", "cardano"]
      }
    ],
    "sources": ["CoinDesk", "CoinTelegraph", ...],
    "sentiment_breakdown": {
      "bullish": 15,               // تعداد اخبار مثبت
      "bearish": 5,                // تعداد اخبار منفی
      "neutral": 5                 // تعداد اخبار خنثی
    }
  },
  
  "community_ideas": {
    "total_count": 12,             // تعداد ایده‌های تحلیلی
    "items": [
      {
        "title": "ADA Breakout!",
        "author": "trader123",
        "likes": 150,
        "isLong": true,            // آیا سیگنال خرید؟
        "isShort": false,          // آیا سیگنال فروش؟
        "sentiment": "bullish"
      }
    ]
  },
  
  "conversation_status": {
    "conversation_count": 45,      // تعداد گفتگوها
    "active_users": 120,           // کاربران فعال
    "bullish_mentions": 30,        // اشاره‌های مثبت
    "bearish_mentions": 15,        // اشاره‌های منفی
    "sentiment_score": 0.35        // امتیاز کلی (-1 تا +1)
  },
  
  "overall_analysis": {
    "sentiment": "bullish",        // سنتیمنت نهایی
    "sentiment_score": 0.42,       // امتیاز (-1 تا +1)
    "confidence": 0.75,            // اطمینان (0 تا 1)
    "recommendation": "BUY - سیگنال مثبت قوی",
    "key_factors": [
      "25 خبر تازه منتشر شده",
      "12 تحلیل کاربران",
      "45 گفتگوی فعال"
    ]
  },
  
  "statistics": {
    "total_news": 25,
    "total_ideas": 12,
    "bullish_signals": 20,
    "bearish_signals": 5,
    "neutral_signals": 12
  }
}
```

---

## 🔄 تغییر ارز دیجیتال

برای دریافت اخبار هر ارز دیجیتال، کافیست نماد آن را تغییر دهید:

```python
# Bitcoin
analyzer_btc = FundamentalNewsAnalyzer("BTCUSDT")

# Ethereum
analyzer_eth = FundamentalNewsAnalyzer("ETHUSDT")

# Cardano
analyzer_ada = FundamentalNewsAnalyzer("ADAUSDT")

# Solana
analyzer_sol = FundamentalNewsAnalyzer("SOLUSDT")

# Binance Coin
analyzer_bnb = FundamentalNewsAnalyzer("BNBUSDT")

# Ripple
analyzer_xrp = FundamentalNewsAnalyzer("XRPUSDT")

# Dogecoin
analyzer_doge = FundamentalNewsAnalyzer("DOGEUSDT")

# Polkadot
analyzer_dot = FundamentalNewsAnalyzer("DOTUSDT")

# Avalanche
analyzer_avax = FundamentalNewsAnalyzer("AVAXUSDT")

# Polygon
analyzer_matic = FundamentalNewsAnalyzer("MATICUSDT")
```

---

## 📊 نحوه تفسیر سنتیمنت

### Bullish (صعودی) 🟢
- **سیگنال:** خرید (BUY)
- **توضیح:** اخبار مثبت، احتمال رشد قیمت بالا
- **اقدام پیشنهادی:** ورود به معامله خرید

### Bearish (نزولی) 🔴
- **سیگنال:** فروش (SELL)
- **توضیح:** اخبار منفی، احتمال افت قیمت بالا
- **اقدام پیشنهادی:** خروج یا فروش

### Neutral (خنثی) ⚪
- **سیگنال:** نگهداری (HOLD)
- **توضیح:** اخبار متناقض یا ناکافی
- **اقدام پیشنهادی:** صبر و نظاره

---

## 🎓 مثال عملی کامل

```python
from fundamental_news import FundamentalNewsAnalyzer
import json

def analyze_crypto(symbol):
    """تحلیل کامل یک ارز دیجیتال"""
    
    print(f"\n{'='*70}")
    print(f"🔍 در حال تحلیل {symbol}...")
    print(f"{'='*70}")
    
    # ایجاد تحلیلگر
    analyzer = FundamentalNewsAnalyzer(symbol)
    
    # دریافت گزارش
    report = analyzer.generate_comprehensive_report()
    
    # ذخیره در فایل
    filepath = analyzer.save_report_to_json(report)
    
    # نمایش خلاصه
    print(f"\n📰 تعداد اخبار: {report['statistics']['total_news']}")
    print(f"💡 تعداد ایده‌ها: {report['statistics']['total_ideas']}")
    print(f"💬 تعداد گفتگوها: {report['conversation_status']['conversation_count']}")
    
    print(f"\n📊 تحلیل سنتیمنت:")
    print(f"  🟢 سیگنال‌های مثبت: {report['statistics']['bullish_signals']}")
    print(f"  🔴 سیگنال‌های منفی: {report['statistics']['bearish_signals']}")
    print(f"  ⚪ سیگنال‌های خنثی: {report['statistics']['neutral_signals']}")
    
    print(f"\n🎯 نتیجه نهایی:")
    print(f"  سنتیمنت: {report['overall_analysis']['sentiment'].upper()}")
    print(f"  امتیاز: {report['overall_analysis']['sentiment_score']:.2f}")
    print(f"  اطمینان: {report['overall_analysis']['confidence']*100:.1f}%")
    print(f"  📈 توصیه: {report['overall_analysis']['recommendation']}")
    
    print(f"\n💾 فایل ذخیره شد: {filepath}")
    
    return report

# مثال: تحلیل 5 ارز برتر
top_cryptos = [
    "BTCUSDT",   # Bitcoin
    "ETHUSDT",   # Ethereum
    "BNBUSDT",   # Binance Coin
    "ADAUSDT",   # Cardano
    "SOLUSDT"    # Solana
]

all_reports = {}

for crypto in top_cryptos:
    report = analyze_crypto(crypto)
    all_reports[crypto] = report

# مقایسه سنتیمنت‌ها
print(f"\n\n{'='*70}")
print("📊 خلاصه مقایسه سنتیمنت ارزها")
print(f"{'='*70}")

for symbol, report in all_reports.items():
    sentiment = report['overall_analysis']['sentiment']
    confidence = report['overall_analysis']['confidence'] * 100
    
    emoji = "🟢" if sentiment == "bullish" else ("🔴" if sentiment == "bearish" else "⚪")
    
    print(f"{emoji} {symbol:12} | {sentiment:8} | اطمینان: {confidence:5.1f}%")
```

---

## ⚙️ لینک‌های TradingView

سیستم از 4 نوع لینک TradingView استفاده می‌کند:

### 1. اخبار سرخط (Headlines - Landing)
```
https://news-headlines.tradingview.com/v2/view/headlines/symbol?client=landing&lang=en&section=&streaming=true&symbol=BINANCE%3AADAUSDT
```

### 2. اخبار خلاصه (Headlines - Overview)
```
https://news-headlines.tradingview.com/v2/view/headlines/symbol?client=overview&lang=en&symbol=BINANCE%3AADAUSDT
```

### 3. ایده‌های کاربران (Community Ideas)
```
https://www.tradingview.com/symbols/ADAUSDT/ideas/?exchange=BINANCE&component-data-only=1
```

### 4. وضعیت گفتگوها (Conversation Status)
```
https://www.tradingview.com/conversation-status/?_rand=0.008761372115593025&offset=0&room_id=general&stat_symbol=BINANCE%3AADAUSDT&is_private=
```

**نکته:** برای تغییر ارز، فقط `ADA` را با نماد دلخواه (مثل `SOL`, `BTC`, `ETH`) جایگزین کنید.

---

## 🔧 عیب‌یابی

### مشکل: اخبار دریافت نمی‌شود
**راه حل:**
```python
# بررسی اتصال اینترنت
import requests
response = requests.get("https://www.tradingview.com")
print(response.status_code)  # باید 200 باشد
```

### مشکل: JSON خالی است
**راه حل:**
- احتمالاً TradingView Rate Limiting دارد
- چند ثانیه صبر کنید و دوباره امتحان کنید
- از VPN استفاده کنید

### مشکل: خطای Timeout
**راه حل:**
```python
# افزایش timeout
analyzer = FundamentalNewsAnalyzer("BTCUSDT")
# در کد داخلی timeout=10 است، می‌توانید آن را افزایش دهید
```

---

## 📝 نکات مهم

1. ✅ **استفاده معقول:** زیاد درخواست نکنید (Rate Limiting)
2. ✅ **ذخیره منظم:** گزارش‌ها را برای تحلیل آینده نگه دارید
3. ✅ **ترکیب با تحلیل تکنیکال:** اخبار را با اندیکاتورها ترکیب کنید
4. ✅ **بررسی Confidence:** به گزارش‌های با اطمینان بالا (>70%) بیشتر توجه کنید
5. ✅ **تحلیل چند منبع:** فقط به یک منبع اکتفا نکنید

---

## 🎯 ادغام با سیستم معاملاتی

```python
from fundamental_news import FundamentalNewsAnalyzer
from ml_engine import MLEngine
from data_handler import DataHandler

# 1. دریافت اخبار
news_analyzer = FundamentalNewsAnalyzer("BTCUSDT")
news_report = news_analyzer.generate_comprehensive_report()
fundamental_signal = news_report['overall_analysis']['sentiment']

# 2. تحلیل تکنیکال
handler = DataHandler()
df = handler.fetch_ohlcv(symbol="BTCUSDT", limit=500)

ml_engine = MLEngine(timeframe="1h")
ml_engine.auto_load_or_train(df)
technical_predictions = ml_engine.predict(df)

# 3. ترکیب سیگنال‌ها
def combine_signals(fundamental, technical_pred):
    """ترکیب هوشمند سیگنال‌های فاندامنتال و تکنیکال"""
    
    # وزن‌دهی: 40% فاندامنتال، 60% تکنیکال
    fund_score = 1 if fundamental == 'bullish' else (-1 if fundamental == 'bearish' else 0)
    tech_score = technical_pred[-1]  # آخرین پیش‌بینی
    
    combined_score = (0.4 * fund_score) + (0.6 * tech_score)
    
    if combined_score > 0.3:
        return "BUY"
    elif combined_score < -0.3:
        return "SELL"
    else:
        return "HOLD"

final_signal = combine_signals(fundamental_signal, technical_predictions)
print(f"🎯 سیگنال نهایی: {final_signal}")
```

---

## 📞 پشتیبانی

در صورت بروز مشکل:
1. فایل‌های JSON ذخیره‌شده را بررسی کنید
2. لاگ‌های سیستم را چک کنید
3. نسخه Python و کتابخانه‌ها را بررسی کنید

---

**نسخه:** 2.0.0  
**تاریخ:** 2025-10-20  
**توسعه‌دهنده:** SALMAN ThinkTank AI Core  
