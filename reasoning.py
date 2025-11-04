import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import logging
import joblib

class MLPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.logger = logging.getLogger(__name__)
        
    def prepare_features(self, data):
        """Prepare features for ML model"""
        feature_columns = [
            'SMA_20', 'SMA_50', 'RSI', 'MACD', 'MACD_Histogram',
            'Volume_SMA', 'Volatility', 'Returns'
        ]
        
        # Create target (1 if price goes up next period, 0 otherwise)
        data = data.copy()
        data['Target'] = (data['Close'].shift(-1) > data['Close']).astype(int)
        
        features = data[feature_columns].copy()
        target = data['Target'].copy()
        
        # Remove rows with NaN values
        valid_idx = features.dropna().index
        features = features.loc[valid_idx]
        target = target.loc[valid_idx]
        
        return features, target
    
    def train_model(self, symbol, data):
        """Train ML model for a symbol"""
        try:
            features, target = self.prepare_features(data)
            
            if len(features) < 50:
                self.logger.warning(f"Not enough data for {symbol}")
                return None
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, target, test_size=0.2, shuffle=False
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.logger.info(f"Model trained for {symbol}, Accuracy: {accuracy:.3f}")
            
            # Save model and scaler
            self.models[symbol] = model
            self.scalers[symbol] = scaler
            
            return accuracy
            
        except Exception as e:
            self.logger.error(f"Error training model for {symbol}: {e}")
            return None
    
    def predict(self, symbol, current_data):
        """Predict next price movement"""
        if symbol not in self.models:
            return "HOLD", 0.5
        
        try:
            # Get latest data point
            latest_data = current_data.iloc[-1:].copy()
            
            # Prepare features
            feature_columns = [
                'SMA_20', 'SMA_50', 'RSI', 'MACD', 'MACD_Histogram',
                'Volume_SMA', 'Volatility', 'Returns'
            ]
            
            features = latest_data[feature_columns]
            
            # Scale features
            scaler = self.scalers[symbol]
            features_scaled = scaler.transform(features)
            
            # Predict
            model = self.models[symbol]
            prediction = model.predict(features_scaled)[0]
            probability = model.predict_proba(features_scaled)[0].max()
            
            action = "BUY" if prediction == 1 else "SELL"
            
            return action, probability
            
        except Exception as e:
            self.logger.error(f"Error predicting for {symbol}: {e}")
            return "HOLD", 0.5

class TechnicalAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, data):
        """Generate technical trading signals"""
        if len(data) < 50:
            return "HOLD"
        
        current = data.iloc[-1]
        
        # RSI signals
        rsi_signal = self._rsi_signal(current['RSI'])
        
        # Moving average signals
        ma_signal = self._moving_average_signal(data)
        
        # MACD signals
        macd_signal = self._macd_signal(data)
        
        # Bollinger Bands signals
        bb_signal = self._bollinger_bands_signal(data)
        
        # Combine signals
        signals = [rsi_signal, ma_signal, macd_signal, bb_signal]
        buy_signals = sum([1 for signal in signals if signal == "BUY"])
        sell_signals = sum([1 for signal in signals if signal == "SELL"])
        
        # Generate final signal
        if buy_signals >= 3:
            return "BUY"
        elif sell_signals >= 3:
            return "SELL"
        else:
            return "HOLD"
    
    def _rsi_signal(self, rsi):
        if rsi < 30:
            return "BUY"
        elif rsi > 70:
            return "SELL"
        else:
            return "HOLD"
    
    def _moving_average_signal(self, data):
        if len(data) < 2:
            return "HOLD"
        
        current = data.iloc[-1]
        previous = data.iloc[-2]
        
        # Golden cross / Death cross
        if (current['SMA_20'] > current['SMA_50'] and 
            previous['SMA_20'] <= previous['SMA_50']):
            return "BUY"
        elif (current['SMA_20'] < current['SMA_50'] and 
              previous['SMA_20'] >= previous['SMA_50']):
            return "SELL"
        else:
            return "HOLD"
    
    def _macd_signal(self, data):
        if len(data) < 2:
            return "HOLD"
        
        current = data.iloc[-1]
        previous = data.iloc[-2]
        
        # MACD crossover
        if (current['MACD'] > current['MACD_Signal'] and 
            previous['MACD'] <= previous['MACD_Signal']):
            return "BUY"
        elif (current['MACD'] < current['MACD_Signal'] and 
              previous['MACD'] >= previous['MACD_Signal']):
            return "SELL"
        else:
            return "HOLD"
    
    def _bollinger_bands_signal(self, data):
        if len(data) < 1:
            return "HOLD"
        
        current = data.iloc[-1]
        
        if current['Close'] <= current['BB_Lower']:
            return "BUY"
        elif current['Close'] >= current['BB_Upper']:
            return "SELL"
        else:
            return "HOLD"

# Test the reasoning engine
if __name__ == "__main__":
    from perception import DataCollector
    
    print("🤖 Testing Reasoning Engine")
    print("=" * 40)
    
    # Get data
    collector = DataCollector()
    data = collector.get_historical_data(["AAPL"], period="6mo", interval="1d")
    
    if "AAPL" in data and not data["AAPL"].empty:
        # Test Technical Analysis
        tech_analyzer = TechnicalAnalyzer()
        signal = tech_analyzer.analyze(data["AAPL"])
        print(f"Technical Analysis Signal: {signal}")
        
        # Test ML Prediction
        ml_predictor = MLPredictor()
        accuracy = ml_predictor.train_model("AAPL", data["AAPL"])
        
        if accuracy:
            prediction, confidence = ml_predictor.predict("AAPL", data["AAPL"])
            print(f"ML Prediction: {prediction} (Confidence: {confidence:.3f})")
        else:
            print("ML model training failed")
    else:
        print("No data available for testing")