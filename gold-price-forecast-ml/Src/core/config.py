import yaml
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuration manager for the gold price forecasting system."""

    DEFAULT_CONFIG_NAME = "config.yaml"
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    def __init__(self, config_path: str = DEFAULT_CONFIG_NAME):
        """Initialize config from YAML file."""
        self.config_path = self._resolve_path(config_path)
        self._config = self._load_config()
    
    def _resolve_path(self, config_path: str) -> Path:
        """Resolve config file path relative to the working directory or project root."""
        path = Path(config_path)
        if path.is_absolute():
            return path

        cwd_path = Path.cwd() / path
        if cwd_path.exists():
            return cwd_path

        project_path = self.PROJECT_ROOT / path
        if project_path.exists():
            return project_path

        return path

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, "r") as file:
            config = yaml.safe_load(file)
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        
        return value
    
    def get_data_config(self) -> Dict[str, Any]:
        """Get data configuration."""
        return self._config.get("data", {})
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration."""
        return self._config.get("model", {})
    
    def get_preprocessing_config(self) -> Dict[str, Any]:
        """Get preprocessing configuration."""
        return self._config.get("preprocessing", {})
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration."""
        return self._config.get("api", {"host": "0.0.0.0", "port": 8000})
    
    @property
    def data_ticker(self) -> str:
        """Get data ticker symbol."""
        return self.get("data.ticker", "GC=F")
    
    @property
    def start_date(self) -> str:
        """Get start date for data fetching."""
        return self.get("data.start_date", "2020-01-01")
    
    @property
    def end_date(self) -> str:
        """Get end date for data fetching."""
        return self.get("data.end_date", "2026-05-25")
    
    @property
    def raw_data_path(self) -> str:
        """Get raw data output path."""
        return self.get("data.raw_output_path", "Data/raw/xauusd_raw.csv")
    
    @property
    def processed_data_path(self) -> str:
        """Get processed data output path."""
        return self.get("data.processed_output_path", "Data/processed/xauusd_features.csv")
    
    @property
    def model_path(self) -> str:
        """Get model save path."""
        return self.get("model.model_path", "Models/xgboost_model.pkl")
    
    @property
    def test_size(self) -> float:
        """Get test size ratio."""
        return self.get("model.test_size", 0.2)
    
    @property
    def random_state(self) -> int:
        """Get random state seed."""
        return self.get("model.random_state", 42)


# Global config instance
_config_instance = None

def get_config() -> Config:
    """Get or create global config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
