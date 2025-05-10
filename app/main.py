"""
Aplicação principal FastAPI para o HUBB ONE Assist
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db.session import engine, Base, get_db
from app.db.models import User
from app.services.user_service import UserService
from app.api.routes_users import router as users_router

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Inicialização do FastAPI
app = FastAPI(
    title="HUBB ONE Assist API",
    description="Backend para o sistema HUBB ONE Assist",
    version="0.1.0",
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
app.include_router(users_router)

# Página inicial HTML
@app.get("/", response_class=HTMLResponse)
async def home():
    """
    Página inicial com informações sobre a API.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HUBB ONE Assist API</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }
            h1 { color: #333; }
            h2 { color: #555; margin-top: 30px; }
            p { margin-bottom: 15px; }
            code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
            pre { background: #f8f8f8; padding: 10px; border-radius: 5px; overflow-x: auto; }
            .container { margin-top: 20px; border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
            .info { color: blue; }
            .note { background: #ffffcc; padding: 10px; border-left: 4px solid #ffcc00; margin-top: 20px; }
            .endpoints { margin-top: 30px; }
            .endpoint { margin-bottom: 15px; }
            .method { display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; margin-right: 5px; }
            .get { background: #61affe; color: white; }
            .post { background: #49cc90; color: white; }
            .put { background: #fca130; color: white; }
            .delete { background: #f93e3e; color: white; }
        </style>
    </head>
    <body>
        <h1>HUBB ONE Assist API</h1>
        
        <div class="container">
            <p>Bem-vindo à API do HUBB ONE Assist!</p>
            
            <p>A API está rodando neste servidor. Você pode acessar:</p>
            
            <ul>
                <li><a href="/docs">/docs</a> - Documentação Swagger UI (interativa)</li>
                <li><a href="/redoc">/redoc</a> - Documentação ReDoc</li>
            </ul>
        </div>
        
        <h2>Endpoints Disponíveis</h2>
        
        <div class="endpoints">
            <div class="endpoint">
                <span class="method get">GET</span> <code>/users/</code> - Listar todos os usuários
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> <code>/users/{user_id}</code> - Obter um usuário específico
            </div>
            <div class="endpoint">
                <span class="method post">POST</span> <code>/users/</code> - Criar um novo usuário
            </div>
            <div class="endpoint">
                <span class="method put">PUT</span> <code>/users/{user_id}</code> - Atualizar um usuário existente
            </div>
            <div class="endpoint">
                <span class="method delete">DELETE</span> <code>/users/{user_id}</code> - Remover um usuário
            </div>
        </div>
        
        <div class="note">
            <p><strong>Nota:</strong> Esta API implementa operações CRUD básicas de usuários.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Rota de informações básicas da API
@app.get("/api-info")
async def api_info():
    """
    Retorna informações básicas sobre a API.
    """
    return {
        "name": "HUBB ONE Assist API",
        "version": "0.1.0",
        "description": "Backend para o sistema HUBB ONE Assist",
    }

# Inicialização do usuário admin padrão
@app.on_event("startup")
async def startup_event():
    """
    Inicializa o usuário admin no primeiro boot se não existir.
    """
    db = next(get_db())
    UserService.create_admin_user(db)