#!/bin/bash
# Este script inicia o servidor FastAPI (API REST simples)

echo "Iniciando o servidor FastAPI na porta 8000..."
cd /home/runner/workspace && exec python -m uvicorn fastapi_app:app --host 0.0.0.0 --port 8000