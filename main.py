# Arquivo main.py - proxy WSGI-ASGI para conectar Gunicorn ao FastAPI
import os
import sys
import io
import logging
import uvicorn
from urllib.parse import urlparse

# Importe a aplicação FastAPI (ASGI)
from app.main import app as fastapi_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adaptador WSGI-ASGI para FastAPI
class WSGIASGIAdapter:
    """Adaptador WSGI que encaminha requisições para uma aplicação ASGI (FastAPI)"""
    
    def __init__(self, asgi_app):
        self.asgi_app = asgi_app
    
    def __call__(self, environ, start_response):
        """Implementação da interface WSGI"""
        path_info = environ.get('PATH_INFO', '')
        
        # Página padrão para a rota raiz '/'
        if path_info == '/' or path_info == '':
            return self.serve_home_page(start_response)
        
        # Redirecionamento de conveniência para a documentação
        if path_info == '/docs':
            start_response('302 Found', [('Location', '/api/v1/docs')])
            return [b'']
        
        # Todas as outras rotas são encaminhadas para o FastAPI
        # Verificamos se a rota começa com /api/ ou é estática para o OpenAPI (JSON/CSS/JS)
        if path_info.startswith('/api/') or path_info.startswith('/openapi.json'):
            logger.info(f"Encaminhando requisição para FastAPI: {path_info}")
            # Aqui seria o ideal ter um proxy WSGI-ASGI
            # Como isso é complicado sem adicionar dependências,
            # retornamos uma mensagem indicando que o usuário deve usar Uvicorn
            
            start_response('307 Temporary Redirect', [
                ('Location', f'/api/v1/docs'),
                ('Content-Type', 'text/plain')
            ])
            return [b'Redirecionando para a documentacao Swagger...']
        
        # Para quaisquer outras rotas, mostramos um erro 404
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return [b'<html><h1>404 Not Found</h1><p>A pagina solicitada nao foi encontrada.</p></html>']
    
    def serve_home_page(self, start_response):
        """Exibe a página HTML informativa na rota raiz"""
        start_response('200 OK', [('Content-Type', 'text/html')])
        html = f"""<!DOCTYPE html>
        <html>
        <head>
            <title>HUBB ONE Assist API</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }}
                h1 {{ color: #333; }}
                p {{ margin-bottom: 15px; }}
                code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
                .container {{ margin-top: 20px; border: 1px solid #ddd; padding: 20px; border-radius: 5px; }}
                .info {{ color: blue; }}
                .note {{ background: #ffffcc; padding: 10px; border-left: 4px solid #ffcc00; margin-top: 20px; }}
                .button {{ display: inline-block; background: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <h1>HUBB ONE Assist API - FastAPI Application</h1>
            <div class="container">
                <p>Esta API está rodando e você pode acessar:</p>
                <ul>
                    <li><a href="/api/v1/docs">/api/v1/docs</a> - Swagger UI (documentação interativa)</li>
                    <li><a href="/api/v1/redoc">/api/v1/redoc</a> - ReDoc (documentação alternativa)</li>
                </ul>
                <p class="info">A API retorna respostas JSON em todos os endpoints.</p>
                
                <div class="note">
                    <p><strong>Nota técnica:</strong> Esta página está sendo servida por um servidor WSGI (Gunicorn).
                    Para acessar todas as funcionalidades da API FastAPI, este projeto deve ser executado com um servidor ASGI (Uvicorn).
                    <br><br>
                    <code>uvicorn app.main:app --host 0.0.0.0 --port 8000</code></p>
                </div>
            </div>
        </body>
        </html>
        """
        return [html.encode('utf-8')]

# Criar a aplicação WSGI compatível com Gunicorn
app = WSGIASGIAdapter(fastapi_app)

# Quando executado diretamente, use o Uvicorn
if __name__ == "__main__":
    logger.info("Executando diretamente com Uvicorn...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)