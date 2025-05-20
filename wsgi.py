"""
Módulo WSGI para iniciar a aplicação através do adaptador
"""
from wsgi_to_asgi import WSGIMiddleware
from app.main import app

application = WSGIMiddleware(app)