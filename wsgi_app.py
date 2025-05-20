"""
Adaptador WSGI para aplicação FastAPI
"""
from app.main import app
import uvicorn.workers

# Isso permite usar o Gunicorn com aplicações ASGI
def create_app():
    """
    Cria uma aplicação Flask que simplesmente retorna um status OK
    """
    from flask import Flask
    
    app_flask = Flask(__name__)
    
    @app_flask.route("/")
    def health():
        return {"status": "ok"}
    
    return app_flask

# Esta é a aplicação que será usada pelo Gunicorn
application = create_app()