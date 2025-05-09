"""
Arquivo para iniciar o servidor FastAPI com Uvicorn
"""

import uvicorn

if __name__ == "__main__":
    print("Iniciando o servidor FastAPI na porta 5000...")
    uvicorn.run("api:app", host="0.0.0.0", port=5000, reload=True)