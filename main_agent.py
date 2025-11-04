import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime
import sys
import os

# Add the src directory to path so we can import our modules
sys.path.append(os.path.dirname(__file__))

from perception import DataCollector
from reasoning import MLPredictor, TechnicalAnalyzer
from execution import TradeExecutor
from risk_management import RiskManager

class AutonomousTradingAgent:
    def __init__(self, symbols, initial_capital=10000, paper_trading=True):
        self.symbols = symbols
        self.initial_capital = initial_capital
        self.paper_trading = paper_trading
        self.is_running = False
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize modules
        self.data_collector = DataCollector()
        self.ml_predictor = MLPredictor()
        self.technical_analyzer = TechnicalAnalyzer()
        self.trade_executor = TradeExecutor(paper_trading=paper_trading)
        self.risk_manager = RiskManager()
        
        # Training state
        self.models_trained = False
        
        self.logger.info("Autonomous Trading Agent Initialized")
        self.logger.info(f"Symbols: {symbols}")
        self.logger.info(f"Initial Capital: ${initial_capital:,}")
        self.logger.info(f"Paper Trading: {paper_trading}")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = "../logs"
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"{log_dir}/trading_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
                logging.StreamHandler()
            ]
        )
    
    def train_models(self):
        """Train ML models on historical data"""
        self.logger.info("Starting model training...")
        
        try:
            # Get historical data
            historical_data = self.data_collector.get_historical_data(
                self.symbols, 
                period="1y", 
                interval="1d"
            )
            
            # Train models for each symbol
            trained_count = 0
            for symbol in self.symbols:
                if symbol in historical_data and len(historical_data[symbol]) > 100:
                    accuracy = self.ml_predictor.train_model(symbol, historical_data[symbol])
                    if accuracy:
                        trained_count += 1
                        self.logger.info(f"Model trained for {symbol}, Accuracy: {accuracy:.3f}")
                    else:
                        self.logger.warning(f"Failed to train model for {symbol}")
                else:
                    self.logger.warning(f"Insufficient data for {symbol}")
            
            self.models_trained = trained_count > 0
            self.logger.info(f"Model training completed: {trained_count}/{len(self.symbols)} symbols trained")
            
        except Exception as e:
            self.logger.error(f"Model training failed: {e}")
    
    def run(self, update_interval=60):
        """Main autonomous trading loop"""
        self.is_running = True
        self.logger.info("Starting autonomous trading agent...")
        
        # Train models if not already trained
        if not self.models_trained:
            self.train_models()
        
        iteration = 0
        while self.is_running:
            try:
                self.logger.info(f"--- Trading Iteration {iteration} ---")
                
                # 1. Collect market data
                market_data = self.data_collector.get_realtime_data(
                    self.symbols, 
                    interval="5m",
                    lookback=50
                )
                
                # 2. Generate trading signals
                trade_signals = self._generate_signals(market_data)
                
                # 3. Execute trades
                if trade_signals:
                    self._execute_trades(trade_signals, market_data)
                
                # 4. Monitor portfolio
                self._monitor_portfolio(market_data)
                
                # 5. Log performance every 10 iterations
                if iteration % 10 == 0:
                    self._log_performance(market_data)
                
                iteration += 1
                
                # Wait for next iteration
                self.logger.info(f"Waiting {update_interval} seconds for next update...")
                time.sleep(update_interval)
                
            except KeyboardInterrupt:
                self.logger.info("Trading interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Error in trading loop: {e}")
                time.sleep(30)
    
    def _generate_signals(self, market_data):
        """Generate trading signals for all symbols"""
        signals = []
        
        for symbol in self.symbols:
            if (symbol not in market_data or 
                len(market_data[symbol]) < 20 or 
                market_data[symbol].empty):
                continue
            
            symbol_data = market_data[symbol]
            # Check if we have data to access
            if len(symbol_data) == 0:
                continue
                
            current_price = symbol_data['Close'].iloc[-1]
            
            # Get signals from different strategies
            technical_signal = self.technical_analyzer.analyze(symbol_data)
            ml_signal, ml_confidence = self.ml_predictor.predict(symbol, symbol_data)
            
            # Combine signals (majority voting)
            signal_votes = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
            signal_votes[technical_signal] += 1
            signal_votes[ml_signal] += 1
            
            # Determine final signal
            final_signal = max(signal_votes, key=signal_votes.get)
            
            # Only generate signal if not HOLD and ML confidence is reasonable
            if final_signal != 'HOLD' and ml_confidence > 0.55:
                # Get portfolio info for position sizing
                current_prices = {}
                for s, data in market_data.items():
                    if not data.empty and len(data) > 0:
                        current_prices[s] = data['Close'].iloc[-1]
                
                portfolio_summary = self.trade_executor.get_portfolio_summary(current_prices)
                
                # Calculate position size based on risk management
                position_size = self.risk_manager.calculate_position_size(
                    symbol, current_price, portfolio_summary['total_value'], ml_confidence
                )
                
                signal_data = {
                    'symbol': symbol,
                    'action': final_signal,
                    'quantity': position_size,
                    'price': current_price,
                    'confidence': ml_confidence,
                    'timestamp': datetime.now(),
                    'technical_signal': technical_signal,
                    'ml_signal': ml_signal
                }
                
                signals.append(signal_data)
                self.logger.info(f"Signal: {symbol} {final_signal} (Qty: {position_size}, Conf: {ml_confidence:.3f})")
        
        return signals
    
    def _execute_trades(self, signals, market_data):
        """Execute validated trades"""
        current_prices = {}
        for symbol, data in market_data.items():
            if not data.empty and len(data) > 0:
                current_prices[symbol] = data['Close'].iloc[-1]
                
        portfolio_summary = self.trade_executor.get_portfolio_summary(current_prices)
        
        for signal in signals:
            symbol = signal['symbol']
            action = signal['action']
            quantity = signal['quantity']
            price = signal['price']
            
            # Risk validation
            is_valid, reasons = self.risk_manager.validate_trade(
                symbol, action, quantity, price,
                self.trade_executor.portfolio,
                portfolio_summary['cash_balance']
            )
            
            if is_valid:
                # Execute trade
                trade_result = self.trade_executor.execute_trade(symbol, action, quantity, price)
                
                if trade_result:
                    # Update risk manager
                    self.risk_manager.increment_daily_trades()
                    self.logger.info(f"Trade executed: {symbol} {action} {quantity} @ ${price:.2f}")
                else:
                    self.logger.error(f"Trade execution failed: {symbol}")
            else:
                self.logger.warning(f"Trade rejected for {symbol}: {', '.join(reasons)}")
    
    def _monitor_portfolio(self, market_data):
        """Monitor portfolio and check for stop losses"""
        current_prices = {}
        for symbol, data in market_data.items():
            if not data.empty and len(data) > 0:
                current_prices[symbol] = data['Close'].iloc[-1]
                
        portfolio_summary = self.trade_executor.get_portfolio_summary(current_prices)
        
        # Update risk manager with P&L
        pnl_change = portfolio_summary['total_value'] - self.initial_capital
        self.risk_manager.update_daily_pnl(pnl_change)
    
    def _log_performance(self, market_data):
        """Log performance metrics"""
        current_prices = {}
        for symbol, data in market_data.items():
            if not data.empty and len(data) > 0:
                current_prices[symbol] = data['Close'].iloc[-1]
                
        portfolio_summary = self.trade_executor.get_portfolio_summary(current_prices)
        
        total_return = (portfolio_summary['total_value'] - self.initial_capital) / self.initial_capital * 100
        
        self.logger.info("=== Performance Summary ===")
        self.logger.info(f"Portfolio Value: ${portfolio_summary['total_value']:,.2f}")
        self.logger.info(f"Cash Balance: ${portfolio_summary['cash_balance']:,.2f}")
        self.logger.info(f"Total Return: {total_return:+.2f}%")
        self.logger.info(f"Positions: {portfolio_summary['number_of_positions']} symbols")
        self.logger.info(f"Daily Trades: {self.risk_manager.daily_trades}")
        self.logger.info("===========================")
    
    def stop(self):
        """Stop the trading agent"""
        self.is_running = False
        self.logger.info("Trading agent stopped")

def main():
    """Main function to run the trading agent"""
    print("Autonomous AI Trading Agent")
    print("=" * 50)
    
    # Define trading symbols
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
    
    # Create agent
    agent = AutonomousTradingAgent(
        symbols=symbols,
        initial_capital=10000,
        paper_trading=True
    )
    
    try:
        # Start the agent
        print("Starting autonomous trading...")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        agent.run(update_interval=60)  # 60 seconds between updates
        
    except KeyboardInterrupt:
        print("\nShutting down trading agent...")
        agent.stop()
    except Exception as e:
        print(f"Unexpected error: {e}")
        agent.stop()

# Test function
def test_agent():
    """Test the trading agent with a short run"""
    print("Autonomous AI Trading Agent - Test Run")
    print("=" * 50)
    
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
    
    agent = AutonomousTradingAgent(
        symbols=symbols,
        initial_capital=10000,
        paper_trading=True
    )
    
    try:
        print("Starting test run (will run for 2 iterations)...")
        print("Press Ctrl+C to stop early")
        print("-" * 50)
        
        agent.is_running = True
        agent.train_models()
        
        for i in range(2):  # Only 2 iterations for testing
            print(f"\n--- Test Iteration {i+1} ---")
            market_data = agent.data_collector.get_realtime_data(symbols, interval="5m", lookback=50)
            signals = agent._generate_signals(market_data)
            
            if signals:
                agent._execute_trades(signals, market_data)
            
            agent._log_performance(market_data)
            time.sleep(5)  # Short wait for testing
            
        print("\nTest completed successfully!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        agent.stop()

if __name__ == "__main__":
    # Run test mode by default, change to main() for full operation
    test_agent()
    # Uncomment the line below to run the full agent:
    # main()