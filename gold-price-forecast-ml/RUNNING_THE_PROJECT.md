# Running the Project

This file explains how to run the Gold Price Forecasting project locally and with Docker.

## 1. Local Setup

### Create a virtual environment

```bash
cd gold-price-forecast-ml
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Create required directories

```bash
mkdir -p Data/raw Data/processed Models logs docs/images
```

## 2. Run the Streamlit App

```bash
python3 -m streamlit run Src/app_improved.py
```

Open the app at:

- `http://localhost:8501`

## 3. Run the FastAPI Service

```bash
python3 -m uvicorn Src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Open the docs at:

- `http://localhost:8000/docs`

## 4. Train the Model

```bash
python3 Src/train_refactored.py
```

This command will:
- load or download raw data
- preprocess the dataset
- train & tune the XGBoost model
- save the model to `Models/xgboost_model.pkl`

## 5. Run with Docker Compose

```bash
docker-compose up --build
```

Services:
- Streamlit UI: `http://localhost:8501`
- FastAPI: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

Stop the services with:

```bash
docker-compose down
```

## 6. Useful Commands

### Check health endpoint

```bash
curl http://localhost:8000/health
```

### Request predictions

```bash
curl -X POST http://localhost:8000/predict   -H "Content-Type: application/json"   -d '{"features": [0.1, 0.2, 0.3], "feature_names": ["SMA_10", "SMA_30", "RSI"]}'
```

### Troubleshooting

- If a module is missing, ensure the virtual environment is activated.
- If the port is in use, change the `--port` value.
- Ensure `config.yaml` exists in the repo root and has the expected settings.
