"""
BiX TradeBOT - Flask API Backend
=================================
RESTful API + WebSocket for real-time trading dashboard.
"""

import sys
from pathlib import Path

# Add src directory to path (2 levels up from web/backend/app.py)
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir / 'src'))

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time

from data.handler import DataHandler
from data.indicators import TechnicalIndicators
from core.strategy import SimpleHybridStrategy
from core.risk_manager import RiskManager
from utils.config import Config

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)  # Enable CORS for React frontend
socketio = SocketIO(app, cors_allowed_origins="*")

# Global instances
data_handler = DataHandler()
risk_manager = RiskManager(Config.INITIAL_CAPITAL)
strategy = SimpleHybridStrategy()

# Bot state
bot_state = {
    'running': False,
    'symbol': 'BTCUSDT',
    'timeframe': '1h',
    'capital': Config.INITIAL_CAPITAL,
    'positions': [],
    'trades': []
}


# ============= Market Data Endpoints =============

@app.route('/api/market/price/<symbol>', methods=['GET'])
def get_price(symbol):
    """Get current price for a symbol"""
    try:
        price = data_handler.fetch_latest_price(symbol)
        return jsonify({
            'success': True,
            'symbol': symbol,
            'price': price,
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/market/ohlcv/<symbol>', methods=['GET'])
def get_ohlcv(symbol):
    """Get OHLCV data for charting"""
    try:
        timeframe = request.args.get('timeframe', '1h')
        limit = int(request.args.get('limit', 500))
        
        df = data_handler.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit
        )
        
        # Convert to list of dicts for JSON
        data = df.reset_index().to_dict('records')
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'timeframe': timeframe,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/market/indicators/<symbol>', methods=['GET'])
def get_indicators(symbol):
    """Get technical indicators"""
    try:
        timeframe = request.args.get('timeframe', '1h')
        
        df = data_handler.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=500
        )
        
        indicators_calc = TechnicalIndicators(df)
        df = indicators_calc.calculate_all()
        
        # Get latest values
        latest = df.iloc[-1]
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'indicators': {
                'ema_fast': float(latest['ema_fast']),
                'ema_slow': float(latest['ema_slow']),
                'rsi': float(latest['rsi']),
                'adx': float(latest['adx']),
                'atr': float(latest['atr']),
                'di_plus': float(latest['di_plus']),
                'di_minus': float(latest['di_minus'])
            },
            'signals': {
                'trend': int(latest['trend_signal']),
                'breakout': int(latest['breakout_signal']),
                'pullback': int(latest['pullback_signal']),
                'combined': int(latest['combined_signal'])
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============= Trading Endpoints =============

@app.route('/api/trading/start', methods=['POST'])
def start_trading():
    """Start the trading bot"""
    try:
        data = request.json
        bot_state['running'] = True
        bot_state['symbol'] = data.get('symbol', 'BTCUSDT')
        bot_state['timeframe'] = data.get('timeframe', '1h')
        
        # Start background thread for trading
        threading.Thread(target=trading_loop, daemon=True).start()
        
        return jsonify({
            'success': True,
            'message': 'Trading bot started',
            'state': bot_state
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/trading/stop', methods=['POST'])
def stop_trading():
    """Stop the trading bot"""
    try:
        bot_state['running'] = False
        
        return jsonify({
            'success': True,
            'message': 'Trading bot stopped'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/trading/status', methods=['GET'])
def get_status():
    """Get bot status"""
    return jsonify({
        'success': True,
        'status': bot_state
    })


@app.route('/api/trading/portfolio', methods=['GET'])
def get_portfolio():
    """Get portfolio info"""
    total_pnl = sum(trade.get('pnl', 0) for trade in bot_state['trades'])
    win_trades = sum(1 for trade in bot_state['trades'] if trade.get('pnl', 0) > 0)
    total_trades = len(bot_state['trades'])
    
    return jsonify({
        'success': True,
        'portfolio': {
            'capital': bot_state['capital'],
            'pnl': total_pnl,
            'open_positions': len(bot_state['positions']),
            'total_trades': total_trades,
            'win_rate': (win_trades / total_trades * 100) if total_trades > 0 else 0
        }
    })


# ============= Analysis Endpoints =============

@app.route('/api/analysis/signals/<symbol>', methods=['GET'])
def get_signals(symbol):
    """Get trading signals for a symbol"""
    try:
        timeframe = request.args.get('timeframe', '1h')
        
        # Fetch and analyze data
        df = data_handler.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=500)
        indicators_calc = TechnicalIndicators(df)
        df = indicators_calc.calculate_all()
        
        # Generate signal
        signal = strategy.generate_signal(df)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'signal': signal,
            'price': float(df['close'].iloc[-1]),
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============= WebSocket Events =============

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connection_response', {'message': 'Connected to BiX TradeBOT'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


@socketio.on('subscribe_price')
def handle_subscribe_price(data):
    """Subscribe to price updates"""
    symbol = data.get('symbol', 'BTCUSDT')
    print(f'Client subscribed to {symbol}')
    
    # Start sending price updates
    threading.Thread(target=price_update_loop, args=(symbol,), daemon=True).start()


# ============= Background Tasks =============

def price_update_loop(symbol):
    """Send real-time price updates"""
    while True:
        try:
            price = data_handler.fetch_latest_price(symbol)
            socketio.emit('price_update', {
                'symbol': symbol,
                'price': price,
                'timestamp': time.time()
            })
            time.sleep(1)  # Update every second
        except Exception as e:
            print(f'Error in price update: {e}')
            time.sleep(5)


def trading_loop():
    """Main trading loop"""
    print('Trading loop started')
    
    while bot_state['running']:
        try:
            # Fetch data
            df = data_handler.fetch_ohlcv(
                symbol=bot_state['symbol'],
                timeframe=bot_state['timeframe'],
                limit=500
            )
            
            # Calculate indicators
            indicators_calc = TechnicalIndicators(df)
            df = indicators_calc.calculate_all()
            
            # Generate signal
            signal = strategy.generate_signal(df)
            
            # Emit signal update
            socketio.emit('signal_update', {
                'symbol': bot_state['symbol'],
                'signal': signal,
                'price': float(df['close'].iloc[-1]),
                'timestamp': time.time()
            })
            
            # Sleep for timeframe duration
            time.sleep(60)  # Check every minute
            
        except Exception as e:
            print(f'Error in trading loop: {e}')
            time.sleep(60)
    
    print('Trading loop stopped')


# ============= Health Check =============

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time()
    })


@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'app': 'BiX TradeBOT API',
        'version': '1.0.0',
        'status': 'running'
    })


if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════╗
    ║   🚀 BiX TradeBOT Flask API Server              ║
    ║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    ║
    ║   API:       http://localhost:5000               ║
    ║   WebSocket: ws://localhost:5000                 ║
    ║   Status:    http://localhost:5000/health        ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
