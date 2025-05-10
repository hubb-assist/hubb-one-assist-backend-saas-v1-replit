"""
Aplicação principal FastAPI para o HUBB ONE Assist
"""

import os
from pathlib import Path
import markdown

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from app.db.session import engine, Base, get_db
from app.db.models import User, Segment, Module, Plan, PlanModule, Subscriber
from app.services.user_service import UserService
from app.api.routes_users import router as users_router
from app.api.routes_segments import router as segments_router
from app.api.routes_modules import router as modules_router
from app.api.routes_plans import router as plans_router
from app.api.routes_auth import router as auth_router
from app.api.routes_subscribers import router as subscribers_router
from app.api.routes_public_segments import router as public_segments_router
from app.api.routes_public_plans import router as public_plans_router

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Inicialização do FastAPI
app = FastAPI(
    title="HUBB ONE Assist API",
    description="Backend para o sistema HUBB ONE Assist",
    version="0.1.0",
)

# Middleware para redirecionar HTTP para HTTPS
@app.middleware("http")
async def force_https(request: Request, call_next):
    """
    Middleware para garantir que todas as requisições sejam via HTTPS.
    Se uma requisição for detectada como HTTP, redireciona para HTTPS.
    
    Args:
        request: Requisição HTTP
        call_next: Próxima função na cadeia de middlewares
        
    Returns:
        Response: Redirecionamento ou resposta da próxima função
    """
    try:
        # Verificar o protocolo via cabeçalho X-Forwarded-Proto (comum em proxies como Replit/Vercel)
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "")
        host = request.headers.get("Host", "")
        
        # Se o protocolo for HTTP e não for localhost, redirecionar para HTTPS
        if forwarded_proto == "http" and not host.startswith("localhost"):
            url = request.url
            https_url = f"https://{host}{url.path}"
            if url.query:
                https_url = f"{https_url}?{url.query}"
            
            return RedirectResponse(https_url, status_code=301)
        
        # Continuar com a requisição original
        return await call_next(request)
    except Exception as e:
        # Registrar o erro para diagnóstico, mas permitir que a requisição continue
        print(f"Erro no middleware HTTPS: {str(e)}")
        # Continuar mesmo se houver um erro no middleware
        return await call_next(request)

# Adicionar middleware CORS com origens específicas (não pode usar * com credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Frontend Vite local
        "http://localhost:3000",  # Frontend React padrão
        "https://32c76b88-78ce-48ad-9c13-04975e5e14a3-00-12ynk9jfvcfqw.worf.replit.dev",  # URL temporário do Replit
        "https://977761fe-66ad-4e57-b1d5-f3356eb27515-00-1yp0n9cqd8r5p.spock.replit.dev",  # Frontend específico mencionado
        "https://977761fe-66ad-4e57-b1d5-f3356eb27515-00-1yp0n9cqd8r5p.replit.dev",  # Frontend específico sem subdomínio
        "https://hubb-one-assist-v1-frontend-replit.replit.app",  # Nome da app do frontend no Replit
        "https://hubb-one-assist-front-hubb-one.replit.app",  # URL de produção do frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Incluir routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(segments_router)
app.include_router(modules_router)
app.include_router(plans_router)
app.include_router(subscribers_router)

# Incluir routers públicos (sem autenticação)
app.include_router(public_segments_router)
app.include_router(public_plans_router)

# Página inicial HTML
@app.get("/", response_class=HTMLResponse)
async def home():
    """
    Página inicial com informações sobre a API e regras do projeto.
    """
    # Ler arquivo rules.md
    rules_file = Path.cwd().parent / 'rules.md'
    
    # Inicializar o conteúdo das regras
    rules_html = ""
    
    # Verificar se o arquivo existe
    try:
        with open(rules_file, 'r', encoding='utf-8') as f:
            rules_content = f.read()
            # Converter markdown para HTML
            rules_html = markdown.markdown(
                rules_content,
                extensions=[]
            )
    except Exception as e:
        rules_html = f"<div class='warning'><p>Não foi possível carregar as regras do projeto: {str(e)}</p></div>"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HUBB ONE Assist API</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 900px; margin: 0 auto; color: #333; }}
            h1 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            h2 {{ color: #444; margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
            h3 {{ color: #555; }}
            p {{ margin-bottom: 15px; }}
            code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-family: monospace; }}
            pre {{ background: #f8f8f8; padding: 10px; border-radius: 5px; overflow-x: auto; font-family: monospace; }}
            .container {{ margin-top: 20px; border: 1px solid #ddd; padding: 20px; border-radius: 5px; background-color: #fafafa; }}
            .info {{ color: #0066cc; }}
            .note {{ background: #ffffcc; padding: 10px; border-left: 4px solid #ffcc00; margin: 20px 0; }}
            .warning {{ background: #ffe6e6; padding: 10px; border-left: 4px solid #ff6666; margin: 20px 0; }}
            .endpoints {{ margin-top: 30px; }}
            .endpoint {{ margin-bottom: 15px; }}
            .method {{ display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; margin-right: 5px; }}
            .get {{ background: #61affe; color: white; }}
            .post {{ background: #49cc90; color: white; }}
            .put {{ background: #fca130; color: white; }}
            .delete {{ background: #f93e3e; color: white; }}
            .tab-container {{ overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; border-radius: 5px 5px 0 0; }}
            .tab-container button {{ background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 14px 16px; transition: 0.3s; }}
            .tab-container button:hover {{ background-color: #ddd; }}
            .tab-container button.active {{ background-color: #5c95ff; color: white; }}
            .tab-content {{ display: none; padding: 20px; border: 1px solid #ccc; border-top: none; border-radius: 0 0 5px 5px; }}
            .tab-content.active {{ display: block; }}
            table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
            th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            tr:hover {{ background-color: #f5f5f5; }}
            blockquote {{ margin: 15px 0; padding: 10px 20px; background-color: #f9f9f9; border-left: 5px solid #ccc; }}
            .emoji {{ font-size: 1.2em; }}
            ul, ol {{ padding-left: 25px; }}
            li {{ margin-bottom: 8px; }}
        </style>
        <script>
            function openTab(evt, tabName) {{
                var i, tabcontent, tablinks;
                tabcontent = document.getElementsByClassName("tab-content");
                for (i = 0; i < tabcontent.length; i++) {{
                    tabcontent[i].style.display = "none";
                }}
                tablinks = document.getElementsByClassName("tablinks");
                for (i = 0; i < tablinks.length; i++) {{
                    tablinks[i].className = tablinks[i].className.replace(" active", "");
                }}
                document.getElementById(tabName).style.display = "block";
                evt.currentTarget.className += " active";
            }}
            
            // Função para abrir a primeira aba por padrão quando a página carregar
            window.onload = function() {{
                document.getElementsByClassName("tablinks")[0].click();
            }};
        </script>
    </head>
    <body>
        <h1>HUBB ONE Assist API</h1>
        
        <div class="tab-container">
            <button class="tablinks" onclick="openTab(event, 'api-info')">Informações da API</button>
            <button class="tablinks" onclick="openTab(event, 'project-rules')">Regras do Projeto</button>
            <button class="tablinks" onclick="openTab(event, 'endpoints')">Endpoints</button>
        </div>
        
        <div id="api-info" class="tab-content">
            <div class="container">
                <h2>Bem-vindo à API do HUBB ONE Assist!</h2>
                <p>Esta API fornece serviços para o sistema HUBB ONE Assist, uma plataforma de assistência e gerenciamento.</p>
                
                <p>A API está rodando neste servidor. Você pode acessar:</p>
                
                <ul>
                    <li><a href="/docs" target="_blank">/docs</a> - Documentação Swagger UI (interativa)</li>
                    <li><a href="/redoc" target="_blank">/redoc</a> - Documentação ReDoc</li>
                </ul>
                
                <div class="note">
                    <p><strong>Módulos Implementados:</strong></p>
                    <ul>
                        <li><strong>Usuários</strong> - CRUD completo para gerenciamento de usuários</li>
                        <li><strong>Segmentos</strong> - Gerenciamento de segmentos de negócio</li>
                        <li><strong>Módulos</strong> - Gerenciamento de módulos funcionais do sistema</li>
                        <li><strong>Planos</strong> - Gerenciamento de planos com módulos vinculados</li>
                        <li><strong>Assinantes</strong> - Gerenciamento de assinantes do sistema</li>
                    </ul>
                </div>
                
                <div class="note">
                    <p><strong>Rotas Públicas:</strong></p>
                    <p>Para facilitar o processo de onboarding, as seguintes rotas estão disponíveis sem autenticação:</p>
                    <ul>
                        <li><code>/public/segments</code> - Lista todos os segmentos ativos</li>
                        <li><code>/public/plans</code> - Lista todos os planos ativos</li>
                        <li><code>/public/plans/[UUID]</code> - Obtém detalhes de um plano ativo específico</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div id="project-rules" class="tab-content">
            {rules_html}
        </div>
        
        <div id="endpoints" class="tab-content">
            <h2>Endpoints Disponíveis</h2>
            
            <div class="endpoints">
                <h3>Usuários do Sistema</h3>
                <div class="endpoint">
                    <span class="method get">GET</span> <code>/users/</code> - Listar todos os usuários (com paginação e filtros)
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> <code>/users/{{user_id}}</code> - Obter um usuário específico
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> <code>/users/</code> - Criar um novo usuário
                </div>
                <div class="endpoint">
                    <span class="method put">PUT</span> <code>/users/{{user_id}}</code> - Atualizar um usuário existente
                </div>
                <div class="endpoint">
                    <span class="method delete">DELETE</span> <code>/users/{{user_id}}</code> - Remover um usuário
                </div>
                
                <h3>Assinantes</h3>
                <div class="endpoint">
                    <span class="method get">GET</span> <code>/subscribers/</code> - Listar todos os assinantes (com paginação e filtros)
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> <code>/subscribers/{{subscriber_id}}</code> - Obter um assinante específico
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> <code>/subscribers/</code> - Criar um novo assinante (também cria um usuário DONO_ASSINANTE)
                </div>
                <div class="endpoint">
                    <span class="method put">PUT</span> <code>/subscribers/{{subscriber_id}}</code> - Atualizar um assinante existente
                </div>
                <div class="endpoint">
                    <span class="method delete">DELETE</span> <code>/subscribers/{{subscriber_id}}</code> - Desativar um assinante
                </div>
                <div class="endpoint">
                    <span class="method patch">PATCH</span> <code>/subscribers/{{subscriber_id}}/activate</code> - Ativar um assinante
                </div>
                <div class="endpoint">
                    <span class="method patch">PATCH</span> <code>/subscribers/{{subscriber_id}}/deactivate</code> - Desativar um assinante
                </div>
            </div>
            
            <div class="note">
                <p><strong>Filtros disponíveis para usuários:</strong></p>
                <ul>
                    <li><code>name</code> - Filtrar por nome (busca parcial)</li>
                    <li><code>email</code> - Filtrar por email (busca parcial)</li>
                    <li><code>role</code> - Filtrar por papel/role (SUPER_ADMIN, DIRETOR, COLABORADOR_NIVEL_2, DONO_ASSINANTE)</li>
                    <li><code>is_active</code> - Filtrar por status de ativação (true/false)</li>
                </ul>
                
                <p><strong>Filtros disponíveis para assinantes:</strong></p>
                <ul>
                    <li><code>name</code> - Filtrar por nome do responsável (busca parcial)</li>
                    <li><code>clinic_name</code> - Filtrar por nome da clínica (busca parcial)</li>
                    <li><code>email</code> - Filtrar por email (busca parcial)</li>
                    <li><code>document</code> - Filtrar por documento (CPF/CNPJ)</li>
                    <li><code>segment_id</code> - Filtrar por segmento (UUID)</li>
                    <li><code>plan_id</code> - Filtrar por plano (UUID)</li>
                    <li><code>is_active</code> - Filtrar por status de ativação (true/false)</li>
                </ul>
                
                <p><strong>Parâmetros de paginação (para todas as listagens):</strong></p>
                <ul>
                    <li><code>skip</code> - Quantos registros pular (default: 0)</li>
                    <li><code>limit</code> - Limite de registros por página (default: 10, max: 100)</li>
                </ul>
            </div>
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

# Rota para servir o arquivo api-config.js
@app.get("/api-config.js", response_class=Response)
async def api_config_js():
    """
    Serve o arquivo de configuração da API para o frontend.
    Este endpoint foi criado para resolver o erro "Unexpected token '<'"
    quando o navegador tenta carregar um arquivo JavaScript mas recebe HTML.
    """
    js_content = """
// Configuração da API
const API_CONFIG = {
  BASE_URL: window.location.hostname.includes('localhost') 
    ? 'http://localhost:5000' 
    : 'https://hubb-one-assist-back-hubb-one.replit.app',
  API_VERSION: 'v1',
  TIMEOUT: 30000,
  WITH_CREDENTIALS: true
};

// Exportar a configuração
export default API_CONFIG;
"""
    return Response(
        content=js_content,
        media_type="application/javascript"
    )

# Inicialização do usuário admin padrão
@app.on_event("startup")
async def startup_event():
    """
    Inicializa o usuário admin no primeiro boot se não existir.
    """
    db = next(get_db())
    UserService.create_admin_user(db)