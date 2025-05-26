"""
Middleware especial para corrigir problemas de CORS 
em rotas específicas, como /subscribers/
"""

import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from typing import Callable

# Configurar logger
cors_fixer_logger = logging.getLogger("cors_fixer")
cors_fixer_logger.setLevel(logging.DEBUG)

class CORSFixerMiddleware(BaseHTTPMiddleware):
    """
    Middleware especial para garantir que headers CORS 
    sejam mantidos mesmo em caso de erros ou redirecionamentos.
    
    Também trata rotas específicas que o frontend pode tentar acessar
    de forma incorreta ou inconsistente.
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        """
        Processa a requisição e garante headers CORS.
        
        Args:
            request: Requisição FastAPI
            call_next: Próxima função middleware
            
        Returns:
            Response: Resposta HTTP com headers CORS
        """
        # Captura a origem para usar nos headers de resposta
        origin = request.headers.get("Origin", "*")
        path = request.url.path
        
        # Verifica se a requisição é para /external-api/subscribers 
        # ou outra rota incorreta que o frontend possa tentar usar
        if path.startswith("/external-api/subscribers"):
            # Log da correção
            cors_fixer_logger.info(f"Redirecionando /external-api/subscribers para /subscribers/")
            
            # Retorna uma resposta direta (evita redirecionamento 307)
            return JSONResponse(
                status_code=400,
                content={
                    "detail": "URL incorreta. Use /subscribers/ em vez de /external-api/subscribers"
                },
                headers={
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With"
                }
            )
            
        # Para rotas /api/subscribers/ que podem tentar fallback
        if path.startswith("/api/subscribers"):
            # Log da correção
            cors_fixer_logger.info(f"Redirecionando /api/subscribers para /subscribers/")
            
            # Retorna uma resposta direta (evita redirecionamento 307)
            return JSONResponse(
                status_code=400,
                content={
                    "detail": "URL incorreta. Use /subscribers/ em vez de /api/subscribers"
                },
                headers={
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With"
                }
            )
            
        # Se não for uma rota especial, continua a requisição normal
        try:
            response = await call_next(request)
            
            # Para TODAS as rotas /subscribers/ (mesmo sem erro) ou qualquer erro 500/404
            if path.startswith("/subscribers/") or response.status_code >= 400:
                cors_fixer_logger.warning(f"Resposta {response.status_code} em {path}, adicionando headers CORS")
                
                # Adiciona headers CORS para garantir que o frontend receba-os sempre
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
                
            return response
            
        except Exception as e:
            # Se ocorrer uma exceção, garante que o erro seja retornado com headers CORS
            cors_fixer_logger.error(f"Exceção em {path}: {str(e)}")
            
            return JSONResponse(
                status_code=500,
                content={"detail": "Erro interno do servidor"},
                headers={
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With"
                }
            )

# Instância pronta para uso
cors_fixer_middleware = CORSFixerMiddleware