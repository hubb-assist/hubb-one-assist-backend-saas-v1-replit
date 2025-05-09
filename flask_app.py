"""
Aplicação Flask simples para servir a página inicial e redirecionar para o FastAPI.
"""

from flask import Flask, render_template_string, redirect

app = Flask(__name__)

@app.route('/')
def index():
    """Página inicial com links para a documentação da API"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API REST Simples</title>
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
        <h1>API REST Simples com FastAPI</h1>
        
        <div class="container">
            <p>Bem-vindo à API REST Simples construída com FastAPI!</p>
            
            <p>Para acessar a documentação e os endpoints da API, você precisa iniciar o servidor FastAPI/Uvicorn em um terminal separado:</p>
            
            <pre><code>python -m uvicorn fastapi_app:app --host 0.0.0.0 --port 8000</code></pre>
            
            <p>Após iniciar o servidor, você pode acessar:
            <ul>
                <li><a href="http://0.0.0.0:8000/docs">http://0.0.0.0:8000/docs</a> - Documentação Swagger UI (interativa)</li>
                <li><a href="http://0.0.0.0:8000/redoc">http://0.0.0.0:8000/redoc</a> - Documentação ReDoc</li>
                <li><a href="http://0.0.0.0:8000/">http://0.0.0.0:8000/</a> - Endpoint raiz da API</li>
            </ul>
            </p>
        </div>
        
        <h2>Endpoints Disponíveis</h2>
        
        <div class="endpoints">
            <div class="endpoint">
                <span class="method get">GET</span> <code>/</code> - Informações sobre a API
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> <code>/items</code> - Listar todos os itens
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> <code>/items/{item_id}</code> - Obter um item específico
            </div>
            <div class="endpoint">
                <span class="method post">POST</span> <code>/items</code> - Criar um novo item
            </div>
            <div class="endpoint">
                <span class="method put">PUT</span> <code>/items/{item_id}</code> - Atualizar um item existente
            </div>
            <div class="endpoint">
                <span class="method delete">DELETE</span> <code>/items/{item_id}</code> - Remover um item
            </div>
        </div>
        
        <div class="note">
            <p><strong>Nota:</strong> Esta API implementa operações CRUD básicas e demonstra a validação de dados com o Pydantic.</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)