"""
FastAPI - API REST Simples (MVP)

Este arquivo contém uma API REST básica construída com FastAPI,
implementando operações CRUD para um modelo de usuário simples.
"""

import os
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict

from fastapi import FastAPI, HTTPException, Query, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field, ConfigDict

# Inicialização do FastAPI
app = FastAPI(
    title="API REST Simples",
    description="MVP de API REST construída com FastAPI",
    version="0.1.0",
)

# Adicionar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enumeração de status
class ItemStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

# Modelo Pydantic para validação de entrada/saída
class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Título do item")
    description: Optional[str] = Field(None, max_length=1000, description="Descrição detalhada do item")
    status: ItemStatus = Field(default=ItemStatus.ACTIVE, description="Status do item")

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="Título do item")
    description: Optional[str] = Field(None, max_length=1000, description="Descrição detalhada do item")
    status: Optional[ItemStatus] = Field(None, description="Status do item")
    
    model_config = ConfigDict(extra="forbid")

class Item(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Banco de dados em memória
items_db = {}
counter = 0

# Dependência para simular acesso ao banco de dados
def get_items_db():
    return items_db

# Página inicial HTML
@app.get("/", response_class=HTMLResponse)
async def home():
    """
    Página inicial com informações sobre a API.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API REST Simples</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }
            h1 { color: #333; }
            h2 { color: #555; margin-top: 30px; }
            p { margin-bottom: 15px; }
            code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
            pre { background: #f8f8f8; padding: 10px; border-radius: 5px; overflow-x: auto; }
            .container { margin-top: 20px; border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
            .info { color: blue; }
            .note { background: #ffffcc; padding: 10px; border-left: 4px solid #ffcc00; margin-top: 20px; }
            .endpoints { margin-top: 30px; }
            .endpoint { margin-bottom: 15px; }
            .method { display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; margin-right: 5px; }
            .get { background: #61affe; color: white; }
            .post { background: #49cc90; color: white; }
            .put { background: #fca130; color: white; }
            .delete { background: #f93e3e; color: white; }
        </style>
    </head>
    <body>
        <h1>API REST Simples com FastAPI</h1>
        
        <div class="container">
            <p>Bem-vindo à API REST Simples construída com FastAPI!</p>
            
            <p>A API está rodando neste servidor. Você pode acessar:</p>
            
            <ul>
                <li><a href="/docs">/docs</a> - Documentação Swagger UI (interativa)</li>
                <li><a href="/redoc">/redoc</a> - Documentação ReDoc</li>
                <li><a href="/api-info">/api-info</a> - Endpoint com informações da API</li>
            </ul>
        </div>
        
        <h2>Endpoints Disponíveis</h2>
        
        <div class="endpoints">
            <div class="endpoint">
                <span class="method get">GET</span> <code>/api-info</code> - Informações sobre a API
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> <code>/items</code> - Listar todos os itens
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> <code>/items/{item_id}</code> - Obter um item específico
            </div>
            <div class="endpoint">
                <span class="method post">POST</span> <code>/items</code> - Criar um novo item
            </div>
            <div class="endpoint">
                <span class="method put">PUT</span> <code>/items/{item_id}</code> - Atualizar um item existente
            </div>
            <div class="endpoint">
                <span class="method delete">DELETE</span> <code>/items/{item_id}</code> - Remover um item
            </div>
        </div>
        
        <div class="note">
            <p><strong>Nota:</strong> Esta API implementa operações CRUD básicas e demonstra a validação de dados com o Pydantic.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Rotas da API
@app.get("/api-info", tags=["Info"])
async def api_info():
    """
    Retorna informações básicas sobre a API.
    """
    return {
        "name": "API REST Simples",
        "version": "0.1.0",
        "description": "MVP de API REST construída com FastAPI",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/items", response_model=List[Item], tags=["Items"])
async def list_items(
    skip: int = Query(0, ge=0, description="Quantidade de itens para pular"),
    limit: int = Query(10, ge=1, le=100, description="Quantidade máxima de itens a retornar"),
    status: Optional[ItemStatus] = Query(None, description="Filtrar por status"),
    db: Dict = Depends(get_items_db)
):
    """
    Lista todos os itens com opções de paginação e filtro por status.
    """
    items = list(db.values())
    
    # Aplicar filtro de status
    if status:
        items = [item for item in items if item["status"] == status]
    
    # Aplicar paginação
    items = items[skip : skip + limit]
    
    return items

@app.get("/items/{item_id}", response_model=Item, tags=["Items"])
async def get_item(item_id: int, db: Dict = Depends(get_items_db)):
    """
    Retorna um item específico pelo ID.
    """
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    return db[item_id]

@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED, tags=["Items"])
async def create_item(item: ItemCreate, db: Dict = Depends(get_items_db)):
    """
    Cria um novo item.
    """
    global counter
    counter += 1
    item_id = counter
    
    item_dict = item.model_dump()
    item_dict.update({
        "id": item_id,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })
    
    db[item_id] = item_dict
    
    return item_dict

@app.put("/items/{item_id}", response_model=Item, tags=["Items"])
async def update_item(item_id: int, item: ItemUpdate, db: Dict = Depends(get_items_db)):
    """
    Atualiza um item existente.
    """
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    stored_item = db[item_id]
    
    update_data = item.model_dump(exclude_unset=True)
    
    # Atualizar apenas os campos fornecidos
    for key, value in update_data.items():
        stored_item[key] = value
    
    # Atualizar timestamp
    stored_item["updated_at"] = datetime.now()
    
    db[item_id] = stored_item
    
    return stored_item

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Items"])
async def delete_item(item_id: int, db: Dict = Depends(get_items_db)):
    """
    Remove um item.
    """
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    del db[item_id]
    
    return None

# Middleware para tratamento global de erros
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Erro interno: {str(exc)}"},
    )

# Criar alguns itens de exemplo
@app.on_event("startup")
async def startup_event():
    # Adicionar alguns itens de exemplo ao iniciar o servidor
    await create_item(
        ItemCreate(
            title="Exemplo 1", 
            description="Este é um item de exemplo", 
            status=ItemStatus.ACTIVE
        ),
        items_db
    )
    
    await create_item(
        ItemCreate(
            title="Exemplo 2", 
            description="Este é outro item de exemplo", 
            status=ItemStatus.PENDING
        ),
        items_db
    )