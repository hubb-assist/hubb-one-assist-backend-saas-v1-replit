#!/bin/bash
# Script para executar o FastAPI com Uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload