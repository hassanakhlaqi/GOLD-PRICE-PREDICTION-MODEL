"""
Refactored training script using modular architecture.
Uses new core modules: config, data_pipeline, preprocessing, model_manager
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import (
    get_config,
    DataPipeline,
    PreprocessingPipeline,
    ModelManager
)
from utils.logger import setup_logging

# Setup logging
setup_logging(log_level="INFO", log_file="logs/training.log")
logger = logging.getLogger(__name__)

def main():
    """Main training pipeline."""
    logger.info("=" * 80)
    logger.info("GOLD PRICE FORECASTING - MODEL TRAINING PIPELINE")
    logger.info("=" * 80)
    
    # Load configuration
    config = get_config()
    logger.info(f"Configuration loaded from: {config.config_path}")
    
    # Step 1: Fetch or load raw data
    logger.info("\n[Step 1] Loading raw data...")
    try:
        # Try to load existing data first
        df_raw = DataPipeline.load_raw_data(config.raw_data_path)
    except FileNotFoundError:
        # Fetch new data if not exists
        logger.info(f"Raw data not found. Fetching from Yahoo Finance...")
        df_raw = DataPipeline.fetch_data(
            ticker=config.data_ticker,
            start_date=config.start_date,
            end_date=config.end_date
        )
        # Save raw data
        DataPipeline.save_data(df_raw, config.raw_data_path)
    
    logger.info(f"Raw data shape: {df_raw.shape}")
    logger.info(f"Date range: {df_raw.index[0]} to {df_raw.index[-1]}")
    
    # Step 2: Preprocessing
    logger.info("\n[Step 2] Preprocessing and feature engineering...")
    preprocessing_pipeline = PreprocessingPipeline()
    X, y, feature_names = preprocessing_pipeline.pipeline(df_raw)
    
    logger.info(f"Features created: {len(feature_names)}")
    logger.info(f"Dataset shape: X={X.shape}, y={y.shape}")
    
    # Save processed data
    processed_df = X.copy()
    processed_df['Target'] = y
    processed_df['Log_Return'] = preprocessing_pipeline.pipeline.__doc__  # Just for structure
    DataPipeline.save_data(processed_df, config.processed_data_path)
    
    # Step 3: Train-test split
    logger.info("\n[Step 3] Splitting data...")
    test_size = config.test_size
    split_idx = int(len(X) * (1 - test_size))
    
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    logger.info(f"Train set: {len(X_train)} samples")
    logger.info(f"Test set: {len(X_test)} samples")
    
    # Step 4: Model training
    logger.info("\n[Step 4] Training XGBoost model...")
    model_manager = ModelManager(random_state=config.random_state)
    
    # Create and train model
    model_manager.create_model(
        n_estimators=config.get("model.n_estimators", 100),
        learning_rate=config.get("model.learning_rate", 0.05),
        max_depth=config.get("model.max_depth", 5)
    )
    
    model_manager.train(X_train, y_train)
    
    # Step 5: Hyperparameter tuning
    logger.info("\n[Step 5] Performing hyperparameter tuning...")
    best_params = model_manager.hyperparameter_tuning(X_train, y_train, n_iter=10)
    logger.info(f"Best parameters: {best_params}")
    
    # Step 6: Evaluation
    logger.info("\n[Step 6] Evaluating model...")
    metrics = model_manager.evaluate(X_test, y_test)
    
    logger.info(f"Accuracy: {metrics['accuracy']:.4f}")
    logger.info(f"F1 Score: {metrics['f1_score']:.4f}")
    logger.info(f"ROC-AUC: {metrics['roc_auc']:.4f}")
    
    # Step 7: Feature importance
    logger.info("\n[Step 7] Feature importance (Top 10):")
    importance_df = model_manager.get_feature_importance(top_n=10)
    logger.info(f"\n{importance_df.to_string()}")
    
    # Step 8: Save model
    logger.info("\n[Step 8] Saving model...")
    model_manager.save(config.model_path)
    
    logger.info("\n" + "=" * 80)
    logger.info("TRAINING COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)
    
    return model_manager, metrics

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Training failed: {str(e)}", exc_info=True)
        sys.exit(1)
