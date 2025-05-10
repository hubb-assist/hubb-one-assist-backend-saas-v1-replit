#!/bin/bash

# Script para iniciar o servidor FastAPI com Uvicorn
echo "Iniciando o servidor FastAPI com Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload