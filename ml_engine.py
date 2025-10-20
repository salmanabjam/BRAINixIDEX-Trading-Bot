"""
BiX TradeBOT - Machine Learning Engine
=======================================
ML model training and prediction for trade signal enhancement.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import pandas as pd
import numpy as np
import pickle
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import lightgbm as lgb
import warnings

warnings.filterwarnings('ignore')

from config import Config

logger = logging.getLogger(__name__)


class MLEngine:
    """
    Machine Learning engine for trade signal prediction.
    Uses LightGBM with engineered features from technical indicators.
    """

    def __init__(self, timeframe: str = None):
        """
        Initialize ML Engine.
        
        Args:
            timeframe: Specific timeframe for model (None = default from config)
        """
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.is_trained = False
        self.timeframe = timeframe or Config.TIMEFRAME

        # Support timeframe-specific models
        if timeframe:
            self.model_path = Path(f'models/model_{timeframe}.pkl')
            self.scaler_path = Path(f'models/scaler_{timeframe}.pkl')
        else:
            self.model_path = Path(Config.MODEL_SAVE_PATH)
            self.scaler_path = Path(Config.SCALER_SAVE_PATH)

        # Create model directory
        self.model_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"🤖 ML Engine initialized (Timeframe: {self.timeframe})")

    def engineer_features(self, df):
        """
        Create ML features from indicator data.

        Args:
            df (pd.DataFrame): DataFrame with technical indicators

        Returns:
            pd.DataFrame: DataFrame with engineered features
        """
        logger.info("🔧 Engineering ML features...")

        df = df.copy()

        # Price momentum features
        df['price_change'] = df['close'].pct_change()
        df['price_change_5'] = df['close'].pct_change(5)
        df['price_change_10'] = df['close'].pct_change(10)

        # Volume features
        df['volume_change'] = df['volume'].pct_change()
        df['volume_ma_ratio'] = df['volume'] / df['volume'].rolling(20).mean()

        # EMA crossover features
        df['ema_diff'] = df['ema_fast'] - df['ema_slow']
        df['ema_diff_pct'] = (
            (df['ema_fast'] - df['ema_slow']) / df['ema_slow'] * 100
        )

        # RSI momentum
        df['rsi_change'] = df['rsi'].diff()
        df['rsi_ma'] = df['rsi'].rolling(5).mean()

        # ATR normalized
        df['atr_pct'] = df['atr'] / df['close'] * 100

        # Donchian position
        df['donchian_position'] = (
            (df['close'] - df['donchian_lower']) /
            (df['donchian_upper'] - df['donchian_lower'])
        )

        # Trend strength
        df['adx_change'] = df['adx'].diff()
        df['di_diff'] = df['di_plus'] - df['di_minus']

        # Rolling statistics
        df['close_z_score'] = (
            (df['close'] - df['close'].rolling(20).mean()) /
            df['close'].rolling(20).std()
        )

        # Lagged features
        df['signal_lag1'] = df['combined_signal'].shift(1)
        df['signal_lag2'] = df['combined_signal'].shift(2)

        # Drop NaN values created by feature engineering
        df = df.dropna()

        logger.info(f"✅ Features engineered. Shape: {df.shape}")
        return df

    def prepare_training_data(self, df, target_column='future_return'):
        """
        Prepare data for training.

        Args:
            df (pd.DataFrame): DataFrame with features
            target_column (str): Name of target column

        Returns:
            tuple: (X_train, X_test, y_train, y_test)
        """
        # Create target: future return
        # Labels: 0 = Sell/Short, 1 = Hold/Neutral, 2 = Buy/Long
        df['future_return'] = df['close'].shift(-1) - df['close']
        df['target'] = 1  # Default: hold/neutral

        # Buy signal: positive future return (label = 2)
        df.loc[df['future_return'] > 0, 'target'] = 2

        # Sell signal: negative future return (label = 0)
        df.loc[df['future_return'] < 0, 'target'] = 0

        # Drop last row (no future data)
        df = df[:-1]

        # Feature selection
        self.feature_columns = [
            'ema_fast', 'ema_slow', 'rsi', 'atr', 'adx',
            'trend_signal', 'breakout_signal', 'pullback_signal',
            'price_change', 'price_change_5', 'price_change_10',
            'volume_change', 'volume_ma_ratio',
            'ema_diff', 'ema_diff_pct',
            'rsi_change', 'rsi_ma',
            'atr_pct', 'donchian_position',
            'adx_change', 'di_diff',
            'close_z_score',
            'signal_lag1', 'signal_lag2'
        ]

        # Filter only existing columns
        available_features = [
            col for col in self.feature_columns if col in df.columns
        ]
        self.feature_columns = available_features

        X = df[self.feature_columns]
        y = df['target']

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=(1 - Config.ML_TRAIN_RATIO),
            shuffle=False  # Keep temporal order
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        logger.info(
            f"📊 Training data: {X_train.shape[0]} samples, "
            f"{X_train.shape[1]} features"
        )
        logger.info(f"📊 Test data: {X_test.shape[0]} samples")

        return X_train_scaled, X_test_scaled, y_train, y_test

    def train(self, df):
        """
        Train LightGBM model.

        Args:
            df (pd.DataFrame): DataFrame with indicators and features

        Returns:
            dict: Training metrics
        """
        logger.info("🎓 Training ML model...")

        # Engineer features
        df_features = self.engineer_features(df)

        # Prepare data
        X_train, X_test, y_train, y_test = self.prepare_training_data(
            df_features
        )

        # LightGBM parameters
        params = {
            'objective': 'multiclass',
            'num_class': 3,  # -1, 0, 1
            'metric': 'multi_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1
        }

        # Create datasets
        train_data = lgb.Dataset(X_train, label=y_train)
        test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

        # Train model
        self.model = lgb.train(
            params,
            train_data,
            num_boost_round=100,
            valid_sets=[test_data],
            callbacks=[lgb.early_stopping(stopping_rounds=10)]
        )

        # Predictions (labels are now 0, 1, 2)
        y_pred_proba = self.model.predict(X_test)
        y_pred = np.argmax(y_pred_proba, axis=1)  # Returns 0, 1, 2

        # y_test already contains labels 0, 1, 2
        y_test_adjusted = y_test.values

        # Metrics
        accuracy = accuracy_score(y_test_adjusted, y_pred)

        # Get unique classes present in test data
        unique_classes = sorted(np.unique(np.concatenate([y_test_adjusted, y_pred])))
        target_names = ['Sell', 'Hold', 'Buy']
        active_target_names = [target_names[i] for i in unique_classes]

        logger.info(f"✅ Model trained! Accuracy: {accuracy:.4f}")
        logger.info(f"📊 Classes in test data: {unique_classes}")
        
        report = classification_report(
            y_test_adjusted, y_pred, 
            labels=unique_classes,
            target_names=active_target_names,
            zero_division=0
        )
        logger.info("\n" + str(report))

        self.is_trained = True

        # Save model
        self.save_model()

        return {
            'accuracy': accuracy,
            'train_size': len(X_train),
            'test_size': len(X_test),
            'features': len(self.feature_columns)
        }

    def predict(self, df):
        """
        Predict trade signals for new data.

        Args:
            df (pd.DataFrame): DataFrame with indicators

        Returns:
            np.array: Predictions (-1, 0, 1)
        """
        if not self.is_trained and not self.load_model():
            logger.error("❌ Model not trained. Train first or load model.")
            return None

        # Engineer features
        df_features = self.engineer_features(df)

        # Select features
        X = df_features[self.feature_columns]

        # Scale
        X_scaled = self.scaler.transform(X)

        # Predict (model outputs 0, 1, 2)
        y_pred_proba = self.model.predict(X_scaled)
        y_pred = np.argmax(y_pred_proba, axis=1)
        
        # Convert to -1, 0, 1 for compatibility
        # 0 -> -1 (Sell), 1 -> 0 (Hold), 2 -> 1 (Buy)
        y_pred_adjusted = y_pred - 1

        logger.debug(f"🔮 Predictions generated for {len(y_pred_adjusted)} samples")
        return y_pred_adjusted

    def get_prediction_confidence(self, df):
        """
        Get prediction probabilities.

        Args:
            df (pd.DataFrame): DataFrame with indicators

        Returns:
            pd.DataFrame: Predictions with confidence scores
        """
        if not self.is_trained and not self.load_model():
            return None

        df_features = self.engineer_features(df)
        X = df_features[self.feature_columns]
        X_scaled = self.scaler.transform(X)

        # Get probabilities (model outputs 0, 1, 2)
        proba = self.model.predict(X_scaled)

        result = pd.DataFrame({
            'sell_prob': proba[:, 0],
            'hold_prob': proba[:, 1],
            'buy_prob': proba[:, 2],
            'prediction': np.argmax(proba, axis=1) - 1,  # Convert to -1, 0, 1
            'confidence': np.max(proba, axis=1)
        }, index=df_features.index)

        return result

    def save_model(self):
        """Save model and scaler to disk"""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'feature_columns': self.feature_columns
                }, f)

            with open(self.scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)

            logger.info(f"💾 Model saved to {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save model: {e}")
            return False

    def load_model(self):
        """Load model and scaler from disk"""
        try:
            if not self.model_path.exists():
                logger.warning("⚠️  Model file not found")
                return False

            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.feature_columns = data['feature_columns']

            with open(self.scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)

            self.is_trained = True
            logger.info(f"✅ Model loaded: {self.model_path.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return False
    
    def auto_load_or_train(self, df, force_train: bool = False):
        """
        خودکار بارگذاری مدل یا آموزش در صورت عدم وجود
        
        Args:
            df: داده برای آموزش
            force_train: آموزش اجباری حتی اگر مدل وجود داشته باشد
            
        Returns:
            True if model is ready
        """
        if force_train:
            logger.info("🔄 Force training requested...")
            self.train(df)
            return True
            
        # ابتدا سعی در بارگذاری مدل موجود
        if self.load_model():
            logger.info("✅ Using existing trained model")
            return True
        
        # اگر مدل وجود نداشت، آموزش بده
        logger.info("📚 No trained model found. Training new model...")
        try:
            self.train(df)
            return True
        except Exception as e:
            logger.error(f"❌ Training failed: {e}")
            return False


if __name__ == "__main__":
    # Test ML Engine
    from data_handler import DataHandler
    from indicators import TechnicalIndicators

    logger.setLevel(logging.INFO)

    # Fetch data
    handler = DataHandler()
    df = handler.fetch_ohlcv(limit=1000)

    # Calculate indicators
    indicators = TechnicalIndicators(df)
    df_indicators = indicators.calculate_all()

    # Train ML model
    ml = MLEngine()
    metrics = ml.train(df_indicators)

    print("\n🎯 Training Results:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")

    # Test prediction
    predictions = ml.get_prediction_confidence(df_indicators.tail(10))
    print("\n🔮 Latest Predictions:")
    print(predictions)
