"""
Este arquivo serve para iniciar a aplicação WSGI com Gunicorn
"""

# Importar a aplicação adaptada para WSGI
from wsgi import application as app