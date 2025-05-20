"""
Adaptador WSGI para FastAPI
Este arquivo cria um adaptador para que o Gunicorn (WSGI) possa servir uma aplicação FastAPI (ASGI)
"""

import uvicorn.workers

# Isso permite que o Gunicorn use o worker ASGI específico do Uvicorn
# para executar a aplicação FastAPI corretamente
# O UvicornWorker faz a ponte entre WSGI (Gunicorn) e ASGI (FastAPI)
class StandaloneApplication(uvicorn.workers.UvicornWorker):
    pass

# Esta é a aplicação FastAPI importada do módulo app.main
from app.main import app