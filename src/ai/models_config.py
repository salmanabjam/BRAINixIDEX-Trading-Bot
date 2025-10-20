"""
🤖 AI Models Configuration
Configure and switch between different AI models for trading predictions

Supports:
- LightGBM (Current, Fast, Local)
- GitHub Models API (GPT-4, Phi-4, DeepSeek, etc.)
- Azure AI Foundry Models
- Custom Fine-tuned Models
"""

import os
from enum import Enum
from typing import Dict, Any, Optional
import json


class ModelType(Enum):
    """Available model types"""
    LIGHTGBM = "lightgbm"
    GITHUB_GPT4 = "github_gpt4"
    GITHUB_PHI4 = "github_phi4"
    GITHUB_DEEPSEEK = "github_deepseek"
    GITHUB_LLAMA = "github_llama"
    AZURE_GPT4 = "azure_gpt4"
    CUSTOM = "custom"


class AIModelsConfig:
    """Configuration for AI models"""
    
    # GitHub Models API Configuration
    GITHUB_MODELS_ENDPOINT = "https://models.github.ai/inference/"
    GITHUB_PAT = os.getenv("GITHUB_TOKEN", "")  # GitHub Personal Access Token
    
    # Model Selection for Trading
    MODEL_CONFIGS = {
        # Local LightGBM (Fast, No API needed)
        ModelType.LIGHTGBM: {
            "name": "LightGBM",
            "description": "Local gradient boosting model (Current)",
            "requires_api": False,
            "cost_per_1m_tokens": 0,
            "speed": "Fast",
            "accuracy_estimate": "Good (48-75%)",
            "parameters": {
                "num_leaves": 31,
                "max_depth": -1,
                "learning_rate": 0.05,
            }
        },
        
        # GitHub Models (Free tier available)
        ModelType.GITHUB_GPT4: {
            "name": "OpenAI GPT-4.1-mini",
            "model_id": "openai/gpt-4.1-mini",
            "description": "Advanced reasoning for market analysis",
            "requires_api": True,
            "cost_per_1m_tokens": 0.7,
            "speed": "Medium",
            "accuracy_estimate": "Very High (85-95%)",
            "context_window": "1M tokens",
            "parameters": {
                "temperature": 0.1,  # Low temp for deterministic predictions
                "max_tokens": 500,
            }
        },
        
        ModelType.GITHUB_PHI4: {
            "name": "Microsoft Phi-4",
            "model_id": "microsoft/phi-4",
            "description": "Efficient reasoning model for trading signals",
            "requires_api": True,
            "cost_per_1m_tokens": 0.2188,
            "speed": "Fast",
            "accuracy_estimate": "High (75-85%)",
            "context_window": "16K tokens",
            "parameters": {
                "temperature": 0.1,
                "max_tokens": 300,
            }
        },
        
        ModelType.GITHUB_DEEPSEEK: {
            "name": "DeepSeek-V3",
            "model_id": "deepseek/deepseek-v3-0324",
            "description": "Advanced reasoning for crypto analysis",
            "requires_api": True,
            "cost_per_1m_tokens": 1.9975,
            "speed": "Medium",
            "accuracy_estimate": "Very High (85-92%)",
            "context_window": "128K tokens",
            "parameters": {
                "temperature": 0.1,
                "max_tokens": 400,
            }
        },
        
        ModelType.GITHUB_LLAMA: {
            "name": "Llama-3.3-70B",
            "model_id": "meta/llama-3.3-70b-instruct",
            "description": "Meta's advanced reasoning model",
            "requires_api": True,
            "cost_per_1m_tokens": 0.71,
            "speed": "Medium",
            "accuracy_estimate": "High (80-90%)",
            "context_window": "128K tokens",
            "parameters": {
                "temperature": 0.1,
                "max_tokens": 300,
            }
        },
        
        # Azure AI Foundry
        ModelType.AZURE_GPT4: {
            "name": "Azure GPT-4",
            "model_id": "gpt-4",
            "description": "Azure-hosted GPT-4 for enterprise",
            "requires_api": True,
            "cost_per_1m_tokens": 15.0,
            "speed": "Medium",
            "accuracy_estimate": "Very High (90-95%)",
            "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            "api_key": os.getenv("AZURE_OPENAI_KEY", ""),
        }
    }
    
    # Default model
    DEFAULT_MODEL = ModelType.LIGHTGBM
    
    @classmethod
    def get_model_config(cls, model_type: ModelType) -> Dict[str, Any]:
        """Get configuration for a specific model"""
        return cls.MODEL_CONFIGS.get(model_type, cls.MODEL_CONFIGS[cls.DEFAULT_MODEL])
    
    @classmethod
    def list_available_models(cls) -> list:
        """List all available models"""
        return [
            {
                "type": model_type.value,
                "name": config["name"],
                "description": config["description"],
                "requires_api": config["requires_api"],
                "cost": f"${config.get('cost_per_1m_tokens', 0)}/1M tokens",
                "speed": config.get("speed", "N/A"),
                "accuracy": config.get("accuracy_estimate", "N/A"),
            }
            for model_type, config in cls.MODEL_CONFIGS.items()
        ]
    
    @classmethod
    def is_api_configured(cls, model_type: ModelType) -> bool:
        """Check if API credentials are configured for a model"""
        config = cls.get_model_config(model_type)
        
        if not config.get("requires_api", False):
            return True  # Local models don't need API
        
        if model_type.value.startswith("github_"):
            return bool(cls.GITHUB_PAT)
        
        if model_type == ModelType.AZURE_GPT4:
            return bool(config.get("endpoint") and config.get("api_key"))
        
        return False
    
    @classmethod
    def get_setup_instructions(cls, model_type: ModelType) -> str:
        """Get setup instructions for a model"""
        config = cls.get_model_config(model_type)
        
        if not config.get("requires_api", False):
            return "✅ No setup required - Local model"
        
        if model_type.value.startswith("github_"):
            return """
📝 GitHub Models Setup:
1. Create GitHub Personal Access Token (PAT):
   https://github.com/settings/tokens
2. Set environment variable:
   Windows: setx GITHUB_TOKEN "your_token_here"
   Linux/Mac: export GITHUB_TOKEN="your_token_here"
3. Restart terminal/IDE
4. Free tier available with rate limits
            """
        
        if model_type == ModelType.AZURE_GPT4:
            return """
📝 Azure OpenAI Setup:
1. Create Azure OpenAI resource
2. Deploy GPT-4 model
3. Set environment variables:
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_KEY=your_api_key
4. Restart terminal/IDE
            """
        
        return "Setup instructions not available"
    
    @classmethod
    def save_preference(cls, model_type: ModelType, filepath: str = "model_preference.json"):
        """Save model preference to file"""
        with open(filepath, 'w') as f:
            json.dump({"selected_model": model_type.value}, f)
    
    @classmethod
    def load_preference(cls, filepath: str = "model_preference.json") -> ModelType:
        """Load model preference from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return ModelType(data.get("selected_model", cls.DEFAULT_MODEL.value))
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            return cls.DEFAULT_MODEL


# 🎯 Trading Prompt Template for LLM Models
TRADING_PROMPT_TEMPLATE = """
You are an expert cryptocurrency trading AI analyzing market data to predict price movement.

📊 Market Data:
Symbol: {symbol}
Timeframe: {timeframe}
Current Price: ${current_price}
24h Change: {price_change_24h}%

📈 Technical Indicators:
RSI: {rsi}
MACD: {macd}
Signal: {macd_signal}
BB Upper: {bb_upper}
BB Lower: {bb_lower}
Volume: {volume}

📰 Fundamental Analysis:
News Sentiment: {news_sentiment}
Market Mood: {market_mood}

🎯 Your Task:
Predict the next price movement with ONE of these signals:
- BUY: Strong bullish indicators, expect price increase
- SELL: Strong bearish indicators, expect price decrease  
- HOLD: Mixed signals, wait for better opportunity

Respond ONLY with JSON format:
{{
    "signal": "BUY|SELL|HOLD",
    "confidence": 0.0-1.0,
    "reasoning": "Brief 1-2 sentence explanation",
    "risk_level": "LOW|MEDIUM|HIGH"
}}
"""


if __name__ == "__main__":
    # Test configuration
    print("🤖 AI Models Configuration\n")
    
    print("Available Models:")
    print("=" * 60)
    for model in AIModelsConfig.list_available_models():
        print(f"\n📦 {model['name']}")
        print(f"   Type: {model['type']}")
        print(f"   Description: {model['description']}")
        print(f"   Speed: {model['speed']}")
        print(f"   Accuracy: {model['accuracy']}")
        print(f"   Cost: {model['cost']}")
        print(f"   API Required: {'Yes' if model['requires_api'] else 'No'}")
    
    print("\n" + "=" * 60)
    print("\n✅ Configuration loaded successfully!")
    
    # Check API setup
    print("\n🔑 API Status:")
    for model_type in ModelType:
        status = "✅ Configured" if AIModelsConfig.is_api_configured(model_type) else "❌ Not configured"
        print(f"   {model_type.value}: {status}")
