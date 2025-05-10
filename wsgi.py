"""
Módulo WSGI para iniciar a aplicação a partir de main.py
"""
from main import app

# Exportar a aplicação WSGI para o Gunicorn
application = app