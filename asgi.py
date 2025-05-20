"""
Módulo ASGI para iniciar a aplicação FastAPI com Uvicorn
"""
from app.main import app

# Exportar a aplicação ASGI para o Uvicorn
application = app