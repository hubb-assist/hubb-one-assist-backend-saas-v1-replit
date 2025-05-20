"""
Módulo ASGI para iniciar a aplicação FastAPI com Uvicorn
"""
import os
from app.main import app

# Configurar host e porta para bind
host = os.getenv("HOST", "0.0.0.0")
port = int(os.getenv("PORT", "5000"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=host, port=port)