"""
Script de inicialização para o servidor FastAPI com uvicorn
"""

import sys
import os
import uvicorn

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        access_log=True
    )