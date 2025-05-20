
"""
Arquivo principal para aplicação FastAPI
"""
from app.main import app as application

# Para compatibilidade com Gunicorn
app = application
