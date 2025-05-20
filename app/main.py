"""
Aplicação principal FastAPI para o HUBB ONE Assist
"""
import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.routes.insumos import router as insumos_router
from app.core.security import get_password_hash

# Importar todos os routers originais
from app.api.routes_auth import router as auth_router
from app.api.routes_users import router as users_router
from app.api.routes_segments import router as segments_router
from app.api.routes_modules import router as modules_router
from app.api.routes_plans import router as plans_router
from app.api.routes_subscribers import router as subscribers_router
from app.api.routes_patients import router as patients_router
from app.api.routes_patients_ddd import router as patients_ddd_router
from app.api.routes_api_compatibility import router as api_compatibility_router
from app.api.routes_public_segments import router as public_segments_router
from app.api.routes_public_plans import router as public_plans_router
from app.api.routes_public_subscribers import router as public_subscribers_router

# Criar aplicação FastAPI
app = FastAPI(
    title="HUBB ONE Assist API",
    description="API para o sistema HUBB ONE Assist",
    version="1.0.0",
)

# Configurar CORS
origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas originais
app.include_router(auth_router, prefix="/auth", tags=["autenticação"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(segments_router, prefix="/segments", tags=["segments"])
app.include_router(modules_router, prefix="/modules", tags=["modules"])
app.include_router(plans_router, prefix="/plans", tags=["plans"])
app.include_router(subscribers_router, prefix="/subscribers", tags=["subscribers"])
app.include_router(patients_router, prefix="/patients", tags=["patients"])
app.include_router(patients_ddd_router, prefix="/patients-ddd", tags=["patients-ddd"])
app.include_router(api_compatibility_router, tags=["external-api-compatibility"])

# Incluir rotas públicas
app.include_router(
    public_segments_router, prefix="/public/segments", tags=["public"]
)
app.include_router(
    public_plans_router, prefix="/public/plans", tags=["public"]
)
app.include_router(
    public_subscribers_router, prefix="/public/subscribers", tags=["public"]
)

# Incluir novas rotas DDD
app.include_router(insumos_router, prefix="/insumos", tags=["insumos"])

@app.get("/", response_class=HTMLResponse)
async def home():
    """
    Página inicial com informações sobre a API e regras do projeto.
    """
    html_content = """
    <html>
        <head>
            <title>HUBB ONE Assist API</title>
            <style>
                body {
                    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    padding: 2rem;
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: #f5f5f5;
                    color: #333;
                }
                h1, h2, h3 {
                    color: #2c3e50;
                }
                a {
                    color: #3498db;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
                .container {
                    background-color: white;
                    padding: 2rem;
                    border-radius: 5px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .footer {
                    margin-top: 2rem;
                    font-size: 0.9rem;
                    color: #7f8c8d;
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>HUBB ONE Assist API</h1>
                <p>Bem-vindo à API do sistema HUBB ONE Assist.</p>
                
                <h2>Links úteis</h2>
                <ul>
                    <li><a href="/docs">Documentação da API (Swagger)</a></li>
                    <li><a href="/redoc">Documentação alternativa (ReDoc)</a></li>
                </ul>
                
                <h2>Recursos disponíveis</h2>
                <ul>
                    <li><a href="/insumos">Gerenciamento de Insumos</a></li>
                </ul>
            </div>
            <div class="footer">
                <p>&copy; 2025 HUBB ONE Assist. Todos os direitos reservados.</p>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/info")
async def api_info():
    """
    Retorna informações básicas sobre a API.
    """
    return {
        "name": "HUBB ONE Assist API",
        "version": "1.0.0",
        "description": "API para o sistema HUBB ONE Assist",
    }

@app.get("/api/config.js")
async def api_config_js():
    """
    Serve o arquivo de configuração da API para o frontend.
    Este endpoint foi criado para resolver o erro "Unexpected token '<'"
    quando o navegador tenta carregar um arquivo JavaScript mas recebe HTML.
    """
    content = f"""
    // API Configuration
    window.API_CONFIG = {{
        BASE_URL: '{os.environ.get("API_BASE_URL", "http://localhost:5000")}',
        VERSION: '1.0.0',
    }};
    """
    return Response(content=content, media_type="application/javascript")

@app.on_event("startup")
async def startup_event():
    """
    Inicializa o usuário admin no primeiro boot se não existir.
    """
    # Esta função será chamada na inicialização da aplicação
    pass