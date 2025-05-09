# Arquivo main.py - wrapper simples para WSGI
import uvicorn

# Importe a aplicação FastAPI
from app.main import app as fastapi_app

# Função para criar um aplicativo WSGI simples que retorna uma mensagem HTML
def create_simple_wsgi_app():
    def app(environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        
        if path_info == '/docs':
            # Redirecionando para o Swagger UI correto
            start_response('302 Found', [('Location', '/api/v1/docs')])
            return [b'']

        # Página HTML informativa
        start_response('200 OK', [('Content-Type', 'text/html')])
        html = f"""<!DOCTYPE html>
        <html>
        <head>
            <title>HUBB ONE Assist API</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }}
                h1 {{ color: #333; }}
                p {{ margin-bottom: 15px; }}
                code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
                .container {{ margin-top: 20px; border: 1px solid #ddd; padding: 20px; border-radius: 5px; }}
                .info {{ color: blue; }}
                .button {{ display: inline-block; background: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <h1>HUBB ONE Assist API - FastAPI Application</h1>
            <div class="container">
                <p>Esta API está rodando e você pode acessar:</p>
                <ul>
                    <li><a href="/api/v1/docs">/api/v1/docs</a> - Swagger UI (documentação interativa)</li>
                    <li><a href="/api/v1/redoc">/api/v1/redoc</a> - ReDoc (documentação alternativa)</li>
                </ul>
                <p class="info">A API retorna respostas JSON em todos os endpoints.</p>
            </div>
        </body>
        </html>
        """
        return [html.encode('utf-8')]
    
    return app

# Crie a aplicação WSGI compatível com Gunicorn
app = create_simple_wsgi_app()

if __name__ == "__main__":
    # Quando executado diretamente, use o Uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)