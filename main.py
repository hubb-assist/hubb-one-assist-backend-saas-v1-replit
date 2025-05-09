# Para compatibilidade com o workflow config do Replit
# que está tentando rodar como app WSGI com Gunicorn

# Importe a aplicação FastAPI
from app.main import app as fastapi_app
import uvicorn

# Redirecionar para a versão ASGI
def application(environ, start_response):
    """
    Aplicação WSGI simples que retorna uma mensagem dizendo para usar o uvicorn
    """
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]
    
    start_response(status, headers)
    
    message = """
    <html>
    <head>
        <title>HUBB ONE Assist API</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }
            h1 { color: #333; }
            p { margin-bottom: 15px; }
            code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>HUBB ONE Assist API - FastAPI Application</h1>
        <p>Esta API foi implementada com FastAPI (ASGI) e está tentando ser executada com Gunicorn (WSGI).</p>
        <p>Para executar corretamente esta aplicação, use o Uvicorn:</p>
        <p><code>uvicorn app.main:app --host 0.0.0.0 --port 5000</code></p>
        <p>Para acessar a documentação da API, visite: <a href="/api/v1/docs">/api/v1/docs</a> (quando rodando no Uvicorn)</p>
    </body>
    </html>
    """
    
    return [message.encode('utf-8')]

# Também exponha a aplicação como 'app' para manter compatibilidade com o Gunicorn
app = application

# Quando executado diretamente, use o Uvicorn
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)