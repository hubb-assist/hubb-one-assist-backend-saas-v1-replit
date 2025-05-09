"""
Este arquivo serve como ponte entre o protocolo WSGI (usado pelo Gunicorn)
e o protocolo ASGI (usado pelo FastAPI).

Ele permite que o Gunicorn sirva a aplicação FastAPI através de um adaptador.
"""

from fastapi.applications import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

# Importe o app FastAPI do arquivo single_main
from single_main import app as fastapi_app

# Crie um app WSGI simples para servir como página inicial
def wsgi_app(environ, start_response):
    """
    Aplicação WSGI simples que exibe uma página inicial e informações úteis.
    """
    path = environ.get('PATH_INFO', '').lstrip('/')
    
    if path == '' or path == '/':
        start_response('200 OK', [('Content-Type', 'text/html')])
        
        # Página HTML com informações sobre a API
        html = """<!DOCTYPE html>
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
                <p>Bem-vindo à API do HUBB ONE Assist! Esta API está rodando com FastAPI.</p>
                
                <p>Você pode acessar:
                <ul>
                    <li><a href="/api/v1/docs">/api/v1/docs</a> - Documentação Swagger UI (interativa)</li>
                    <li><a href="/api/v1/redoc">/api/v1/redoc</a> - Documentação ReDoc</li>
                    <li><a href="/api/v1/status">/api/v1/status</a> - Status da API</li>
                </ul>
                </p>
            </div>
            
            <h2>Endpoints Principais</h2>
            
            <div class="endpoints">
                <div class="endpoint">
                    <span class="method post">POST</span> <code>/api/v1/auth/login</code> - Login (obter token JWT)
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> <code>/api/v1/auth/refresh</code> - Renovar token
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> <code>/api/v1/users</code> - Listar usuários
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> <code>/api/v1/users/me</code> - Informações do usuário atual
                </div>
            </div>
            
            <div class="note">
                <p><strong>Nota:</strong> Esta API usa autenticação JWT. Use o endpoint <code>/api/v1/auth/login</code> 
                para obter um token e inclua-o no cabeçalho <code>Authorization: Bearer &lt;token&gt;</code> para as requisições protegidas.</p>
            </div>
        </body>
        </html>
        """
        return [html.encode('utf-8')]
    else:
        # Redirecionar outras rotas para o FastAPI
        start_response('302 Found', [('Location', f'/api/{path}')])
        return [f"Redirecionando para /api/{path}".encode('utf-8')]

# Crie um FastAPI wrapper que inclui o app WSGI para a rota raiz
app = FastAPI()

# Monte o app FastAPI original no caminho /api
app.mount("/api", fastapi_app)

# Monte a aplicação WSGI para a rota raiz
app.mount("/", WSGIMiddleware(wsgi_app))

# Quando executado diretamente, inicie o servidor Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("wsgi:app", host="0.0.0.0", port=5000, reload=True)