"""
Adaptador para permitir que o FastAPI (ASGI) funcione com Gunicorn (WSGI)
Usa o uvicorn.workers.UvicornWorker, que é um trabalhador do Gunicorn que pode lidar com aplicativos ASGI
"""
import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Registrar informações sobre o ambiente
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")

# Redirecionar para o arquivo main.py que importa a aplicação FastAPI do app.main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.main import app  # noqa

# Aplicação para Gunicorn
application = app