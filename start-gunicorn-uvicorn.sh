#!/bin/bash

# Script para iniciar o FastAPI com Gunicorn usando UvicornWorker
# Este é o método recomendado para produção

gunicorn -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5000 \
  --access-logfile - \
  main:app