"""
Proxy WSGI para encaminhar solicitações ao FastAPI.

Este módulo serve como uma camada de adaptação entre o servidor WSGI (Gunicorn)
e a aplicação ASGI (FastAPI), para permitir uma experiência de desenvolvimento
mais amigável no Replit.

Em produção, o ideal seria usar diretamente o servidor ASGI (Uvicorn).
"""
import os
import sys
import logging
import urllib.request
import urllib.error
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL do servidor ASGI (Uvicorn) rodando na porta 8000
ASGI_SERVER_URL = "http://localhost:8000"

def create_proxy_app():
    """
    Cria uma aplicação WSGI que:
    1. Serve uma página HTML informativa no caminho raiz (/)
    2. Tenta encaminhar solicitações para caminhos que começam com /api/ para o Uvicorn
    3. Fornece feedback se o Uvicorn não estiver disponível
    """
    
    def proxy_app(environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        
        # Servir página HTML informativa na raiz
        if path_info == '/' or path_info == '':
            return serve_home_page(start_response)
        
        # Redirecionamento para a documentação
        if path_info == '/docs':
            start_response('302 Found', [('Location', '/api/v1/docs')])
            return [b'Redirecionando...']
        
        # Para solicitações de API, tente encaminhar para o Uvicorn
        if path_info.startswith('/api/') or path_info.startswith('/openapi.json'):
            try:
                # Tente fazer uma solicitação para o servidor Uvicorn
                target_url = f"{ASGI_SERVER_URL}{path_info}"
                
                # Log para debug
                logger.info(f"Tentando proxy para: {target_url}")
                
                # Tente fazer uma solicitação simples para o servidor Uvicorn
                response = urllib.request.urlopen(target_url)
                
                # Se chegou aqui, o Uvicorn está disponível, então faça o redirecionamento
                start_response('302 Found', [('Location', target_url)])
                return [b'Redirecionando para o servidor Uvicorn...']
                
            except (urllib.error.URLError, ConnectionRefusedError) as e:
                # O servidor Uvicorn não está disponível
                logger.warning(f"Falha ao conectar ao Uvicorn: {e}")
                return serve_uvicorn_not_running(start_response)
        
        # Para qualquer outro caminho, mostrar um 404
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return [b'<html><body><h1>404 Not Found</h1><p>A pagina solicitada nao existe.</p></body></html>']
    
    return proxy_app

def serve_home_page(start_response):
    """Exibe a página HTML informativa na rota raiz"""
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
            .warning { color: #f33; }
            .note { background: #ffffcc; padding: 10px; border-left: 4px solid #ffcc00; margin-top: 20px; }
            .button { display: inline-block; background: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px; }
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
                <p><strong>Nota técnica:</strong> Esta página é servida por um servidor WSGI (Gunicorn).
                Para ter acesso completo à API FastAPI, certifique-se de que o servidor Uvicorn esteja rodando:
                <br><br>
                <code>python -m uvicorn app.main:app --host 0.0.0.0 --port 8000</code></p>
            </div>
        </div>
    </body>
    </html>
    """
    return [html.encode('utf-8')]

def serve_uvicorn_not_running(start_response):
    """Exibe uma página de erro quando o Uvicorn não está rodando"""
    start_response('503 Service Unavailable', [('Content-Type', 'text/html')])
    html = """<!DOCTYPE html>
    <html>
    <head>
        <title>Servidor ASGI Não Disponível</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }
            h1 { color: #c00; }
            .container { margin-top: 20px; border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
            .error { color: #c00; }
            code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
            pre { background: #f8f8f8; padding: 10px; overflow: auto; border-radius: 3px; }
            .button { display: inline-block; background: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px; margin-top: 15px; }
        </style>
    </head>
    <body>
        <h1>Servidor ASGI (Uvicorn) Não Encontrado</h1>
        <div class="container">
            <p class="error">O servidor Uvicorn não está em execução na porta 8000.</p>
            <p>Para acessar a API FastAPI e sua documentação, você precisa iniciar o servidor Uvicorn:</p>
            
            <pre>python -m uvicorn app.main:app --host 0.0.0.0 --port 8000</pre>
            
            <p>Uma vez que o Uvicorn esteja em execução, você poderá acessar:</p>
            <ul>
                <li>A API: <code>http://localhost:8000/api/...</code></li>
                <li>Swagger UI: <code>http://localhost:8000/api/v1/docs</code></li>
                <li>ReDoc: <code>http://localhost:8000/api/v1/redoc</code></li>
            </ul>
            
            <a href="/" class="button">Voltar para a página inicial</a>
        </div>
    </body>
    </html>
    """
    return [html.encode('utf-8')]

# Criar a aplicação proxy
application = create_proxy_app()