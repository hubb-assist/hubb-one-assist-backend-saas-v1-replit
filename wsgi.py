import os
import sys

# Adicione o caminho atual ao PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))

# Importe a aplicação WSGI proxy que serve a página inicial e redireciona para o Uvicorn
from app.wsgi_proxy import application

# Este é o objeto de aplicação WSGI para o Gunicorn
# 'application' é o nome da variável padrão que o Gunicorn procura
app = application