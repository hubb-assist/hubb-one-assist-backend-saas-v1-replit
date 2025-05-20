"""
Arquivo principal para aplicação FastAPI
"""
import os
import json
from fastapi import FastAPI

# Importar o app principal
from app.main import app as main_app

# Para garantir que a aplicação tenha um endpoint raiz
@main_app.get("/")
async def root():
    """
    Endpoint raiz para health checks do deploy.
    """
    return {
        "status": "online",
        "version": "0.1.0",
        "app": "HUBB ONE Assist API"
    }

# Este é o objeto que o gunicorn vai usar
app = main_app