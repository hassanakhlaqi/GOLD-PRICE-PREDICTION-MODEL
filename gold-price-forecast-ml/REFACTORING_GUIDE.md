# Refactoring Guide

This guide explains the refactored architecture for the Gold Price Forecasting project and how to work with the current codebase.

## Goals of the Refactor

- Separate concerns into reusable modules
- Improve maintainability and readability
- Enable clear configuration management
- Support both UI (Streamlit) and API (FastAPI)
- Add Docker-based deployment

## Project Layout

### `Src/core/`
Contains the core ML and data-processing modules:

- `config.py` — Loads and exposes `config.yaml` values
- `data_pipeline.py` — Handles data load/save and Yahoo Finance fetching
- `preprocessing.py` — Builds technical indicators and feature matrices
- `model_manager.py` — Manages XGBoost model training, tuning, evaluation, persistence

### `Src/api/`
Contains the FastAPI service:

- `main.py` — Defines API routes and handles model loading

### `Src/utils/`
Utility helpers for logging and environment setup:

- `logger.py` — Configures file and console logging

### `Src/app_improved.py`
Improved Streamlit application with:
- Real-time market dashboard
- Technical analysis charts
- Model performance overview
- Market insights and risk metrics
- System status panel

### `Src/train_refactored.py`
End-to-end training pipeline that:
- loads raw data
- preprocesses data
- trains the XGBoost model
- runs hyperparameter tuning
- saves the final model

## Key Refactor Patterns

### Configuration
`config.yaml` is the single source of truth.
Use `get_config()` from `Src/core/config.py` to access all values.

### Data and preprocessing
The pipeline is built around `DataPipeline` and `PreprocessingPipeline`.
This keeps data ingestion and feature engineering separate from model logic.

### Model manager
`ModelManager` encapsulates:
- model creation
- training
- tuning
- evaluation
- inference
- persistence

### API readiness
The FastAPI service loads the model on startup and exposes endpoints for health checks, predictions, feature metadata, and model info.

### UI readiness
The Streamlit app uses the same core modules for consistency.
This ensures model input format, feature names, and config values remain aligned.

## How to Update the Project

### 1. Add or change features
- Update `Src/core/preprocessing.py`
- Add new indicator functions
- Update feature extraction in `pipeline()`
- Use `feature_names` to preserve feature order

### 2. Change model behavior
- Update `ModelManager.create_model()` or `ModelManager.train()`
- Modify hyperparameter search in `ModelManager.hyperparameter_tuning()`

### 3. Adjust UI or API
- Update Streamlit views in `Src/app_improved.py`
- Update API payloads or routes in `Src/api/main.py`

### 4. Add new deployment options
- Modify `Dockerfile` or `docker-compose.yml`
- Add service-specific configuration in `config.yaml`

## Recommended Workflows

### Local development
1. Create a virtual environment
2. Install requirements
3. Run `Src/train_refactored.py` to build the model
4. Run Streamlit and FastAPI in separate shells

### Containerized deployment
1. Build with `docker-compose up --build`
2. Use `docker-compose logs -f` for runtime checks
3. Scale or extend services from the compose file

---

## Notes

Keep these best practices in mind:
- Use sequential time-split training for time-series data
- Avoid shuffling datasets in the preprocessing pipeline
- Keep feature engineering deterministic and reproducible
- Use the config file for experiment parameters instead of hard-coded values
