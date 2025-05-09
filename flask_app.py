"""
Aplicação Flask simples para servir a página inicial e redirecionar para o FastAPI.
"""

from flask import Flask, render_template_string, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    """Página inicial com links para a documentação da API"""
    html = """
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
            <p>Bem-vindo à API do HUBB ONE Assist! Esta API está rodando com FastAPI.</p>
            
            <p>Para acessar a documentação e os endpoints da API, você precisa iniciar o servidor FastAPI/Uvicorn em um terminal separado:</p>
            
            <pre><code>python -m uvicorn single_main:app --host 0.0.0.0 --port 8000</code></pre>
            
            <p>Após iniciar o servidor, você pode acessar:
            <ul>
                <li><a href="http://0.0.0.0:8000/api/v1/docs">http://0.0.0.0:8000/api/v1/docs</a> - Documentação Swagger UI (interativa)</li>
                <li><a href="http://0.0.0.0:8000/api/v1/redoc">http://0.0.0.0:8000/api/v1/redoc</a> - Documentação ReDoc</li>
                <li><a href="http://0.0.0.0:8000/api/v1/status">http://0.0.0.0:8000/api/v1/status</a> - Status da API</li>
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
    return render_template_string(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)