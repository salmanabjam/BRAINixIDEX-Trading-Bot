# 🔧 Setup Guide

Complete guide to setting up BRAINixIDEX Trading Bot.

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [API Keys Setup](#api-keys-setup)
4. [Configuration](#configuration)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

## 💻 System Requirements

### Minimum
- **OS**: Windows 10+, Linux, macOS
- **Python**: 3.8 or higher
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Internet**: Stable connection

### Recommended
- **Python**: 3.10+
- **RAM**: 8GB+
- **Storage**: 5GB+ (for historical data)

---

## 📦 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/salmanabjam/BRAINixIDEX-Trading-Bot.git
cd BRAINixIDEX-Trading-Bot
```

### Step 2: Create Virtual Environment (Recommended)

#### Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Linux/macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install as a package:

```bash
pip install -e .
```

### Step 4: Verify Installation

```bash
python run.py --help
```

You should see the help menu.

---

## 🔑 API Keys Setup

### 1. GitHub Models (FREE) ⭐

**Time**: ~5 minutes  
**Cost**: FREE  
**Models**: GPT-4.1, Phi-4, DeepSeek-V3, Llama-3.3

#### Steps:

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Name: `BRAINixIDEX Trading Bot`
4. Scopes: ✅ `read:packages`
5. Expiration: `No expiration` (or 90 days)
6. Click **"Generate token"**
7. **Copy the token** (starts with `ghp_`)

#### Configure:

**Windows:**
```powershell
.\scripts\setup_tokens.ps1 -Service GitHub -Token "ghp_YOUR_TOKEN"
```

**Linux/macOS:**
```bash
export GITHUB_TOKEN="ghp_YOUR_TOKEN"
echo 'export GITHUB_TOKEN="ghp_YOUR_TOKEN"' >> ~/.bashrc
```

---

### 2. Google Gemini (FREE) ⭐

**Time**: ~3 minutes  
**Cost**: FREE  
**Models**: Gemini Pro, Gemini Flash

#### Steps:

1. Go to: https://aistudio.google.com/apikey
2. Sign in with Google account
3. Click **"Create API Key"**
4. Select a Google Cloud project (or create new)
5. **Copy the API key** (starts with `AIza`)

#### Configure:

**Windows:**
```powershell
.\scripts\setup_tokens.ps1 -Service Google -Token "AIzaSy_YOUR_KEY"
```

**Linux/macOS:**
```bash
export GOOGLE_API_KEY="AIzaSy_YOUR_KEY"
echo 'export GOOGLE_API_KEY="AIzaSy_YOUR_KEY"' >> ~/.bashrc
```

---

### 3. Hugging Face (FREE) ⭐

**Time**: ~2 minutes  
**Cost**: FREE  
**Models**: Various open-source models

#### Steps:

1. Go to: https://huggingface.co/settings/tokens
2. Sign in or create account
3. Click **"New token"**
4. Name: `BRAINixIDEX`
5. Role: `Read`
6. Click **"Generate"**
7. **Copy the token** (starts with `hf_`)

#### Configure:

**Windows:**
```powershell
.\scripts\setup_tokens.ps1 -Service HuggingFace -Token "hf_YOUR_TOKEN"
```

**Linux/macOS:**
```bash
export HUGGINGFACE_TOKEN="hf_YOUR_TOKEN"
echo 'export HUGGINGFACE_TOKEN="hf_YOUR_TOKEN"' >> ~/.bashrc
```

---

### 4. OpenAI (Optional - $5 Free Credit)

**Time**: ~7 minutes  
**Cost**: $5 free credit, then pay-as-you-go  
**Models**: GPT-4, GPT-3.5

#### Steps:

1. Go to: https://platform.openai.com/signup
2. Create account (phone verification required)
3. Go to: https://platform.openai.com/api-keys
4. Click **"Create new secret key"**
5. Name: `BRAINixIDEX`
6. **Copy the key** (starts with `sk-`)

#### Configure:

**Windows:**
```powershell
.\scripts\setup_tokens.ps1 -Service OpenAI -Token "sk-YOUR_KEY"
```

**Linux/macOS:**
```bash
export OPENAI_API_KEY="sk-YOUR_KEY"
echo 'export OPENAI_API_KEY="sk-YOUR_KEY"' >> ~/.bashrc
```

---

### 5. Anthropic (Optional - $5 Free Credit)

**Time**: ~7 minutes  
**Cost**: $5 free credit, then pay-as-you-go  
**Models**: Claude 3

#### Steps:

1. Go to: https://console.anthropic.com/
2. Create account
3. Go to: https://console.anthropic.com/settings/keys
4. Click **"Create Key"**
5. **Copy the key** (starts with `sk-ant-`)

#### Configure:

**Windows:**
```powershell
.\scripts\setup_tokens.ps1 -Service Anthropic -Token "sk-ant-YOUR_KEY"
```

**Linux/macOS:**
```bash
export ANTHROPIC_API_KEY="sk-ant-YOUR_KEY"
echo 'export ANTHROPIC_API_KEY="sk-ant-YOUR_KEY"' >> ~/.bashrc
```

---

### 6. Binance API (Optional - For Live Trading)

**Time**: ~10 minutes  
**Cost**: FREE (for API access)  
**Purpose**: Market data, live trading

⚠️ **Note**: Only needed for live trading. Bot works without it using testnet.

#### Steps:

1. Create Binance account: https://www.binance.com/
2. Complete KYC verification
3. Enable 2FA
4. Go to: https://www.binance.com/en/my/settings/api-management
5. Create new API Key
6. Name: `BRAINixIDEX Bot`
7. Enable **"Enable Reading"** only (for safety)
8. **Copy API Key and Secret**

#### Configure:

Edit `.env` file:

```properties
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_secret
BINANCE_TESTNET=False
```

---

## ⚙️ Configuration

### Environment Variables

Copy template and edit:

```bash
cp .env.template .env
```

Edit `.env`:

```properties
# Binance API (Optional)
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
BINANCE_TESTNET=True  # Set False for real market data

# AI Model Tokens
GITHUB_TOKEN=ghp_xxxxx
GOOGLE_API_KEY=AIza_xxxxx
HUGGINGFACE_TOKEN=hf_xxxxx
OPENAI_API_KEY=sk-xxxxx  # Optional
ANTHROPIC_API_KEY=sk-ant-xxxxx  # Optional

# Telegram Notifications (Optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

### Bot Configuration

Edit `src/utils/config.py` for advanced settings:

```python
# Trading Parameters
SYMBOL = 'BTCUSDT'
TIMEFRAME = '1h'
INITIAL_CAPITAL = 10000

# Risk Management
MAX_POSITION_SIZE = 0.1  # 10% of capital
STOP_LOSS_PERCENT = 0.02  # 2%
TAKE_PROFIT_PERCENT = 0.05  # 5%

# AI Models
ML_ENABLED = True
AI_VOTING_THRESHOLD = 0.6  # 60% agreement needed
```

---

## ✅ Verification

### Test Installation

```bash
python run.py test
```

Expected output:
```
✅ System tests passed
✅ Data handler working
✅ ML engine loaded
✅ Strategy initialized
```

### Test AI Models

```bash
python run.py test --ai-only
```

Expected output:
```
🤖 Testing AI Models...

✅ GitHub Models: 4 models
✅ Google Gemini: Working
✅ Hugging Face: Connected
✅ OpenAI: API Key valid
✅ Anthropic: API Key valid

🗳️ Voting Test: PASSED
```

### Test Price Data

```bash
python run.py price
```

Should display current Bitcoin price from multiple sources.

### Run Quick Analysis

```bash
python run.py analyze --symbol BTCUSDT --timeframe 1h
```

Should show market analysis with signals.

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Module Not Found Error

```
ModuleNotFoundError: No module named 'xxx'
```

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

#### 2. API Key Invalid

```
❌ API Key not valid
```

**Solution:**
- Check `.env` file for typos
- Regenerate API key
- Restart terminal to reload environment variables

#### 3. No Market Data

```
❌ Failed to fetch market data
```

**Solution:**
- Check internet connection
- Verify `BINANCE_TESTNET` setting in `.env`
- Try: `python scripts/update_cache.py`

#### 4. Import Errors After Restructuring

```
ImportError: cannot import name 'xxx'
```

**Solution:**
```bash
# Reinstall package
pip install -e . --force-reinstall
```

#### 5. Permission Denied (Linux/macOS)

```
Permission denied: 'xxx'
```

**Solution:**
```bash
chmod +x run.py
chmod +x scripts/*.py
```

### Get Help

1. **Check Documentation**: [docs/README.md](README.md)
2. **Run Diagnostics**: `python run.py test`
3. **Check Logs**: `data/logs/`
4. **GitHub Issues**: https://github.com/salmanabjam/BRAINixIDEX-Trading-Bot/issues

---

## 🚀 Next Steps

After successful setup:

1. ✅ **Run backtest**: `python run.py backtest`
2. ✅ **Analyze market**: `python run.py analyze`
3. ✅ **Monitor prices**: `python run.py price --live`
4. ✅ **Start dashboard**: `python run.py dashboard`
5. 📚 **Read API docs**: [docs/API.md](API.md)

---

## 📞 Support

- **Email**: support@brainixidex.com
- **GitHub Issues**: https://github.com/salmanabjam/BRAINixIDEX-Trading-Bot/issues
- **Documentation**: [docs/](.)

---

**Happy Trading! 🚀📈**
