"""
Arquivo principal para compatibilidade com deploy do Replit.
Importa a aplicação FastAPI do backend.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)