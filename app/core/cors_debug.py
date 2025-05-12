"""
Middleware de depuração CORS para identificar problemas de comunicação entre origens.
Pode ser ativado temporariamente no main.py para diagnosticar problemas com CORS.

Uso:
    from app.core.cors_debug import cors_debug_middleware
    
    # Adicionar middleware após o CORSMiddleware regular
    app.add_middleware(cors_debug_middleware)
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

# Configurar logger específico para CORS
cors_logger = logging.getLogger("cors_debug")
cors_logger.setLevel(logging.DEBUG)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
cors_logger.addHandler(console_handler)

class CORSDebugMiddleware(BaseHTTPMiddleware):
    """
    Middleware de diagnóstico para problemas CORS.
    Registra detalhes sobre requisições CORS e cabeçalhos relevantes.
    Use apenas temporariamente para diagnóstico.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Processa a requisição e registra informações de diagnóstico CORS.
        
        Args:
            request: Requisição FastAPI
            call_next: Próxima função middleware
            
        Returns:
            Response: Resposta HTTP
        """
        # Informações da requisição
        origin = request.headers.get("Origin", "Desconhecida")
        method = request.method
        path = request.url.path
        
        cors_logger.info(f"[CORS-DEBUG] Requisição recebida:")
        cors_logger.info(f"  Origem: {origin}")
        cors_logger.info(f"  Método: {method}")
        cors_logger.info(f"  Caminho: {path}")
        
        # Cabeçalhos importantes da requisição
        if request.headers.get("Cookie"):
            cors_logger.info(f"  Cookies presentes: Sim")
        else:
            cors_logger.warning(f"  Cookies presentes: Não - Possível problema de autenticação")
            
        # Log de cabeçalhos da requisição
        if method == "OPTIONS":
            cors_logger.info(f"  Preflight OPTIONS detectado")
            cors_logger.info(f"  Access-Control-Request-Method: {request.headers.get('Access-Control-Request-Method', 'Ausente')}")
            cors_logger.info(f"  Access-Control-Request-Headers: {request.headers.get('Access-Control-Request-Headers', 'Ausente')}")
        
        # Processar a requisição
        response = await call_next(request)
        
        # Verificar cabeçalhos CORS da resposta
        cors_logger.info(f"[CORS-DEBUG] Resposta enviada:")
        
        if "Access-Control-Allow-Origin" in response.headers:
            allow_origin = response.headers["Access-Control-Allow-Origin"]
            cors_logger.info(f"  Access-Control-Allow-Origin: {allow_origin}")
            
            # Verificar se a origem está autorizada
            if origin != "Desconhecida" and allow_origin != "*" and origin != allow_origin:
                cors_logger.error(f"  [ERRO] Origem {origin} não está na lista de origens permitidas: {allow_origin}")
        else:
            cors_logger.error(f"  [ERRO] Cabeçalho Access-Control-Allow-Origin está ausente!")
            
        # Verificar outros cabeçalhos importantes
        cors_logger.info(f"  Access-Control-Allow-Credentials: {response.headers.get('Access-Control-Allow-Credentials', 'Ausente')}")
        cors_logger.info(f"  Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'Ausente')}")
        cors_logger.info(f"  Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'Ausente')}")
        
        # Alertas críticos para problemas comuns
        if ("Access-Control-Allow-Credentials" not in response.headers or 
            response.headers["Access-Control-Allow-Credentials"] != "true"):
            cors_logger.error(f"  [ERRO CRÍTICO] Access-Control-Allow-Credentials não está definido como 'true'!")
            cors_logger.error(f"  Isso impedirá o envio de cookies e autenticação JWT!")
            
        if (method == "OPTIONS" and 
            "Access-Control-Allow-Methods" not in response.headers):
            cors_logger.error(f"  [ERRO] Preflight OPTIONS não retornou Access-Control-Allow-Methods!")
        
        return response

# Instância pré-configurada para uso direto
cors_debug_middleware = CORSDebugMiddleware