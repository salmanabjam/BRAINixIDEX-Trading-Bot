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
        """Test DataHandler component"""
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
            
            # Test initialization
            dh = DataHandler(use_ccxt=False)
            test['details']['initialization'] = 'PASS'
            
            # Test data fetching
            df = dh.fetch_ohlcv('BTCUSDT', '1h', limit=100)
            
            if df is not None and len(df) > 0:
                test['details']['data_fetch'] = 'PASS'
                test['details']['rows_fetched'] = len(df)
                test['details']['columns'] = list(df.columns)
            else:
                test['details']['data_fetch'] = 'FAIL'
                test['message'] = 'No data returned'
                test['status'] = 'FAIL'
                return test
            
            # Test latest price
            price = dh.fetch_latest_price('BTCUSDT')
            if price and price > 0:
                test['details']['latest_price'] = f"${price:,.2f}"
                test['details']['price_fetch'] = 'PASS'
            else:
                test['details']['price_fetch'] = 'FAIL'
            
            test['status'] = 'PASS'
            test['message'] = f"Successfully fetched {len(df)} candles"
            
        except Exception as e:
            test['status'] = 'FAIL'
            test['message'] = str(e)
            test['details']['error'] = str(e)
        
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
            
            # Test position sizing with ATR
            position = rm.calculate_position_size(
                entry_price=50000,
                atr=500,
                direction='long'
            )
            
            test['details']['position_calculation'] = {
                'quantity': position['quantity'],
                'position_size_usd': f"${position['position_size_usd']:,.2f}",
                'risk_amount_usd': f"${position['risk_amount_usd']:,.2f}",
                'stop_loss': position['stop_loss']
            }
            
            test['status'] = 'PASS'
            test['message'] = 'Risk calculations working'
            
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
            test['details']['signal'] = signal
            
            test['status'] = 'PASS'
            test['message'] = f'Generated signal: {signal}'
            
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
            
            test['details']['configs'] = configs
            test['status'] = 'PASS'
            test['message'] = 'Configuration loaded'
            
        except Exception as e:
            test['status'] = 'FAIL'
            test['message'] = str(e)
            test['details']['error'] = str(e)
        
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
