# 🚀 BiX TradeBOT - راهنمای سریع Dashboard

## 🎯 مراحل شروع کار:

### 1️⃣ **تنظیمات اولیه (Sidebar)**
```
- Trading Pair: BTCUSDT (پیش‌فرض)
- Timeframe: 1h
- Use Testnet: ✅ (برای امنیت)
- Enable ML: ✅
- Initial Capital: $10,000
- Risk per Trade: 1.5%
```

### 2️⃣ **Tab 1: Live Analysis** 📊

**مرحله 1:** روی دکمه **"▶️ Analyze Market"** کلیک کنید

**مرحله 2:** منتظر بمانید تا:
- داده‌ها از Binance دریافت شود
- شاخص‌های تکنیکال محاسبه شود
- مدل ML پیش‌بینی کند

**مرحله 3:** نتایج شامل:
- 💰 قیمت فعلی
- 🎯 سیگنال (BUY/SELL/HOLD)
- ⭐ قدرت سیگنال
- 📊 RSI و ADX
- 📈 چارت تعاملی Candlestick

### 3️⃣ **Tab 2: Live Market Feed** 🌐

**برای دیدن Top 50 ارز:**
1. "🔄 Fetch Once" - یکبار دریافت
2. "▶️ Start Live Feed" - بروزرسانی مداوم

**نمایش:**
- قیمت‌های real-time
- درصد تغییرات 24 ساعته
- Top Gainers & Losers
- Market Heat Map

### 4️⃣ **Tab 3: Backtest** 📈

**برای تست استراتژی:**
1. انتخاب Start Date و End Date
2. کلیک روی "🚀 Run Backtest"
3. بررسی نتایج:
   - Total Return %
   - Sharpe Ratio
   - Max Drawdown
   - Win Rate

### 5️⃣ **Tab 4: ML Training** 🤖

**آموزش مدل (اولین بار ضروری است):**
1. Training Data Size: 2000 candles (پیش‌فرض)
2. کلیک روی "🎓 Train Model (Quick)"
3. منتظر بمانید (2-3 دقیقه)
4. بررسی Accuracy (باید >80% باشد)

**نکته مهم:** قبل از استفاده از ML در Tab 1، حتماً مدل را آموزش دهید!

### 6️⃣ **Tab 5: Settings** ⚙️

**تنظیمات:**
- انتخاب AI Model
- پیکربندی API Keys
- پارامترهای استراتژی

---

## ⚡ Quick Start (5 دقیقه):

```
1. Tab 4 → "🎓 Train Model" → صبر کنید
2. Tab 1 → "▶️ Analyze Market" → نتایج را ببینید
3. Tab 3 → "🚀 Run Backtest" → عملکرد را بررسی کنید
```

---

## ❌ رفع مشکلات رایج:

### مشکل: "Found array with 0 sample(s)"
**حل:** 
- Symbol را به BTCUSDT تغییر دهید
- دکمه "🔄 Refresh Data" را بزنید

### مشکل: "No trained model found"
**حل:**
- برو به Tab 4
- روی "🎓 Train Model" کلیک کن
- صبر کن تا آموزش تمام شه

### مشکل: "Error fetching data"
**حل:**
- اتصال اینترنت را بررسی کنید
- از BTCUSDT استفاده کنید (stable)
- تعداد candles را کمتر کنید

---

## 💡 نکات مهم:

1. **اولین استفاده:** حتماً مدل ML را train کنید (Tab 4)
2. **Symbol پایدار:** BTCUSDT بهترین گزینه است
3. **Timeframe:** 1h برای شروع مناسب است
4. **Risk Management:** Risk per Trade را بالای 2% نبرید
5. **Testnet:** همیشه فعال باشد (امن‌تر)

---

## 📊 توضیح شاخص‌ها:

**EMA (Exponential Moving Average):**
- Fast (50): میانگین کوتاه‌مدت
- Slow (200): میانگین بلندمدت
- Crossover = سیگنال خرید/فروش

**RSI (Relative Strength Index):**
- >70: اشباع خرید (احتمال ریزش)
- <30: اشباع فروش (احتمال صعود)
- 40-60: خنثی

**ADX (Average Directional Index):**
- >25: روند قوی
- <20: بازار خنثی
- >40: روند بسیار قوی

**ATR (Average True Range):**
- نوسانات بازار
- برای محاسبه Stop Loss

---

## 🎯 سیگنال‌ها:

**🟢 BUY:**
- EMA Fast > EMA Slow
- RSI < 70
- ADX > 25
- ML: Bullish

**🔴 SELL:**
- EMA Fast < EMA Slow
- RSI > 30
- ADX > 25
- ML: Bearish

**⚪ HOLD:**
- سیگنال‌های متناقض
- نوسانات کم
- ML: Neutral

---

**موفق باشید! 🚀**
