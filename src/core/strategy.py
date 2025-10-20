"""
BiX TradeBOT - Hybrid Trading Strategy
=======================================
Combines Trend Following, Breakout, and Pullback strategies with ML.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import pandas as pd
import numpy as np
from backtesting import Strategy
from utils.config import Config
import logging

logger = logging.getLogger(__name__)


class HybridStrategy(Strategy):
    """
    Hybrid trading strategy combining multiple approaches:
    1. Trend Following (EMA crossover + ADX filter)
    2. Breakout Detection (Donchian Channel)
    3. Pullback Trading (RSI extremes)
    4. ML Signal Enhancement (optional)
    """

    # Strategy parameters (can be optimized)
    ema_fast = Config.EMA_FAST
    ema_slow = Config.EMA_SLOW
    rsi_period = Config.RSI_PERIOD
    atr_period = Config.ATR_PERIOD
    adx_threshold = Config.ADX_THRESHOLD
    risk_per_trade = Config.RISK_PER_TRADE
    atr_stop_mult = Config.ATR_STOP_MULTIPLIER
    rr_ratio = Config.RISK_REWARD_RATIO

    def init(self):
        """Initialize strategy indicators"""
        # Access pre-calculated indicators from data
        close = self.data.Close

        # Signals are already calculated in the data
        # We just need to reference them
        self.trend_signal = self.data.df['trend_signal']
        self.breakout_signal = self.data.df['breakout_signal']
        self.pullback_signal = self.data.df['pullback_signal']
        self.combined_signal = self.data.df['combined_signal']
        self.atr = self.data.df['atr']

        # ML predictions (if available)
        if 'ml_prediction' in self.data.df.columns:
            self.ml_signal = self.data.df['ml_prediction']
            self.ml_confidence = self.data.df['ml_confidence']
        else:
            self.ml_signal = pd.Series(0, index=self.data.df.index)
            self.ml_confidence = pd.Series(0, index=self.data.df.index)

        logger.debug("✅ Strategy initialized")

    def next(self):
        """Execute strategy logic on each candle"""
        # Get current signals
        combined = self.combined_signal[-1]
        ml_pred = self.ml_signal[-1]
        ml_conf = self.ml_confidence[-1]
        current_atr = self.atr[-1]
        current_price = self.data.Close[-1]

        # Skip if no valid signal
        if pd.isna(combined) or pd.isna(current_atr):
            return

        # Calculate position size based on risk
        equity = self.equity
        risk_amount = equity * self.risk_per_trade
        stop_distance = current_atr * self.atr_stop_mult
        position_size = risk_amount / stop_distance

        # Normalize position size
        max_position_value = equity * Config.MAX_POSITION_SIZE
        position_value = position_size * current_price
        if position_value > max_position_value:
            position_size = max_position_value / current_price

        # Decision logic: Combined signal + ML confirmation
        # Strong Buy: combined >= 2 AND (ml_pred == 1 OR ml not used)
        strong_buy = (
            combined >= 2 and
            (ml_pred >= 0 or ml_conf < 0.5)
        )

        # Strong Sell: combined <= -2 AND (ml_pred == -1 OR ml not used)
        strong_sell = (
            combined <= -2 and
            (ml_pred <= 0 or ml_conf < 0.5)
        )

        # Entry Logic
        if not self.position:
            if strong_buy:
                # Calculate stop loss and take profit
                stop_loss = current_price - stop_distance
                take_profit = current_price + (stop_distance * self.rr_ratio)

                # Open long position
                self.buy(
                    size=position_size,
                    sl=stop_loss,
                    tp=take_profit
                )
                logger.debug(
                    f"🟢 LONG @ {current_price:.2f} | "
                    f"SL: {stop_loss:.2f} | TP: {take_profit:.2f}"
                )

            elif strong_sell:
                # Calculate stop loss and take profit
                stop_loss = current_price + stop_distance
                take_profit = current_price - (stop_distance * self.rr_ratio)

                # Open short position
                self.sell(
                    size=position_size,
                    sl=stop_loss,
                    tp=take_profit
                )
                logger.debug(
                    f"🔴 SHORT @ {current_price:.2f} | "
                    f"SL: {stop_loss:.2f} | TP: {take_profit:.2f}"
                )

        # Exit Logic: Reverse signal
        elif self.position:
            # Close long if strong sell signal
            if self.position.is_long and strong_sell:
                self.position.close()
                logger.debug(f"❌ Closed LONG @ {current_price:.2f}")

            # Close short if strong buy signal
            elif self.position.is_short and strong_buy:
                self.position.close()
                logger.debug(f"❌ Closed SHORT @ {current_price:.2f}")


class SimpleHybridStrategy:
    """
    Simplified version for manual trading (non-backtesting).
    Returns clear BUY/SELL/HOLD signals.
    """

    def __init__(self, use_ml=True, ml_weight=0.3):
        """
        Initialize strategy.

        Args:
            use_ml (bool): Use ML predictions
            ml_weight (float): Weight for ML signal (0-1)
        """
        self.use_ml = use_ml
        self.ml_weight = ml_weight
        self.signal_threshold = 2  # Minimum combined signal strength

    def generate_signal(self, indicators_dict, ml_prediction=None,
                        ml_confidence=None):
        """
        Generate trading signal from indicators.

        Args:
            indicators_dict (dict): Latest indicator values
            ml_prediction (int): ML model prediction (-1, 0, 1)
            ml_confidence (float): ML confidence score

        Returns:
            dict: {
                'action': 'BUY'|'SELL'|'HOLD',
                'strength': signal strength (0-5),
                'reason': explanation string
            }
        """
        # Extract signals
        combined = indicators_dict.get('combined_signal', 0)
        trend = indicators_dict.get('trend_signal', 0)
        breakout = indicators_dict.get('breakout_signal', 0)
        pullback = indicators_dict.get('pullback_signal', 0)

        # Apply ML adjustment if enabled
        if self.use_ml and ml_prediction is not None:
            ml_score = ml_prediction * (ml_confidence or 0.5)
            combined += ml_score * self.ml_weight

        # Determine action
        if combined >= self.signal_threshold:
            action = 'BUY'
            strength = min(int(combined), 5)
            reason = self._build_reason(trend, breakout, pullback, ml_prediction)
        elif combined <= -self.signal_threshold:
            action = 'SELL'
            strength = min(int(abs(combined)), 5)
            reason = self._build_reason(trend, breakout, pullback, ml_prediction)
        else:
            action = 'HOLD'
            strength = 0
            reason = "No strong signal detected"

        return {
            'action': action,
            'strength': strength,
            'reason': reason,
            'combined_score': round(combined, 2)
        }

    def _build_reason(self, trend, breakout, pullback, ml_pred):
        """Build human-readable explanation"""
        reasons = []

        if trend == 1:
            reasons.append("Bullish trend")
        elif trend == -1:
            reasons.append("Bearish trend")

        if breakout == 1:
            reasons.append("Upward breakout")
        elif breakout == -1:
            reasons.append("Downward breakout")

        if pullback == 1:
            reasons.append("Oversold (potential bounce)")
        elif pullback == -1:
            reasons.append("Overbought (potential pullback)")

        if ml_pred == 1:
            reasons.append("ML: Bullish")
        elif ml_pred == -1:
            reasons.append("ML: Bearish")

        return " | ".join(reasons) if reasons else "Mixed signals"


if __name__ == "__main__":
    # Test strategy signal generation
    logger.setLevel(logging.DEBUG)

    strategy = SimpleHybridStrategy(use_ml=True)

    # Sample indicator data
    indicators = {
        'trend_signal': 1,
        'breakout_signal': 1,
        'pullback_signal': 0,
        'combined_signal': 2
    }

    signal = strategy.generate_signal(
        indicators,
        ml_prediction=1,
        ml_confidence=0.75
    )

    print("\n🎯 Generated Signal:")
    for key, value in signal.items():
        print(f"  {key}: {value}")
