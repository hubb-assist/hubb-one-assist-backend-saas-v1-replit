#!/bin/bash

# Script para iniciar o FastAPI com Uvicorn
# Este script usa corretamente o protocolo ASGI para servir o FastAPI

uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload