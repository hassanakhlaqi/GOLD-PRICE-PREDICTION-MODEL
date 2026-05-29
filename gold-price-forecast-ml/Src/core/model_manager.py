import pickle
import os
import logging
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score, roc_auc_score
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages model training, evaluation, and predictions."""
    
    def __init__(self, random_state: int = 42):
        """Initialize model manager."""
        self.model = None
        self.random_state = random_state
        self.feature_importance = None
        self.best_params = None
    
    def create_model(self, n_estimators: int = 100, learning_rate: float = 0.05,
                    max_depth: int = 5, **kwargs) -> XGBClassifier:
        """Create XGBoost model with specified parameters."""
        params = {
            'n_estimators': n_estimators,
            'learning_rate': learning_rate,
            'max_depth': max_depth,
            'eval_metric': 'logloss',
            'random_state': self.random_state,
        }
        params.update(kwargs)
        
        self.model = XGBClassifier(**params)
        logger.info(f"Created XGBoost model with params: {params}")
        
        return self.model
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """Train the model."""
        if self.model is None:
            self.create_model()
        
        logger.info(f"Training model with {len(X_train)} samples...")
        self.model.fit(X_train, y_train)
        
        # Store feature importance
        self.feature_importance = dict(zip(X_train.columns, self.model.feature_importances_))
        
        logger.info("Model training completed")
    
    def hyperparameter_tuning(self, X_train: pd.DataFrame, y_train: pd.Series,
                            n_iter: int = 20) -> Dict[str, Any]:
        """Perform hyperparameter tuning using Randomized Search."""
        logger.info("Starting hyperparameter tuning...")
        
        # Calculate scale_pos_weight for class imbalance
        ratio = float(y_train.value_counts()[0] / y_train.value_counts()[1])
        
        param_dist = {
            'n_estimators': [100, 200, 300],
            'max_depth': [3, 4, 5, 7],
            'learning_rate': [0.01, 0.05, 0.1],
            'subsample': [0.6, 0.8, 1.0],
            'colsample_bytree': [0.6, 0.8, 1.0],
            'gamma': [0, 0.5, 1, 2],
            'min_child_weight': [1, 3, 5]
        }
        
        base_model = XGBClassifier(
            eval_metric='logloss',
            random_state=self.random_state,
            scale_pos_weight=ratio
        )
        
        tscv = TimeSeriesSplit(n_splits=5)
        
        random_search = RandomizedSearchCV(
            estimator=base_model,
            param_distributions=param_dist,
            n_iter=n_iter,
            cv=tscv,
            scoring='f1_macro',
            random_state=self.random_state,
            n_jobs=-1
        )
        
        random_search.fit(X_train, y_train)
        
        self.model = random_search.best_estimator_
        self.best_params = random_search.best_params_
        
        logger.info(f"Best parameters found: {self.best_params}")
        
        return self.best_params
    
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
        """Evaluate model performance."""
        if self.model is None:
            raise ValueError("Model not trained. Train model first.")
        
        logger.info("Evaluating model...")
        
        predictions = self.model.predict(X_test)
        pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y_test, predictions),
            'f1_score': f1_score(y_test, predictions),
            'roc_auc': roc_auc_score(y_test, pred_proba)
        }
        
        logger.info(f"Model evaluation - Accuracy: {metrics['accuracy']:.4f}, "
                   f"F1: {metrics['f1_score']:.4f}, ROC-AUC: {metrics['roc_auc']:.4f}")
        logger.info(f"Classification Report:\n{classification_report(y_test, predictions)}")
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        if self.model is None:
            raise ValueError("Model not trained. Train model first.")
        
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Get prediction probabilities."""
        if self.model is None:
            raise ValueError("Model not trained. Train model first.")
        
        return self.model.predict_proba(X)
    
    def save(self, file_path: str) -> None:
        """Save model to file."""
        if self.model is None:
            raise ValueError("Model not trained. Cannot save.")
        
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"Model saved to {file_path}")
        
        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")
            raise
    
    def load(self, file_path: str) -> None:
        """Load model from file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Model file not found: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"Model loaded from {file_path}")
        
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def get_feature_importance(self, top_n: int = 10) -> pd.DataFrame:
        """Get feature importance."""
        if self.feature_importance is None:
            raise ValueError("Model not trained. Train model first to get importance.")
        
        importance_df = pd.DataFrame(
            list(self.feature_importance.items()),
            columns=['Feature', 'Importance']
        ).sort_values('Importance', ascending=False)
        
        return importance_df.head(top_n)
