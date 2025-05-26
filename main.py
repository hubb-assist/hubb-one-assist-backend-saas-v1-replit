"""
Arquivo principal para compatibilidade com deploy do Replit.
Importa a aplicação FastAPI do backend.
"""

import sys
import os

# Adicionar o diretório backend ao Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Importar a aplicação FastAPI
from app.main import app

# Exportar para o Gunicorn
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)