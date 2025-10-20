"""
🧪 تست مدل‌های هوش مصنوعی
Test all AI models (LightGBM, GitHub Models, Azure)
"""

import sys
from ai_predictor import AIPredictor
from ai_models_config import ModelType, AIModelsConfig
from data_handler import DataHandler
from indicators import TechnicalIndicators


def test_model(model_type: ModelType, symbol: str = "BTCUSDT"):
    """Test a specific AI model"""
    model_name = AIModelsConfig.get_model_config(model_type)['name']
    
    print(f"\n{'='*70}")
    print(f"🧪 Testing: {model_name}")
    print(f"{'='*70}")
    
    # Check API configuration
    if not AIModelsConfig.is_api_configured(model_type):
        print(f"⚠️  Model requires API setup")
        print(AIModelsConfig.get_setup_instructions(model_type))
        print(f"❌ SKIPPED - Not configured\n")
        return None
    
    try:
        # Create predictor
        print(f"   🔧 Initializing predictor...")
        predictor = AIPredictor(model_type=model_type, timeframe="1h")
        
        # Fetch and prepare data
        print(f"   📥 Fetching market data...")
        handler = DataHandler()
        df = handler.fetch_ohlcv(symbol=symbol, timeframe="1h", limit=100)
        
        print(f"   📊 Calculating indicators...")
        indicators = TechnicalIndicators(df)
        df_with_indicators = indicators.calculate_all()
        
        # Make prediction
        print(f"   🤖 Making prediction...")
        result = predictor.predict(
            df=df_with_indicators,
            symbol=symbol,
            news_sentiment="BULLISH",
            market_mood="POSITIVE"
        )
        
        # Display result
        if result['success']:
            print(f"\n   ✅ Prediction successful!")
            print(f"   📊 Signal: {result['signal']}")
            print(f"   📈 Confidence: {result['confidence']:.2%}")
            print(f"   ⚠️  Risk: {result['risk_level']}")
            print(f"   💭 Reasoning: {result['reasoning'][:80]}...")
            print(f"   🤖 Model: {result['model_used']}")
            print(f"\n   ✅ PASSED")
            return result
        else:
            print(f"\n   ❌ Prediction failed!")
            print(f"   Error: {result['reasoning']}")
            print(f"   ❌ FAILED")
            return None
            
    except Exception as e:
        print(f"\n   ❌ Exception occurred!")
        print(f"   Error: {str(e)}")
        print(f"   ❌ FAILED")
        return None


def main():
    """Run all tests"""
    print("="*70)
    print("🚀 تست تمام مدل‌های هوش مصنوعی")
    print("   Testing All AI Models")
    print("="*70)
    
    symbol = "BTCUSDT"
    
    # Models to test
    models_to_test = [
        (ModelType.LIGHTGBM, "LightGBM (Local)"),
        (ModelType.GITHUB_PHI4, "Microsoft Phi-4"),
        (ModelType.GITHUB_GPT4, "OpenAI GPT-4.1-mini"),
        (ModelType.GITHUB_DEEPSEEK, "DeepSeek-V3"),
        (ModelType.GITHUB_LLAMA, "Llama-3.3-70B"),
        (ModelType.AZURE_GPT4, "Azure GPT-4"),
    ]
    
    results = []
    passed = 0
    failed = 0
    skipped = 0
    
    for model_type, model_name in models_to_test:
        result = test_model(model_type, symbol)
        
        if result is not None:
            results.append((model_name, result))
            passed += 1
        elif result is None and AIModelsConfig.is_api_configured(model_type):
            failed += 1
        else:
            skipped += 1
    
    # Summary
    print("\n" + "="*70)
    print("📊 Summary of AI Models Test")
    print("="*70)
    
    if results:
        print(f"\n✅ Successful Predictions ({passed}):")
        print("-"*70)
        for model_name, result in results:
            print(f"   {model_name:25} → {result['signal']:5} "
                  f"({result['confidence']:.0%} confidence)")
    
    if failed > 0:
        print(f"\n❌ Failed: {failed}")
    
    if skipped > 0:
        print(f"\n⏭️  Skipped (not configured): {skipped}")
    
    # Voting results
    if results:
        print("\n" + "="*70)
        print("🗳️  Voting Results (All Models)")
        print("="*70)
        
        signals = [r[1]['signal'] for r in results]
        buy_votes = signals.count('BUY')
        sell_votes = signals.count('SELL')
        hold_votes = signals.count('HOLD')
        
        print(f"   BUY:  {buy_votes} votes")
        print(f"   SELL: {sell_votes} votes")
        print(f"   HOLD: {hold_votes} votes")
        
        # Final decision
        if buy_votes > sell_votes and buy_votes > hold_votes:
            final_signal = "BUY 🟢"
        elif sell_votes > buy_votes and sell_votes > hold_votes:
            final_signal = "SELL 🔴"
        else:
            final_signal = "HOLD 🟡"
        
        avg_confidence = sum(r[1]['confidence'] for r in results) / len(results)
        
        print(f"\n   ✅ Final Decision: {final_signal}")
        print(f"   📊 Average Confidence: {avg_confidence:.2%}")
    
    print("\n" + "="*70)
    print(f"🎯 Total: {passed} passed, {failed} failed, {skipped} skipped")
    print("="*70)
    
    # Setup instructions for skipped models
    if skipped > 0:
        print("\n💡 To enable GitHub Models (Free tier available):")
        print("   1. Get GitHub Token: https://github.com/settings/tokens")
        print("   2. Enable 'read:packages' permission")
        print("   3. Run:")
        print("      setx GITHUB_TOKEN \"ghp_your_token\"")
        print("   4. Restart terminal and run this test again")


if __name__ == "__main__":
    main()
