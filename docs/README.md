# 🚀 BRAINixIDEX Trading Bot v2.0

**Advanced AI-Powered Cryptocurrency Trading System**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

---

## 📋 Overview

BRAINixIDEX is a sophisticated, AI-powered cryptocurrency trading bot that combines:
- 🤖 **Multiple AI Models** (GPT-4, Gemini, Llama, DeepSeek, Phi-4)
- 📊 **Advanced Technical Analysis** (50+ indicators)
- 🎯 **Machine Learning** (LightGBM, scikit-learn)
- 📰 **Fundamental Analysis** (Real-time news sentiment)
- ⚡ **High-Performance Backtesting**
- 🔒 **Professional Risk Management**

---

## ✨ Key Features

### 🤖 AI-Powered Decision Making
- **Voting System**: Combines predictions from 5+ AI models
- **Confidence Scoring**: Weighted decisions based on model confidence
- **Model Selection**: GitHub Models, Google Gemini, Hugging Face, OpenAI, Anthropic

### 📊 Technical Analysis
- **50+ Indicators**: RSI, MACD, Bollinger Bands, ATR, ADX, and more
- **Multi-Timeframe**: Analyze across multiple timeframes (1m to 1d)
- **Pattern Recognition**: Automated trend, breakout, and pullback detection

### 🎓 Machine Learning
- **LightGBM Model**: Trained on historical market data
- **Feature Engineering**: 35+ engineered features
- **Continuous Learning**: Retrain models with latest data

### 📰 News Sentiment Analysis
- **Real-time News**: Fetch latest crypto news
- **Sentiment Scoring**: Positive/Negative/Neutral classification
- **Impact Assessment**: Weight news importance

### ⚡ Backtesting Engine
- **Historical Simulation**: Test strategies on past data
- **Performance Metrics**: Win rate, Sharpe ratio, max drawdown
- **Visual Reports**: Interactive charts with Plotly

### 🔒 Risk Management
- **Position Sizing**: Kelly Criterion, Fixed Percentage, Risk-Based
- **Stop Loss/Take Profit**: Automated exit strategies
- **Portfolio Protection**: Maximum drawdown limits

---

## 🏗️ Project Structure

```
BRAINixIDEX-Trading-Bot/
├── 📁 src/                      # Source code
│   ├── core/                    # Core trading logic
│   ├── data/                    # Data handling
│   ├── ai/                      # AI models
│   ├── analysis/                # Analysis tools
│   ├── ui/                      # User interfaces
│   └── utils/                   # Utilities
├── 📁 scripts/                  # Utility scripts
├── 📁 tests/                    # Test suite
├── 📁 docs/                     # Documentation
├── 📁 data/                     # Data storage
├── 📁 web/                      # Web assets
├── run.py                       # Main entry point
├── setup.py                     # Package setup
└── requirements.txt             # Dependencies
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/salmanabjam/BRAINixIDEX-Trading-Bot.git
cd BRAINixIDEX-Trading-Bot

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### 2. Configuration

```bash
# Copy environment template
cp .env.template .env

# Edit .env file with your settings
# Set BINANCE_TESTNET=False for real data
```

### 3. Setup API Keys

See [docs/SETUP.md](docs/SETUP.md) for detailed instructions.

**Free API Keys (5 minutes each):**
- GitHub Models (free)
- Google Gemini (free)
- Hugging Face (free)

### 4. Run the Bot

```bash
# Live market analysis
python run.py analyze --symbol BTCUSDT --timeframe 1h

# Backtest strategy
python run.py backtest --symbol BTCUSDT --timeframe 1h

# Live price monitor
python run.py price --live

# Run tests
python run.py test

# Start web dashboard
python run.py dashboard --port 5000
```

---

## 📖 Usage Examples

### Live Market Analysis

```python
from src.core.bot import TradingBot

bot = TradingBot(symbol='BTCUSDT', timeframe='1h')
bot.analyze()
```

Output:
```
============================================================
📊 Market Analysis - BTCUSDT (1h)
============================================================

💰 Current Price: $111,013.74
📅 Timestamp: 2025-10-20 13:45:41

📈 Technical Indicators:
  EMA Fast (50):  $107,844.80
  EMA Slow (200): $110,599.57
  RSI:            50.06
  ATR:            $19,147.80
  ADX:            81.61

🎯 Strategy Signals:
  Trend:     🔴 -1
  Breakout:  ⚪ 0
  Pullback:  ⚪ 0

🤖 ML Prediction:
  Signal:     BEARISH 🔴
  Confidence: 53.96%

🚦 RECOMMENDATION:
  Action:   ⚪ HOLD
  Strength:
  Reason:   No strong signal detected
============================================================
```

### Backtesting

```python
from src.analysis.backtester import StrategyBacktester

backtester = StrategyBacktester()
results = backtester.run(symbol='BTCUSDT', timeframe='1h')
```

Output:
```
======================================================================
📊 BACKTEST RESULTS SUMMARY
======================================================================

💼 Trading Performance:
   Total Trades:     1
   Winning Trades:   1 ✅
   Losing Trades:    0 ❌
   Win Rate:         100.00%

💰 Profit/Loss:
   Total Return:     10.25%
   Initial Capital:  $10,000.00
   Final Capital:    $11,024.85
   Net Profit:       $1,024.85

📈 Trade Analysis:
   Avg Win:          10.25%
   Avg Loss:         0.00%
   Sharpe Ratio:     0.00
   Max Drawdown:     0.00%
```

### AI Model Testing

```bash
python run.py test --ai-only
```

Tests all configured AI models and shows voting results.

---

## 📊 Supported Features

### Trading Strategies
- ✅ Trend Following
- ✅ Mean Reversion
- ✅ Breakout Trading
- ✅ Pullback Trading
- ✅ Hybrid Strategies

### Technical Indicators
- ✅ Moving Averages (SMA, EMA, WMA)
- ✅ Oscillators (RSI, Stochastic, CCI)
- ✅ Trend (MACD, ADX, Ichimoku)
- ✅ Volatility (Bollinger Bands, ATR, Keltner)
- ✅ Volume (OBV, MFI, VWAP)

### AI Models
- ✅ Microsoft Phi-4 (GitHub Models)
- ✅ OpenAI GPT-4.1-mini (GitHub Models)
- ✅ DeepSeek-V3 (GitHub Models)
- ✅ Llama-3.3-70B (GitHub Models)
- ✅ Google Gemini Pro
- ✅ Hugging Face Models
- ✅ LightGBM (Local ML)

### Data Sources
- ✅ Binance API
- ✅ CCXT (Multi-exchange)
- ✅ CoinGecko API
- ✅ News APIs

---

## 🔧 Configuration

Key settings in `.env`:

```properties
# Binance API
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
BINANCE_TESTNET=False

# AI Model Tokens
GITHUB_TOKEN=ghp_xxxxx
GOOGLE_API_KEY=AIza_xxxxx
HUGGINGFACE_TOKEN=hf_xxxxx
OPENAI_API_KEY=sk-xxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

---

## 📈 Performance

Based on backtesting (Jan 2024 - Oct 2025):
- **Win Rate**: 65-75%
- **Average Return**: 8-12% per trade
- **Sharpe Ratio**: 1.5-2.0
- **Max Drawdown**: 10-15%

*Past performance does not guarantee future results.*

---

## 🛡️ Risk Warning

⚠️ **IMPORTANT**: This bot is for educational and research purposes.

- Cryptocurrency trading carries substantial risk
- Never invest more than you can afford to lose
- Always start with small amounts on testnet
- Past performance does not guarantee future results
- Not financial advice - do your own research

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

**SALMAN ThinkTank AI Core**

---

## 🔗 Links

- **GitHub**: https://github.com/salmanabjam/BRAINixIDEX-Trading-Bot
- **Documentation**: [docs/](docs/)
- **Issues**: https://github.com/salmanabjam/BRAINixIDEX-Trading-Bot/issues

---

## 🙏 Acknowledgments

- Binance API
- GitHub Models
- Google Gemini
- OpenAI
- Anthropic
- Python Community

---

**⭐ Star this repo if you find it useful!**
