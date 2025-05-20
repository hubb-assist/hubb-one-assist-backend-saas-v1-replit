#!/bin/bash

# Script para iniciar o servidor FastAPI com Uvicorn
echo "Iniciando o servidor FastAPI com Uvicorn..."
exec uvicorn asgi:application --host 0.0.0.0 --port 5000 --reload