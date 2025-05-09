# Arquivo main.py - Ponto de entrada para WSGI com Gunicorn e redirecionamento para Uvicorn
import uvicorn
import logging
import os
import sys
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtenha a URL base do Replit
def get_replit_url():
    """
    Tenta obter a URL base do Replit a partir do ambiente
    """
    # Para simplificar, usamos a URL atual
    server_name = os.environ.get('HTTP_HOST', '')
    if server_name:
        return f"https://{server_name}"
    
    # URL de fallback (usar o domínio atual sem porta)
    return ""

# Função simples WSGI para quando o Gunicorn tentar carregar este arquivo
def app(environ, start_response):
    """
    Retorna uma página HTML informativa ou redireciona para o servidor Uvicorn
    """
    path_info = environ.get('PATH_INFO', '')
    
    # Inicie o servidor Uvicorn se ele não estiver rodando
    # Você pode iniciar manualmente com: ./start-fastapi.sh
    
    # Para a rota raiz, mostre a página informativa
    if path_info == "/" or path_info == "":
        start_response('200 OK', [('Content-Type', 'text/html')])
        base_url = get_replit_url()
        # Pegar o hostname a partir do environ
        server_name = environ.get('HTTP_HOST', 'localhost:5000')
        base_domain = server_name.split(':')[0]
        
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
                .success {{ color: green; }}
                .warning {{ color: #ff4500; }}
                .note {{ background: #ffffcc; padding: 10px; border-left: 4px solid #ffcc00; margin-top: 20px; }}
                .button {{ display: inline-block; background: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <h1>HUBB ONE Assist API</h1>
            <div class="container">
                <p class="success">A API FastAPI está configurada e pronta para uso!</p>
                
                <p>Para acessar a documentação Swagger e utilizar a API, você precisa:</p>
                
                <ol>
                    <li>Abrir um novo terminal no Replit</li>
                    <li>Executar o comando: <code>uvicorn app.main:app --host 0.0.0.0 --port 8000</code></li>
                    <li>Manter esse terminal aberto (ele executará o servidor Uvicorn)</li>
                    <li>Acessar a documentação Swagger em: <a href="https://{base_domain}:8000/api/v1/docs" target="_blank">https://{base_domain}:8000/api/v1/docs</a></li>
                </ol>
                
                <p>Ou, para maior comodidade, execute o script:</p>
                <pre><code>./start-fastapi.sh</code></pre>
                
                <div class="note">
                    <p><strong>Importante:</strong> O Swagger UI e outros recursos da API FastAPI só estarão disponíveis enquanto o servidor Uvicorn estiver em execução no terminal.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return [html.encode('utf-8')]
    
    # Para as rotas da API, redirecionamos para a porta 8000
    elif path_info.startswith('/api/'):
        replit_url = get_replit_url()
        target_url = f"{replit_url}:8000{path_info}"
        start_response('302 Found', [('Location', target_url)])
        return [f"Redirecionando para {target_url}".encode('utf-8')]
    
    # Para outras rotas, retorne 404
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return [b'<html><body><h1>404 Not Found</h1><p>A pagina solicitada nao existe.</p></body></html>']

# Quando executado diretamente, inicie o servidor Uvicorn
if __name__ == "__main__":
    logger.info("Iniciando o servidor Uvicorn para a API FastAPI...")
    
    try:
        # Tente iniciar o aplicativo FastAPI com Uvicorn
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        logger.error(f"Erro ao iniciar Uvicorn: {e}")
        print(f"ERRO: Falha ao iniciar o servidor Uvicorn: {e}")
        sys.exit(1)