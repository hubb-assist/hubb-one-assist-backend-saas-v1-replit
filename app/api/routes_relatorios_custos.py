"""
Rotas para gerenciamento de relatórios de custos
"""
from datetime import date
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.schemas.relatorio_custos import (
    RelatorioCustosCreate,
    RelatorioCustosUpdate,
    RelatorioCustosResponse,
    RelatorioCustosList,
    RelatorioCustosDetalhado,
    ReportTypeEnum
)
from app.services.relatorio_custos_service import RelatorioCustosService


# Criar o router
router = APIRouter(
    prefix="/custos/relatorios",
    tags=["custos", "relatorios"],
    responses={404: {"description": "Not found"}}
)


@router.post("/", response_model=RelatorioCustosResponse)
async def criar_relatorio(
    data: RelatorioCustosCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Cria um novo relatório de custos para o período especificado.
    """
    # Verificar se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=400, 
            detail="Usuário não está associado a um assinante"
        )
    
    # Criar serviço e executar
    service = RelatorioCustosService(db)
    try:
        relatorio = service.criar_relatorio(subscriber_id, data)
        return relatorio
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Erro ao criar relatório: {str(e)}"
        )


@router.get("/", response_model=RelatorioCustosList)
async def listar_relatorios(
    skip: int = Query(0, ge=0, description="Quantos registros pular (paginação)"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros a retornar"),
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Lista todos os relatórios de custos do assinante com paginação.
    Opcionalmente filtra por ano.
    """
    # Verificar se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        return RelatorioCustosList(items=[], total=0, skip=skip, limit=limit)
    
    # Criar serviço e executar
    service = RelatorioCustosService(db)
    relatorios, total = service.listar_relatorios(
        subscriber_id=subscriber_id,
        skip=skip,
        limit=limit,
        ano=ano
    )
    
    return RelatorioCustosList(
        items=relatorios,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/periodos")
async def obter_periodos_predefinidos():
    """
    Retorna informações sobre os tipos de períodos predefinidos disponíveis para relatórios.
    """
    return {
        "tipos": [
            {
                "id": ReportTypeEnum.MENSAL,
                "nome": "Mensal",
                "descricao": "Relatório do mês atual"
            },
            {
                "id": ReportTypeEnum.TRIMESTRAL,
                "nome": "Trimestral",
                "descricao": "Relatório do trimestre atual"
            },
            {
                "id": ReportTypeEnum.ANUAL,
                "nome": "Anual",
                "descricao": "Relatório do ano atual"
            },
            {
                "id": ReportTypeEnum.CUSTOMIZADO,
                "nome": "Personalizado",
                "descricao": "Relatório com período personalizado"
            }
        ]
    }


@router.get("/sugestao-periodo/{tipo}")
async def sugerir_periodo(
    tipo: ReportTypeEnum = Path(..., description="Tipo de período para o relatório"),
    data_referencia: Optional[date] = Query(None, description="Data de referência (padrão: hoje)")
):
    """
    Retorna sugestão de datas para o tipo de relatório selecionado.
    """
    service = RelatorioCustosService(None)  # Não precisa de DB para esta operação
    date_from, date_to, title = service.obter_datas_para_tipo_relatorio(
        report_type=tipo,
        reference_date=data_referencia
    )
    
    return {
        "date_from": date_from,
        "date_to": date_to,
        "title": title
    }


@router.get("/{relatorio_id}", response_model=RelatorioCustosResponse)
async def obter_relatorio(
    relatorio_id: UUID = Path(..., description="ID do relatório"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtém um relatório específico pelo ID.
    """
    # Verificar se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=400, 
            detail="Usuário não está associado a um assinante"
        )
    
    # Criar serviço e executar
    service = RelatorioCustosService(db)
    relatorio = service.obter_relatorio(relatorio_id, subscriber_id)
    
    if not relatorio:
        raise HTTPException(
            status_code=404, 
            detail="Relatório não encontrado"
        )
    
    return relatorio


@router.get("/{relatorio_id}/detalhado", response_model=RelatorioCustosDetalhado)
async def obter_relatorio_detalhado(
    relatorio_id: UUID = Path(..., description="ID do relatório"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtém um relatório detalhado com informações adicionais sobre os custos.
    """
    # Verificar se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=400, 
            detail="Usuário não está associado a um assinante"
        )
    
    # Criar serviço e executar
    service = RelatorioCustosService(db)
    relatorio = service.obter_relatorio(relatorio_id, subscriber_id)
    
    if not relatorio:
        raise HTTPException(
            status_code=404, 
            detail="Relatório não encontrado"
        )
    
    # Obter detalhes adicionais
    detalhes = service.obter_detalhes_custos_por_categoria(
        subscriber_id=subscriber_id,
        date_from=relatorio.date_from,
        date_to=relatorio.date_to
    )
    
    # Calcular distribuição percentual
    distribuicao = service.calcular_distribuicao_percentual(
        subscriber_id=subscriber_id,
        date_from=relatorio.date_from,
        date_to=relatorio.date_to
    )
    
    # Calcular evolução mensal
    evolucao = service.calcular_evolucao_mensal(
        subscriber_id=subscriber_id,
        date_from=relatorio.date_from,
        date_to=relatorio.date_to
    )
    
    # Criar resposta detalhada
    resposta = RelatorioCustosDetalhado(
        **relatorio.__dict__,
        detalhes_fixos=detalhes["custos_fixos"],
        detalhes_variaveis=detalhes["custos_variaveis"],
        detalhes_clinicos=detalhes["custos_clinicos"],
        detalhes_insumos=detalhes["custos_insumos"],
        distribuicao_percentual=distribuicao,
        evolucao_mensal=evolucao
    )
    
    return resposta


@router.put("/{relatorio_id}", response_model=RelatorioCustosResponse)
async def atualizar_relatorio(
    relatorio_id: UUID,
    data: RelatorioCustosUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Atualiza um relatório existente.
    """
    # Verificar se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=400, 
            detail="Usuário não está associado a um assinante"
        )
    
    # Verificar se pelo menos um campo para atualização foi fornecido
    update_data = data.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=400, 
            detail="Pelo menos um campo deve ser fornecido para atualização"
        )
    
    # Criar serviço e executar
    service = RelatorioCustosService(db)
    try:
        relatorio = service.atualizar_relatorio(relatorio_id, subscriber_id, data)
        
        if not relatorio:
            raise HTTPException(
                status_code=404, 
                detail="Relatório não encontrado"
            )
        
        return relatorio
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Erro ao atualizar relatório: {str(e)}"
        )


@router.delete("/{relatorio_id}")
async def remover_relatorio(
    relatorio_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Remove (desativa) um relatório.
    """
    # Verificar se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=400, 
            detail="Usuário não está associado a um assinante"
        )
    
    # Criar serviço e executar
    service = RelatorioCustosService(db)
    result = service.remover_relatorio(relatorio_id, subscriber_id)
    
    if not result:
        raise HTTPException(
            status_code=404, 
            detail="Relatório não encontrado"
        )
    
    return {"success": True, "message": "Relatório removido com sucesso"}