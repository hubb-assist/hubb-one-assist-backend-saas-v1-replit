"""
Arquivo principal do monorepo - compatível com uvicorn
Baseado nas regras do projeto: usar uvicorn, não gunicorn
"""
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Importar aplicação FastAPI
from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)