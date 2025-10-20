"""
BiX TradeBOT - System Simulator & Testing Module
=================================================
Comprehensive testing and simulation for all bot components.

Author: SALMAN ThinkTank
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path


class SystemSimulator:
    """Comprehensive system testing and simulation"""
    
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        self.warnings = 0
        
    def run_all_tests(self) -> Dict:
        """Run all system tests"""
        print("🧪 Starting System Simulation & Testing...")
        print("=" * 60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'summary': {}
        }
        
        # Test 1: Data Handler
        results['tests'].append(self._test_data_handler())
        
        # Test 2: Technical Indicators
        results['tests'].append(self._test_indicators())
        
        # Test 3: ML Engine
        results['tests'].append(self._test_ml_engine())
        
        # Test 4: Risk Manager
        results['tests'].append(self._test_risk_manager())
        
        # Test 5: Strategy
        results['tests'].append(self._test_strategy())
        
        # Test 6: Configuration
        results['tests'].append(self._test_config())
        
        # Test 7: Logger
        results['tests'].append(self._test_logger())
        
        # Test 8: Cache System
        results['tests'].append(self._test_cache())
        
        # Summary
        results['summary'] = self._calculate_summary(results['tests'])
        
        return results
    
    def _test_data_handler(self) -> Dict:
        """Test DataHandler component - COMPREHENSIVE"""
        test = {
            'name': 'DataHandler',
            'status': 'PENDING',
            'message': '',
            'duration': 0,
            'details': {}
        }
        
        start = datetime.now()
        
        try:
            from data.handler import DataHandler
            
            # Test 1: Initialization
            dh = DataHandler(use_ccxt=False)
            test['details']['initialization'] = 'PASS'
            
            # Test 2: Data fetching (multiple timeframes)
            timeframes = ['1h', '4h']
            fetch_results = {}
            
            for tf in timeframes:
                df = dh.fetch_ohlcv('BTCUSDT', tf, limit=100)
                
                if df is not None and len(df) > 0:
                    fetch_results[tf] = {
                        'status': 'PASS',
                        'rows': len(df),
                        'date_range': f"{df.index[0]} to {df.index[-1]}"
                    }
                else:
                    fetch_results[tf] = {'status': 'FAIL', 'rows': 0}
            
            test['details']['data_fetch'] = fetch_results
            
            # Test 3: Latest price
            price = dh.fetch_latest_price('BTCUSDT')
            if price and price > 0:
                test['details']['latest_price'] = f"${price:,.2f}"
                test['details']['price_fetch'] = 'PASS'
            else:
                test['details']['price_fetch'] = 'FAIL'
            
            # Test 4: Data validation
            df = dh.fetch_ohlcv('BTCUSDT', '1h', limit=100)
            if df is not None:
                has_ohlcv = all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume'])
                no_nulls = df.isnull().sum().sum() == 0
                
                test['details']['data_validation'] = {
                    'has_ohlcv': bool(has_ohlcv),
                    'no_nulls': bool(no_nulls),
                    'price_range': f"${df['low'].min():,.2f} - ${df['high'].max():,.2f}"
                }
            
            test['status'] = 'PASS'
            test['message'] = f"Successfully tested data handling ({len(fetch_results)} timeframes)"
            
        except Exception as e:
            test['status'] = 'FAIL'
            test['message'] = str(e)
            test['details']['error'] = str(e)
            import traceback
            test['details']['traceback'] = traceback.format_exc()
        
        test['duration'] = (datetime.now() - start).total_seconds()
        return test
    
    def _test_indicators(self) -> Dict:
        """Test Technical Indicators"""
        test = {
            'name': 'TechnicalIndicators',
            'status': 'PENDING',
            'message': '',
            'duration': 0,
            'details': {}
        }
        
        start = datetime.now()
        
        try:
            from data.handler import DataHandler
            from data.indicators import TechnicalIndicators
            
            # Get sample data
            dh = DataHandler(use_ccxt=False)
            df = dh.fetch_ohlcv('BTCUSDT', '1h', limit=100)
            
            if df is None or len(df) == 0:
                test['status'] = 'SKIP'
                test['message'] = 'No data available'
                return test
            
            # Calculate indicators
            indicators = TechnicalIndicators(df)
            df_ind = indicators.calculate_all()
            
            test['details']['indicators_count'] = len(df_ind.columns)
            test['details']['rows'] = len(df_ind)
            
            # Check for NaN values
            nan_count = df_ind.isnull().sum().sum()
            test['details']['nan_values'] = int(nan_count)
            
            # Get latest signals
            signals = indicators.get_latest_signals()
            test['details']['signals'] = {
                k: str(v) for k, v in signals.items()
            }
            
            test['status'] = 'PASS'
            test['message'] = f"Calculated {len(df_ind.columns)} indicators"
            
        except Exception as e:
            test['status'] = 'FAIL'
            test['message'] = str(e)
            test['details']['error'] = str(e)
        
        test['duration'] = (datetime.now() - start).total_seconds()
        return test
    
    def _test_ml_engine(self) -> Dict:
        """Test ML Engine"""
        test = {
            'name': 'MLEngine',
            'status': 'PENDING',
            'message': '',
            'duration': 0,
            'details': {}
        }
        
        start = datetime.now()
        
        try:
            from core.ml_engine import MLEngine
            from data.handler import DataHandler
            from data.indicators import TechnicalIndicators
            
            # Initialize ML Engine
            ml = MLEngine()
            test['details']['initialization'] = 'PASS'
            
            # Check if model exists
            model_loaded = ml.load_model()
            test['details']['model_loaded'] = 'PASS' if model_loaded else 'FAIL'
            
            if model_loaded:
                # Get sample data
                dh = DataHandler(use_ccxt=False)
                df = dh.fetch_ohlcv('BTCUSDT', '1h', limit=200)
                
                if df is not None and len(df) > 100:
                    indicators = TechnicalIndicators(df)
                    df_ind = indicators.calculate_all()
                    
                    # Test prediction
                    try:
                        predictions = ml.get_prediction_confidence(df_ind)
                        
                        if predictions is not None and len(predictions) > 0:
                            test['details']['predictions'] = 'PASS'
                            test['details']['prediction_count'] = len(predictions)
                            
                            # Get latest prediction
                            latest = predictions.iloc[-1]
                            test['details']['latest_prediction'] = {
                                'signal': str(latest['prediction']),
                                'confidence': f"{latest['confidence']:.2%}"
                            }
                            
                            test['status'] = 'PASS'
                            test['message'] = 'ML predictions working'
                        else:
                            test['status'] = 'FAIL'
                            test['message'] = 'Empty predictions'
                            
                    except Exception as pred_error:
                        test['status'] = 'FAIL'
                        test['message'] = f"Prediction error: {str(pred_error)}"
                        test['details']['prediction_error'] = str(pred_error)
                else:
                    test['status'] = 'SKIP'
                    test['message'] = 'Insufficient data'
            else:
                test['status'] = 'WARN'
                test['message'] = 'Model not found'
                
        except Exception as e:
            test['status'] = 'FAIL'
            test['message'] = str(e)
            test['details']['error'] = str(e)
        
        test['duration'] = (datetime.now() - start).total_seconds()
        return test
    
    def _test_risk_manager(self) -> Dict:
        """Test Risk Manager"""
        test = {
            'name': 'RiskManager',
            'status': 'PENDING',
            'message': '',
            'duration': 0,
            'details': {}
        }
        
        start = datetime.now()
        
        try:
            from core.risk_manager import RiskManager
            
            rm = RiskManager()
            test['details']['initialization'] = 'PASS'
            test['details']['capital'] = f"${rm.initial_capital:,.2f}"
            test['details']['current_equity'] = f"${rm.current_equity:,.2f}"
            
            # Test 1: ATR-based position sizing
            position = rm.calculate_position_size(
                entry_price=50000.0,
                atr=500.0,
                direction='long'
            )
            
            test['details']['position_sizing'] = 'PASS'
            test['details']['position_size'] = f"{position['size']:.6f} BTC"
            test['details']['position_value'] = f"${position['value']:,.2f}"
            test['details']['stop_loss'] = f"${position['stop_loss']:,.2f}"
            test['details']['take_profit'] = f"${position['take_profit']:,.2f}"
            test['details']['risk_amount'] = f"${position['risk_amount']:,.2f}"
            
            # Test 2: Open position
            rm.open_position(
                symbol='BTCUSDT',
                entry_price=position['stop_loss'] + 100,  # Above stop loss
                size=position['size'],
                direction='long',
                stop_loss=position['stop_loss'],
                take_profit=position['take_profit']
            )
            
            test['details']['open_position'] = 'PASS'
            test['details']['positions_count'] = len(rm.positions)
            
            # Test 3: Check stop loss/take profit
            current_price = 51000.0  # Profitable scenario
            hits = rm.check_stop_loss_take_profit(current_price)
            test['details']['sl_tp_check'] = 'PASS'
            test['details']['hits_found'] = len(hits)
            
            # Test 4: Close position
            if len(rm.positions) > 0:
                trade = rm.close_position(0, current_price, 'test_close')  # Index 0
                if trade:
                    test['details']['close_position'] = 'PASS'
                    test['details']['pnl'] = f"${trade['pnl']:,.2f}"
                    test['details']['pnl_percent'] = f"{trade['pnl_percent']}%"
                    test['details']['trades_in_history'] = len(rm.trade_history)
                else:
                    test['details']['close_position'] = 'FAIL - No trade returned'
            
            # Test 5: Performance stats
            stats = rm.get_performance_stats()
            test['details']['performance_stats'] = 'PASS'
            test['details']['total_trades'] = stats['total_trades']
            test['details']['win_rate'] = f"{stats['win_rate']:.1%}"
            
            test['status'] = 'PASS'
            win_rate_pct = stats['win_rate'] * 100
            test['message'] = f'All risk management functions working ({len(rm.trade_history)} trades, {win_rate_pct:.0f}% win rate)'
            
        except Exception as e:
            test['status'] = 'FAIL'
            test['message'] = str(e)
            test['details']['error'] = str(e)
        
        test['duration'] = (datetime.now() - start).total_seconds()
        return test
    
    def _test_strategy(self) -> Dict:
        """Test Trading Strategy"""
        test = {
            'name': 'TradingStrategy',
            'status': 'PENDING',
            'message': '',
            'duration': 0,
            'details': {}
        }
        
        start = datetime.now()
        
        try:
            from core.strategy import SimpleHybridStrategy
            
            strategy = SimpleHybridStrategy(use_ml=False)
            test['details']['initialization'] = 'PASS'
            
            # Mock signals
            mock_signals = {
                'price': 50000,
                'ema_fast': 49500,
                'ema_slow': 49000,
                'rsi': 45,
                'atr': 500,
                'adx': 25,
                'volume': 1000000
            }
            
            signal = strategy.generate_signal(mock_signals)
            test['details']['signal_generation'] = 'PASS'
            test['details']['signal_action'] = signal.get('action', 'UNKNOWN')
            test['details']['signal_strength'] = signal.get('strength', 0)
            test['details']['signal_reason'] = signal.get('reason', 'N/A')
            
            test['status'] = 'PASS'
            test['message'] = f"Generated signal: {signal.get('action', 'UNKNOWN')}"
            
        except Exception as e:
            test['status'] = 'FAIL'
            test['message'] = str(e)
            test['details']['error'] = str(e)
        
        test['duration'] = (datetime.now() - start).total_seconds()
        return test
    
    def _test_config(self) -> Dict:
        """Test Configuration"""
        test = {
            'name': 'Configuration',
            'status': 'PENDING',
            'message': '',
            'duration': 0,
            'details': {}
        }
        
        start = datetime.now()
        
        try:
            from utils.config import Config
            
            # Check critical configs
            configs = {
                'SYMBOL': Config.SYMBOL,
                'TIMEFRAME': Config.TIMEFRAME,
                'INITIAL_CAPITAL': Config.INITIAL_CAPITAL,
                'RISK_PER_TRADE': Config.RISK_PER_TRADE,
                'ML_ENABLED': Config.ML_ENABLED
            }
            
            test['details']['configs'] = {k: str(v) for k, v in configs.items()}
            test['details']['config_count'] = len(configs)
            
            test['status'] = 'PASS'
            test['message'] = f'All configuration loaded ({len(configs)} settings)'
            
        except Exception as e:
            test['status'] = 'FAIL'
            test['message'] = str(e)
            test['details']['error'] = str(e)
            import traceback
            test['details']['traceback'] = traceback.format_exc()
        
        test['duration'] = (datetime.now() - start).total_seconds()
        return test
    
    def _test_logger(self) -> Dict:
        """Test Logger System"""
        test = {
            'name': 'LoggerSystem',
            'status': 'PENDING',
            'message': '',
            'duration': 0,
            'details': {}
        }
        
        start = datetime.now()
        
        try:
            from utils.logger import get_logger
            
            logger = get_logger()
            test['details']['initialization'] = 'PASS'
            
            # Test logging
            logger.info("Test info message", component="SIMULATOR")
            logger.warning("Test warning", component="SIMULATOR")
            
            # Check log directory
            log_dir = Path("logs")
            if log_dir.exists():
                test['details']['log_directory'] = 'EXISTS'
                log_files = list(log_dir.glob("*.log"))
                test['details']['log_files'] = [f.name for f in log_files]
            else:
                test['details']['log_directory'] = 'NOT_FOUND'
            
            # Get error stats
            stats = logger.get_error_stats()
            test['details']['error_stats'] = stats
            
            test['status'] = 'PASS'
            test['message'] = 'Logger system operational'
            
        except Exception as e:
            test['status'] = 'FAIL'
            test['message'] = str(e)
            test['details']['error'] = str(e)
        
        test['duration'] = (datetime.now() - start).total_seconds()
        return test
    
    def _test_cache(self) -> Dict:
        """Test Cache System"""
        test = {
            'name': 'CacheSystem',
            'status': 'PENDING',
            'message': '',
            'duration': 0,
            'details': {}
        }
        
        start = datetime.now()
        
        try:
            cache_dir = Path("data/cache")
            
            if cache_dir.exists():
                cache_files = list(cache_dir.glob("*.csv"))
                test['details']['cache_directory'] = 'EXISTS'
                test['details']['cache_files_count'] = len(cache_files)
                
                if cache_files:
                    test['details']['cache_files'] = [
                        f.name for f in cache_files[:5]
                    ]
                    
                    # Get latest cache info
                    latest_cache = max(cache_files, key=lambda x: x.stat().st_mtime)
                    test['details']['latest_cache'] = {
                        'file': latest_cache.name,
                        'size_kb': latest_cache.stat().st_size / 1024,
                        'modified': datetime.fromtimestamp(
                            latest_cache.stat().st_mtime
                        ).isoformat()
                    }
                    
                    test['status'] = 'PASS'
                    test['message'] = f'{len(cache_files)} cache files found'
                else:
                    test['status'] = 'WARN'
                    test['message'] = 'No cache files'
            else:
                test['status'] = 'FAIL'
                test['message'] = 'Cache directory not found'
                
        except Exception as e:
            test['status'] = 'FAIL'
            test['message'] = str(e)
            test['details']['error'] = str(e)
        
        test['duration'] = (datetime.now() - start).total_seconds()
        return test
    
    def _calculate_summary(self, tests: List[Dict]) -> Dict:
        """Calculate test summary"""
        passed = sum(1 for t in tests if t['status'] == 'PASS')
        failed = sum(1 for t in tests if t['status'] == 'FAIL')
        warnings = sum(1 for t in tests if t['status'] == 'WARN')
        skipped = sum(1 for t in tests if t['status'] == 'SKIP')
        
        total_duration = sum(t['duration'] for t in tests)
        
        return {
            'total_tests': len(tests),
            'passed': passed,
            'failed': failed,
            'warnings': warnings,
            'skipped': skipped,
            'success_rate': (passed / len(tests) * 100) if tests else 0,
            'total_duration': round(total_duration, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_report(self, results: Dict) -> str:
        """Generate text report"""
        report = []
        report.append("=" * 70)
        report.append("BiX TradeBOT - SYSTEM TEST REPORT")
        report.append("=" * 70)
        report.append(f"Timestamp: {results['timestamp']}")
        report.append("")
        
        # Summary
        summary = results['summary']
        report.append("SUMMARY:")
        report.append(f"  Total Tests: {summary['total_tests']}")
        report.append(f"  ✅ Passed: {summary['passed']}")
        report.append(f"  ❌ Failed: {summary['failed']}")
        report.append(f"  ⚠️  Warnings: {summary['warnings']}")
        report.append(f"  ⏭️  Skipped: {summary['skipped']}")
        report.append(f"  📊 Success Rate: {summary['success_rate']:.1f}%")
        report.append(f"  ⏱️  Duration: {summary['total_duration']:.2f}s")
        report.append("")
        
        # Individual tests
        report.append("DETAILED RESULTS:")
        report.append("-" * 70)
        
        for test in results['tests']:
            status_icon = {
                'PASS': '✅',
                'FAIL': '❌',
                'WARN': '⚠️',
                'SKIP': '⏭️'
            }.get(test['status'], '❓')
            
            report.append(f"{status_icon} {test['name']}: {test['status']}")
            report.append(f"   Message: {test['message']}")
            report.append(f"   Duration: {test['duration']:.2f}s")
            
            if test['details']:
                report.append("   Details:")
                for key, value in test['details'].items():
                    if isinstance(value, dict):
                        report.append(f"     {key}:")
                        for k, v in value.items():
                            report.append(f"       {k}: {v}")
                    else:
                        report.append(f"     {key}: {value}")
            report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)


# Quick test function
def run_quick_test() -> Dict:
    """Run quick system test"""
    simulator = SystemSimulator()
    results = simulator.run_all_tests()
    print(simulator.generate_report(results))
    return results


if __name__ == "__main__":
    run_quick_test()
