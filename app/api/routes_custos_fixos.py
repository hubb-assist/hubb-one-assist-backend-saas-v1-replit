from typing import Optional
from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.schemas.custo_fixo import CustoFixoCreate, CustoFixoUpdate, CustoFixoResponse, CustoFixoList
from app.services.custo_fixo_service import CustoFixoService

# Criar o router
router = APIRouter(
    prefix="/custos/fixos",
    tags=["custos"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=CustoFixoList)
async def list_custos_fixos(
    skip: int = Query(0, ge=0, description="Quantos registros pular (paginação)"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros a retornar"),
    date_from: Optional[date] = Query(None, description="Data inicial para filtro (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Data final para filtro (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retorna uma lista paginada de custos fixos do assinante do usuário atual.
    Opcionalmente filtra por intervalo de datas.
    """
    return CustoFixoService.get_custos_fixos(
        db=db, 
        current_user=current_user, 
        skip=skip, 
        limit=limit,
        date_from=date_from,
        date_to=date_to
    )

@router.get("/{custo_fixo_id}", response_model=CustoFixoResponse)
async def get_custo_fixo(
    custo_fixo_id: UUID = Path(..., description="ID do custo fixo"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retorna os detalhes de um custo fixo específico.
    """
    custo_fixo = CustoFixoService.get_custo_fixo_by_id(
        db=db, 
        custo_fixo_id=custo_fixo_id, 
        current_user=current_user
    )
    
    if not custo_fixo:
        raise HTTPException(status_code=404, detail="Custo fixo não encontrado")
        
    return custo_fixo

@router.post("/", response_model=CustoFixoResponse)
async def create_custo_fixo(
    custo_fixo: CustoFixoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Cria um novo custo fixo para o assinante do usuário atual.
    """
    # Verificar se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=400, 
            detail="Usuário não está associado a um assinante"
        )
    
    try:
        result = CustoFixoService.create_custo_fixo(
            db=db, 
            custo_fixo=custo_fixo, 
            current_user=current_user
        )
        
        if not result:
            raise HTTPException(
                status_code=400, 
                detail="Erro ao criar custo fixo"
            )
            
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Erro ao criar custo fixo: {str(e)}"
        )

@router.put("/{custo_fixo_id}", response_model=CustoFixoResponse)
async def update_custo_fixo(
    custo_fixo_id: UUID,
    custo_fixo: CustoFixoUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Atualiza um custo fixo existente.
    """
    # Verificar se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=400, 
            detail="Usuário não está associado a um assinante"
        )
    
    # Verificar se pelo menos um campo para atualização foi fornecido
    update_data = custo_fixo.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=400, 
            detail="Pelo menos um campo deve ser fornecido para atualização"
        )
    
    try:
        result = CustoFixoService.update_custo_fixo(
            db=db, 
            custo_fixo_id=custo_fixo_id, 
            custo_fixo=custo_fixo, 
            current_user=current_user
        )
        
        if not result:
            raise HTTPException(
                status_code=404, 
                detail="Custo fixo não encontrado"
            )
            
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Erro ao atualizar custo fixo: {str(e)}"
        )

@router.delete("/{custo_fixo_id}")
async def delete_custo_fixo(
    custo_fixo_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Remove (desativa) um custo fixo.
    """
    # Verificar se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=400, 
            detail="Usuário não está associado a um assinante"
        )
    
    result = CustoFixoService.delete_custo_fixo(
        db=db, 
        custo_fixo_id=custo_fixo_id, 
        current_user=current_user
    )
    
    if not result:
        raise HTTPException(
            status_code=404, 
            detail="Custo fixo não encontrado"
        )
        
    return {"success": True, "message": "Custo fixo removido com sucesso"}