import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.main import app

# Para compatibilidade com Gunicorn, usar worker uvicorn
# Comando correto: gunicorn -k uvicorn.workers.UvicornWorker main:app
application = app