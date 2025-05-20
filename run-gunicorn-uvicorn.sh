#!/bin/bash

# Script para iniciar o FastAPI com Gunicorn usando UvicornWorker
# Esta é a abordagem apropriada para servidores de produção

gunicorn \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5000 \
  app.main:app