#!/bin/bash
echo "Iniciando o servidor FastAPI na porta 5000..."
exec uvicorn api:app --host 0.0.0.0 --port 5000