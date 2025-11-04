import pandas as pd
import numpy as np
import yfinance as yf
import logging
from datetime import datetime, timedelta

class DataCollector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_historical_data(self, symbols, period="1y", interval="1d"):
        """Fetch historical data for training"""
        data = {}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist_data = ticker.history(period=period, interval=interval)
                data[symbol] = self._add_technical_indicators(hist_data)
                self.logger.info(f"Fetched historical data for {symbol}")
            except Exception as e:
                self.logger.error(f"Error fetching data for {symbol}: {e}")
        return data
    
    def get_realtime_data(self, symbols, interval="1m", lookback=100):
        """Get recent data for real-time trading"""
        data = {}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist_data = ticker.history(period="1d", interval=interval)
                if len(hist_data) > lookback:
                    hist_data = hist_data.tail(lookback)
                data[symbol] = self._add_technical_indicators(hist_data)
                self.logger.info(f"Fetched real-time data for {symbol}")
            except Exception as e:
                self.logger.error(f"Error fetching real-time data for {symbol}: {e}")
        return data
    
    def _add_technical_indicators(self, df):
        """Add technical indicators to dataframe"""
        data = df.copy()
        
        # Moving Averages
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['EMA_12'] = data['Close'].ewm(span=12).mean()
        data['EMA_26'] = data['Close'].ewm(span=26).mean()
        
        # RSI
        data['RSI'] = self._calculate_rsi(data['Close'])
        
        # MACD
        data['MACD'] = data['EMA_12'] - data['EMA_26']
        data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
        data['MACD_Histogram'] = data['MACD'] - data['MACD_Signal']
        
        # Bollinger Bands
        data['BB_Middle'] = data['Close'].rolling(window=20).mean()
        bb_std = data['Close'].rolling(window=20).std()
        data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
        data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
        
        # Volume indicators
        data['Volume_SMA'] = data['Volume'].rolling(window=20).mean()
        
        # Price transformations
        data['Returns'] = data['Close'].pct_change()
        data['Volatility'] = data['Returns'].rolling(window=20).std()
        
        return data.dropna()
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

# Test the module
# Test the module
if __name__ == "__main__":
    collector = DataCollector()
    print("Testing data collection...")
    
    # Try with longer period and different symbols
    test_data = collector.get_historical_data(["AAPL", "MSFT"], period="6mo", interval="1d")
    
    for symbol, data in test_data.items():
        print(f"\n{symbol} Data Shape: {data.shape}")
        if not data.empty:
            print(f"Latest {symbol} price: ${data['Close'].iloc[-1]:.2f}")
            print(f"Data from {data.index[0]} to {data.index[-1]}")
            print("Latest 5 rows:")
            print(data.tail())
        else:
            print(f"No data returned for {symbol}")
    
    # Test real-time data
    print("\n" + "="*50)
    print("Testing real-time data...")
    realtime_data = collector.get_realtime_data(["AAPL"], interval="5m", lookback=10)
    
    for symbol, data in realtime_data.items():
        print(f"\n{symbol} Real-time Data Shape: {data.shape}")
        if not data.empty:
            print(f"Latest {symbol} price: ${data['Close'].iloc[-1]:.2f}")
        else:
            print(f"No real-time data for {symbol}")