"""
Arquivo principal do monorepo - solução definitiva para deployment no Replit
Baseado nas regras do projeto: usar uvicorn com backend.app.main:app
"""
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Importar aplicação FastAPI do módulo correto
from app.main import app

# Para compatibilidade com diferentes formas de deployment
application = app

if __name__ == "__main__":
    import uvicorn
    # Comando correto para Replit: uvicorn backend.app.main:app
    uvicorn.run(
        "backend.app.main:app",  # Caminho correto do módulo
        host="0.0.0.0", 
        port=5000, 
        reload=True
    )