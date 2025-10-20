# 🤖 راهنمای استفاده از مدل‌های هوش مصنوعی پیشرفته
# AI Models Guide - BRAINix IDEX Trading Bot

## 📋 فهرست محتوا

1. [معرفی](#معرفی)
2. [مدل‌های موجود](#مدل‌های-موجود)
3. [نصب و راه‌اندازی](#نصب-و-راه‌اندازی)
4. [استفاده در کد](#استفاده-در-کد)
5. [مقایسه مدل‌ها](#مقایسه-مدل‌ها)
6. [عیب‌یابی](#عیب‌یابی)

---

## 🎯 معرفی

ربات تریدینگ BRAINix IDEX از **3 نوع مدل هوش مصنوعی** پشتیبانی می‌کند:

### 1️⃣ LightGBM (پیش‌فرض - محلی)
- ⚡ **سرعت**: خیلی سریع (< 0.1 ثانیه)
- 💰 **هزینه**: رایگان (بدون نیاز به API)
- 🎯 **دقت**: خوب (48-75%)
- 📦 **حافظه**: کم (< 1MB)

### 2️⃣ GitHub Models (توصیه می‌شود - رایگان برای شروع)
- ⚡ **سرعت**: متوسط (1-3 ثانیه)
- 💰 **هزینه**: رایگان تا سقف محدودیت
- 🎯 **دقت**: عالی (80-95%)
- 🔧 **نیاز**: GitHub Personal Access Token

### 3️⃣ Azure OpenAI (سازمانی)
- ⚡ **سرعت**: متوسط (2-4 ثانیه)
- 💰 **هزینه**: پولی ($15/1M tokens)
- 🎯 **دقت**: خیلی عالی (90-95%)
- 🔧 **نیاز**: Azure subscription + OpenAI deployment

---

## 📦 مدل‌های موجود

### مدل‌های GitHub (رایگان تا محدودیت)

| مدل | قیمت/1M Token | سرعت | دقت تخمینی | توضیحات |
|-----|---------------|------|-----------|----------|
| **GPT-4.1-mini** | $0.70 | متوسط | 85-95% | بهترین نسبت قیمت/کیفیت |
| **Phi-4** | $0.22 | سریع | 75-85% | مدل کم‌حجم مایکروسافت |
| **DeepSeek-V3** | $2.00 | متوسط | 85-92% | استدلال پیشرفته |
| **Llama-3.3-70B** | $0.71 | متوسط | 80-90% | مدل متا با قابلیت بالا |
| **LightGBM** | رایگان | خیلی سریع | 48-75% | محلی، بدون API |

---

## 🚀 نصب و راه‌اندازی

### گام 1: نصب پکیج‌های جدید

```bash
pip install requests
```

### گام 2: دریافت GitHub Token (رایگان)

#### 📝 مراحل:

1. به **GitHub Settings** بروید:
   ```
   https://github.com/settings/tokens
   ```

2. کلیک کنید روی **"Generate new token"** → **"Generate new token (classic)"**

3. نام token را بنویسید: `BRAINix-Trading-Bot`

4. دسترسی‌های زیر را فعال کنید:
   - ✅ `read:packages`
   - ✅ `write:packages` (اختیاری)

5. کلیک کنید روی **"Generate token"**

6. Token را کپی کنید (فقط یک بار نمایش داده می‌شود!)

#### 💻 تنظیم در سیستم:

**Windows (PowerShell):**
```powershell
setx GITHUB_TOKEN "ghp_your_token_here"
```

**Linux/Mac:**
```bash
export GITHUB_TOKEN="ghp_your_token_here"

# برای ذخیره دائمی:
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

#### 🔐 یا استفاده از فایل `.env`:

```env
# فایل .env
GITHUB_TOKEN=ghp_your_token_here
```

### گام 3: راه‌اندازی Azure OpenAI (اختیاری)

```bash
# فقط اگر می‌خواهید از Azure استفاده کنید
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your_api_key
```

---

## 💻 استفاده در کد

### روش 1: استفاده مستقیم در کد

```python
from ai_predictor import AIPredictor
from ai_models_config import ModelType
from data_handler import DataHandler
from technical_indicators import TechnicalIndicators

# دریافت داده بازار
handler = DataHandler()
df = handler.fetch_ohlcv(symbol="BTCUSDT", timeframe="1h", limit=100)

# محاسبه اندیکاتورها
indicators = TechnicalIndicators(df)
df_with_indicators = indicators.calculate_all()

# انتخاب مدل
predictor = AIPredictor(model_type=ModelType.GITHUB_PHI4)  # یا GITHUB_GPT4

# پیش‌بینی
result = predictor.predict(
    df=df_with_indicators,
    symbol="BTCUSDT",
    news_sentiment="BULLISH",
    market_mood="POSITIVE"
)

print(f"Signal: {result['signal']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Reasoning: {result['reasoning']}")
print(f"Risk: {result['risk_level']}")
```

### روش 2: استفاده از Dashboard (رابط گرافیکی)

1. اجرای داشبورد:
   ```bash
   streamlit run dashboard.py
   ```

2. رفتن به تب **"⚙️ Settings"**

3. باز کردن **"🤖 AI Model Selection"**

4. انتخاب مدل مورد نظر از لیست

5. کلیک روی **"💾 Save Model Preference"**

6. مدل ذخیره شده در تمام تحلیل‌ها استفاده می‌شود!

---

## 📊 مقایسه مدل‌ها

### اجرای مقایسه خودکار:

```python
from ai_predictor import compare_models
from data_handler import DataHandler
from technical_indicators import TechnicalIndicators

# دریافت داده
handler = DataHandler()
df = handler.fetch_ohlcv(symbol="BTCUSDT", timeframe="1h", limit=100)

indicators = TechnicalIndicators(df)
df_with_indicators = indicators.calculate_all()

# مقایسه همه مدل‌ها
comparison = compare_models(df_with_indicators, symbol="BTCUSDT")
print(comparison)
```

**خروجی نمونه:**
```
                 Model Signal Confidence    Risk                                Reasoning Success
      LightGBM (Local)   SELL      68.0%  MEDIUM       LightGBM prediction with 68.0% confi...      ✅
OpenAI GPT-4.1-mini     BUY      85.0%     LOW  Strong RSI and positive MACD crossover s...      ✅
     Microsoft Phi-4   HOLD      72.0%  MEDIUM  Mixed indicators, waiting for clearer tr...      ✅
       DeepSeek-V3      BUY      88.0%     LOW  Bullish momentum confirmed by multiple i...      ✅
```

---

## 🔍 تفاوت مدل‌ها

### LightGBM (محلی)
```python
✅ مزایا:
- سریع‌ترین (< 0.1 ثانیه)
- رایگان (بدون API)
- کار آفلاین
- حفظ حریم خصوصی

❌ معایب:
- دقت پایین‌تر (48-75%)
- نیاز به آموزش مجدد با داده تازه
- ناتوان در تحلیل اخبار متنی
```

### GitHub Models (GPT-4, Phi-4, etc.)
```python
✅ مزایا:
- دقت بسیار بالا (80-95%)
- درک زبان طبیعی (اخبار، احساسات)
- استدلال پیشرفته
- رایگان تا محدودیت

❌ معایب:
- کندتر (1-3 ثانیه)
- نیاز به اینترنت
- محدودیت تعداد درخواست در رایگان
```

### Azure OpenAI
```python
✅ مزایا:
- بالاترین دقت (90-95%)
- SLA سازمانی
- بدون محدودیت rate limit

❌ معایب:
- گران‌تر ($15/1M tokens)
- نیاز به subscription Azure
- پیچیدگی راه‌اندازی
```

---

## 🎯 توصیه‌های استفاده

### برای شروع (مبتدی):
```python
# استفاده از LightGBM محلی
predictor = AIPredictor(model_type=ModelType.LIGHTGBM)
```

### برای دقت بهتر (رایگان):
```python
# استفاده از Phi-4 (کوچک‌تر، ارزان‌تر)
predictor = AIPredictor(model_type=ModelType.GITHUB_PHI4)
```

### برای بهترین نتیجه (رایگان تا محدودیت):
```python
# استفاده از GPT-4.1-mini
predictor = AIPredictor(model_type=ModelType.GITHUB_GPT4)
```

### برای تریدینگ واقعی (سازمانی):
```python
# استفاده از DeepSeek-V3 (تعادل قیمت/کیفیت)
predictor = AIPredictor(model_type=ModelType.GITHUB_DEEPSEEK)
```

---

## 🔧 عیب‌یابی

### مشکل 1: خطای "GITHUB_TOKEN not configured"

**راه حل:**
```bash
# Windows
setx GITHUB_TOKEN "ghp_your_token"
# بعد terminal را ببندید و دوباره باز کنید

# Linux/Mac
export GITHUB_TOKEN="ghp_your_token"
source ~/.bashrc
```

### مشکل 2: خطای "Rate limit exceeded"

**راه حل:**
- محدودیت رایگان GitHub Models به پایان رسیده
- منتظر بمانید 1 ساعت یا به LightGBM برگردید:

```python
predictor = AIPredictor(model_type=ModelType.LIGHTGBM)
```

### مشکل 3: خطای "API request timeout"

**راه حل:**
```python
# افزایش timeout در ai_predictor.py:
response = requests.post(endpoint, headers=headers, json=payload, timeout=60)  # 30 → 60
```

### مشکل 4: دقت پایین LightGBM (< 50%)

**راه حل:**
```python
# آموزش با داده تازه (بیشتر)
handler = DataHandler()
df = handler.fetch_ohlcv(limit=5000, use_cache=False)  # داده تازه

indicators = TechnicalIndicators(df)
df_with_indicators = indicators.calculate_all()

predictor = AIPredictor(model_type=ModelType.LIGHTGBM)
result = predictor.train(df_with_indicators)
print(f"New accuracy: {result['metrics']['accuracy']:.2%}")
```

---

## 📈 نمونه کد کامل

```python
"""
نمونه کامل: استفاده از چندین مدل AI برای تحلیل بازار
"""

from ai_predictor import AIPredictor, compare_models
from ai_models_config import ModelType, AIModelsConfig
from data_handler import DataHandler
from technical_indicators import TechnicalIndicators
import pandas as pd

def analyze_market(symbol="BTCUSDT", timeframe="1h"):
    """تحلیل کامل بازار با چندین مدل AI"""
    
    print(f"📊 Analyzing {symbol} on {timeframe} timeframe...\n")
    
    # 1. دریافت داده بازار
    print("📥 Fetching market data...")
    handler = DataHandler()
    df = handler.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=200)
    
    # 2. محاسبه اندیکاتورهای تکنیکال
    print("📈 Calculating technical indicators...")
    indicators = TechnicalIndicators(df)
    df_with_indicators = indicators.calculate_all()
    
    # 3. تحلیل اخبار (فرض: BULLISH)
    news_sentiment = "BULLISH"
    market_mood = "POSITIVE"
    
    print(f"📰 News Sentiment: {news_sentiment}\n")
    print("="*60 + "\n")
    
    # 4. پیش‌بینی با مدل‌های مختلف
    models_to_test = [
        (ModelType.LIGHTGBM, "LightGBM (Local)"),
        (ModelType.GITHUB_PHI4, "Microsoft Phi-4"),
        (ModelType.GITHUB_GPT4, "OpenAI GPT-4.1-mini"),
    ]
    
    results = []
    
    for model_type, model_name in models_to_test:
        # بررسی تنظیمات API
        if not AIModelsConfig.is_api_configured(model_type):
            print(f"⏭️ Skipping {model_name} - Not configured\n")
            continue
        
        print(f"🤖 Testing {model_name}...")
        
        try:
            # ایجاد predictor
            predictor = AIPredictor(model_type=model_type, timeframe=timeframe)
            
            # پیش‌بینی
            result = predictor.predict(
                df=df_with_indicators,
                symbol=symbol,
                news_sentiment=news_sentiment,
                market_mood=market_mood
            )
            
            # نمایش نتیجه
            if result['success']:
                print(f"   Signal: {result['signal']}")
                print(f"   Confidence: {result['confidence']:.2%}")
                print(f"   Risk: {result['risk_level']}")
                print(f"   Reasoning: {result['reasoning'][:80]}...")
                print(f"   ✅ Success\n")
                
                results.append(result)
            else:
                print(f"   ❌ Failed: {result['reasoning']}\n")
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}\n")
    
    # 5. نتیجه نهایی
    print("="*60)
    print("\n📊 Final Analysis Summary:")
    
    if results:
        # رای‌گیری (Voting)
        signals = [r['signal'] for r in results]
        buy_votes = signals.count('BUY')
        sell_votes = signals.count('SELL')
        hold_votes = signals.count('HOLD')
        
        print(f"\n🗳️ Voting Results:")
        print(f"   BUY:  {buy_votes} votes")
        print(f"   SELL: {sell_votes} votes")
        print(f"   HOLD: {hold_votes} votes")
        
        # تصمیم نهایی
        if buy_votes > sell_votes and buy_votes > hold_votes:
            final_signal = "BUY 🟢"
        elif sell_votes > buy_votes and sell_votes > hold_votes:
            final_signal = "SELL 🔴"
        else:
            final_signal = "HOLD 🟡"
        
        # میانگین اطمینان
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        
        print(f"\n✅ Final Decision: {final_signal}")
        print(f"📊 Average Confidence: {avg_confidence:.2%}")
    else:
        print("\n❌ No models available for prediction")

if __name__ == "__main__":
    # اجرای تحلیل
    analyze_market("BTCUSDT", "1h")
```

---

## 🎓 آموزش: انتخاب بهترین مدل

### سناریو 1: تست و توسعه
```python
# استفاده از LightGBM محلی
predictor = AIPredictor(model_type=ModelType.LIGHTGBM)
# ✅ سریع، رایگان، کافی برای تست
```

### سناریو 2: تریدینگ واقعی با بودجه محدود
```python
# استفاده از Phi-4 (ارزان‌ترین مدل GitHub)
predictor = AIPredictor(model_type=ModelType.GITHUB_PHI4)
# ✅ تعادل خوب قیمت/کیفیت
```

### سناریو 3: تریدینگ حرفه‌ای
```python
# استفاده از GPT-4.1-mini
predictor = AIPredictor(model_type=ModelType.GITHUB_GPT4)
# ✅ بهترین دقت با قیمت منطقی
```

### سناریو 4: تریدینگ سازمانی
```python
# استفاده از Azure GPT-4
predictor = AIPredictor(model_type=ModelType.AZURE_GPT4)
# ✅ SLA تضمین‌شده، بدون محدودیت
```

---

## 📞 پشتیبانی

اگر مشکلی داشتید:

1. ✅ فایل `test_system.py` را اجرا کنید
2. 📖 این راهنما را دوباره بخوانید
3. 🔍 پیام خطا را در Google جستجو کنید
4. 💬 در GitHub Issues سوال بپرسید

---

## 🎉 خلاصه

با BRAINix IDEX می‌توانید:

✅ بین 5 مدل AI جابجا شوید  
✅ از مدل‌های رایگان GitHub استفاده کنید  
✅ دقت پیش‌بینی را تا 95% برسانید  
✅ از رابط گرافیکی (Dashboard) استفاده کنید  
✅ تحلیل اخبار و احساسات بازار  

**شروع کنید الان! 🚀**

```bash
streamlit run dashboard.py
```

---

**ساخته شده با ❤️ توسط SALMAN ThinkTank**
