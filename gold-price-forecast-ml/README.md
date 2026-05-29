# Gold Price Forecasting System

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![XGBoost](https://img.shields.io/badge/Model-XGBoost-orange)
![FastAPI](https://img.shields.io/badge/API-FastAPI-lightgrey)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-blue)

A refactored end-to-end gold price forecasting project for **XAUUSD directional prediction**. This repository includes a modular data pipeline, XGBoost model manager, enhanced Streamlit dashboard, FastAPI prediction API, and Docker deployment support.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Key Features](#key-features)
4. [Getting Started](#getting-started)
5. [Running the Project](#running-the-project)
6. [API Endpoints](#api-endpoints)
7. [Docker Support](#docker-support)
8. [Configuration](#configuration)
9. [Notes](#notes)

---

## Project Overview

This project predicts next-day gold price direction using historical gold data, technical indicators, and an XGBoost classifier. It is designed to be easy to extend, maintain, and deploy.

The repo includes:
- `Data/raw/` and `Data/processed/` data storage
- Modular core pipeline modules in `Src/core/`
- A production-ready API in `Src/api/main.py`
- A modern Streamlit-based UI in `Src/app_improved.py`
- Docker support for local deployment

---

## Repository Structure

```text
gold-price-forecast-ml/
├── config.yaml
├── Dockerfile
├── docker-compose.yml
├── README.md
├── REQUIREMENTS.txt
├── RUNNING_THE_PROJECT.md
├── REFACTORING_GUIDE.md
├── REFACTORING_SUMMARY.md
├── requirements.txt
├── Data/
│   ├── processed/
│   └── raw/
├── docs/
│   └── images/
├── Models/
├── Src/
│   ├── api/
│   │   └── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── data_pipeline.py
│   │   ├── model_manager.py
│   │   └── preprocessing.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py
│   ├── app_improved.py
│   ├── train_refactored.py
│   ├── data_loader.py
│   ├── evaluate.py
│   ├── features.py
│   ├── train.py
│   └── tune.py
└── requirements.txt
```

---

## Key Features

- Modular data pipeline with configuration management
- Feature engineering for time-series forecasting
- XGBoost classifier for directional prediction
- Streamlit dashboard for interactive analysis
- FastAPI endpoints for prediction and model introspection
- Docker support for reproducible deployment

---

## Getting Started

### Requirements
- Python 3.11+ (3.13 is supported in your environment)
- `pip`
- Optional: `docker` and `docker-compose` for containerized deployment

### Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Running the Project

### 1. Run the Streamlit app

```bash
python3 -m streamlit run Src/app_improved.py
```

Then open:

- `http://localhost:8501`

### 2. Run the FastAPI service

```bash
python3 -m uvicorn Src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Then open:

- `http://localhost:8000/docs`

### 3. Train the model with the refactored pipeline

```bash
python3 Src/train_refactored.py
```

This script:
- fetches raw gold data if missing
- runs preprocessing
- trains and tunes XGBoost
- saves the trained model to `Models/xgboost_model.pkl`

---

## API Endpoints

- `GET /health` — health check
- `POST /predict` — predict a direction from feature values
- `GET /features` — list model feature names
- `GET /feature-importance` — return feature importances
- `GET /model-info` — model metadata
- `GET /` — root summary endpoint

Example prediction request:

```bash
curl -X POST http://localhost:8000/predict   -H "Content-Type: application/json"   -d '{"features": [0.1, 0.2, 0.3], "feature_names": ["SMA_10", "SMA_30", "RSI"]}'
```

---

## Docker Support

### Build and run with Docker Compose

```bash
docker-compose up --build
```

Services available at:
- Streamlit: `http://localhost:8501`
- FastAPI docs: `http://localhost:8000/docs`

### Build individual image

```bash
docker build -t gold-price-forecast .
```

### Run containers

```bash
docker run -p 8501:8501 gold-price-forecast
```

or for API:

```bash
docker run -p 8000:8000 gold-price-forecast   python3 -m uvicorn Src.api.main:app --host 0.0.0.0 --port 8000
```

---

## Configuration

Edit `config.yaml` to customize:

- `data.ticker`
- `data.start_date`
- `data.end_date`
- model hyperparameters like `n_estimators`, `learning_rate`, `max_depth`
- file locations for raw/processed data and saved model

---

## Notes

- The code assumes `Data/raw/` and `Data/processed/` directories exist.
- The Streamlit UI and API are separate services and can run simultaneously.
- This project is intended for research and should not be used as financial advice.
