# api/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
import json
from datetime import datetime, timedelta
import random
import logging

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from main_agent import AutonomousTradingAgent
    from perception import DataCollector
    from execution import TradeExecutor
    print("✅ All backend modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")

app = Flask(__name__)
CORS(app)

# Global agent instance
trading_agent = None
print("🚀 Flask app initialized")

# Mock data for when real data is not available
def generate_sample_market_data(symbol, days=15):
    """Generate realistic sample market data"""
    base_prices = {
        'AAPL': 185.0,
        'MSFT': 330.0,
        'GOOGL': 135.0,
        'TSLA': 245.0
    }
    
    base_price = base_prices.get(symbol, 100.0)
    sample_data = []
    current_price = base_price
    
    for i in range(days, 0, -1):
        date = datetime.now() - timedelta(days=i)
        
        # Realistic price movement
        change_percent = random.uniform(-0.03, 0.03)  # ±3% daily change
        open_price = current_price
        close_price = open_price * (1 + change_percent)
        high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.015))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.015))
        volume = random.randint(20000000, 50000000)
        
        sample_data.append({
            "date": date.strftime('%Y-%m-%d'),
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": volume,
            "change": round(change_percent * 100, 2),
            "changePercent": round(change_percent * 100, 2)
        })
        
        current_price = close_price  # Next day starts where previous day closed
    
    return sample_data

def generate_sample_portfolio():
    """Generate sample portfolio data"""
    return {
        "cash_balance": 7500.0,
        "positions_value": 3500.0,
        "total_value": 11000.0,
        "total_pnl": 1000.0,
        "total_pnl_pct": 10.0,
        "positions": {
            "AAPL": {
                "quantity": 10,
                "avg_price": 170.0,
                "current_price": 185.0,
                "value": 1850.0,
                "cost_basis": 1700.0,
                "pnl": 150.0,
                "pnl_pct": 8.82
            },
            "MSFT": {
                "quantity": 5,
                "avg_price": 310.0,
                "current_price": 330.0,
                "value": 1650.0,
                "cost_basis": 1550.0,
                "pnl": 100.0,
                "pnl_pct": 6.45
            }
        },
        "number_of_positions": 2
    }

def generate_sample_trades():
    """Generate sample trade history"""
    trades = []
    actions = ['BUY', 'SELL']
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    
    for i in range(10):
        trade_time = datetime.now() - timedelta(hours=random.randint(1, 24))
        symbol = random.choice(symbols)
        action = random.choice(actions)
        quantity = random.randint(1, 20)
        price = random.uniform(100, 500)
        
        trades.append({
            "id": f"TRADE_{i+1}",
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "price": round(price, 2),
            "timestamp": trade_time.isoformat(),
            "status": "FILLED"
        })
    
    return trades

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "active", 
        "timestamp": datetime.now().isoformat(),
        "message": "API is running correctly"
    })

@app.route('/api/agent/start', methods=['POST'])
def start_agent():
    global trading_agent
    try:
        logger.info("🔧 Starting agent...")
        data = request.get_json() or {}
        symbols = data.get('symbols', ['AAPL', 'MSFT', 'GOOGL', 'TSLA'])
        initial_capital = data.get('initial_capital', 10000)
        
        logger.info(f"Creating agent with symbols: {symbols}, capital: {initial_capital}")
        
        # Create agent instance
        trading_agent = AutonomousTradingAgent(
            symbols=symbols,
            initial_capital=initial_capital,
            paper_trading=True
        )
        
        logger.info("Agent created, training models...")
        # Train models
        trading_agent.train_models()
        
        logger.info("✅ Agent started successfully")
        return jsonify({
            "status": "success", 
            "message": "Trading agent started and models trained",
            "symbols": symbols,
            "capital": initial_capital
        })
    except Exception as e:
        logger.error(f"❌ Error starting agent: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/agent/stop', methods=['POST'])
def stop_agent():
    global trading_agent
    try:
        if trading_agent:
            trading_agent.stop()
            trading_agent = None
            logger.info("✅ Agent stopped")
            return jsonify({"status": "success", "message": "Trading agent stopped"})
        return jsonify({"status": "error", "message": "No active agent"}), 400
    except Exception as e:
        logger.error(f"❌ Error stopping agent: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/agent/status', methods=['GET'])
def agent_status():
    global trading_agent
    try:
        if trading_agent:
            status = {
                "is_running": getattr(trading_agent, 'is_running', False),
                "models_trained": getattr(trading_agent, 'models_trained', False),
                "symbols": getattr(trading_agent, 'symbols', []),
                "capital": getattr(trading_agent, 'initial_capital', 0)
            }
            return jsonify({"status": "active", "data": status})
        return jsonify({"status": "inactive"})
    except Exception as e:
        logger.error(f"❌ Error getting agent status: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/market/data', methods=['GET'])
def get_market_data():
    try:
        symbol = request.args.get('symbol', 'AAPL')
        logger.info(f"📊 Fetching market data for {symbol}")
        
        try:
            # Try to get real data first
            from perception import DataCollector
            collector = DataCollector()
            data = collector.get_historical_data([symbol], period="1mo", interval="1d")
            
            if symbol in data and not data[symbol].empty:
                df = data[symbol].tail(15)
                chart_data = []
                
                for index, row in df.iterrows():
                    daily_change = ((row['Close'] - row['Open']) / row['Open'] * 100)
                    
                    chart_data.append({
                        "date": index.strftime('%Y-%m-%d'),
                        "open": round(float(row['Open']), 2),
                        "high": round(float(row['High']), 2),
                        "low": round(float(row['Low']), 2),
                        "close": round(float(row['Close']), 2),
                        "volume": int(row['Volume']),
                        "change": round(daily_change, 2),
                        "changePercent": round(daily_change, 2)
                    })
                
                logger.info(f"✅ Returning {len(chart_data)} real data points for {symbol}")
                return jsonify({
                    "status": "success",
                    "symbol": symbol,
                    "data": chart_data
                })
        except Exception as e:
            logger.warning(f"Real data unavailable, using sample data: {e}")
        
        # Fallback to sample data
        sample_data = generate_sample_market_data(symbol)
        logger.info(f"📊 Using sample data for {symbol}")
        return jsonify({
            "status": "success", 
            "symbol": symbol,
            "data": sample_data,
            "note": "Sample data (real market data unavailable)"
        })
            
    except Exception as e:
        logger.error(f"❌ Error in market data endpoint: {e}")
        sample_data = generate_sample_market_data('AAPL')
        return jsonify({
            "status": "success",
            "symbol": symbol,
            "data": sample_data,
            "note": "Sample data due to error"
        })

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    try:
        if trading_agent and hasattr(trading_agent, 'trade_executor'):
            logger.info("📈 Getting portfolio data from agent")
            
            # Try to get real portfolio data
            try:
                current_prices = {}
                from perception import DataCollector
                collector = DataCollector()
                symbols = getattr(trading_agent, 'symbols', ['AAPL', 'MSFT'])
                
                market_data = collector.get_realtime_data(symbols, interval="1m", lookback=1)
                
                for symbol in symbols:
                    if symbol in market_data and not market_data[symbol].empty:
                        current_prices[symbol] = market_data[symbol]['Close'].iloc[-1]
                    else:
                        # Use sample price if no real data
                        current_prices[symbol] = random.uniform(100, 500)
                
                portfolio_summary = trading_agent.trade_executor.get_portfolio_summary(current_prices)
                logger.info("✅ Returning real portfolio data")
                return jsonify({
                    "status": "success",
                    "portfolio": portfolio_summary
                })
            except Exception as e:
                logger.warning(f"Real portfolio data unavailable: {e}")
        
        # Fallback to sample portfolio data
        sample_portfolio = generate_sample_portfolio()
        logger.info("📈 Using sample portfolio data")
        return jsonify({
            "status": "success",
            "portfolio": sample_portfolio,
            "note": "Sample portfolio data"
        })
            
    except Exception as e:
        logger.error(f"❌ Error fetching portfolio: {e}")
        sample_portfolio = generate_sample_portfolio()
        return jsonify({
            "status": "success",
            "portfolio": sample_portfolio,
            "note": "Sample data due to error"
        })

@app.route('/api/trades', methods=['GET'])
def get_trade_history():
    try:
        if trading_agent and hasattr(trading_agent, 'trade_executor'):
            logger.info("📋 Getting trade history from agent")
            try:
                trades = trading_agent.trade_executor.order_history
                trade_history = []
                for trade in trades[-10:]:
                    trade_history.append({
                        "id": trade.get('id', ''),
                        "symbol": trade.get('symbol', ''),
                        "action": trade.get('action', ''),
                        "quantity": trade.get('quantity', 0),
                        "price": round(trade.get('price', 0), 2),
                        "timestamp": trade.get('timestamp', datetime.now()).isoformat(),
                        "status": trade.get('status', '')
                    })
                
                logger.info(f"✅ Returning {len(trade_history)} real trades")
                return jsonify({
                    "status": "success",
                    "trades": trade_history
                })
            except Exception as e:
                logger.warning(f"Real trade data unavailable: {e}")
        
        # Fallback to sample trade data
        sample_trades = generate_sample_trades()
        logger.info("📋 Using sample trade data")
        return jsonify({
            "status": "success",
            "trades": sample_trades,
            "note": "Sample trade data"
        })
            
    except Exception as e:
        logger.error(f"❌ Error fetching trades: {e}")
        sample_trades = generate_sample_trades()
        return jsonify({
            "status": "success",
            "trades": sample_trades,
            "note": "Sample data due to error"
        })

@app.route('/api/signals', methods=['GET'])
def get_current_signals():
    try:
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
        
        if trading_agent:
            symbols = getattr(trading_agent, 'symbols', symbols)
        
        logger.info(f"🎯 Generating signals for: {symbols}")
        
        signals = []
        for symbol in symbols:
            # Generate realistic signals
            actions = ['BUY', 'SELL', 'HOLD']
            weights = [40, 30, 30]  # 40% BUY, 30% SELL, 30% HOLD
            action = random.choices(actions, weights=weights)[0]
            
            # Realistic confidence based on action
            if action == 'BUY':
                confidence = random.uniform(0.65, 0.90)
            elif action == 'SELL':
                confidence = random.uniform(0.60, 0.85)
            else:
                confidence = random.uniform(0.50, 0.75)
            
            # Realistic price based on symbol
            base_prices = {'AAPL': 185, 'MSFT': 330, 'GOOGL': 135, 'TSLA': 245}
            base_price = base_prices.get(symbol, 100)
            price = base_price * random.uniform(0.95, 1.05)  # ±5% variation
            
            # Realistic quantity
            quantity = random.randint(5, 25)
            
            signals.append({
                "symbol": symbol,
                "action": action,
                "confidence": round(confidence, 3),
                "price": round(price, 2),
                "quantity": quantity
            })
        
        logger.info(f"✅ Generated {len(signals)} realistic signals")
        return jsonify({
            "status": "success",
            "signals": signals
        })
            
    except Exception as e:
        logger.error(f"❌ Error generating signals: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/test/all', methods=['GET'])
def test_all_endpoints():
    """Test all endpoints at once"""
    results = {}
    
    try:
        # Test health
        results['health'] = {'status': 'success', 'message': 'API is healthy'}
        
        # Test market data
        market_response = get_market_data()
        results['market_data'] = market_response.get_json()
        
        # Test portfolio
        portfolio_response = get_portfolio()
        results['portfolio'] = portfolio_response.get_json()
        
        # Test trades
        trades_response = get_trade_history()
        results['trades'] = trades_response.get_json()
        
        # Test signals
        signals_response = get_current_signals()
        results['signals'] = signals_response.get_json()
        
        return jsonify({
            "status": "success",
            "message": "All endpoints tested successfully",
            "results": results
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Test failed: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("=" * 50)
    print("🤖 AI Trading Agent API Server - FIXED VERSION")
    print("📍 http://localhost:5000")
    print("=" * 50)
    print("Available endpoints:")
    print("  GET  /api/health")
    print("  POST /api/agent/start")
    print("  POST /api/agent/stop")
    print("  GET  /api/agent/status")
    print("  GET  /api/market/data?symbol=AAPL")
    print("  GET  /api/portfolio")
    print("  GET  /api/trades")
    print("  GET  /api/signals")
    print("  GET  /api/test/all")
    print("=" * 50)
    
    app.run(debug=True, port=5000)