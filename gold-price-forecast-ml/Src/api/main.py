from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
import logging
from typing import List, Dict, Any

from ..core import get_config, ModelManager, DataPipeline

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Gold Price Forecasting API",
    description="API for gold price prediction using XGBoost",
    version="1.0.0"
)

# Pydantic models for request/response
class PredictionInput(BaseModel):
    features: List[float]
    feature_names: List[str] = None

class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    confidence: float

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool

# Global model manager
model_manager = None

def init_model():
    """Initialize model on startup."""
    global model_manager
    config = get_config()
    model_manager = ModelManager()
    
    try:
        model_manager.load(config.model_path)
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    init_model()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        model_loaded=model_manager is not None and model_manager.model is not None
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict(input_data: PredictionInput):
    """Make prediction endpoint."""
    if model_manager is None or model_manager.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert input to dataframe
        features_array = np.array(input_data.features).reshape(1, -1)
        
        # Make prediction
        prediction = model_manager.predict(features_array)[0]
        proba = model_manager.predict_proba(features_array)[0]
        
        return PredictionResponse(
            prediction=int(prediction),
            probability=float(proba[prediction]),
            confidence=float(max(proba))
        )
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/features")
async def get_features():
    """Get feature names."""
    if model_manager is None or model_manager.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "feature_count": len(model_manager.model.get_booster().feature_names),
        "features": model_manager.model.get_booster().feature_names
    }

@app.get("/feature-importance")
async def get_feature_importance(top_n: int = 10):
    """Get feature importance."""
    if model_manager is None or model_manager.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        importance_df = model_manager.get_feature_importance(top_n)
        return importance_df.to_dict('records')
    
    except Exception as e:
        logger.error(f"Feature importance error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/model-info")
async def get_model_info():
    """Get model information."""
    if model_manager is None or model_manager.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_type": "XGBoost",
        "n_estimators": model_manager.model.n_estimators,
        "learning_rate": model_manager.model.learning_rate,
        "max_depth": model_manager.model.max_depth,
        "best_params": model_manager.best_params
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Gold Price Forecasting API",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "features": "/features",
            "feature_importance": "/feature-importance",
            "model_info": "/model-info",
            "docs": "/docs"
        }
    }
