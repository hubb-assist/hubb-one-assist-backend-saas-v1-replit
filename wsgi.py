"""
Adaptador WSGI funcional para FastAPI usando uvicorn workers
"""
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.main import app

# Para gunicorn funcionar com FastAPI
application = app