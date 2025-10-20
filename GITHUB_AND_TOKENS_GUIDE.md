# 🚀 راهنمای ایجاد Repository در GitHub و دریافت توکن‌ها

## 📦 مرحله 1: ایجاد Repository در GitHub

### گام‌های ایجاد:
1. به لینک زیر بروید:
   ```
   https://github.com/new
   ```

2. **Repository name** را وارد کنید:
   ```
   BRAINixIDEX-Trading-Bot
   ```

3. **Description** (اختیاری):
   ```
   Advanced Trading Bot with AI Models & Backtesting
   ```

4. **Public یا Private** انتخاب کنید:
   - Public: همه می‌توانند ببینند (توصیه می‌شود)
   - Private: فقط شما می‌توانید ببینید

5. **Initialize this repository** را خالی بگذارید (چون ما قبلاً init کرده‌ایم)

6. **Create repository** کلیک کنید

---

## 🔗 مرحله 2: اتصال به GitHub

بعد از ایجاد repository، این دستورات را اجرا کنید:

```powershell
cd "e:\Ai\Projects\BRAINixIDEX\Bix New Trade BOT"

# اضافه کردن remote (USERNAME خود را جایگزین کنید)
git remote add origin https://github.com/USERNAME/BRAINixIDEX-Trading-Bot.git

# تنظیم branch
git branch -M main

# Push کردن
git push -u origin main
```

**نکته**: اگر خطای authentication گرفتید، Personal Access Token نیاز است.

---

## 🔑 مرحله 3: دریافت توکن‌های رایگان به ترتیب

---

### 🤖 توکن 1: GitHub Models (رایگان) ⭐

#### مزایا:
- ✅ کاملاً رایگان
- ✅ 5 مدل AI قدرتمند
- ✅ 15,000 درخواست/روز برای هر مدل

#### مدل‌های موجود:
1. GPT-4o-mini (OpenAI)
2. Phi-4 (Microsoft)
3. DeepSeek-V3
4. Llama-3.3-70B (Meta)
5. Claude 3.5 Sonnet (Anthropic)

#### مراحل دریافت:

**گام 1**: برو به:
```
https://github.com/settings/tokens
```

**گام 2**: کلیک کن روی:
```
Generate new token → Generate new token (classic)
```

**گام 3**: پر کردن فرم:
- **Note**: `BRAINixIDEX Trading Bot - GitHub Models`
- **Expiration**: `No expiration` (بدون انقضا)

**گام 4**: دسترسی‌ها را فعال کن:
✅ **repo** (Full control of private repositories)
✅ **read:packages** (Download packages from GitHub Package Registry)
✅ **write:packages** (Upload packages to GitHub Package Registry)

**گام 5**: پایین صفحه کلیک کن:
```
Generate token
```

**گام 6**: توکن را کپی کن (شکل: `ghp_xxxxxxxxxxxx`)

**گام 7**: در PowerShell اجرا کن:
```powershell
setx GITHUB_TOKEN "ghp_your_token_here"
```

**گام 8**: Terminal را ببند و دوباره باز کن

**گام 9**: تست کن:
```powershell
python test_ai_models.py
```

**اگر موفق شد**: ✅ به توکن بعدی برو  
**اگر خطا داد**: ❌ مراحل را دوباره بررسی کن

---

### 🧠 توکن 2: Google Gemini (رایگان) ⭐⭐⭐

#### مزایا:
- ✅ کاملاً رایگان
- ✅ بدون نیاز به کارت اعتباری
- ✅ 60 درخواست/دقیقه

#### مدل‌های موجود:
1. Gemini 1.5 Pro (قدرتمندترین)
2. Gemini 1.5 Flash (سریع‌ترین)

#### مراحل دریافت:

**گام 1**: برو به:
```
https://aistudio.google.com/app/apikey
```

**گام 2**: اگر login نکردی، با Google Account login کن

**گام 3**: کلیک کن روی:
```
Create API Key
```

**گام 4**: انتخاب کن:
```
Create API key in new project
```

**گام 5**: API key نمایش داده می‌شود (شکل: `AIzaSy...`)

**گام 6**: کپی کن و در PowerShell اجرا کن:
```powershell
setx GOOGLE_API_KEY "AIzaSy_your_key_here"
```

**گام 7**: Terminal را ببند و دوباره باز کن

**گام 8**: تست کن (کد پایین را بنویس):
```python
import os
import requests

api_key = os.getenv('GOOGLE_API_KEY')
url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}'

response = requests.post(url, json={
    "contents": [{
        "parts": [{"text": "Say hello"}]
    }]
})

print("✅ Google Gemini OK!" if response.status_code == 200 else "❌ Error")
```

**اگر موفق شد**: ✅ به توکن بعدی برو  
**اگر خطا داد**: ❌ API key را دوباره بگیر

---

### 💬 توکن 3: OpenAI (5$ رایگان برای کاربران جدید) ⚠️

#### مزایا:
- ✅ 5$ اعتبار رایگان
- ✅ GPT-4o-mini بسیار ارزان ($0.15/1M tokens)
- ⚠️ نیاز به تایید شماره تلفن

#### مراحل دریافت:

**گام 1**: برو به:
```
https://platform.openai.com/signup
```

**گام 2**: ثبت‌نام کن با email

**گام 3**: تایید email

**گام 4**: تایید شماره تلفن (نیاز است)

**گام 5**: برو به:
```
https://platform.openai.com/api-keys
```

**گام 6**: کلیک کن:
```
Create new secret key
```

**گام 7**: نام بده: `BRAINixIDEX Trading Bot`

**گام 8**: کپی کن (شکل: `sk-proj-...`)

**گام 9**: در PowerShell اجرا کن:
```powershell
setx OPENAI_API_KEY "sk-proj-your_key_here"
```

**گام 10**: Terminal را ببند و دوباره باز کن

**گام 11**: تست کن:
```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say hello"}],
    max_tokens=10
)
print("✅ OpenAI OK!" if response else "❌ Error")
```

**اگر موفق شد**: ✅ به توکن بعدی برو  
**اگر خطا داد**: ❌ شماره تلفن را تایید کن

---

### 🤖 توکن 4: Anthropic Claude (5$ رایگان) ⚠️

#### مزایا:
- ✅ 5$ اعتبار رایگان
- ✅ Claude 3.5 Sonnet (بسیار قدرتمند)
- ⚠️ نیاز به تایید شماره تلفن

#### مراحل دریافت:

**گام 1**: برو به:
```
https://console.anthropic.com/
```

**گام 2**: Sign up با email

**گام 3**: تایید email

**گام 4**: تایید شماره تلفن

**گام 5**: برو به:
```
https://console.anthropic.com/settings/keys
```

**گام 6**: کلیک کن:
```
Create Key
```

**گام 7**: نام بده: `Trading Bot`

**گام 8**: کپی کن (شکل: `sk-ant-...`)

**گام 9**: در PowerShell اجرا کن:
```powershell
setx ANTHROPIC_API_KEY "sk-ant-your_key_here"
```

**گام 10**: Terminal را ببند و دوباره باز کن

**گام 11**: تست کن:
```python
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=10,
    messages=[{"role": "user", "content": "Say hello"}]
)
print("✅ Claude OK!" if message else "❌ Error")
```

**اگر موفق شد**: ✅ تمام شد! 🎉  
**اگر خطا داد**: ❌ شماره تلفن را تایید کن

---

### 🔵 توکن 5: Azure OpenAI (نیاز به اشتراک Azure) 💰

#### نکات:
- ❌ رایگان نیست
- 💰 نیاز به اشتراک Azure
- 💳 نیاز به کارت اعتباری

**اگر اشتراک Azure دارید:**

**گام 1**: برو به:
```
https://portal.azure.com
```

**گام 2**: Azure OpenAI resource ایجاد کن

**گام 3**: GPT-4 deploy کن

**گام 4**: Keys را کپی کن

**گام 5**: در PowerShell:
```powershell
setx AZURE_OPENAI_ENDPOINT "https://your-resource.openai.azure.com/"
setx AZURE_OPENAI_KEY "your_azure_key"
```

---

## 📊 خلاصه توکن‌های رایگان

| # | سرویس | رایگان؟ | محدودیت | نیاز به شماره | توصیه |
|---|--------|---------|---------|---------------|-------|
| 1 | **GitHub Models** | ✅ بله | 15K/روز | ❌ خیر | ⭐⭐⭐⭐⭐ |
| 2 | **Google Gemini** | ✅ بله | 60/دقیقه | ❌ خیر | ⭐⭐⭐⭐⭐ |
| 3 | **OpenAI** | ⚠️ 5$ رایگان | محدود | ✅ بله | ⭐⭐⭐ |
| 4 | **Anthropic** | ⚠️ 5$ رایگان | محدود | ✅ بله | ⭐⭐⭐ |
| 5 | **Azure OpenAI** | ❌ خیر | پولی | ✅ بله | ⭐ |

---

## 🎯 توصیه نهایی

### ترتیب اولویت برای دریافت:

1. **GitHub Models** (شروع اینجا!) ⭐⭐⭐⭐⭐
   - کاملاً رایگان
   - بدون نیاز به شماره
   - 5 مدل قدرتمند

2. **Google Gemini** ⭐⭐⭐⭐⭐
   - کاملاً رایگان
   - بدون نیاز به شماره
   - سریع و دقیق

3. **OpenAI** (اختیاری) ⭐⭐⭐
   - 5$ رایگان
   - نیاز به تایید شماره

4. **Anthropic** (اختیاری) ⭐⭐⭐
   - 5$ رایگان
   - نیاز به تایید شماره

5. **Azure** (برای سازمان‌ها) ⭐
   - پولی
   - نیاز به اشتراک

---

## ✅ بعد از دریافت هر توکن

```powershell
# تست سریع
python -c "import os; print('✅ Token set' if os.getenv('GITHUB_TOKEN') else '❌ Not set')"

# تست کامل
python test_ai_models.py
```

---

## 🎉 آماده شدید!

بعد از دریافت توکن‌ها، به من بگویید تا به مرحله بعدی برویم:
- آموزش مدل‌ها
- تست با مدل‌های مختلف
- Backtest با چند مدل

موفق باشید! 🚀
