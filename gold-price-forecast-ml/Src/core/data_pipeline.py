import pandas as pd
import yfinance as yf
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DataPipeline:
    """Data loading and management pipeline."""
    
    @staticmethod
    def fetch_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch historical data from Yahoo Finance."""
        logger.info(f"Fetching data for {ticker} from {start_date} to {end_date}...")
        
        try:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if df.empty:
                raise ValueError(f"No data fetched for ticker {ticker}")
            
            # Handle MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
            
            logger.info(f"Successfully fetched {len(df)} rows of data")
            return df
        
        except Exception as e:
            logger.error(f"Failed to fetch data: {str(e)}")
            raise
    
    @staticmethod
    def load_raw_data(file_path: str) -> pd.DataFrame:
        """Load raw data from CSV file."""
        logger.info(f"Loading raw data from {file_path}...")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        try:
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            logger.info(f"Successfully loaded {len(df)} rows")
            return df
        
        except Exception as e:
            logger.error(f"Failed to load data: {str(e)}")
            raise
    
    @staticmethod
    def load_processed_data(file_path: str) -> pd.DataFrame:
        """Load processed data from CSV file."""
        logger.info(f"Loading processed data from {file_path}...")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Processed data file not found: {file_path}")
        
        try:
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            logger.info(f"Successfully loaded {len(df)} rows with {len(df.columns)} features")
            return df
        
        except Exception as e:
            logger.error(f"Failed to load processed data: {str(e)}")
            raise
    
    @staticmethod
    def save_data(df: pd.DataFrame, file_path: str) -> None:
        """Save data to CSV file."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            df.to_csv(file_path)
            logger.info(f"Data saved to {file_path}")
        
        except Exception as e:
            logger.error(f"Failed to save data: {str(e)}")
            raise
    
    @staticmethod
    def get_train_test_split(df: pd.DataFrame, test_size: float = 0.2) -> tuple:
        """Split data into train and test sets (time-series aware)."""
        split_idx = int(len(df) * (1 - test_size))
        
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        
        logger.info(f"Train: {len(train_df)} samples, Test: {len(test_df)} samples")
        
        return train_df, test_df
