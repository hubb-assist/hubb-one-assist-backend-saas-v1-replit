"""
Proxy WSGI/ASGI usando a biblioteca a-wsgi para converter chamadas WSGI para ASGI
Esta é uma abordagem mais completa para permitir que o Gunicorn (WSGI) chame o FastAPI (ASGI)
"""

import os
import sys
import uvicorn
import asyncio
import logging
from urllib.parse import urlparse

# Adicione o caminho atual ao PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))

# Importar o adaptador ASGI/WSGI
from asgiref.wsgi import WsgiToAsgi

# Classe de fallback caso asgiref não esteja disponível (não deveria acontecer agora)
if not 'WsgiToAsgi' in locals():
    class WsgiToAsgi:
        def __init__(self, wsgi_app):
            self.wsgi_app = wsgi_app
        
        async def __call__(self, scope, receive, send):
            if scope["type"] != "http":
                return
            
            # Para requisições HTTP, simplesmente retorne uma mensagem
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", b"text/html")],
            })
            await send({
                "type": "http.response.body",
                "body": b"FastAPI is running but requires an ASGI server (Uvicorn)",
            })

# Importe o aplicativo FastAPI
from app.main import app as fastapi_app

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adaptador de página inicial
class HomePageAdapter:
    """
    Intercepta apenas a rota raiz (/) e exibe uma página HTML informativa.
    Todas as outras rotas são encaminhadas para o FastAPI.
    """
    
    def __init__(self, asgi_app):
        self.asgi_app = asgi_app
    
    async def __call__(self, scope, receive, send):
        # Verificar o tipo de requisição
        if scope["type"] != "http":
            return await self.asgi_app(scope, receive, send)
        
        # Verificar se é a rota raiz
        path = scope.get("path", "")
        if path == "/" or path == "":
            return await self._serve_home_page(scope, receive, send)
        
        # Se não for a rota raiz, encaminhar para o FastAPI
        return await self.asgi_app(scope, receive, send)
    
    async def _serve_home_page(self, scope, receive, send):
        """Serve a página HTML informativa"""
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
                    <p><strong>Nota técnica:</strong> Esta API está sendo executada com FastAPI e pode ser acessada
                    diretamente através dos endpoints listados acima.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Envie a resposta HTTP
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                (b"content-type", b"text/html"),
            ],
        })
        
        # Envie o corpo da resposta
        await send({
            "type": "http.response.body",
            "body": html.encode("utf-8"),
        })

# Função para criar o aplicativo ASGI
def create_asgi_app():
    """
    Cria um aplicativo ASGI que intercepta a rota raiz
    e encaminha todas as outras para o FastAPI
    """
    return HomePageAdapter(fastapi_app)

# Função para criar o aplicativo WSGI
def create_wsgi_app():
    """
    Cria um aplicativo WSGI que converte chamadas WSGI para ASGI
    """
    asgi_app = create_asgi_app()
    return WsgiToAsgi(asgi_app)

# Cria uma aplicação WSGI para uso com Gunicorn
application = create_wsgi_app()

# Atalho para o Gunicorn
app = application

# Ponto de entrada para execução direta
if __name__ == "__main__":
    # Quando executado diretamente, use o Uvicorn
    logger.info("Starting with Uvicorn...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)