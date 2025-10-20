"""
Advanced Chart Analysis Module
===============================
تشخیص خودکار الگوها، خطوط روند، فیبوناچی و سطوح حمایت/مقاومت

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class AdvancedChartAnalysis:
    """تحلیل پیشرفته نمودار با تشخیص الگوها و سطوح کلیدی"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with OHLCV dataframe
        
        Args:
            df: DataFrame با ستون‌های open, high, low, close, volume
        """
        self.df = df.copy()
        self.support_levels = []
        self.resistance_levels = []
        self.trend_lines = []
        self.fibonacci_levels = {}
        self.patterns = []
    
    def find_support_resistance(self, window: int = 20, threshold: float = 0.02) -> Dict:
        """
        پیدا کردن سطوح حمایت و مقاومت
        
        Args:
            window: تعداد کندل‌های اطراف برای بررسی
            threshold: آستانه درصد برای گروه‌بندی سطوح نزدیک
        
        Returns:
            Dict با لیست سطوح حمایت و مقاومت
        """
        try:
            # پیدا کردن نقاط local minima (حمایت)
            local_min_idx = argrelextrema(
                self.df['low'].values, 
                np.less_equal, 
                order=window
            )[0]
            
            # پیدا کردن نقاط local maxima (مقاومت)
            local_max_idx = argrelextrema(
                self.df['high'].values, 
                np.greater_equal, 
                order=window
            )[0]
            
            # استخراج قیمت‌های حمایت
            support_prices = self.df['low'].iloc[local_min_idx].values
            
            # استخراج قیمت‌های مقاومت
            resistance_prices = self.df['high'].iloc[local_max_idx].values
            
            # گروه‌بندی سطوح نزدیک به هم
            self.support_levels = self._cluster_levels(support_prices, threshold)
            self.resistance_levels = self._cluster_levels(resistance_prices, threshold)
            
            logger.info(f"✅ {len(self.support_levels)} حمایت و {len(self.resistance_levels)} مقاومت یافت شد")
            
            return {
                'support': self.support_levels,
                'resistance': self.resistance_levels
            }
            
        except Exception as e:
            logger.error(f"خطا در پیدا کردن سطوح: {str(e)}")
            return {'support': [], 'resistance': []}
    
    def _cluster_levels(self, prices: np.ndarray, threshold: float) -> List[float]:
        """
        گروه‌بندی قیمت‌های نزدیک به هم
        
        Args:
            prices: آرایه قیمت‌ها
            threshold: آستانه درصد
        
        Returns:
            لیست قیمت‌های گروه‌بندی شده
        """
        if len(prices) == 0:
            return []
        
        # مرتب‌سازی قیمت‌ها
        sorted_prices = np.sort(prices)
        
        clusters = []
        current_cluster = [sorted_prices[0]]
        
        for price in sorted_prices[1:]:
            # اگر قیمت نزدیک به میانگین کلاستر فعلی بود
            if abs(price - np.mean(current_cluster)) / np.mean(current_cluster) <= threshold:
                current_cluster.append(price)
            else:
                # کلاستر جدید
                clusters.append(np.mean(current_cluster))
                current_cluster = [price]
        
        # اضافه کردن آخرین کلاستر
        clusters.append(np.mean(current_cluster))
        
        return sorted(clusters)
    
    def detect_trend_lines(self, lookback: int = 50) -> List[Dict]:
        """
        تشخیص خطوط روند صعودی و نزولی
        
        Args:
            lookback: تعداد کندل‌های اخیر برای تحلیل
        
        Returns:
            لیست خطوط روند با مختصات
        """
        try:
            df_recent = self.df.tail(lookback).copy()
            df_recent = df_recent.reset_index(drop=True)
            
            trend_lines = []
            
            # خط روند صعودی (اتصال قعرها)
            lows = df_recent['low'].values
            low_indices = argrelextrema(lows, np.less_equal, order=5)[0]
            
            if len(low_indices) >= 2:
                # اتصال دو قعر پایین‌ترین
                sorted_lows = sorted(zip(low_indices, lows[low_indices]), key=lambda x: x[1])
                
                if len(sorted_lows) >= 2:
                    idx1, price1 = sorted_lows[0]
                    idx2, price2 = sorted_lows[1]
                    
                    # محاسبه شیب
                    slope = (price2 - price1) / (idx2 - idx1) if idx2 != idx1 else 0
                    
                    # پیش‌بینی برای نقطه آخر
                    last_idx = len(df_recent) - 1
                    projected_price = price1 + slope * (last_idx - idx1)
                    
                    trend_lines.append({
                        'type': 'support_trendline',
                        'start_idx': int(idx1),
                        'start_price': float(price1),
                        'end_idx': int(last_idx),
                        'end_price': float(projected_price),
                        'slope': float(slope),
                        'direction': 'bullish' if slope > 0 else 'bearish'
                    })
            
            # خط روند نزولی (اتصال قله‌ها)
            highs = df_recent['high'].values
            high_indices = argrelextrema(highs, np.greater_equal, order=5)[0]
            
            if len(high_indices) >= 2:
                # اتصال دو قله بالاترین
                sorted_highs = sorted(zip(high_indices, highs[high_indices]), key=lambda x: x[1], reverse=True)
                
                if len(sorted_highs) >= 2:
                    idx1, price1 = sorted_highs[0]
                    idx2, price2 = sorted_highs[1]
                    
                    # محاسبه شیب
                    slope = (price2 - price1) / (idx2 - idx1) if idx2 != idx1 else 0
                    
                    # پیش‌بینی برای نقطه آخر
                    last_idx = len(df_recent) - 1
                    projected_price = price1 + slope * (last_idx - idx1)
                    
                    trend_lines.append({
                        'type': 'resistance_trendline',
                        'start_idx': int(idx1),
                        'start_price': float(price1),
                        'end_idx': int(last_idx),
                        'end_price': float(projected_price),
                        'slope': float(slope),
                        'direction': 'bearish' if slope < 0 else 'bullish'
                    })
            
            self.trend_lines = trend_lines
            
            logger.info(f"✅ {len(trend_lines)} خط روند یافت شد")
            
            return trend_lines
            
        except Exception as e:
            logger.error(f"خطا در تشخیص خطوط روند: {str(e)}")
            return []
    
    def calculate_fibonacci_levels(self, lookback: int = 100) -> Dict:
        """
        محاسبه سطوح فیبوناچی ریتریسمنت
        
        Args:
            lookback: تعداد کندل‌های اخیر برای یافتن سوئینگ
        
        Returns:
            Dict با سطوح فیبوناچی
        """
        try:
            df_recent = self.df.tail(lookback)
            
            # پیدا کردن بالاترین و پایین‌ترین قیمت
            swing_high = df_recent['high'].max()
            swing_low = df_recent['low'].min()
            
            # محاسبه اختلاف
            diff = swing_high - swing_low
            
            # سطوح استاندارد فیبوناچی
            fib_ratios = {
                '0.0': swing_high,
                '0.236': swing_high - 0.236 * diff,
                '0.382': swing_high - 0.382 * diff,
                '0.5': swing_high - 0.5 * diff,
                '0.618': swing_high - 0.618 * diff,
                '0.786': swing_high - 0.786 * diff,
                '1.0': swing_low,
                # سطوح اضافی
                '1.272': swing_low - 0.272 * diff,
                '1.618': swing_low - 0.618 * diff
            }
            
            self.fibonacci_levels = fib_ratios
            
            logger.info(f"✅ سطوح فیبوناچی محاسبه شد (Swing: ${swing_high:.2f} - ${swing_low:.2f})")
            
            return {
                'levels': fib_ratios,
                'swing_high': swing_high,
                'swing_low': swing_low
            }
            
        except Exception as e:
            logger.error(f"خطا در محاسبه فیبوناچی: {str(e)}")
            return {'levels': {}, 'swing_high': 0, 'swing_low': 0}
    
    def detect_candlestick_patterns(self, lookback: int = 20) -> List[Dict]:
        """
        تشخیص الگوهای شمعی (Candlestick Patterns)
        
        Args:
            lookback: تعداد کندل‌های اخیر برای تحلیل
        
        Returns:
            لیست الگوهای شناسایی شده
        """
        try:
            df_recent = self.df.tail(lookback).copy()
            df_recent = df_recent.reset_index(drop=True)
            
            patterns = []
            
            for i in range(2, len(df_recent)):
                prev2 = df_recent.iloc[i-2]
                prev1 = df_recent.iloc[i-1]
                current = df_recent.iloc[i]
                
                # Hammer (چکش)
                if self._is_hammer(current):
                    patterns.append({
                        'pattern': 'Hammer',
                        'type': 'bullish',
                        'index': i,
                        'price': current['close'],
                        'confidence': 'متوسط'
                    })
                
                # Shooting Star (ستاره دنباله‌دار)
                if self._is_shooting_star(current):
                    patterns.append({
                        'pattern': 'Shooting Star',
                        'type': 'bearish',
                        'index': i,
                        'price': current['close'],
                        'confidence': 'متوسط'
                    })
                
                # Engulfing Bullish (پوشش صعودی)
                if self._is_bullish_engulfing(prev1, current):
                    patterns.append({
                        'pattern': 'Bullish Engulfing',
                        'type': 'bullish',
                        'index': i,
                        'price': current['close'],
                        'confidence': 'قوی'
                    })
                
                # Engulfing Bearish (پوشش نزولی)
                if self._is_bearish_engulfing(prev1, current):
                    patterns.append({
                        'pattern': 'Bearish Engulfing',
                        'type': 'bearish',
                        'index': i,
                        'price': current['close'],
                        'confidence': 'قوی'
                    })
                
                # Doji (دوجی)
                if self._is_doji(current):
                    patterns.append({
                        'pattern': 'Doji',
                        'type': 'neutral',
                        'index': i,
                        'price': current['close'],
                        'confidence': 'ضعیف'
                    })
                
                # Morning Star (ستاره صبحگاهی)
                if i >= 2 and self._is_morning_star(prev2, prev1, current):
                    patterns.append({
                        'pattern': 'Morning Star',
                        'type': 'bullish',
                        'index': i,
                        'price': current['close'],
                        'confidence': 'بسیار قوی'
                    })
                
                # Evening Star (ستاره عصرگاهی)
                if i >= 2 and self._is_evening_star(prev2, prev1, current):
                    patterns.append({
                        'pattern': 'Evening Star',
                        'type': 'bearish',
                        'index': i,
                        'price': current['close'],
                        'confidence': 'بسیار قوی'
                    })
            
            self.patterns = patterns
            
            logger.info(f"✅ {len(patterns)} الگوی شمعی یافت شد")
            
            return patterns
            
        except Exception as e:
            logger.error(f"خطا در تشخیص الگوها: {str(e)}")
            return []
    
    def _is_hammer(self, candle: pd.Series) -> bool:
        """بررسی الگوی Hammer"""
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        
        return (
            lower_shadow >= 2 * body and
            upper_shadow <= 0.1 * body and
            body > 0
        )
    
    def _is_shooting_star(self, candle: pd.Series) -> bool:
        """بررسی الگوی Shooting Star"""
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        
        return (
            upper_shadow >= 2 * body and
            lower_shadow <= 0.1 * body and
            body > 0
        )
    
    def _is_bullish_engulfing(self, prev: pd.Series, current: pd.Series) -> bool:
        """بررسی الگوی Bullish Engulfing"""
        prev_bearish = prev['close'] < prev['open']
        current_bullish = current['close'] > current['open']
        
        return (
            prev_bearish and
            current_bullish and
            current['close'] > prev['open'] and
            current['open'] < prev['close']
        )
    
    def _is_bearish_engulfing(self, prev: pd.Series, current: pd.Series) -> bool:
        """بررسی الگوی Bearish Engulfing"""
        prev_bullish = prev['close'] > prev['open']
        current_bearish = current['close'] < current['open']
        
        return (
            prev_bullish and
            current_bearish and
            current['close'] < prev['open'] and
            current['open'] > prev['close']
        )
    
    def _is_doji(self, candle: pd.Series) -> bool:
        """بررسی الگوی Doji"""
        body = abs(candle['close'] - candle['open'])
        range_size = candle['high'] - candle['low']
        
        return body <= 0.1 * range_size
    
    def _is_morning_star(self, candle1: pd.Series, candle2: pd.Series, candle3: pd.Series) -> bool:
        """بررسی الگوی Morning Star"""
        # کندل اول نزولی بزرگ
        first_bearish = candle1['close'] < candle1['open']
        first_large = abs(candle1['close'] - candle1['open']) > (candle1['high'] - candle1['low']) * 0.7
        
        # کندل دوم کوچک (Doji یا Spinning Top)
        second_small = abs(candle2['close'] - candle2['open']) < (candle1['high'] - candle1['low']) * 0.3
        
        # کندل سوم صعودی بزرگ
        third_bullish = candle3['close'] > candle3['open']
        third_large = abs(candle3['close'] - candle3['open']) > (candle3['high'] - candle3['low']) * 0.7
        
        return first_bearish and first_large and second_small and third_bullish and third_large
    
    def _is_evening_star(self, candle1: pd.Series, candle2: pd.Series, candle3: pd.Series) -> bool:
        """بررسی الگوی Evening Star"""
        # کندل اول صعودی بزرگ
        first_bullish = candle1['close'] > candle1['open']
        first_large = abs(candle1['close'] - candle1['open']) > (candle1['high'] - candle1['low']) * 0.7
        
        # کندل دوم کوچک
        second_small = abs(candle2['close'] - candle2['open']) < (candle1['high'] - candle1['low']) * 0.3
        
        # کندل سوم نزولی بزرگ
        third_bearish = candle3['close'] < candle3['open']
        third_large = abs(candle3['close'] - candle3['open']) > (candle3['high'] - candle3['low']) * 0.7
        
        return first_bullish and first_large and second_small and third_bearish and third_large
    
    def suggest_entry_exit_points(self, current_price: float) -> Dict:
        """
        پیشنهاد نقاط ورود و خروج بر اساس تحلیل
        
        Args:
            current_price: قیمت فعلی
        
        Returns:
            Dict با نقاط ورود، خروج و stop loss پیشنهادی
        """
        try:
            suggestions = {
                'entry_points': [],
                'exit_points': [],
                'stop_loss': None,
                'take_profit': None
            }
            
            # نقاط ورود نزدیک سطوح حمایت
            for support in self.support_levels:
                if support < current_price and (current_price - support) / current_price <= 0.02:
                    suggestions['entry_points'].append({
                        'price': support,
                        'reason': 'نزدیک به حمایت',
                        'type': 'buy'
                    })
            
            # نقاط خروج نزدیک سطوح مقاومت
            for resistance in self.resistance_levels:
                if resistance > current_price and (resistance - current_price) / current_price <= 0.05:
                    suggestions['exit_points'].append({
                        'price': resistance,
                        'reason': 'نزدیک به مقاومت',
                        'type': 'sell'
                    })
            
            # Stop Loss نزدیک‌ترین حمایت
            supports_below = [s for s in self.support_levels if s < current_price]
            if supports_below:
                suggestions['stop_loss'] = max(supports_below)
            
            # Take Profit نزدیک‌ترین مقاومت
            resistances_above = [r for r in self.resistance_levels if r > current_price]
            if resistances_above:
                suggestions['take_profit'] = min(resistances_above)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"خطا در پیشنهاد نقاط: {str(e)}")
            return {'entry_points': [], 'exit_points': [], 'stop_loss': None, 'take_profit': None}
    
    def get_complete_analysis(self, current_price: float) -> Dict:
        """
        تحلیل کامل نمودار
        
        Args:
            current_price: قیمت فعلی
        
        Returns:
            Dict با تمام تحلیل‌ها
        """
        return {
            'support_resistance': self.find_support_resistance(),
            'trend_lines': self.detect_trend_lines(),
            'fibonacci': self.calculate_fibonacci_levels(),
            'patterns': self.detect_candlestick_patterns(),
            'suggestions': self.suggest_entry_exit_points(current_price)
        }
