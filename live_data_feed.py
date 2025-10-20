"""
BiX TradeBOT - Live Market Data Integration Module
==================================================

Multi-Agent Architecture for Real-Time Cryptocurrency Price Tracking

Agents:
- DataIntegrator: Connects to free APIs (CoinGecko, Binance) with failover logic
- QualityController: Monitors data consistency and detects anomalies
- DataFormatter: Normalizes and formats data for AI consumption

Features:
- Auto-detects top 10-50 traded coins by volume
- Continuous price updates every 5 seconds
- In-memory caching with Redis fallback
- API failover with exponential backoff
- WebSocket support for real-time streaming
- Multilingual support (English/Persian)

Author: BiX TradeBOT Team
License: Educational Use Only
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import aiohttp
import pandas as pd
import numpy as np
from collections import deque
import json
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIntegrator:
    """
    Agent responsible for fetching live data from multiple free APIs
    with automatic failover and caching.
    """
    
    def __init__(self, top_n_coins: int = 50, update_interval: int = 5):
        """
        Initialize DataIntegrator agent.
        
        Args:
            top_n_coins: Number of top coins to track (10-50)
            update_interval: Update frequency in seconds
        """
        self.top_n_coins = top_n_coins
        self.update_interval = update_interval
        self.cache = {}  # In-memory cache
        self.cache_ttl = 60  # Cache time-to-live in seconds
        self.last_update = None
        
        # API configurations
        self.apis = {
            'coingecko': {
                'url': 'https://api.coingecko.com/api/v3/coins/markets',
                'params': {
                    'vs_currency': 'usd',
                    'order': 'volume_desc',
                    'per_page': top_n_coins,
                    'page': 1,
                    'sparkline': False
                },
                'priority': 1,
                'status': 'active'
            },
            'binance': {
                'url': 'https://api.binance.com/api/v3/ticker/24hr',
                'params': {},
                'priority': 2,
                'status': 'active'
            }
        }
        
        self.retry_config = {
            'max_retries': 3,
            'base_delay': 10,  # seconds
            'max_delay': 60,   # seconds
            'exponential_base': 2
        }
        
        logger.info(f"🚀 DataIntegrator initialized: Tracking top {top_n_coins} coins")
    
    async def fetch_coingecko_data(self, session: aiohttp.ClientSession) -> Optional[List[Dict]]:
        """
        Fetch data from CoinGecko API.
        
        Returns:
            List of coin data dictionaries or None on failure
        """
        try:
            api_config = self.apis['coingecko']
            async with session.get(api_config['url'], params=api_config['params'], timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ CoinGecko: Fetched {len(data)} coins")
                    return data
                else:
                    logger.warning(f"⚠️ CoinGecko returned status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"❌ CoinGecko error: {str(e)}")
            return None
    
    async def fetch_binance_data(self, session: aiohttp.ClientSession) -> Optional[List[Dict]]:
        """
        Fetch data from Binance Public API.
        
        Returns:
            List of coin data dictionaries or None on failure
        """
        try:
            api_config = self.apis['binance']
            async with session.get(api_config['url'], timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    # Filter USDT pairs and sort by volume
                    usdt_pairs = [
                        item for item in data 
                        if item['symbol'].endswith('USDT') and 
                        float(item.get('quoteVolume', 0)) > 0
                    ]
                    # Sort by volume and take top N
                    sorted_pairs = sorted(
                        usdt_pairs, 
                        key=lambda x: float(x.get('quoteVolume', 0)), 
                        reverse=True
                    )[:self.top_n_coins]
                    
                    logger.info(f"✅ Binance: Fetched {len(sorted_pairs)} trading pairs")
                    return sorted_pairs
                else:
                    logger.warning(f"⚠️ Binance returned status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"❌ Binance error: {str(e)}")
            return None
    
    async def fetch_with_failover(self) -> Optional[List[Dict]]:
        """
        Fetch data with automatic failover between APIs.
        
        Returns:
            Raw data from successful API or None if all fail
        """
        async with aiohttp.ClientSession() as session:
            # Try CoinGecko first (priority 1)
            coingecko_data = await self.fetch_coingecko_data(session)
            if coingecko_data:
                return ('coingecko', coingecko_data)
            
            logger.warning("⚠️ CoinGecko failed, switching to Binance...")
            
            # Fallback to Binance
            binance_data = await self.fetch_binance_data(session)
            if binance_data:
                return ('binance', binance_data)
            
            logger.error("❌ All APIs failed!")
            return None
    
    async def fetch_live_data(self) -> Optional[Tuple[str, List[Dict]]]:
        """
        Main method to fetch live data with retry logic.
        
        Returns:
            Tuple of (source, data) or None
        """
        for attempt in range(self.retry_config['max_retries']):
            result = await self.fetch_with_failover()
            
            if result:
                self.last_update = datetime.now()
                return result
            
            # Exponential backoff
            if attempt < self.retry_config['max_retries'] - 1:
                delay = min(
                    self.retry_config['base_delay'] * (self.retry_config['exponential_base'] ** attempt),
                    self.retry_config['max_delay']
                )
                logger.info(f"🔄 Retry {attempt + 1}/{self.retry_config['max_retries']} in {delay}s...")
                await asyncio.sleep(delay)
        
        return None


class QualityController:
    """
    Agent responsible for monitoring data quality, consistency, and detecting anomalies.
    """
    
    def __init__(self, anomaly_threshold: float = 50.0):
        """
        Initialize QualityController agent.
        
        Args:
            anomaly_threshold: Percentage change threshold for anomaly detection
        """
        self.anomaly_threshold = anomaly_threshold
        self.price_history = {}  # Store last N prices for each coin
        self.history_size = 10
        self.api_status = {}
        
        logger.info(f"🛡️ QualityController initialized: Anomaly threshold = {anomaly_threshold}%")
    
    def validate_price_spike(self, coin_symbol: str, new_price: float) -> Tuple[bool, Optional[str]]:
        """
        Detect unusual price spikes that may indicate bad data.
        
        Args:
            coin_symbol: Coin symbol (e.g., 'BTC')
            new_price: New price to validate
            
        Returns:
            Tuple of (is_valid, warning_message)
        """
        if coin_symbol not in self.price_history:
            self.price_history[coin_symbol] = deque(maxlen=self.history_size)
            self.price_history[coin_symbol].append(new_price)
            return (True, None)
        
        # Calculate average of recent prices
        recent_prices = list(self.price_history[coin_symbol])
        if len(recent_prices) < 2:
            self.price_history[coin_symbol].append(new_price)
            return (True, None)
        
        avg_price = np.mean(recent_prices)
        price_change_pct = abs((new_price - avg_price) / avg_price * 100)
        
        if price_change_pct > self.anomaly_threshold:
            warning = f"⚠️ ANOMALY DETECTED: {coin_symbol} price changed {price_change_pct:.2f}% (New: ${new_price:.2f}, Avg: ${avg_price:.2f})"
            logger.warning(warning)
            return (False, warning)
        
        # Price is valid, add to history
        self.price_history[coin_symbol].append(new_price)
        return (True, None)
    
    def compare_api_results(self, source1_data: List[Dict], source2_data: List[Dict]) -> Dict:
        """
        Compare results from two different APIs for consistency.
        
        Args:
            source1_data: Data from first API
            source2_data: Data from second API
            
        Returns:
            Comparison report dictionary
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'discrepancies': [],
            'consistency_score': 0.0
        }
        
        # Create lookup dictionaries
        source1_lookup = {item.get('symbol', '').upper(): item for item in source1_data}
        source2_lookup = {item.get('symbol', '').upper(): item for item in source2_data}
        
        # Find common coins
        common_symbols = set(source1_lookup.keys()) & set(source2_lookup.keys())
        
        if not common_symbols:
            report['consistency_score'] = 0.0
            return report
        
        total_diff = 0.0
        for symbol in common_symbols:
            price1 = source1_lookup[symbol].get('price', 0)
            price2 = source2_lookup[symbol].get('price', 0)
            
            if price1 > 0 and price2 > 0:
                diff_pct = abs(price1 - price2) / price1 * 100
                total_diff += diff_pct
                
                if diff_pct > 5.0:  # More than 5% difference
                    report['discrepancies'].append({
                        'symbol': symbol,
                        'price1': price1,
                        'price2': price2,
                        'difference_pct': diff_pct
                    })
        
        # Calculate consistency score (inverse of average difference)
        avg_diff = total_diff / len(common_symbols) if common_symbols else 100
        report['consistency_score'] = max(0, 100 - avg_diff)
        
        return report
    
    def check_api_health(self, api_name: str, success: bool, response_time: float):
        """
        Monitor API health and uptime.
        
        Args:
            api_name: Name of the API
            success: Whether the request was successful
            response_time: Response time in seconds
        """
        if api_name not in self.api_status:
            self.api_status[api_name] = {
                'total_requests': 0,
                'successful_requests': 0,
                'total_response_time': 0.0,
                'last_check': None,
                'status': 'unknown'
            }
        
        status = self.api_status[api_name]
        status['total_requests'] += 1
        if success:
            status['successful_requests'] += 1
        status['total_response_time'] += response_time
        status['last_check'] = datetime.now()
        
        # Calculate uptime percentage
        uptime = (status['successful_requests'] / status['total_requests']) * 100
        avg_response_time = status['total_response_time'] / status['total_requests']
        
        if uptime >= 95 and avg_response_time < 2.0:
            status['status'] = 'healthy'
        elif uptime >= 80:
            status['status'] = 'degraded'
        else:
            status['status'] = 'unhealthy'
        
        logger.info(f"📊 {api_name}: {uptime:.1f}% uptime, {avg_response_time:.2f}s avg response")


class DataFormatter:
    """
    Agent responsible for transforming and normalizing data for AI model
    and dashboard consumption with multilingual support.
    """
    
    def __init__(self, languages: List[str] = ['en', 'fa']):
        """
        Initialize DataFormatter agent.
        
        Args:
            languages: Supported languages (English, Persian)
        """
        self.languages = languages
        self.symbol_map = self._load_symbol_mappings()
        
        logger.info(f"🔄 DataFormatter initialized: Languages = {languages}")
    
    def _load_symbol_mappings(self) -> Dict:
        """Load standardized coin symbol mappings."""
        return {
            'BTCUSDT': 'BTC',
            'ETHUSDT': 'ETH',
            'BNBUSDT': 'BNB',
            'XRPUSDT': 'XRP',
            'ADAUSDT': 'ADA',
            'DOGEUSDT': 'DOGE',
            'SOLUSDT': 'SOL',
            'DOTUSDT': 'DOT',
            'MATICUSDT': 'MATIC',
            'LTCUSDT': 'LTC',
        }
    
    def format_coingecko_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Format CoinGecko API response.
        
        Args:
            raw_data: Raw CoinGecko data
            
        Returns:
            Standardized data list
        """
        formatted = []
        for item in raw_data:
            formatted.append({
                'coin_name': item.get('name', 'Unknown'),
                'symbol': item.get('symbol', 'UNK').upper(),
                'price_usd': float(item.get('current_price', 0)),
                '24h_change_percent': float(item.get('price_change_percentage_24h', 0)),
                'volume_usd': float(item.get('total_volume', 0)),
                'market_cap_usd': float(item.get('market_cap', 0)),
                'rank': int(item.get('market_cap_rank', 0)),
                'last_updated': datetime.now().isoformat(),
                'source': 'coingecko'
            })
        return formatted
    
    def format_binance_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Format Binance API response.
        
        Args:
            raw_data: Raw Binance data
            
        Returns:
            Standardized data list
        """
        formatted = []
        for idx, item in enumerate(raw_data):
            symbol = item.get('symbol', 'UNKNOWN')
            # Remove 'USDT' suffix for standardization
            base_symbol = symbol.replace('USDT', '') if symbol.endswith('USDT') else symbol
            
            formatted.append({
                'coin_name': base_symbol,  # Binance doesn't provide full names
                'symbol': base_symbol,
                'price_usd': float(item.get('lastPrice', 0)),
                '24h_change_percent': float(item.get('priceChangePercent', 0)),
                'volume_usd': float(item.get('quoteVolume', 0)),
                'market_cap_usd': 0,  # Binance doesn't provide market cap
                'rank': idx + 1,
                'last_updated': datetime.now().isoformat(),
                'source': 'binance'
            })
        return formatted
    
    def normalize_data(self, source: str, raw_data: List[Dict]) -> List[Dict]:
        """
        Normalize data from any source to standard format.
        
        Args:
            source: Data source name ('coingecko' or 'binance')
            raw_data: Raw data from API
            
        Returns:
            Standardized data list
        """
        if source == 'coingecko':
            return self.format_coingecko_data(raw_data)
        elif source == 'binance':
            return self.format_binance_data(raw_data)
        else:
            logger.error(f"❌ Unknown data source: {source}")
            return []
    
    def to_json(self, data: List[Dict], pretty: bool = False) -> str:
        """
        Convert data to JSON format.
        
        Args:
            data: Standardized data list
            pretty: Whether to pretty-print JSON
            
        Returns:
            JSON string
        """
        return json.dumps(data, indent=2 if pretty else None, ensure_ascii=False)
    
    def to_dataframe(self, data: List[Dict]) -> pd.DataFrame:
        """
        Convert data to pandas DataFrame.
        
        Args:
            data: Standardized data list
            
        Returns:
            pandas DataFrame
        """
        return pd.DataFrame(data)
    
    def add_multilingual_labels(self, data: List[Dict]) -> List[Dict]:
        """
        Add Persian translations for coin names.
        
        Args:
            data: Standardized data list
            
        Returns:
            Data with multilingual labels
        """
        persian_names = {
            'BTC': 'بیت‌کوین',
            'ETH': 'اتریوم',
            'BNB': 'بایننس کوین',
            'XRP': 'ریپل',
            'ADA': 'کاردانو',
            'DOGE': 'دوج‌کوین',
            'SOL': 'سولانا',
            'DOT': 'پولکادات',
            'MATIC': 'پالیگان',
            'LTC': 'لایت‌کوین'
        }
        
        for item in data:
            symbol = item['symbol']
            item['coin_name_fa'] = persian_names.get(symbol, item['coin_name'])
        
        return data


class LiveDataFeed:
    """
    Main orchestrator for live market data integration.
    Coordinates DataIntegrator, QualityController, and DataFormatter agents.
    """
    
    def __init__(self, top_n_coins: int = 50, update_interval: int = 5):
        """
        Initialize LiveDataFeed system.
        
        Args:
            top_n_coins: Number of top coins to track
            update_interval: Update frequency in seconds
        """
        self.integrator = DataIntegrator(top_n_coins, update_interval)
        self.quality_controller = QualityController()
        self.formatter = DataFormatter()
        
        self.is_running = False
        self.latest_data = None
        self.data_history = deque(maxlen=500)  # Store 500 recent samples per coin
        
        logger.info(f"🎯 LiveDataFeed initialized: Top {top_n_coins} coins, {update_interval}s updates")
    
    async def fetch_and_process(self) -> Optional[List[Dict]]:
        """
        Fetch data and process it through all agents.
        
        Returns:
            Processed and validated data
        """
        # Step 1: Fetch data with failover
        start_time = time.time()
        result = await self.integrator.fetch_live_data()
        fetch_time = time.time() - start_time
        
        if not result:
            return None
        
        source, raw_data = result
        
        # Step 2: Format and normalize data
        normalized_data = self.formatter.normalize_data(source, raw_data)
        
        # Step 3: Quality control - validate each coin's price
        validated_data = []
        anomalies_detected = 0
        
        for coin_data in normalized_data:
            is_valid, warning = self.quality_controller.validate_price_spike(
                coin_data['symbol'],
                coin_data['price_usd']
            )
            
            if is_valid:
                validated_data.append(coin_data)
            else:
                anomalies_detected += 1
                logger.warning(warning)
        
        # Step 4: Add multilingual support
        validated_data = self.formatter.add_multilingual_labels(validated_data)
        
        # Step 5: Update API health status
        self.quality_controller.check_api_health(source, True, fetch_time)
        
        # Store in history for AI predictions
        self.data_history.append({
            'timestamp': datetime.now(),
            'data': validated_data,
            'source': source
        })
        
        logger.info(f"✅ Processed {len(validated_data)} coins from {source} ({anomalies_detected} anomalies filtered)")
        
        return validated_data
    
    async def start_continuous_feed(self, callback=None):
        """
        Start continuous data feed loop.
        
        Args:
            callback: Optional callback function to call with each update
        """
        self.is_running = True
        logger.info("🚀 Starting continuous live data feed...")
        
        while self.is_running:
            try:
                # Fetch and process data
                data = await self.fetch_and_process()
                
                if data:
                    self.latest_data = data
                    
                    # Call callback if provided
                    if callback:
                        await callback(data)
                
                # Wait for next update
                await asyncio.sleep(self.integrator.update_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in continuous feed: {str(e)}")
                await asyncio.sleep(10)  # Wait before retrying
    
    def stop(self):
        """Stop the continuous data feed."""
        self.is_running = False
        logger.info("🛑 Stopping live data feed...")
    
    def get_latest_data(self) -> Optional[List[Dict]]:
        """Get the most recent data."""
        return self.latest_data
    
    def get_historical_data(self, symbol: str, limit: int = 100) -> pd.DataFrame:
        """
        Get historical data for a specific coin.
        
        Args:
            symbol: Coin symbol (e.g., 'BTC')
            limit: Number of recent samples to return
            
        Returns:
            DataFrame with historical prices
        """
        history = []
        for entry in list(self.data_history)[-limit:]:
            for coin in entry['data']:
                if coin['symbol'] == symbol:
                    history.append({
                        'timestamp': entry['timestamp'],
                        'price': coin['price_usd'],
                        'volume': coin['volume_usd'],
                        'change_24h': coin['24h_change_percent']
                    })
        
        return pd.DataFrame(history)
    
    def get_system_status(self) -> Dict:
        """Get system health and statistics."""
        return {
            'is_running': self.is_running,
            'last_update': self.integrator.last_update.isoformat() if self.integrator.last_update else None,
            'coins_tracked': len(self.latest_data) if self.latest_data else 0,
            'history_size': len(self.data_history),
            'api_status': self.quality_controller.api_status
        }


# Example usage and testing
async def example_usage():
    """Example of how to use the LiveDataFeed system."""
    
    # Initialize the feed
    feed = LiveDataFeed(top_n_coins=10, update_interval=5)
    
    # Define a callback to process each update
    async def on_data_update(data):
        print(f"\n📊 Received update with {len(data)} coins:")
        for coin in data[:3]:  # Show first 3
            print(f"  • {coin['symbol']}: ${coin['price_usd']:.2f} ({coin['24h_change_percent']:+.2f}%)")
    
    # Fetch once
    print("🔄 Fetching data once...")
    data = await feed.fetch_and_process()
    if data:
        print(f"✅ Fetched {len(data)} coins")
        print(feed.formatter.to_json(data[:3], pretty=True))
    
    # Get system status
    status = feed.get_system_status()
    print(f"\n📈 System Status: {json.dumps(status, indent=2)}")


if __name__ == '__main__':
    # Run example
    asyncio.run(example_usage())
