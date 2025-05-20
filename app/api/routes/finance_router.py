from uuid import UUID
from datetime import date, datetime
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.application.use_cases.finance_use_cases import (
    # Payables
    CreatePayableUseCase,
    GetPayableUseCase,
    ListPayablesUseCase,
    UpdatePayableUseCase,
    DeletePayableUseCase,
    # Receivables
    CreateReceivableUseCase,
    GetReceivableUseCase,
    ListReceivablesUseCase,
    UpdateReceivableUseCase,
    DeleteReceivableUseCase,
    # Cash Flow & Profit
    GetCashFlowUseCase,
    CalculateProfitUseCase,
)
from app.infrastructure.repositories.finance_sqlalchemy import FinanceSQLAlchemyRepository
from app.schemas.finance_schema import (
    PayableCreate,
    PayableUpdate,
    PayableResponse,
    PayableListResponse,
    ReceivableCreate,
    ReceivableUpdate,
    ReceivableResponse,
    ReceivableListResponse,
    CashFlowResponse,
    ProfitResponse,
)
from app.db.models import User

# Criar router com prefixo e tags
router = APIRouter(prefix="/finance", tags=["finance"])

# --- Dependências ---
def get_finance_repository(db: Session = Depends(get_db)):
    return FinanceSQLAlchemyRepository(db)


# --- PAYABLES (Contas a Pagar) ---
@router.post("/payables", response_model=PayableResponse, status_code=201)
async def create_payable(
    data: PayableCreate,
    current_user: User = Depends(get_current_user),
    repo: FinanceSQLAlchemyRepository = Depends(get_finance_repository),
):
    """
    Cria um novo registro de conta a pagar
    """
    try:
        use_case = CreatePayableUseCase(repo)
        result = use_case.execute(data, current_user.subscriber_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao criar conta a pagar: {str(e)}")


@router.get("/payables/{payable_id}", response_model=PayableResponse)
async def get_payable(
    payable_id: UUID,
    current_user: User = Depends(get_current_user),
    repo: FinanceSQLAlchemyRepository = Depends(get_finance_repository),
):
    """
    Obtém detalhes de uma conta a pagar por ID
    """
    try:
        use_case = GetPayableUseCase(repo)
        result = use_case.execute(payable_id, current_user.subscriber_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao buscar conta a pagar: {str(e)}")


@router.get("/payables", response_model=PayableListResponse)
async def list_payables(
    skip: int = Query(0, ge=0, description="Quantos itens pular (paginação)"),
    limit: int = Query(100, ge=1, le=100, description="Limite de itens retornados"),
    paid: Optional[bool] = Query(None, description="Filtrar por status de pagamento"),
    due_from: Optional[date] = Query(None, description="Data inicial de vencimento (YYYY-MM-DD)"),
    due_to: Optional[date] = Query(None, description="Data final de vencimento (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    repo: FinanceSQLAlchemyRepository = Depends(get_finance_repository),
):
    """
    Lista contas a pagar com filtros opcionais
    """
    try:
        use_case = ListPayablesUseCase(repo)
        results = use_case.execute(
            current_user.subscriber_id,
            skip=skip,
            limit=limit,
            paid=paid,
            due_from=due_from,
            due_to=due_to
        )
        return {"items": results, "total": len(results)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao listar contas a pagar: {str(e)}")


@router.put("/payables/{payable_id}", response_model=PayableResponse)
async def update_payable(
    payable_id: UUID,
    data: PayableUpdate,
    current_user: User = Depends(get_current_user),
    repo: FinanceSQLAlchemyRepository = Depends(get_finance_repository),
):
    """
    Atualiza uma conta a pagar existente
    """
    try:
        use_case = UpdatePayableUseCase(repo)
        result = use_case.execute(payable_id, data, current_user.subscriber_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao atualizar conta a pagar: {str(e)}")


@router.delete("/payables/{payable_id}", status_code=204)
async def delete_payable(
    payable_id: UUID,
    current_user: User = Depends(get_current_user),
    repo: FinanceSQLAlchemyRepository = Depends(get_finance_repository),
):
    """
    Remove (logicamente) uma conta a pagar
    """
    try:
        use_case = DeletePayableUseCase(repo)
        use_case.execute(payable_id, current_user.subscriber_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao excluir conta a pagar: {str(e)}")


# --- RECEIVABLES (Contas a Receber) ---
@router.post("/receivables", response_model=ReceivableResponse, status_code=201)
async def create_receivable(
    data: ReceivableCreate,
    current_user: User = Depends(get_current_user),
    repo: FinanceSQLAlchemyRepository = Depends(get_finance_repository),
):
    """
    Cria um novo registro de conta a receber
    """
    try:
        use_case = CreateReceivableUseCase(repo)
        result = use_case.execute(data, current_user.subscriber_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao criar conta a receber: {str(e)}")


@router.get("/receivables/{receivable_id}", response_model=ReceivableResponse)
async def get_receivable(
    receivable_id: UUID,
    current_user: User = Depends(get_current_user),
    repo: FinanceSQLAlchemyRepository = Depends(get_finance_repository),
):
    """
    Obtém detalhes de uma conta a receber por ID
    """
    try:
        use_case = GetReceivableUseCase(repo)
        result = use_case.execute(receivable_id, current_user.subscriber_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao buscar conta a receber: {str(e)}")


@router.get("/receivables", response_model=ReceivableListResponse)
async def list_receivables(
    skip: int = Query(0, ge=0, description="Quantos itens pular (paginação)"),
    limit: int = Query(100, ge=1, le=100, description="Limite de itens retornados"),
    received: Optional[bool] = Query(None, description="Filtrar por status de recebimento"),
    due_from: Optional[date] = Query(None, description="Data inicial de vencimento (YYYY-MM-DD)"),
    due_to: Optional[date] = Query(None, description="Data final de vencimento (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    repo: FinanceSQLAlchemyRepository = Depends(get_finance_repository),
):
    """
    Lista contas a receber com filtros opcionais
    """
    try:
        use_case = ListReceivablesUseCase(repo)
        results = use_case.execute(
            current_user.subscriber_id,
            skip=skip,
            limit=limit,
            received=received,
            due_from=due_from,
            due_to=due_to
        )
        return {"items": results, "total": len(results)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao listar contas a receber: {str(e)}")


@router.put("/receivables/{receivable_id}", response_model=ReceivableResponse)
async def update_receivable(
    receivable_id: UUID,
    data: ReceivableUpdate,
    current_user: User = Depends(get_current_user),
    repo: FinanceSQLAlchemyRepository = Depends(get_finance_repository),
):
    """
    Atualiza uma conta a receber existente
    """
    try:
        use_case = UpdateReceivableUseCase(repo)
        result = use_case.execute(receivable_id, data, current_user.subscriber_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao atualizar conta a receber: {str(e)}")


@router.delete("/receivables/{receivable_id}", status_code=204)
async def delete_receivable(
    receivable_id: UUID,
    current_user: User = Depends(get_current_user),
    repo: FinanceSQLAlchemyRepository = Depends(get_finance_repository),
):
    """
    Remove (logicamente) uma conta a receber
    """
    try:
        use_case = DeleteReceivableUseCase(repo)
        use_case.execute(receivable_id, current_user.subscriber_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao excluir conta a receber: {str(e)}")


# --- CASH FLOW & PROFIT (Fluxo de Caixa e Lucro) ---
@router.get("/cashflow", response_model=CashFlowResponse)
async def get_cashflow(
    from_date: date = Query(..., description="Data inicial do período (YYYY-MM-DD)"),
    to_date: date = Query(..., description="Data final do período (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    repo: FinanceSQLAlchemyRepository = Depends(get_finance_repository),
):
    """
    Calcula o fluxo de caixa em um determinado período
    """
    try:
        use_case = GetCashFlowUseCase(repo)
        result = use_case.execute(current_user.subscriber_id, from_date, to_date)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao calcular fluxo de caixa: {str(e)}")


@router.get("/profit", response_model=ProfitResponse)
async def calculate_profit(
    period_from: date = Query(..., description="Data inicial do período (YYYY-MM-DD)"),
    period_to: date = Query(..., description="Data final do período (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    repo: FinanceSQLAlchemyRepository = Depends(get_finance_repository),
):
    """
    Calcula o lucro em um determinado período
    """
    try:
        use_case = CalculateProfitUseCase(repo)
        result = use_case.execute(current_user.subscriber_id, period_from, period_to)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao calcular lucro: {str(e)}")