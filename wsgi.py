"""
Adaptador WSGI funcional para FastAPI usando uvicorn workers
"""
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.main import app

# Para gunicorn funcionar com FastAPI, precisamos usar workers uvicorn
import uvicorn.workers

class UvicornWorker(uvicorn.workers.UvicornWorker):
    CONFIG_KWARGS = {"loop": "asyncio", "http": "h11", "lifespan": "on"}

# Exportar a aplicação
application = app