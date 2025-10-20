"""
🤖 AI Predictor - Unified interface for multiple AI models
Seamlessly switch between LightGBM and GitHub/Azure models

Usage:
    predictor = AIPredictor(model_type=ModelType.GITHUB_PHI4)
    signal = predictor.predict(market_data, technical_indicators, fundamental_data)
"""

import os
import json
import requests
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from ai.models_config import (
    ModelType, AIModelsConfig, TRADING_PROMPT_TEMPLATE
)


class AIPredictor:
    """Unified AI predictor supporting multiple models"""
    
    def __init__(self, model_type: ModelType = ModelType.LIGHTGBM, timeframe: str = "1h"):
        """
        Initialize AI predictor
        
        Args:
            model_type: Type of model to use (from ModelType enum)
            timeframe: Trading timeframe (1h, 4h, 1d, etc.)
        """
        self.model_type = model_type
        self.timeframe = timeframe
        self.config = AIModelsConfig.get_model_config(model_type)
        
        # Initialize the appropriate engine
        if model_type == ModelType.LIGHTGBM:
            from core.ml_engine import MLEngine
            self.engine = MLEngine(timeframe=timeframe)
        else:
            self.engine = None  # Will use API calls
            
        # Verify API configuration
        if not AIModelsConfig.is_api_configured(model_type):
            print(f"⚠️ Warning: {self.config['name']} requires API setup")
            print(AIModelsConfig.get_setup_instructions(model_type))
    
    def predict(
        self,
        df: pd.DataFrame,
        symbol: str = "BTCUSDT",
        news_sentiment: str = "NEUTRAL",
        market_mood: str = "MIXED"
    ) -> Dict[str, Any]:
        """
        Make prediction using configured model
        
        Args:
            df: DataFrame with OHLCV and technical indicators
            symbol: Trading symbol
            news_sentiment: Fundamental news sentiment (BULLISH/BEARISH/NEUTRAL)
            market_mood: Overall market mood
            
        Returns:
            {
                'signal': 'BUY'|'SELL'|'HOLD',
                'confidence': 0.0-1.0,
                'reasoning': 'Explanation',
                'risk_level': 'LOW'|'MEDIUM'|'HIGH',
                'model_used': 'Model name',
                'success': True|False
            }
        """
        if self.model_type == ModelType.LIGHTGBM:
            return self._predict_lightgbm(df)
        else:
            return self._predict_llm(df, symbol, news_sentiment, market_mood)
    
    def _predict_lightgbm(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Predict using local LightGBM model"""
        try:
            # Make prediction
            predictions = self.engine.predict(df)
            
            if predictions is None or len(predictions) == 0:
                raise ValueError("No predictions returned from model")
            
            # Get last prediction
            signal = int(predictions[-1])
            
            # Get confidence (use prediction probabilities if available)
            try:
                confidence_df = self.engine.get_prediction_confidence(df)
                if confidence_df is not None and len(confidence_df) > 0:
                    last_pred = confidence_df.iloc[-1]
                    confidence = float(max(
                        last_pred.get('prob_sell', 0),
                        last_pred.get('prob_hold', 0),
                        last_pred.get('prob_buy', 0)
                    ))
                else:
                    confidence = 0.6  # Default confidence
            except:
                confidence = 0.6  # Default if confidence calculation fails
            
            # Map signal to standard format (signal is -1, 0, 1)
            signal_map = {-1: 'SELL', 0: 'HOLD', 1: 'BUY'}
            signal_name = signal_map.get(signal, 'HOLD')
            
            # Determine risk level based on confidence
            if confidence > 0.7:
                risk_level = 'LOW'
            elif confidence > 0.5:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'HIGH'
            
            return {
                'signal': signal_name,
                'confidence': float(confidence),
                'reasoning': f'LightGBM prediction with {confidence:.1%} confidence',
                'risk_level': risk_level,
                'model_used': 'LightGBM (Local)',
                'success': True
            }
        except Exception as e:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'reasoning': f'Error: {str(e)}',
                'risk_level': 'HIGH',
                'model_used': 'LightGBM (Error)',
                'success': False
            }
    
    def _predict_llm(
        self,
        df: pd.DataFrame,
        symbol: str,
        news_sentiment: str,
        market_mood: str
    ) -> Dict[str, Any]:
        """Predict using LLM via GitHub/Azure API"""
        try:
            # Extract latest market data
            latest = df.iloc[-1]
            
            # Prepare prompt with market data
            prompt = TRADING_PROMPT_TEMPLATE.format(
                symbol=symbol,
                timeframe=self.timeframe,
                current_price=latest.get('close', 0),
                price_change_24h=self._calc_price_change(df),
                rsi=latest.get('rsi', 50),
                macd=latest.get('macd', 0),
                macd_signal=latest.get('macd_signal', 0),
                bb_upper=latest.get('bb_upper', 0),
                bb_lower=latest.get('bb_lower', 0),
                volume=latest.get('volume', 0),
                news_sentiment=news_sentiment,
                market_mood=market_mood
            )
            
            # Call appropriate API
            if self.model_type.value.startswith('github_'):
                response = self._call_github_api(prompt)
            elif self.model_type == ModelType.AZURE_GPT4:
                response = self._call_azure_api(prompt)
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
            
            # Parse JSON response
            result = json.loads(response)
            result['model_used'] = self.config['name']
            result['success'] = True
            
            return result
            
        except Exception as e:
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'reasoning': f'API Error: {str(e)}',
                'risk_level': 'HIGH',
                'model_used': f'{self.config["name"]} (Error)',
                'success': False
            }
    
    def _call_github_api(self, prompt: str) -> str:
        """Call GitHub Models API"""
        endpoint = f"{AIModelsConfig.GITHUB_MODELS_ENDPOINT}chat/completions"
        
        headers = {
            "Authorization": f"Bearer {AIModelsConfig.GITHUB_PAT}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config['model_id'],
            "messages": [
                {
                    "role": "system",
                    "content": "You are a cryptocurrency trading expert. Respond ONLY with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.config['parameters'].get('temperature', 0.1),
            "max_tokens": self.config['parameters'].get('max_tokens', 500)
        }
        
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        # Extract response content
        data = response.json()
        content = data['choices'][0]['message']['content']
        
        # Clean JSON if wrapped in markdown
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        return content
    
    def _call_azure_api(self, prompt: str) -> str:
        """Call Azure OpenAI API"""
        endpoint = self.config['endpoint']
        api_key = self.config['api_key']
        
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a cryptocurrency trading expert. Respond ONLY with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }
        
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        content = data['choices'][0]['message']['content']
        
        # Clean JSON
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        
        return content
    
    def _calc_price_change(self, df: pd.DataFrame) -> float:
        """Calculate 24h price change percentage"""
        if len(df) < 24:
            return 0.0
        
        current_price = df.iloc[-1]['close']
        old_price = df.iloc[-24]['close']
        
        return ((current_price - old_price) / old_price) * 100
    
    def train(self, df: pd.DataFrame, force_retrain: bool = False) -> Dict[str, Any]:
        """
        Train model (only applicable for LightGBM)
        
        Args:
            df: Training data with indicators
            force_retrain: Force retraining even if model exists
            
        Returns:
            Training metrics or error message
        """
        if self.model_type != ModelType.LIGHTGBM:
            return {
                'success': False,
                'message': f'{self.config["name"]} does not require training'
            }
        
        try:
            metrics = self.engine.train(df)
            return {
                'success': True,
                'metrics': metrics,
                'message': 'Training completed successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Training failed: {str(e)}'
            }
    
    def auto_load_or_train(self, df: pd.DataFrame, force_train: bool = False) -> bool:
        """
        Auto-load existing model or train new one (LightGBM only)
        
        Args:
            df: Training data with indicators
            force_train: Force training even if model exists
            
        Returns:
            True if successful, False otherwise
        """
        if self.model_type != ModelType.LIGHTGBM:
            # API models don't need training
            return True
        
        try:
            return self.engine.auto_load_or_train(df, force_train=force_train)
        except Exception as e:
            print(f"❌ Error in auto_load_or_train: {str(e)}")
            return False


# 🧪 Test and comparison function
def compare_models(df: pd.DataFrame, symbol: str = "BTCUSDT") -> pd.DataFrame:
    """
    Compare predictions from all available models
    
    Args:
        df: Market data with technical indicators
        symbol: Trading symbol
        
    Returns:
        DataFrame with comparison results
    """
    results = []
    
    print("🔬 Comparing AI Models...\n")
    
    for model_type in ModelType:
        # Check if model is configured
        if not AIModelsConfig.is_api_configured(model_type):
            print(f"⏭️ Skipping {model_type.value} - Not configured")
            continue
        
        print(f"Testing {model_type.value}...")
        
        try:
            predictor = AIPredictor(model_type=model_type)
            prediction = predictor.predict(df, symbol=symbol)
            
            results.append({
                'Model': prediction['model_used'],
                'Signal': prediction['signal'],
                'Confidence': f"{prediction['confidence']:.2%}",
                'Risk': prediction['risk_level'],
                'Reasoning': prediction['reasoning'][:50] + '...',
                'Success': '✅' if prediction['success'] else '❌'
            })
            
        except Exception as e:
            results.append({
                'Model': model_type.value,
                'Signal': 'ERROR',
                'Confidence': '0%',
                'Risk': 'N/A',
                'Reasoning': str(e)[:50] + '...',
                'Success': '❌'
            })
    
    return pd.DataFrame(results)


if __name__ == "__main__":
    print("🤖 AI Predictor Test\n")
    
    # Test with sample data
    from data.handler import DataHandler
    from data.indicators import TechnicalIndicators
    
    print("📥 Fetching market data...")
    handler = DataHandler()
    df = handler.fetch_ohlcv(symbol="BTCUSDT", timeframe="1h", limit=100)
    
    print("📊 Calculating indicators...")
    indicators = TechnicalIndicators(df)
    df_indicators = indicators.calculate_all()
    
    print("\n" + "="*60 + "\n")
    
    # Test LightGBM (default)
    print("🧪 Testing LightGBM...")
    predictor = AIPredictor(model_type=ModelType.LIGHTGBM)
    result = predictor.predict(df_indicators)
    
    print(f"Signal: {result['signal']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Risk: {result['risk_level']}")
    print(f"Reasoning: {result['reasoning']}")
    
    print("\n" + "="*60 + "\n")
    
    # Compare all models (if APIs are configured)
    print("📊 Model Comparison:")
    comparison = compare_models(df_indicators, symbol="BTCUSDT")
    print(comparison.to_string(index=False))
