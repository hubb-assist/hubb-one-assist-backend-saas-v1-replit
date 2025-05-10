"""
Arquivo principal para aplicação WSGI
"""

# Criando uma aplicação WSGI simples para compatibilidade com Gunicorn
def simple_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response(status, headers)

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
            <p>Para acessar a API FastAPI real, por favor execute:</p>
            <pre>python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000</pre>
            <p>E então acesse: <a href="http://0.0.0.0:8000">http://0.0.0.0:8000</a></p>
            
            <div class="note">
                <p><strong>Nota:</strong> FastAPI (ASGI) não é diretamente compatível com o servidor Gunicorn (WSGI) 
                sem um adaptador especial. Precisamos executar o servidor Uvicorn separadamente.</p>
            </div>
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
    </body>
    </html>
    """
    
    return [html_content.encode('utf-8')]

# Exportar a aplicação para o Gunicorn
app = simple_app