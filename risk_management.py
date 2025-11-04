import logging
from datetime import datetime

class RiskManager:
    def __init__(self, max_position_size=0.1, max_daily_loss=0.05, stop_loss=0.02):
        self.max_position_size = max_position_size  # 10% of portfolio per trade
        self.max_daily_loss = max_daily_loss        # 5% max daily loss
        self.stop_loss = stop_loss                  # 2% stop loss per position
        self.daily_pnl = 0
        self.daily_trades = 0
        self.max_daily_trades = 20
        self.logger = logging.getLogger(__name__)
        
    def validate_trade(self, symbol, action, quantity, price, portfolio, cash_balance):
        """Validate if trade meets risk criteria"""
        reasons = []
        
        trade_value = quantity * price
        portfolio_value = cash_balance + sum(
            portfolio.get(s, 0) * price for s in portfolio.keys()
        )
        
        # Position size check (max 10% of portfolio per trade)
        max_position_value = portfolio_value * self.max_position_size
        if trade_value > max_position_value:
            reasons.append(f"Position size ${trade_value:.2f} > max ${max_position_value:.2f}")
        
        # Daily loss check (max 5% daily drawdown)
        if self.daily_pnl < -abs(portfolio_value * self.max_daily_loss):
            reasons.append(f"Daily loss limit exceeded: ${self.daily_pnl:.2f}")
        
        # Daily trade limit
        if self.daily_trades >= self.max_daily_trades:
            reasons.append(f"Daily trade limit reached: {self.daily_trades}/{self.max_daily_trades}")
        
        # Concentration risk (max 30% in one symbol)
        current_symbol_value = portfolio.get(symbol, 0) * price
        if current_symbol_value + trade_value > portfolio_value * 0.3:
            reasons.append("Position would exceed 30% concentration limit")
        
        is_valid = len(reasons) == 0
        return is_valid, reasons
    
    def update_daily_pnl(self, pnl_change):
        """Update daily P&L tracking"""
        self.daily_pnl += pnl_change
        
    def increment_daily_trades(self):
        """Increment daily trade count"""
        self.daily_trades += 1
        
    def reset_daily_metrics(self):
        """Reset daily metrics (call this at market open)"""
        self.daily_pnl = 0
        self.daily_trades = 0
        
    def calculate_position_size(self, symbol, price, portfolio_value, confidence=0.5):
        """Calculate appropriate position size based on risk parameters"""
        # Base size: max position size adjusted by confidence
        base_size = portfolio_value * self.max_position_size * confidence
        shares = int(base_size / price)
        
        # Minimum 1 share, maximum based on available balance
        shares = max(1, min(shares, int(portfolio_value * 0.2 / price)))
        
        return shares
    
    def check_stop_loss(self, symbol, entry_price, current_price, position_type):
        """Check if stop loss is triggered"""
        if position_type.upper() == 'LONG':
            loss_pct = (entry_price - current_price) / entry_price
            if loss_pct >= self.stop_loss:
                return True, f"Stop loss triggered: {loss_pct:.2%}"
        elif position_type.upper() == 'SHORT':
            loss_pct = (current_price - entry_price) / entry_price
            if loss_pct >= self.stop_loss:
                return True, f"Stop loss triggered: {loss_pct:.2%}"
        
        return False, ""

# Test the risk management
if __name__ == "__main__":
    print("🛡️ Testing Risk Management")
    print("=" * 40)
    
    risk_manager = RiskManager()
    
    # Test trade validation
    test_cases = [
        ('AAPL', 'BUY', 100, 268.78, {'AAPL': 50}, 5000),
        ('MSFT', 'BUY', 50, 513.54, {}, 10000),
        ('GOOGL', 'BUY', 10, 2500.00, {}, 10000)
    ]
    
    for symbol, action, quantity, price, portfolio, cash in test_cases:
        is_valid, reasons = risk_manager.validate_trade(
            symbol, action, quantity, price, portfolio, cash
        )
        
        status = "✅ APPROVED" if is_valid else "❌ REJECTED"
        print(f"{status} {action} {quantity} {symbol} @ ${price:.2f}")
        if reasons:
            print(f"   Reasons: {', '.join(reasons)}")
    
    # Test position sizing
    print(f"\n📊 Position Sizing Examples:")
    portfolio_value = 10000
    test_symbols = [('AAPL', 268.78), ('MSFT', 513.54), ('TSLA', 850.50)]
    
    for symbol, price in test_symbols:
        size = risk_manager.calculate_position_size(symbol, price, portfolio_value, 0.7)
        trade_value = size * price
        print(f"   {symbol}: {size} shares = ${trade_value:.2f} ({trade_value/portfolio_value:.1%} of portfolio)")