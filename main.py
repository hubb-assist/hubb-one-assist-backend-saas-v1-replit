"""
Arquivo principal para aplicação FastAPI

Este arquivo importa a instância app do módulo principal (app.main)
para ser usado pelo Gunicorn com UvicornWorker ou diretamente pelo Uvicorn.
"""

from app.main import app