#!/bin/bash

# Script para iniciar o servidor FastAPI (Uvicorn)
echo "Iniciando o servidor FastAPI com Uvicorn na porta 8000..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000