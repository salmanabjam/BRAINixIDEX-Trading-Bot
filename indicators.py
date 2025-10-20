"""
BiX TradeBOT - Technical Indicators Module
===========================================
Calculates technical indicators for strategy signals using pandas_ta.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
from config import Config
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """
    Technical indicator calculator for trading strategies.
    Implements: EMA, RSI, ATR, ADX, Donchian Channel, and derived signals.
    """

    def __init__(self, df):
        """
        Initialize with OHLCV DataFrame.

        Args:
            df (pd.DataFrame): OHLCV data with columns
            [open, high, low, close, volume]
        """
        self.df = df.copy()
        self.validate_input()

    def validate_input(self):
        """Ensure DataFrame has required columns"""
        required = ['open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def calculate_all(self):
        """
        Calculate all indicators and return enriched DataFrame.

        Returns:
            pd.DataFrame: Original data with added indicator columns
        """
        logger.info("🔧 Calculating technical indicators...")

        # Trend indicators
        self.add_ema()

        # Momentum indicators
        self.add_rsi()
        self.add_adx()

        # Volatility indicators
        self.add_atr()

        # Breakout indicators
        self.add_donchian_channel()

        # Derived signals
        self.add_trend_signal()
        self.add_breakout_signal()
        self.add_pullback_signal()

        # Combined signal
        self.add_combined_signal()

        logger.info(f"✅ Indicators calculated. Shape: {self.df.shape}")
        return self.df

    def add_ema(self):
        """Add Exponential Moving Averages (EMA)"""
        self.df['ema_fast'] = ta.ema(
            self.df['close'],
            length=Config.EMA_FAST
        )
        self.df['ema_slow'] = ta.ema(
            self.df['close'],
            length=Config.EMA_SLOW
        )
        logger.debug(
            f"Added EMA: fast={Config.EMA_FAST}, slow={Config.EMA_SLOW}"
        )

    def add_rsi(self):
        """Add Relative Strength Index (RSI)"""
        self.df['rsi'] = ta.rsi(
            self.df['close'],
            length=Config.RSI_PERIOD
        )
        logger.debug(f"Added RSI with period={Config.RSI_PERIOD}")

    def add_atr(self):
        """Add Average True Range (ATR) for volatility measurement"""
        self.df['atr'] = ta.atr(
            self.df['high'],
            self.df['low'],
            self.df['close'],
            length=Config.ATR_PERIOD
        )
        logger.debug(f"Added ATR with period={Config.ATR_PERIOD}")

    def add_adx(self):
        """Add Average Directional Index (ADX) for trend strength"""
        adx_df = ta.adx(
            self.df['high'],
            self.df['low'],
            self.df['close'],
            length=Config.ADX_PERIOD
        )

        if adx_df is not None:
            self.df['adx'] = adx_df[f'ADX_{Config.ADX_PERIOD}']
            self.df['di_plus'] = adx_df[f'DMP_{Config.ADX_PERIOD}']
            self.df['di_minus'] = adx_df[f'DMN_{Config.ADX_PERIOD}']
        else:
            self.df['adx'] = 0
            self.df['di_plus'] = 0
            self.df['di_minus'] = 0

        logger.debug(f"Added ADX with period={Config.ADX_PERIOD}")

    def add_donchian_channel(self):
        """Add Donchian Channel for breakout detection"""
        donchian = ta.donchian(
            self.df['high'],
            self.df['low'],
            lower_length=Config.DONCHIAN_PERIOD,
            upper_length=Config.DONCHIAN_PERIOD
        )

        if donchian is not None:
            self.df['donchian_upper'] = donchian[
                f'DCU_{Config.DONCHIAN_PERIOD}_{Config.DONCHIAN_PERIOD}'
            ]
            self.df['donchian_lower'] = donchian[
                f'DCL_{Config.DONCHIAN_PERIOD}_{Config.DONCHIAN_PERIOD}'
            ]
            self.df['donchian_mid'] = donchian[
                f'DCM_{Config.DONCHIAN_PERIOD}_{Config.DONCHIAN_PERIOD}'
            ]
        else:
            period = Config.DONCHIAN_PERIOD
            self.df['donchian_upper'] = self.df['high'].rolling(
                window=period
            ).max()
            self.df['donchian_lower'] = self.df['low'].rolling(
                window=period
            ).min()
            self.df['donchian_mid'] = (
                self.df['donchian_upper'] + self.df['donchian_lower']
            ) / 2

        logger.debug(
            f"Added Donchian Channel with period={Config.DONCHIAN_PERIOD}"
        )

    def add_trend_signal(self):
        """
        Generate trend-following signal.
        Long: EMA fast > EMA slow AND ADX > threshold
        Short: EMA fast < EMA slow AND ADX > threshold
        """
        self.df['trend_signal'] = 0

        # Long condition
        long_cond = (
            (self.df['ema_fast'] > self.df['ema_slow']) &
            (self.df['adx'] > Config.ADX_THRESHOLD)
        )
        self.df.loc[long_cond, 'trend_signal'] = 1

        # Short condition
        short_cond = (
            (self.df['ema_fast'] < self.df['ema_slow']) &
            (self.df['adx'] > Config.ADX_THRESHOLD)
        )
        self.df.loc[short_cond, 'trend_signal'] = -1

        logger.debug("Added trend signal (EMA crossover + ADX filter)")

    def add_breakout_signal(self):
        """
        Generate breakout signal using Donchian Channel.
        Long: Close breaks above upper band
        Short: Close breaks below lower band
        """
        self.df['breakout_signal'] = 0

        # Long breakout
        long_breakout = (
            self.df['close'] > self.df['donchian_upper'].shift(1)
        )
        self.df.loc[long_breakout, 'breakout_signal'] = 1

        # Short breakout
        short_breakout = (
            self.df['close'] < self.df['donchian_lower'].shift(1)
        )
        self.df.loc[short_breakout, 'breakout_signal'] = -1

        logger.debug("Added breakout signal (Donchian Channel)")

    def add_pullback_signal(self):
        """
        Generate pullback/reversal signal using RSI.
        Long: RSI < oversold (price may bounce up)
        Short: RSI > overbought (price may pull back)
        """
        self.df['pullback_signal'] = 0

        # Oversold - potential long
        oversold = self.df['rsi'] < Config.RSI_OVERSOLD
        self.df.loc[oversold, 'pullback_signal'] = 1

        # Overbought - potential short
        overbought = self.df['rsi'] > Config.RSI_OVERBOUGHT
        self.df.loc[overbought, 'pullback_signal'] = -1

        logger.debug("Added pullback signal (RSI extremes)")

    def add_combined_signal(self):
        """
        Combine all three signals into a unified score.
        Score ranges from -3 (strong short) to +3 (strong long).
        """
        self.df['combined_signal'] = (
            self.df['trend_signal'] +
            self.df['breakout_signal'] +
            self.df['pullback_signal']
        )

        logger.debug("Added combined signal (sum of all strategies)")

    def get_latest_signals(self):
        """
        Get the most recent signal values.

        Returns:
            dict: Latest indicator values and signals
        """
        latest = self.df.iloc[-1]
        return {
            'timestamp': latest.name,
            'close': latest['close'],
            'ema_fast': latest['ema_fast'],
            'ema_slow': latest['ema_slow'],
            'rsi': latest['rsi'],
            'atr': latest['atr'],
            'adx': latest['adx'],
            'trend_signal': int(latest['trend_signal']),
            'breakout_signal': int(latest['breakout_signal']),
            'pullback_signal': int(latest['pullback_signal']),
            'combined_signal': int(latest['combined_signal'])
        }

    def export_to_csv(self, filename='indicators_output.csv'):
        """Export calculated indicators to CSV"""
        output_path = f"results/{filename}"
        self.df.to_csv(output_path)
        logger.info(f"💾 Indicators exported to {output_path}")
        return output_path


if __name__ == "__main__":
    # Test indicators
    from data_handler import DataHandler

    logger.setLevel(logging.DEBUG)

    handler = DataHandler()
    df = handler.fetch_ohlcv(limit=500)

    indicators = TechnicalIndicators(df)
    result_df = indicators.calculate_all()

    print("\n📊 Indicator Summary:")
    print(result_df[['close', 'ema_fast', 'ema_slow', 'rsi',
                     'atr', 'adx', 'combined_signal']].tail(10))

    print("\n🎯 Latest Signals:")
    signals = indicators.get_latest_signals()
    for key, value in signals.items():
        print(f"  {key}: {value}")
