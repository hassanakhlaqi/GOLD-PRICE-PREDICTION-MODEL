import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)

class PreprocessingPipeline:
    """Comprehensive preprocessing pipeline for gold price forecasting."""
    
    def __init__(self):
        """Initialize preprocessing pipeline."""
        self.scaler_params = {}
        self.feature_names = []
    
    def create_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create technical indicators for feature engineering."""
        df = df.copy()
        
        # Simple Moving Averages
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_30'] = df['Close'].rolling(window=30).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Exponential Moving Average
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']
        
        # RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        rolling_mean = df['Close'].rolling(window=20).mean()
        rolling_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = rolling_mean + (rolling_std * 2)
        df['BB_Lower'] = rolling_mean - (rolling_std * 2)
        df['BB_Width'] = (rolling_std * 4) / rolling_mean
        
        # ATR (Average True Range)
        df['H-L'] = df['High'] - df['Low']
        df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
        df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        df['ATR'] = df['TR'].rolling(window=14).mean()
        
        # Returns and Lags
        df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
        df['Lag_1'] = df['Log_Return'].shift(1)
        df['Lag_2'] = df['Log_Return'].shift(2)
        df['Lag_3'] = df['Log_Return'].shift(3)
        
        # Volume-based indicators
        if 'Volume' in df.columns:
            df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
            df['Price_Volume'] = (df['Close'] * df['Volume']).rolling(window=20).mean()
        
        # Stochastic Oscillator
        low_min = df['Low'].rolling(window=14).min()
        high_max = df['High'].rolling(window=14).max()
        df['Stochastic'] = 100 * ((df['Close'] - low_min) / (high_max - low_min))
        
        logger.info(f"Created {len(df.columns)} features after technical indicators")
        
        return df
    
    def create_target_variable(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create target variable for binary classification."""
        df = df.copy()
        df['Target'] = (df['Log_Return'].shift(-1) > 0).astype(int)
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and handle missing values."""
        df = df.copy()
        
        # Drop rows with NaN values
        initial_rows = len(df)
        df = df.dropna()
        dropped_rows = initial_rows - len(df)
        
        logger.info(f"Dropped {dropped_rows} rows with missing values")
        
        # Remove infinite values
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.dropna()
        
        return df
    
    def prepare_features(self, df: pd.DataFrame, 
                        exclude_cols: list = None) -> Tuple[pd.DataFrame, pd.Series, list]:
        """Prepare features and target variable."""
        if exclude_cols is None:
            exclude_cols = ['Target', 'Log_Return', 'H-L', 'H-PC', 'L-PC', 'TR']
        
        X = df.drop(columns=[col for col in exclude_cols if col in df.columns])
        y = df['Target'] if 'Target' in df.columns else None
        
        self.feature_names = X.columns.tolist()
        
        logger.info(f"Prepared {len(self.feature_names)} features for model training")
        
        return X, y, self.feature_names
    
    def pipeline(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, list]:
        """Execute full preprocessing pipeline."""
        logger.info("Starting preprocessing pipeline...")
        
        # Create technical indicators
        df = self.create_technical_indicators(df)
        
        # Create target variable
        df = self.create_target_variable(df)
        
        # Clean data
        df = self.clean_data(df)
        
        # Prepare features
        X, y, feature_names = self.prepare_features(df)
        
        logger.info("Preprocessing pipeline completed successfully")
        
        return X, y, feature_names
