"""
Improved ML Training Script
============================
Enhanced ML model training with better features and hyperparameters.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pandas as pd
import numpy as np
from data.handler import DataHandler
from data.indicators import TechnicalIndicators
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import lightgbm as lgb
import pickle
from colorama import init, Fore, Style

init(autoreset=True)


def create_advanced_features(df):
    """Create advanced ML features"""
    df = df.copy()
    
    print(f"{Fore.YELLOW}🔧 Engineering advanced features...{Style.RESET_ALL}")
    
    # Price features
    df['returns'] = df['close'].pct_change()
    df['returns_5'] = df['close'].pct_change(5)
    df['returns_10'] = df['close'].pct_change(10)
    df['returns_20'] = df['close'].pct_change(20)
    
    # Volatility features
    df['volatility_5'] = df['returns'].rolling(5).std()
    df['volatility_20'] = df['returns'].rolling(20).std()
    
    # Volume features
    df['volume_change'] = df['volume'].pct_change()
    df['volume_ma_5'] = df['volume'].rolling(5).mean()
    df['volume_ma_20'] = df['volume'].rolling(20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma_20']
    
    # Trend features
    df['ema_diff'] = df['ema_fast'] - df['ema_slow']
    df['ema_trend'] = np.where(df['ema_fast'] > df['ema_slow'], 1, 0)
    df['ema_cross'] = df['ema_trend'].diff()
    
    # RSI features
    df['rsi_change'] = df['rsi'].diff()
    df['rsi_ma'] = df['rsi'].rolling(5).mean()
    df['rsi_oversold'] = np.where(df['rsi'] < 30, 1, 0)
    df['rsi_overbought'] = np.where(df['rsi'] > 70, 1, 0)
    
    # ADX features
    df['adx_strong_trend'] = np.where(df['adx'] > 25, 1, 0)
    df['di_diff'] = df['di_plus'] - df['di_minus']
    
    # Donchian features
    df['donchian_range'] = df['donchian_upper'] - df['donchian_lower']
    df['price_to_upper'] = df['close'] / df['donchian_upper']
    df['price_to_lower'] = df['close'] / df['donchian_lower']
    
    # ATR features
    df['atr_pct'] = df['atr'] / df['close'] * 100
    
    # Drop NaN
    df = df.dropna()
    
    return df


def create_target(df, forward_periods=5, profit_threshold=0.01):
    """
    Create target variable for ML:
    0 = SELL (price will drop > threshold)
    1 = HOLD (price stays within threshold)
    2 = BUY (price will rise > threshold)
    """
    forward_return = df['close'].shift(-forward_periods) / df['close'] - 1
    
    df['target'] = 1  # Default HOLD
    df.loc[forward_return > profit_threshold, 'target'] = 2  # BUY
    df.loc[forward_return < -profit_threshold, 'target'] = 0  # SELL
    
    return df


def main():
    print("=" * 70)
    print(f"{Fore.CYAN}🎓 Advanced ML Model Training{Style.RESET_ALL}")
    print("=" * 70)
    
    # 1. Load data
    print(f"\n{Fore.YELLOW}📊 Loading market data...{Style.RESET_ALL}")
    dh = DataHandler()
    df = dh.fetch_ohlcv(symbol='BTCUSDT', timeframe='1h', use_cache=True)
    print(f"   Loaded {len(df)} candles")
    
    # 2. Calculate indicators
    print(f"\n{Fore.YELLOW}📈 Calculating technical indicators...{Style.RESET_ALL}")
    indicators = TechnicalIndicators(df)
    df = indicators.calculate_all()
    print(f"   Calculated {len(df.columns)} indicators")
    
    # 3. Engineer features
    df = create_advanced_features(df)
    print(f"   Created {len(df.columns)} total features")
    
    # 4. Create target variable
    print(f"\n{Fore.YELLOW}🎯 Creating target variable...{Style.RESET_ALL}")
    df = create_target(df, forward_periods=5, profit_threshold=0.015)
    df = df[:-5]  # Remove last 5 rows (no future data)
    
    # Check class distribution
    print(f"\n📊 Class Distribution:")
    print(df['target'].value_counts())
    print(f"   SELL (0): {(df['target'] == 0).sum()}")
    print(f"   HOLD (1): {(df['target'] == 1).sum()}")
    print(f"   BUY (2):  {(df['target'] == 2).sum()}")
    
    # 5. Prepare features
    feature_cols = [
        'returns', 'returns_5', 'returns_10', 'returns_20',
        'volatility_5', 'volatility_20',
        'volume_change', 'volume_ratio',
        'ema_diff', 'ema_trend', 'ema_cross',
        'rsi', 'rsi_change', 'rsi_ma', 'rsi_oversold', 'rsi_overbought',
        'atr_pct', 'adx', 'adx_strong_trend', 'di_diff',
        'donchian_range', 'price_to_upper', 'price_to_lower',
        'trend_signal', 'breakout_signal', 'pullback_signal'
    ]
    
    X = df[feature_cols]
    y = df['target']
    
    # 6. Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n{Fore.YELLOW}📊 Dataset split:{Style.RESET_ALL}")
    print(f"   Training samples: {len(X_train)}")
    print(f"   Test samples:     {len(X_test)}")
    
    # 7. Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 8. Train multiple models and compare
    print(f"\n{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🤖 Training Models...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
    
    models = {}
    
    # LightGBM with better parameters
    print(f"\n1️⃣  {Fore.YELLOW}Training LightGBM...{Style.RESET_ALL}")
    lgbm = lgb.LGBMClassifier(
        objective='multiclass',
        num_class=3,
        n_estimators=200,
        learning_rate=0.05,
        max_depth=7,
        num_leaves=31,
        min_child_samples=20,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbose=-1
    )
    lgbm.fit(X_train_scaled, y_train)
    lgbm_pred = lgbm.predict(X_test_scaled)
    lgbm_acc = accuracy_score(y_test, lgbm_pred)
    models['LightGBM'] = (lgbm, lgbm_acc, lgbm_pred)
    print(f"   Accuracy: {Fore.GREEN}{lgbm_acc:.2%}{Style.RESET_ALL}")
    
    # Random Forest
    print(f"\n2️⃣  {Fore.YELLOW}Training Random Forest...{Style.RESET_ALL}")
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train_scaled, y_train)
    rf_pred = rf.predict(X_test_scaled)
    rf_acc = accuracy_score(y_test, rf_pred)
    models['Random Forest'] = (rf, rf_acc, rf_pred)
    print(f"   Accuracy: {Fore.GREEN}{rf_acc:.2%}{Style.RESET_ALL}")
    
    # Gradient Boosting
    print(f"\n3️⃣  {Fore.YELLOW}Training Gradient Boosting...{Style.RESET_ALL}")
    gb = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    gb.fit(X_train_scaled, y_train)
    gb_pred = gb.predict(X_test_scaled)
    gb_acc = accuracy_score(y_test, gb_pred)
    models['Gradient Boosting'] = (gb, gb_acc, gb_pred)
    print(f"   Accuracy: {Fore.GREEN}{gb_acc:.2%}{Style.RESET_ALL}")
    
    # 9. Select best model
    best_model_name = max(models, key=lambda k: models[k][1])
    best_model, best_acc, best_pred = models[best_model_name]
    
    print(f"\n{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🏆 Best Model: {best_model_name} ({best_acc:.2%}){Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
    
    # 10. Detailed metrics
    print(f"\n📊 Classification Report:\n")
    print(classification_report(
        y_test, best_pred,
        target_names=['SELL', 'HOLD', 'BUY'],
        digits=4
    ))
    
    # 11. Save best model
    print(f"\n{Fore.YELLOW}💾 Saving model and scaler...{Style.RESET_ALL}")
    Path('models').mkdir(exist_ok=True)
    
    with open('models/trained_model.pkl', 'wb') as f:
        pickle.dump(best_model, f)
    
    with open('models/scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    with open('models/feature_columns.pkl', 'wb') as f:
        pickle.dump(feature_cols, f)
    
    print(f"{Fore.GREEN}✅ Model saved successfully!{Style.RESET_ALL}")
    print(f"   Model: models/trained_model.pkl")
    print(f"   Scaler: models/scaler.pkl")
    print(f"   Features: models/feature_columns.pkl")
    
    print(f"\n{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ Training Complete!{Style.RESET_ALL}")
    print(f"   Best Model: {best_model_name}")
    print(f"   Accuracy:   {best_acc:.2%}")
    print(f"   Features:   {len(feature_cols)}")
    print(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
