import logging
from datetime import datetime
import pandas as pd

class TradeExecutor:
    def __init__(self, paper_trading=True):
        self.paper_trading = paper_trading
        self.portfolio = {}
        self.order_history = []
        self.positions = {}
        self.cash_balance = 10000  # Starting cash
        self.logger = logging.getLogger(__name__)
        
    def execute_trade(self, symbol, action, quantity, current_price):
        """Execute a trade with risk checks"""
        try:
            # Basic validation
            if quantity <= 0:
                self.logger.error(f"Invalid quantity: {quantity}")
                return None
            
            trade_value = quantity * current_price
            
            # Check if we have enough cash for buy orders
            if action.upper() == 'BUY' and trade_value > self.cash_balance:
                self.logger.warning(f"Insufficient cash for {symbol} buy: ${trade_value:.2f} > ${self.cash_balance:.2f}")
                return None
            
            # Check if we have enough shares for sell orders
            if action.upper() == 'SELL':
                current_position = self.portfolio.get(symbol, 0)
                if quantity > current_position:
                    self.logger.warning(f"Insufficient shares for {symbol} sell: {quantity} > {current_position}")
                    return None
            
            # Execute the trade
            if self.paper_trading:
                trade_result = self._paper_trade(symbol, action, quantity, current_price)
            else:
                trade_result = self._live_trade(symbol, action, quantity, current_price)
            
            if trade_result:
                self.logger.info(f"Trade executed: {symbol} {action} {quantity} @ ${current_price:.2f}")
                return trade_result
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Trade execution failed: {e}")
            return None
    
    def _paper_trade(self, symbol, action, quantity, price):
        """Simulate trade execution"""
        trade_value = quantity * price
        
        trade_record = {
            'id': f"PAPER_{len(self.order_history) + 1}",
            'symbol': symbol,
            'action': action.upper(),
            'quantity': quantity,
            'price': price,
            'value': trade_value,
            'status': 'FILLED',
            'timestamp': datetime.now(),
            'type': 'PAPER'
        }
        
        # Update portfolio and cash balance
        if action.upper() == 'BUY':
            self.cash_balance -= trade_value
            self.portfolio[symbol] = self.portfolio.get(symbol, 0) + quantity
        elif action.upper() == 'SELL':
            self.cash_balance += trade_value
            self.portfolio[symbol] = self.portfolio.get(symbol, 0) - quantity
            # Remove symbol if position is zero
            if self.portfolio[symbol] == 0:
                del self.portfolio[symbol]
        
        self.order_history.append(trade_record)
        return trade_record
    
    def _live_trade(self, symbol, action, quantity, price):
        """Execute real trade through broker API"""
        # Placeholder for actual broker API integration
        # For now, we'll just paper trade
        return self._paper_trade(symbol, action, quantity, price)
    
    def get_portfolio_value(self, current_prices):
        """Calculate current portfolio value"""
        portfolio_value = self.cash_balance
        
        for symbol, quantity in self.portfolio.items():
            if symbol in current_prices and quantity > 0:
                portfolio_value += quantity * current_prices[symbol]
        
        return portfolio_value
    
    def get_position(self, symbol):
        """Get current position for a symbol"""
        return self.portfolio.get(symbol, 0)
    
    def get_portfolio_summary(self, current_prices):
        """Get detailed portfolio summary"""
        positions_value = 0
        positions_detail = {}
        
        for symbol, quantity in self.portfolio.items():
            if symbol in current_prices and quantity > 0:
                position_value = quantity * current_prices[symbol]
                positions_value += position_value
                positions_detail[symbol] = {
                    'quantity': quantity,
                    'current_price': current_prices[symbol],
                    'value': position_value
                }
        
        total_value = self.cash_balance + positions_value
        
        return {
            'cash_balance': self.cash_balance,
            'positions_value': positions_value,
            'total_value': total_value,
            'positions': positions_detail,
            'number_of_positions': len(self.portfolio)
        }

# Test the execution module
if __name__ == "__main__":
    print("🤖 Testing Trade Execution")
    print("=" * 40)
    
    executor = TradeExecutor(paper_trading=True)
    
    # Test trades
    test_trades = [
        ('AAPL', 'BUY', 10, 268.78),
        ('MSFT', 'BUY', 5, 513.54),
        ('AAPL', 'SELL', 5, 270.00)
    ]
    
    for symbol, action, quantity, price in test_trades:
        trade = executor.execute_trade(symbol, action, quantity, price)
        if trade:
            print(f"✅ {trade['action']} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f}")
        else:
            print(f"❌ Trade failed: {action} {quantity} {symbol}")
    
    # Show portfolio summary
    current_prices = {'AAPL': 270.00, 'MSFT': 515.00}
    summary = executor.get_portfolio_summary(current_prices)
    
    print(f"\n📊 Portfolio Summary:")
    print(f"Cash: ${summary['cash_balance']:.2f}")
    print(f"Positions Value: ${summary['positions_value']:.2f}")
    print(f"Total Value: ${summary['total_value']:.2f}")
    print(f"Positions: {summary['positions']}")