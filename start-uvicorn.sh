#!/bin/bash

# Script para iniciar o FastAPI com Uvicorn
uvicorn main:app --host 0.0.0.0 --port 5000 --reload