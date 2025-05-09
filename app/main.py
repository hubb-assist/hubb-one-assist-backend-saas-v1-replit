import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes_users import router as users_router
from app.core.config import settings
from app.db.session import create_tables

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="HUBB ONE - Assist SaaS API",
    # Configurar URLs para documentação
    docs_url=None,  # Desabilita o endpoint automático /docs 
    redoc_url=None,  # Desabilita o endpoint automático /redoc
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Adicionar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(users_router, prefix=settings.API_V1_STR)

# Endpoints personalizados para documentação
@app.get(f"{settings.API_V1_STR}/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Endpoint personalizado para Swagger UI"""
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get(f"{settings.API_V1_STR}/redoc", include_in_schema=False)
async def redoc_html():
    """Endpoint personalizado para ReDoc"""
    return get_redoc_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )

@app.get(f"{settings.API_V1_STR}/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    """Endpoint para retornar o esquema OpenAPI"""
    return JSONResponse(
        get_openapi(
            title=settings.PROJECT_NAME,
            version=settings.PROJECT_VERSION,
            description="HUBB ONE - Assist SaaS API",
            routes=app.routes,
        )
    )

@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização do aplicativo"""
    create_tables()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página inicial da API com links para documentação"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{settings.PROJECT_NAME}</title>
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
                <li><a href="{settings.API_V1_STR}/docs">{settings.API_V1_STR}/docs</a> - Swagger UI (documentação interativa)</li>
                <li><a href="{settings.API_V1_STR}/redoc">{settings.API_V1_STR}/redoc</a> - ReDoc (documentação alternativa)</li>
            </ul>
            <p class="info">A API retorna respostas JSON em todos os endpoints.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Endpoint de status para verificação de integridade
@app.get(f"{settings.API_V1_STR}/status")
async def status():
    """Endpoint simples para verificar se a API está online"""
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
