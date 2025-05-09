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
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, ConfigDict

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

# Rotas da API
@app.get("/", tags=["Root"])
async def root():
    """
    Retorna informações básicas sobre a API.
    """
    return {
        "message": "API REST Simples construída com FastAPI",
        "docs": "/docs",
        "redoc": "/redoc"
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
    
    item_dict = item.dict()
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

# Executar o servidor quando o script for executado diretamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8000, reload=True)