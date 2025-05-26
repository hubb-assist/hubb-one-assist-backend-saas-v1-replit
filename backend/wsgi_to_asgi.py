"""
Adaptador WSGI para ASGI para o FastAPI
"""
import asyncio
import typing

from app.main import app as asgi_app


class ASGItoWSGIAdapter:
    """
    Adapta um aplicativo ASGI (FastAPI) para a interface WSGI (Gunicorn)
    """
    
    def __init__(self, asgi_app):
        self.asgi_app = asgi_app
        
    def __call__(self, environ, start_response):
        """
        Função de chamada compatível com WSGI
        """
        # Criar o escopo ASGI a partir do ambiente WSGI
        scope = self._convert_wsgi_environ_to_asgi_scope(environ)
        
        # Preparar os objetos de resposta
        response_started = False
        response_status = None
        response_headers = None
        response_chunks = []
        
        # Função de recepção ASGI (simulada para WSGI)
        async def receive():
            """Simula a recepção ASGI"""
            body = environ.get('wsgi.input')
            if body:
                return {
                    'type': 'http.request',
                    'body': body.read(),
                    'more_body': False
                }
            return {
                'type': 'http.request',
                'body': b'',
                'more_body': False
            }
        
        # Função de envio ASGI
        async def send(message):
            """
            Processa mensagens ASGI e as adapta para WSGI
            """
            nonlocal response_started, response_status, response_headers, response_chunks
            
            message_type = message['type']
            
            if message_type == 'http.response.start':
                response_started = True
                response_status = message['status']
                response_headers = [(name.decode('latin1'), value.decode('latin1')) 
                                    for name, value in message.get('headers', [])]
                
            elif message_type == 'http.response.body':
                body = message.get('body', b'')
                if body:
                    response_chunks.append(body)
        
        # Executar o aplicativo ASGI
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self.asgi_app(scope, receive, send))
        finally:
            loop.close()
        
        # Iniciar a resposta WSGI
        status = f"{response_status} OK"
        start_response(status, response_headers or [])
        
        # Retornar o corpo da resposta
        return response_chunks or [b'']
    
    def _convert_wsgi_environ_to_asgi_scope(self, environ):
        """
        Converte o ambiente WSGI em um escopo ASGI
        """
        # Construir os cabeçalhos
        headers = []
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                name = key[5:].replace('_', '-').lower().encode('latin1')
                headers.append((name, str(value).encode('latin1')))
        
        if environ.get('CONTENT_TYPE'):
            headers.append((b'content-type', environ['CONTENT_TYPE'].encode('latin1')))
            
        if environ.get('CONTENT_LENGTH'):
            headers.append((b'content-length', environ['CONTENT_LENGTH'].encode('latin1')))
        
        # Construir o escopo ASGI
        return {
            'type': 'http',
            'asgi': {
                'version': '3.0',
                'spec_version': '2.0',
            },
            'http_version': environ.get('SERVER_PROTOCOL', 'HTTP/1.1').replace('HTTP/', ''),
            'method': environ['REQUEST_METHOD'],
            'scheme': environ.get('wsgi.url_scheme', 'http'),
            'path': environ['PATH_INFO'],
            'raw_path': environ['PATH_INFO'].encode('latin1'),
            'query_string': environ.get('QUERY_STRING', '').encode('latin1'),
            'root_path': environ.get('SCRIPT_NAME', ''),
            'headers': headers,
            'client': (environ.get('REMOTE_ADDR', '127.0.0.1'), int(environ.get('REMOTE_PORT', 0))),
            'server': (environ.get('SERVER_NAME', 'localhost'), int(environ.get('SERVER_PORT', 8000))),
        }


# Criar o aplicativo WSGI adaptado
application = ASGItoWSGIAdapter(asgi_app)