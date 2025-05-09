"""
Arquivo para iniciar o servidor FastAPI com Uvicorn
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8000, reload=True)