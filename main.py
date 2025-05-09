# Arquivo main.py - Ponto de entrada simplificado
import uvicorn
import logging
import subprocess
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função simples WSGI para quando o Gunicorn tentar carregar este arquivo
def app(environ, start_response):
    """
    Retorna uma página HTML informativa que instrui sobre a necessidade de usar o Uvicorn
    """
    start_response('200 OK', [('Content-Type', 'text/html')])
    html = """<!DOCTYPE html>
    <html>
    <head>
        <title>HUBB ONE Assist API</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }
            h1 { color: #333; }
            p { margin-bottom: 15px; }
            code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
            .container { margin-top: 20px; border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
            .info { color: blue; }
            .warning { color: #ff4500; }
            .note { background: #ffffcc; padding: 10px; border-left: 4px solid #ffcc00; margin-top: 20px; }
            .button { display: inline-block; background: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px; }
        </style>
    </head>
    <body>
        <h1>HUBB ONE Assist API</h1>
        <div class="container">
            <p class="warning">A API FastAPI deve ser executada com Uvicorn, não com Gunicorn.</p>
            
            <p>Para acessar a API e sua documentação, execute:</p>
            <code>./start-fastapi.sh</code>
            <p>ou</p>
            <code>uvicorn app.main:app --host 0.0.0.0 --port 8000</code>
            
            <p>Depois disso, você poderá acessar:</p>
            <ul>
                <li>API Root: <a href="http://localhost:8000/">http://localhost:8000/</a></li>
                <li>Swagger UI: <a href="http://localhost:8000/api/v1/docs">http://localhost:8000/api/v1/docs</a></li>
                <li>ReDoc: <a href="http://localhost:8000/api/v1/redoc">http://localhost:8000/api/v1/redoc</a></li>
            </ul>
        </div>
    </body>
    </html>
    """
    return [html.encode('utf-8')]

# Quando executado diretamente, inicie o servidor Uvicorn
if __name__ == "__main__":
    logger.info("Iniciando o servidor Uvicorn para a API FastAPI...")
    
    try:
        # Tente iniciar o aplicativo FastAPI com Uvicorn
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        logger.error(f"Erro ao iniciar Uvicorn: {e}")
        print(f"ERRO: Falha ao iniciar o servidor Uvicorn: {e}")
        sys.exit(1)