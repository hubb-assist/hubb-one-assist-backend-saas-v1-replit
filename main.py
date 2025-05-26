"""
Arquivo principal para rodar FastAPI com uvicorn através do Gunicorn
"""

import sys
import os

# Adicionar o diretório backend ao Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Importar a aplicação FastAPI
from app.main import app

# Para compatibilidade com deploy - exportar app diretamente
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)