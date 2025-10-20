# 🔑 راهنمای تنظیم توکن GitHub برای مدل‌های AI

## ❌ مشکل فعلی
توکن فعلی با خطای **403 Forbidden** مواجه شد. این به معنای عدم دسترسی به GitHub Models API است.

## ✅ راه‌حل: دریافت توکن جدید

### مرحله 1: رفتن به صفحه توکن‌ها
1. به لینک زیر بروید:
   ```
   https://github.com/settings/tokens
   ```

2. روی **"Generate new token"** کلیک کنید
3. **"Generate new token (classic)"** را انتخاب کنید

### مرحله 2: تنظیم دسترسی‌ها (مهم!)
در صفحه ایجاد توکن، تیک‌های زیر را حتماً فعال کنید:

#### دسترسی‌های ضروری:
- ✅ **read:packages** - دسترسی خواندن به GitHub Packages
- ✅ **read:org** - دسترسی خواندن اطلاعات سازمان (اختیاری)
- ✅ **repo** - دسترسی کامل به repository‌ها (برای برخی مدل‌ها)

#### تنظیمات اضافی:
- **Note**: یک نام مناسب بنویسید مثل "Trading Bot AI Models"
- **Expiration**: 90 days یا No expiration (بدون انقضا)

### مرحله 3: کپی کردن توکن
1. روی **"Generate token"** کلیک کنید
2. توکن نمایش داده می‌شود (فقط یک بار!)
3. توکن را کپی کنید (شکل: `ghp_xxxxxxxxxxxx`)

### مرحله 4: تنظیم توکن در Windows
بعد از دریافت توکن، در PowerShell این دستورات را اجرا کنید:

```powershell
# تنظیم دائمی (برای همیشه)
setx GITHUB_TOKEN "ghp_your_new_token_here"

# تنظیم موقت (برای همین Terminal)
$env:GITHUB_TOKEN = "ghp_your_new_token_here"
```

### مرحله 5: راه‌اندازی مجدد
1. Terminal را ببندید و دوباره باز کنید
2. یا VS Code را Restart کنید
3. دستور تست را دوباره اجرا کنید:
   ```bash
   python test_ai_models.py
   ```

---

## 🔐 توکن‌های جایگزین

### گزینه A: استفاده از GitHub Models مستقیم
اگر GitHub Models رایگان کار نکرد، می‌توانید از API‌های رایگان دیگر استفاده کنید:

#### 1. OpenAI Free Tier
```bash
# دریافت API key از: https://platform.openai.com/api-keys
setx OPENAI_API_KEY "sk-proj-xxxxx"
```

#### 2. Anthropic Claude (Free Trial)
```bash
# دریافت API key از: https://console.anthropic.com/
setx ANTHROPIC_API_KEY "sk-ant-xxxxx"
```

#### 3. Google Gemini (رایگان)
```bash
# دریافت API key از: https://makersuite.google.com/app/apikey
setx GOOGLE_API_KEY "AIzaSy-xxxxx"
```

### گزینه B: استفاده فقط از LightGBM
اگر نمی‌خواهید توکن دریافت کنید، می‌توانید فقط با **LightGBM محلی** کار کنید:
- ✅ رایگان 100%
- ✅ سرعت بالا
- ✅ بدون نیاز به API
- ⚠️ دقت متوسط (48-54%)

برای بهبود دقت LightGBM:
1. به Tab 4 در Dashboard بروید
2. "🔄 Train with Fresh Data" را کلیک کنید
3. داده‌های بیشتر (1000+ کندل) استفاده کنید

---

## 🧪 تست مدل‌ها

### تست تمام مدل‌ها
```bash
python test_ai_models.py
```

### تست فقط یک مدل خاص
```python
from ai_predictor import AIPredictor
from ai_models_config import ModelType

# تست LightGBM
predictor = AIPredictor(ModelType.LIGHTGBM)
signal, confidence, reasoning, risk = predictor.predict()
print(f"Signal: {signal}, Confidence: {confidence}%")

# تست GPT-4 (نیاز به توکن)
predictor = AIPredictor(ModelType.GITHUB_GPT4)
signal, confidence, reasoning, risk = predictor.predict()
print(f"Signal: {signal}, Confidence: {confidence}%")
```

---

## ❓ سوالات متداول

### Q: چرا همه مدل‌ها خطا می‌دهند؟
**A:** توکن معتبر نیست یا دسترسی‌های لازم را ندارد. توکن جدیدی با دسترسی **read:packages** بگیرید.

### Q: آیا GitHub Models رایگان است؟
**A:** بله! GitHub Models تا محدودیت مشخصی رایگان است:
- GPT-4.1-mini: 15,000 درخواست/روز
- Phi-4: 15,000 درخواست/روز
- DeepSeek-V3: 15,000 درخواست/روز

### Q: کدام مدل بهترین است؟
**A:** بستگی به نیاز شما دارد:
- **سرعت**: Phi-4 (9/10)
- **دقت**: DeepSeek-V3 (95%)
- **قیمت**: LightGBM (رایگان محلی)
- **توصیه**: GPT-4.1-mini (متوازن)

### Q: آیا می‌توانم چند مدل را باهم استفاده کنم؟
**A:** بله! سیستم Voting دارد که نظر تمام مدل‌ها را ترکیب می‌کند:
```python
from ai_predictor import compare_models

# مقایسه تمام مدل‌ها
results = compare_models()
print(results)
```

---

## 📞 در صورت نیاز به کمک

1. **مشکل با توکن**: https://github.com/settings/tokens
2. **مستندات GitHub Models**: https://docs.github.com/en/github-models
3. **API Reference**: https://platform.openai.com/docs

---

## ✅ چک‌لیست تکمیل

- [ ] توکن جدید دریافت شد
- [ ] دسترسی **read:packages** فعال شد
- [ ] توکن در Windows تنظیم شد (`setx` اجرا شد)
- [ ] Terminal دوباره باز شد
- [ ] `test_ai_models.py` بدون خطا اجرا شد
- [ ] حداقل 2 مدل کار می‌کنند

