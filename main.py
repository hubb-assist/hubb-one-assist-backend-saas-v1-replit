"""
Arquivo principal para aplicação FastAPI
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Criando app especialmente para o deploy
app = FastAPI(title="HUBB ONE Assist API")

# Endpoint raiz simples especificamente para health checks
@app.get("/")
async def root():
    """
    Endpoint raiz para health checks.
    """
    return {"status": "online", "version": "0.1.0"}

# Redirecionar para a documentação
@app.get("/docs-redirect")
async def docs_redirect():
    """
    Redireciona para a documentação Swagger.
    """
    return {"message": "Acesse a documentação em /docs"}