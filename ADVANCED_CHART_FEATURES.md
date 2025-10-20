# 📊 ویژگی‌های پیشرفته تحلیل نمودار

## نمای کلی

داشبورد فارسی BRAINixIDEX اکنون با **سیستم تحلیل پیشرفته نمودار** ارتقا یافته است که ابزارهای حرفه‌ای معامله‌گری را ارائه می‌دهد.

---

## 🎯 ویژگی‌های جدید

### 1️⃣ **تشخیص سطوح حمایت و مقاومت (Support/Resistance)**
- **الگوریتم خودکار**: تشخیص سطوح کلیدی قیمت با استفاده از scipy.signal
- **خوشه‌بندی هوشمند**: گروه‌بندی سطوح نزدیک به هم
- **نمایش بصری**:
  - خطوط **سبز افقی** = سطوح حمایت 🟢
  - خطوط **قرمز افقی** = سطوح مقاومت 🔴
- **برچسب قیمت**: نمایش دقیق قیمت هر سطح

**مثال خروجی:**
```
حمایت: $108,450.23
حمایت: $106,890.50
مقاومت: $112,340.78
مقاومت: $115,200.00
```

---

### 2️⃣ **تشخیص خطوط روند (Trend Lines)**
- **اتصال خودکار**: اتصال swing highs و swing lows
- **محاسبه شیب**: تعیین قدرت روند
- **تشخیص جهت**: صعودی یا نزولی
- **نمایش بصری**:
  - خطوط **بنفش تیره** = روند صعودی 📈
  - خطوط **قهوه‌ای** = روند نزولی 📉

**پارامترها:**
- `lookback=50`: تعداد کندل‌های مورد بررسی
- Slope calculation: محاسبه زاویه خط روند

---

### 3️⃣ **سطوح فیبوناچی (Fibonacci Retracement)**
- **9 سطح استاندارد**:
  - 0.236 (23.6%)
  - 0.382 (38.2%)
  - 0.500 (50%)
  - 0.618 (61.8%) - Golden Ratio ✨
  - 0.786 (78.6%)
  - 1.000 (100%)
  - 1.272 (127.2%)
  - 1.618 (161.8%) - Fibonacci Extension
  
- **نمایش بصری**:
  - خطوط **نارنجی تیره با خط چین** 🟠
  - برچسب‌گذاری واضح با قیمت دقیق

**محاسبه:**
```python
swing_high = max(last 100 candles)
swing_low = min(last 100 candles)
fib_level = swing_high - (ratio × (swing_high - swing_low))
```

---

### 4️⃣ **تشخیص الگوهای کندل استیک (Candlestick Patterns)**

تشخیص **7 الگوی حرفه‌ای**:

#### الگوهای صعودی 🟢
1. **Hammer (چکش)**
   - سایه پایین ≥ 2× بدنه
   - سایه بالا ≤ 0.1× بدنه
   - نشانه برگشت صعودی

2. **Bullish Engulfing (پوشش صعودی)**
   - کندل صعودی کامل کندل نزولی قبلی را می‌پوشاند
   - سیگنال خرید قوی

3. **Morning Star (ستاره صبحگاهی)**
   - الگوی 3 کندلی
   - نزولی → کوچک → صعودی
   - برگشت صعودی قدرتمند

#### الگوهای نزولی 🔴
4. **Shooting Star (ستاره دنباله‌دار)**
   - سایه بالا ≥ 2× بدنه
   - سایه پایین ≤ 0.1× بدنه
   - نشانه برگشت نزولی

5. **Bearish Engulfing (پوشش نزولی)**
   - کندل نزولی کامل کندل صعودی قبلی را می‌پوشاند
   - سیگنال فروش قوی

6. **Evening Star (ستاره شامگاهی)**
   - الگوی 3 کندلی
   - صعودی → کوچک → نزولی
   - برگشت نزولی قدرتمند

#### الگوهای خنثی ⚪
7. **Doji (دوجی)**
   - قیمت باز و بسته تقریباً برابر
   - عدم تصمیم بازار
   - احتمال برگشت

**نمایش بصری:**
- 🔔 آیکون زنگ روی نمودار
- رنگ **سبز** = صعودی
- رنگ **قرمز** = نزولی
- درصد **اعتماد** (Confidence): 75-95%

---

### 5️⃣ **پیشنهادات نقاط ورود و خروج (Entry/Exit Points)**

#### نقاط ورود 💚
- محاسبه بر اساس سطوح حمایت
- نمایش با **مارکر سبز** و فلش
- قیمت دقیق پیشنهادی

```
💚 نقطه ورود: $108,450.23
```

#### نقاط خروج ❤️
- محاسبه بر اساس سطوح مقاومت
- نمایش با **مارکر قرمز** و فلش
- قیمت دقیق پیشنهادی

```
❤️ نقطه خروج: $112,340.78
```

#### حد ضرر (Stop Loss) ⚠️
```
⚠️ حد ضرر پیشنهادی: $106,500.00
```

#### حد سود (Take Profit) ℹ️
```
ℹ️ حد سود پیشنهادی: $115,000.00
```

---

## 📈 نحوه استفاده

### گام 1: راه‌اندازی داشبورد
```bash
cd "e:\Ai\Projects\BRAINixIDEX\Bix New Trade BOT"
streamlit run src/ui/dashboard_fa.py --server.port 8502
```

یا استفاده از launcher script:
```bash
python scripts/run_dashboard_fa.py
```

### گام 2: انتخاب نماد
- از سایدبار، نماد دلخواه را انتخاب کنید (مثلاً `BTCUSDT`)

### گام 3: انتخاب تایم‌فریم
- تایم‌فریم مورد نظر را انتخاب کنید:
  - `1m` - 1 دقیقه
  - `5m` - 5 دقیقه
  - `15m` - 15 دقیقه
  - `1h` - 1 ساعت
  - `4h` - 4 ساعت
  - `1d` - روزانه

### گام 4: مشاهده تحلیل پیشرفته
نمودار به طور خودکار شامل موارد زیر خواهد بود:

✅ **کندل‌های رنگی** (سبز/قرمز)
✅ **EMA سریع** (آبی)
✅ **EMA کند** (قرمز)
✅ **سطوح حمایت** (سبز افقی)
✅ **سطوح مقاومت** (قرمز افقی)
✅ **سطوح فیبوناچی** (نارنجی تیره با خط چین)
✅ **خطوط روند** (بنفش/قهوه‌ای)
✅ **الگوهای کندل** (آیکون 🔔 با توضیحات)
✅ **نقاط ورود/خروج** (💚 / ❤️)
✅ **RSI** (زیر نمودار اصلی)
✅ **حجم معاملات** (نمودار میله‌ای)

### گام 5: خلاصه تحلیل
زیر نمودار، 3 ستون اطلاعاتی نمایش داده می‌شود:

1. **🟢 سطوح حمایت**
2. **🔴 سطوح مقاومت**
3. **📈 خطوط روند** (با شیب)

### گام 6: الگوهای شناسایی شده
جدول الگوهای کندل استیک با اطلاعات زیر:
- نام الگو
- نوع (صعودی/نزولی)
- درصد اعتماد
- قیمت تشکیل

### گام 7: پیشنهادات معاملاتی
4 بخش رنگی:
- ✅ **سبز**: نقاط ورود پیشنهادی
- ❌ **قرمز**: نقاط خروج پیشنهادی
- ⚠️ **زرد**: حد ضرر
- ℹ️ **آبی**: حد سود

---

## 🔧 پارامترهای سفارشی‌سازی

### تنظیمات Support/Resistance
```python
chart_analyzer.find_support_resistance(
    window=20,        # اندازه پنجره (کندل)
    threshold=0.02    # آستانه خوشه‌بندی (2%)
)
```

### تنظیمات Trend Lines
```python
chart_analyzer.detect_trend_lines(
    lookback=50       # تعداد کندل‌های بررسی شده
)
```

### تنظیمات Fibonacci
```python
chart_analyzer.calculate_fibonacci_levels(
    lookback=100      # تعداد کندل برای یافتن swing high/low
)
```

### تنظیمات Pattern Detection
```python
chart_analyzer.detect_candlestick_patterns(
    lookback=20       # بررسی 20 کندل اخیر
)
```

---

## 📊 ساختار کلاس AdvancedChartAnalysis

```python
class AdvancedChartAnalysis:
    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: دیتافریم با ستون‌های: open, high, low, close, volume
        """
        self.df = df
        self.current_price = df['close'].iloc[-1]
    
    def find_support_resistance(self, window=20, threshold=0.02):
        """تشخیص سطوح حمایت و مقاومت"""
        
    def detect_trend_lines(self, lookback=50):
        """تشخیص خطوط روند"""
        
    def calculate_fibonacci_levels(self, lookback=100):
        """محاسبه سطوح فیبوناچی"""
        
    def detect_candlestick_patterns(self, lookback=20):
        """تشخیص الگوهای کندل استیک"""
        
    def suggest_entry_exit_points(self, current_price):
        """پیشنهاد نقاط ورود و خروج"""
        
    def get_complete_analysis(self, current_price):
        """دریافت تحلیل کامل"""
        return {
            'support_resistance': {...},
            'trend_lines': [...],
            'fibonacci': {...},
            'patterns': [...],
            'suggestions': {...}
        }
```

---

## 🧮 الگوریتم‌ها

### 1. تشخیص Support/Resistance

```python
# استفاده از scipy برای یافتن local minima/maxima
from scipy.signal import argrelextrema

# Local minima = سطوح حمایت
support_indices = argrelextrema(df['low'].values, np.less, order=window)[0]

# Local maxima = سطوح مقاومت
resistance_indices = argrelextrema(df['high'].values, np.greater, order=window)[0]

# خوشه‌بندی سطوح نزدیک
clustered_levels = cluster_nearby_levels(levels, threshold=0.02)
```

### 2. تشخیص Trend Lines

```python
# یافتن swing highs
swing_highs = [(i, price) for i, price in enumerate(highs) if is_swing_high(i)]

# اتصال swing points
for i in range(len(swing_highs) - 1):
    start = swing_highs[i]
    end = swing_highs[i + 1]
    slope = (end[1] - start[1]) / (end[0] - start[0])
    
    # تعیین جهت
    direction = "صعودی" if slope > 0 else "نزولی"
```

### 3. محاسبه Fibonacci

```python
swing_high = df['high'].iloc[-lookback:].max()
swing_low = df['low'].iloc[-lookback:].min()
diff = swing_high - swing_low

fib_levels = {
    '0.236': swing_high - (0.236 * diff),
    '0.382': swing_high - (0.382 * diff),
    '0.618': swing_high - (0.618 * diff),  # Golden Ratio
    # ...
}
```

### 4. Pattern Detection - Hammer

```python
def is_hammer(row):
    body = abs(row['close'] - row['open'])
    lower_shadow = min(row['open'], row['close']) - row['low']
    upper_shadow = row['high'] - max(row['open'], row['close'])
    
    if lower_shadow >= 2 * body and upper_shadow <= 0.1 * body:
        return True, 85  # 85% confidence
    return False, 0
```

---

## 🎨 کاربردهای واقعی

### سناریو 1: تشخیص نقطه ورود
1. قیمت به سطح حمایت نزدیک می‌شود 🟢
2. الگوی **Hammer** تشکیل می‌شود 🔔
3. خط روند **صعودی** تایید می‌کند 📈
4. سیستم نقطه ورود پیشنهاد می‌دهد 💚

**نتیجه:** سیگنال خرید قوی ✅

### سناریو 2: تشخیص نقطه خروج
1. قیمت به سطح مقاومت می‌رسد 🔴
2. الگوی **Shooting Star** ظاهر می‌شود 🔔
3. سطح فیبوناچی 0.618 تایید می‌کند 🟠
4. سیستم نقطه خروج پیشنهاد می‌دهد ❤️

**نتیجه:** سیگنال فروش قوی ✅

### سناریو 3: مدیریت ریسک
1. قیمت ورود: $108,450 💚
2. حد ضرر: $106,500 ⚠️ (زیر حمایت)
3. حد سود: $115,000 ℹ️ (نزدیک مقاومت)

**Risk/Reward Ratio:** 1:3.36 ✅

---

## 🚀 مزایای سیستم

✅ **خودکار بودن**: تحلیل بدون دخالت دستی
✅ **سرعت بالا**: پردازش real-time با scipy
✅ **دقت بالا**: الگوریتم‌های حرفه‌ای
✅ **چندگانه**: ترکیب 5 تکنیک مختلف
✅ **بصری**: نمایش واضح روی نمودار
✅ **فارسی**: رابط کاربری RTL با فونت وزیر
✅ **قابل سفارشی‌سازی**: پارامترهای قابل تنظیم

---

## 🔬 وابستگی‌ها

```bash
pip install scipy numpy pandas plotly streamlit
```

**نسخه‌های توصیه شده:**
- `scipy>=1.10.0` - برای argrelextrema
- `numpy>=1.24.0` - محاسبات ماتریسی
- `pandas>=2.0.0` - مدیریت داده
- `plotly>=5.14.0` - نمودارهای تعاملی
- `streamlit>=1.28.0` - رابط کاربری

---

## 📝 نکات مهم

⚠️ **هشدار 1**: این پیشنهادات بر اساس تحلیل تکنیکال است و تضمین سود نیست.

⚠️ **هشدار 2**: همیشه از مدیریت ریسک استفاده کنید.

⚠️ **هشدار 3**: حد ضرر را رعایت کنید.

💡 **نکته 1**: ترکیب چندین سیگنال، اعتبار بیشتری دارد.

💡 **نکته 2**: سطوح فیبوناچی 0.618 و 0.382 از همه مهم‌تر هستند.

💡 **نکته 3**: الگوهای 3 کندلی (Morning/Evening Star) قدرتمندترند.

---

## 🎓 منابع آموزشی

### کتاب‌های توصیه شده:
1. **"Japanese Candlestick Charting Techniques"** - Steve Nison
2. **"Technical Analysis of the Financial Markets"** - John Murphy
3. **"Fibonacci Trading: How to Master the Time and Price Advantage"** - Carolyn Boroden

### دوره‌های آنلاین:
- Investopedia: Technical Analysis Course
- Udemy: Complete Guide to Fibonacci Trading
- Coursera: Financial Markets by Yale University

---

## 🐛 عیب‌یابی

### مشکل 1: نمودار الگویی نمایش نمی‌دهد
**راه‌حل:**
- تایم‌فریم کوچکتر انتخاب کنید (مثلاً 15m)
- تعداد کندل‌های بیشتری دریافت کنید
- پارامتر `lookback` را افزایش دهید

### مشکل 2: خطوط روند نامشخص
**راه‌حل:**
```python
# افزایش lookback
chart_analyzer.detect_trend_lines(lookback=100)
```

### مشکل 3: سطوح فیبوناچی نامرتب
**راه‌حل:**
- اطمینان از وجود swing high/low واضح
- افزایش `lookback=200`

### مشکل 4: خطای scipy
**راه‌حل:**
```bash
pip install --upgrade scipy
```

---

## 📞 پشتیبانی

- **GitHub Issues**: برای گزارش باگ
- **Pull Requests**: برای مشارکت در کد
- **Telegram**: [@BRAINixIDEX_Support](https://t.me/BRAINixIDEX_Support)

---

## 🌟 آپدیت‌های آینده

🔜 **نسخه 2.0**:
- ✨ ابزارهای کشیدن دستی (Manual Drawing Tools)
- ✨ Volume Profile Analysis
- ✨ Order Flow Visualization
- ✨ Alert System برای الگوها
- ✨ گزارش PDF از تحلیل‌ها
- ✨ Backtesting روی الگوها
- ✨ Machine Learning برای پیش‌بینی الگوها

---

## 📜 مجوز

این پروژه تحت مجوز MIT منتشر شده است.

```
MIT License

Copyright (c) 2025 BRAINixIDEX

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🙏 قدردانی

تشکر ویژه از:
- **Scipy Team** - برای کتابخانه عالی signal processing
- **Plotly Team** - برای نمودارهای تعاملی
- **Streamlit Team** - برای فریمورک کاربرپسند
- **جامعه معامله‌گران ایرانی** - برای بازخوردها

---

**✨ موفق باشید! ✨**

*آخرین بروزرسانی: 2025-01-24*
*نسخه: 1.0.0 Advanced*
