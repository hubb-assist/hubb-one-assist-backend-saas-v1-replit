"""
Script para deploy no Replit
Este arquivo fornece uma função de saúde na raiz (/) para o health check do Replit
"""
import uvicorn
from app.main import app

@app.get("/")
async def health_check():
    """
    Endpoint de saúde para verificar o status da API.
    Usado nos health checks do deploy do Replit.
    """
    return {
        "status": "online",
        "version": "0.1.0",
        "name": "HUBB ONE Assist API"
    }

if __name__ == "__main__":
    # Inicia o servidor Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000)