#!/bin/bash
# Quick start script for Gold Price Forecasting System

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Gold Price Forecasting System - Quick Start Guide        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}[1/5] Checking Python version...${NC}"
python3 --version

# Install dependencies
echo -e "${BLUE}[2/5] Installing dependencies...${NC}"
pip install -r requirements.txt

# Create necessary directories
echo -e "${BLUE}[3/5] Creating necessary directories...${NC}"
mkdir -p Data/raw Data/processed Models logs docs/images

# Optional: Train model
read -p "Do you want to train the model? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}[4/5] Training model...${NC}"
    python3 Src/train_refactored.py
fi

echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo -e "${YELLOW}Available commands:${NC}"
echo ""
echo "  Streamlit UI (Enhanced):"
echo -e "  ${GREEN}python3 -m streamlit run Src/app_improved.py${NC}"
echo ""
echo "  FastAPI (API Server):"
echo -e "  ${GREEN}python3 -m uvicorn Src.api.main:app --host 0.0.0.0 --port 8000${NC}"
echo ""
echo "  Docker Compose (All Services):"
echo -e "  ${GREEN}docker-compose up --build${NC}"
echo ""
echo -e "${YELLOW}Access points:${NC}"
echo "  - Streamlit UI: http://localhost:8501"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Documentation:${NC}"
echo "  - See REFACTORING_GUIDE.md for detailed documentation"
echo "  - See REFACTORING_SUMMARY.md for architecture overview"
echo ""
