import os
import sys

# Adicione o caminho atual ao PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))

# Importe o aplicativo WSGI do novo arquivo wsgi_app.py
from wsgi_app import application

# Este é o objeto de aplicação WSGI para o Gunicorn
# 'application' é o nome da variável padrão que o Gunicorn procura
app = application