"""
Adaptador WSGI para aplicação FastAPI para o deploy do Replit
"""
import asyncio
from urllib.parse import urlparse
import typing

# Importar a aplicação FastAPI
from app.main import app as asgi_app


def to_asgi_app(app):
    """
    Converte uma aplicação ASGI para WSGI
    """
    async def app_wrapper(scope, receive, send):
        await app(scope, receive, send)
    
    def wsgi_app(environ, start_response):
        # Extrair informações do ambiente WSGI
        path = environ['PATH_INFO']
        method = environ['REQUEST_METHOD']
        query_string = environ.get('QUERY_STRING', '').encode('utf-8')
        
        # Criar o escopo ASGI
        scope = {
            'type': 'http',
            'asgi': {
                'version': '3.0',
                'spec_version': '2.0',
            },
            'method': method,
            'path': path,
            'raw_path': path.encode('utf-8'),
            'query_string': query_string,
            'headers': [],
        }
        
        # Converter headers
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-').lower().encode('utf-8')
                header_value = value.encode('utf-8')
                scope['headers'].append((header_name, header_value))
        
        # Resposta
        response_status = None
        response_headers = None
        response_body = []
        
        # Função para receber dados
        async def receive():
            return {
                'type': 'http.request',
                'body': b'',
                'more_body': False,
            }
        
        # Função para enviar dados
        async def send(message):
            nonlocal response_status, response_headers, response_body
            
            if message['type'] == 'http.response.start':
                response_status = message['status']
                response_headers = [(name.decode('utf-8'), value.decode('utf-8')) 
                                   for name, value in message.get('headers', [])]
            
            elif message['type'] == 'http.response.body':
                response_body.append(message.get('body', b''))
        
        # Executar a aplicação ASGI
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(app_wrapper(scope, receive, send))
        finally:
            loop.close()
        
        # Iniciar a resposta
        status = f"{response_status} OK"
        start_response(status, response_headers or [])
        
        # Retornar o corpo da resposta
        return response_body
    
    return wsgi_app


# Criar a aplicação WSGI
application = to_asgi_app(asgi_app)