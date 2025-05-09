#!/bin/bash
# Script para iniciar o servidor FastAPI (Uvicorn) em segundo plano
echo "Iniciando o servidor FastAPI com Uvicorn na porta 8000..."
cd /home/runner/workspace && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'
