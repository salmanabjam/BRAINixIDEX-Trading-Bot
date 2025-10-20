# 🚀 راهنمای سریع: GitHub و توکن‌ها

## ✅ مرحله 1: حذف فایل‌های اضافی (انجام شد)
✅ 12 فایل حذف شد

## ✅ مرحله 2: کامیت Git (انجام شد)
✅ 41 فایل commit شد

---

## 📦 مرحله 3: ایجاد Repository در GitHub

### 🔗 لینک مستقیم:
```
https://github.com/new
```

### ⚙️ تنظیمات:
- **Repository name**: `BRAINixIDEX-Trading-Bot`
- **Description**: `Advanced Trading Bot with AI Models`
- **Public/Private**: Public (توصیه می‌شود)
- **Initialize**: خالی بگذارید

### 📤 بعد از ایجاد، این دستورات را اجرا کن:
```powershell
cd "e:\Ai\Projects\BRAINixIDEX\Bix New Trade BOT"

# USERNAME خود را جایگزین کن
git remote add origin https://github.com/USERNAME/BRAINixIDEX-Trading-Bot.git
git branch -M main
git push -u origin main
```

---

## 🔑 مرحله 4: دریافت توکن‌ها به ترتیب

---

### 1️⃣ توکن GitHub Models (رایگان) ⭐⭐⭐⭐⭐

**چرا این اول؟**
✅ کاملاً رایگان  
✅ 5 مدل AI قدرتمند  
✅ بدون نیاز به شماره تلفن  

**مراحل:**
1. برو: https://github.com/settings/tokens
2. کلیک کن: `Generate new token (classic)`
3. تیک بزن:
   - ✅ `repo`
   - ✅ `read:packages`
   - ✅ `write:packages`
4. `Generate token` کلیک کن
5. توکن را کپی کن (مثل: `ghp_xxxxx`)
6. در PowerShell:
   ```powershell
   setx GITHUB_TOKEN "ghp_your_token_here"
   ```
7. Terminal را ببند و باز کن
8. تست کن:
   ```powershell
   python test_ai_models.py
   ```

**✅ اگر موفق شد**: توکن را به من بفرست تا تست کنم  
**❌ اگر خطا داد**: مراحل را دوباره امتحان کن

---

### 2️⃣ توکن Google Gemini (رایگان) ⭐⭐⭐⭐⭐

**چرا این دومی؟**
✅ کاملاً رایگان  
✅ سریع و قدرتمند  
✅ بدون نیاز به شماره  

**مراحل:**
1. برو: https://aistudio.google.com/app/apikey
2. Login با Google
3. کلیک کن: `Create API Key`
4. انتخاب کن: `Create API key in new project`
5. API key را کپی کن (مثل: `AIzaSy...`)
6. در PowerShell:
   ```powershell
   setx GOOGLE_API_KEY "AIzaSy_your_key"
   ```
7. Terminal را ببند و باز کن

**✅ اگر موفق شد**: توکن را به من بفرست  
**❌ اگر خطا داد**: دوباره API key بگیر

---

### 3️⃣ توکن OpenAI (5$ رایگان) ⚠️

**نکته:** نیاز به تایید شماره تلفن

**مراحل:**
1. برو: https://platform.openai.com/signup
2. ثبت‌نام کن
3. شماره تلفن را تایید کن
4. برو: https://platform.openai.com/api-keys
5. کلیک کن: `Create new secret key`
6. API key را کپی کن (مثل: `sk-proj-...`)
7. در PowerShell:
   ```powershell
   setx OPENAI_API_KEY "sk-proj_your_key"
   ```
8. Terminal را ببند و باز کن

**✅ اگر موفق شد**: توکن را به من بفرست  
**❌ اگر خطا داد**: شماره تلفن دیگری امتحان کن

---

### 4️⃣ توکن Anthropic Claude (5$ رایگان) ⚠️

**نکته:** نیاز به تایید شماره تلفن

**مراحل:**
1. برو: https://console.anthropic.com/
2. Sign up
3. شماره تلفن را تایید کن
4. برو: https://console.anthropic.com/settings/keys
5. کلیک کن: `Create Key`
6. API key را کپی کن (مثل: `sk-ant-...`)
7. در PowerShell:
   ```powershell
   setx ANTHROPIC_API_KEY "sk-ant_your_key"
   ```
8. Terminal را ببند و باز کن

**✅ اگر موفق شد**: توکن را به من بفرست  
**❌ اگر خطا داد**: شماره تلفن دیگری امتحان کن

---

## 📊 خلاصه

| # | سرویس | رایگان | نیاز به شماره | اولویت |
|---|--------|--------|---------------|--------|
| 1 | GitHub Models | ✅ | ❌ | ⭐⭐⭐⭐⭐ |
| 2 | Google Gemini | ✅ | ❌ | ⭐⭐⭐⭐⭐ |
| 3 | OpenAI | 5$ | ✅ | ⭐⭐⭐ |
| 4 | Anthropic | 5$ | ✅ | ⭐⭐⭐ |

---

## 🎯 چه کار کنیم؟

### حالا:
1. ✅ Repository در GitHub بساز
2. ✅ توکن GitHub Models بگیر
3. ✅ توکن را به من بفرست

### بعد:
4. من تست می‌کنم
5. توکن Google Gemini بگیر
6. بقیه اختیاری

---

## 💬 الان چی کار کنیم؟

**گام 1:** Repository بساز:
```
https://github.com/new
```

**گام 2:** USERNAME خودت را بگو تا دستورات Push را بدهم

**گام 3:** توکن GitHub بگیر و بفرست

آماده‌ای؟ بگو USERNAME چیه؟ 😊
