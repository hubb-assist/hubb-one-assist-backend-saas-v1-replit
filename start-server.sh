#!/bin/bash
# Script para iniciar o servidor FastAPI com Uvicorn

echo "Iniciando servidor FastAPI na porta 8000..."
python -m uvicorn fastapi_app:app --host 0.0.0.0 --port 8000