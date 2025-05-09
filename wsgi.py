"""
Arquivo para adaptar a aplicação ASGI (FastAPI) para WSGI (Gunicorn)
"""

import asyncio
import io
import sys
import typing
from contextlib import AsyncExitStack
from typing import List, Optional, Tuple, Dict

from app.main import app as fastapi_app


class WsgiToAsgiAdapter:
    """
    Adaptador que permite executar uma aplicação ASGI (FastAPI) como uma aplicação WSGI (Gunicorn).
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        """
        Interface WSGI.
        """
        # Preparar evento 'scope'
        scope = self._prepare_scope(environ)
        
        # Criar uma resposta para armazenar os dados
        response = {}
        response_started = False
        body_chunks = []
        
        # Função assíncrona para receber a resposta
        async def receive():
            return {
                "type": "http.request",
                "body": environ.get("wsgi.input", io.BytesIO()).read(),
                "more_body": False,
            }
        
        # Função assíncrona para enviar a resposta
        async def send(event):
            nonlocal response_started, body_chunks
            
            if event["type"] == "http.response.start":
                response["status"] = event["status"]
                response["headers"] = event.get("headers", [])
                response_started = True
            
            elif event["type"] == "http.response.body":
                body_chunks.append(event.get("body", b""))
        
        # Executar a aplicação ASGI
        async def call_asgi():
            await self.app(scope, receive, send)
        
        # Criar um novo loop de eventos e executar a aplicação
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(call_asgi())
        finally:
            loop.close()
        
        # Preparar a resposta para o WSGI
        status = str(response.get("status", 500))
        headers = response.get("headers", [])
        # Convertendo cabeçalhos de bytes para strings
        wsgi_headers = [(k.decode("latin1"), v.decode("latin1")) if isinstance(k, bytes) else (k, v) 
                        for k, v in headers]
        
        # Chamar a função start_response
        start_response(f"{status} ", wsgi_headers)
        
        # Retornar o corpo da resposta
        if body_chunks:
            return [chunk for chunk in body_chunks if chunk]
        return [b""]
    
    def _prepare_scope(self, environ):
        """
        Converter os cabeçalhos HTTP do WSGI para o formato ASGI.
        """
        path = environ.get("PATH_INFO", "")
        if not path.startswith("/"):
            path = "/" + path
        
        raw_query = environ.get("QUERY_STRING", "")
        query_string = raw_query.encode("ascii")
        
        # Obter os cabeçalhos HTTP do WSGI
        headers = []
        for key, value in environ.items():
            if key.startswith("HTTP_"):
                header_name = key[5:].replace("_", "-").lower().encode("ascii")
                header_value = value.encode("ascii")
                headers.append((header_name, header_value))
        
        # Cabeçalhos especiais
        if environ.get("CONTENT_TYPE"):
            headers.append((b"content-type", environ["CONTENT_TYPE"].encode("ascii")))
        if environ.get("CONTENT_LENGTH"):
            headers.append((b"content-length", environ["CONTENT_LENGTH"].encode("ascii")))
        
        # Criar o escopo ASGI
        scope = {
            "type": "http",
            "asgi": {
                "version": "3.0",
                "spec_version": "2.0",
            },
            "http_version": environ.get("SERVER_PROTOCOL", "HTTP/1.1").split("/")[1],
            "method": environ.get("REQUEST_METHOD", "GET"),
            "scheme": environ.get("wsgi.url_scheme", "http"),
            "path": path,
            "raw_path": path.encode("ascii"),
            "query_string": query_string,
            "headers": headers,
            "client": (environ.get("REMOTE_ADDR", ""), int(environ.get("REMOTE_PORT", 0))),
            "server": (environ.get("SERVER_NAME", ""), int(environ.get("SERVER_PORT", 0))),
        }
        
        return scope


# Criar o adaptador WSGI para a aplicação FastAPI
application = WsgiToAsgiAdapter(fastapi_app)