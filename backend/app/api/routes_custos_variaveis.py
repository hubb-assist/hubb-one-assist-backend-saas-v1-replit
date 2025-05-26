from typing import Optional
from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.schemas.custo_variavel import CustoVariavelCreate, CustoVariavelUpdate, CustoVariavelResponse, CustoVariavelList
from app.services.custo_variavel_service import CustoVariavelService

# Criar o router
router = APIRouter(
    prefix="/custos/variaveis",
    tags=["custos"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=CustoVariavelList)
async def list_custos_variaveis(
    skip: int = Query(0, ge=0, description="Quantos registros pular (paginação)"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros a retornar"),
    date_from: Optional[date] = Query(None, description="Data inicial para filtro (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Data final para filtro (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retorna uma lista paginada de custos variáveis do assinante do usuário atual.
    Opcionalmente filtra por intervalo de datas.
    """
    return CustoVariavelService.get_custos_variaveis(
        db=db, 
        current_user=current_user, 
        skip=skip, 
        limit=limit,
        date_from=date_from,
        date_to=date_to
    )

@router.get("/{custo_variavel_id}", response_model=CustoVariavelResponse)
async def get_custo_variavel(
    custo_variavel_id: UUID = Path(..., description="ID do custo variável"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retorna os detalhes de um custo variável específico.
    """
    custo_variavel = CustoVariavelService.get_custo_variavel_by_id(
        db=db, 
        custo_variavel_id=custo_variavel_id, 
        current_user=current_user
    )
    
    if not custo_variavel:
        raise HTTPException(status_code=404, detail="Custo variável não encontrado")
        
    return custo_variavel

@router.post("/", response_model=CustoVariavelResponse)
async def create_custo_variavel(
    custo_variavel: CustoVariavelCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Cria um novo custo variável para o assinante do usuário atual.
    """
    # Verificar se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=400, 
            detail="Usuário não está associado a um assinante"
        )
    
    try:
        result = CustoVariavelService.create_custo_variavel(
            db=db, 
            custo_variavel=custo_variavel, 
            current_user=current_user
        )
        
        if not result:
            raise HTTPException(
                status_code=400, 
                detail="Erro ao criar custo variável"
            )
            
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Erro ao criar custo variável: {str(e)}"
        )

@router.put("/{custo_variavel_id}", response_model=CustoVariavelResponse)
async def update_custo_variavel(
    custo_variavel_id: UUID,
    custo_variavel: CustoVariavelUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Atualiza um custo variável existente.
    """
    # Verificar se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=400, 
            detail="Usuário não está associado a um assinante"
        )
    
    # Verificar se pelo menos um campo para atualização foi fornecido
    update_data = custo_variavel.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=400, 
            detail="Pelo menos um campo deve ser fornecido para atualização"
        )
    
    try:
        result = CustoVariavelService.update_custo_variavel(
            db=db, 
            custo_variavel_id=custo_variavel_id, 
            custo_variavel=custo_variavel, 
            current_user=current_user
        )
        
        if not result:
            raise HTTPException(
                status_code=404, 
                detail="Custo variável não encontrado"
            )
            
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Erro ao atualizar custo variável: {str(e)}"
        )

@router.delete("/{custo_variavel_id}")
async def delete_custo_variavel(
    custo_variavel_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Remove (desativa) um custo variável.
    """
    # Verificar se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=400, 
            detail="Usuário não está associado a um assinante"
        )
    
    result = CustoVariavelService.delete_custo_variavel(
        db=db, 
        custo_variavel_id=custo_variavel_id, 
        current_user=current_user
    )
    
    if not result:
        raise HTTPException(
            status_code=404, 
            detail="Custo variável não encontrado"
        )
        
    return {"success": True, "message": "Custo variável removido com sucesso"}