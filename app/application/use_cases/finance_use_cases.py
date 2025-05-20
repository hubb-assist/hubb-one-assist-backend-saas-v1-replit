from uuid import UUID
from datetime import date
from typing import List, Dict, Any

from app.domain.finance.interfaces import IFinanceRepository
from app.domain.finance.entities import (
    PayableEntity, ReceivableEntity, CashFlowSummary, ProfitCalculation
)
from app.schemas.finance_schema import (
    PayableCreate, PayableUpdate, ReceivableCreate, ReceivableUpdate
)

# --- Payables Use Cases ---
class CreatePayableUseCase:
    """
    Caso de uso para criar um novo registro de conta a pagar
    """
    
    def __init__(self, repo: IFinanceRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repo: Implementação de IFinanceRepository
        """
        self.repo = repo

    def execute(self, data: PayableCreate, subscriber_id: UUID) -> Dict[str, Any]:
        """
        Executa o caso de uso - cria uma nova conta a pagar
        
        Args:
            data: Dados da conta a pagar
            subscriber_id: ID do assinante (segurança multi-tenant)
            
        Returns:
            Dict[str, Any]: Dicionário representando a conta a pagar criada
            
        Raises:
            ValueError: Se houver erro na validação ou criação
        """
        try:
            entity = self.repo.create_payable(data, subscriber_id)
            return entity.to_dict()
        except Exception as e:
            raise ValueError(f"Erro ao criar conta a pagar: {str(e)}")


class GetPayableUseCase:
    """
    Caso de uso para recuperar um registro de conta a pagar por ID
    """
    
    def __init__(self, repo: IFinanceRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repo: Implementação de IFinanceRepository
        """
        self.repo = repo

    def execute(self, id: UUID, subscriber_id: UUID) -> Dict[str, Any]:
        """
        Executa o caso de uso - busca uma conta a pagar por ID
        
        Args:
            id: ID da conta a pagar
            subscriber_id: ID do assinante (segurança multi-tenant)
            
        Returns:
            Dict[str, Any]: Dicionário representando a conta a pagar
            
        Raises:
            ValueError: Se a conta a pagar não for encontrada
        """
        try:
            entity = self.repo.get_payable(id, subscriber_id)
            if not entity:
                raise ValueError(f"Conta a pagar com ID {id} não encontrada")
            return entity.to_dict()
        except Exception as e:
            raise ValueError(f"Erro ao buscar conta a pagar: {str(e)}")


class ListPayablesUseCase:
    """
    Caso de uso para listar registros de contas a pagar com filtros
    """
    
    def __init__(self, repo: IFinanceRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repo: Implementação de IFinanceRepository
        """
        self.repo = repo

    def execute(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        paid: bool = None,
        due_from: date = None,
        due_to: date = None,
    ) -> List[Dict[str, Any]]:
        """
        Executa o caso de uso - lista contas a pagar com filtros
        
        Args:
            subscriber_id: ID do assinante (segurança multi-tenant)
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros para retornar
            paid: Filtro pelo status de pagamento (opcional)
            due_from: Data de vencimento inicial para filtro (opcional)
            due_to: Data de vencimento final para filtro (opcional)
            
        Returns:
            List[Dict[str, Any]]: Lista de dicionários representando contas a pagar
            
        Raises:
            ValueError: Se houver erro na listagem
        """
        try:
            entities = self.repo.list_payables(
                subscriber_id=subscriber_id,
                skip=skip,
                limit=limit,
                paid=paid,
                due_from=due_from,
                due_to=due_to
            )
            return [entity.to_dict() for entity in entities]
        except Exception as e:
            raise ValueError(f"Erro ao listar contas a pagar: {str(e)}")


class UpdatePayableUseCase:
    """
    Caso de uso para atualizar um registro de conta a pagar
    """
    
    def __init__(self, repo: IFinanceRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repo: Implementação de IFinanceRepository
        """
        self.repo = repo

    def execute(self, id: UUID, data: PayableUpdate, subscriber_id: UUID) -> Dict[str, Any]:
        """
        Executa o caso de uso - atualiza uma conta a pagar
        
        Args:
            id: ID da conta a pagar
            data: Dados a serem atualizados
            subscriber_id: ID do assinante (segurança multi-tenant)
            
        Returns:
            Dict[str, Any]: Dicionário representando a conta a pagar atualizada
            
        Raises:
            ValueError: Se a conta a pagar não for encontrada ou houver erro na validação
        """
        try:
            entity = self.repo.update_payable(id, data, subscriber_id)
            if not entity:
                raise ValueError(f"Conta a pagar com ID {id} não encontrada")
            return entity.to_dict()
        except Exception as e:
            raise ValueError(f"Erro ao atualizar conta a pagar: {str(e)}")


class DeletePayableUseCase:
    """
    Caso de uso para excluir (logicamente) um registro de conta a pagar
    """
    
    def __init__(self, repo: IFinanceRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repo: Implementação de IFinanceRepository
        """
        self.repo = repo

    def execute(self, id: UUID, subscriber_id: UUID) -> bool:
        """
        Executa o caso de uso - exclui logicamente uma conta a pagar
        
        Args:
            id: ID da conta a pagar
            subscriber_id: ID do assinante (segurança multi-tenant)
            
        Returns:
            bool: True se a exclusão foi bem-sucedida
            
        Raises:
            ValueError: Se a conta a pagar não for encontrada
        """
        try:
            self.repo.delete_payable(id, subscriber_id)
            return True
        except Exception as e:
            raise ValueError(f"Erro ao excluir conta a pagar: {str(e)}")


# --- Receivables Use Cases ---
class CreateReceivableUseCase:
    """
    Caso de uso para criar um novo registro de conta a receber
    """
    
    def __init__(self, repo: IFinanceRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repo: Implementação de IFinanceRepository
        """
        self.repo = repo

    def execute(self, data: ReceivableCreate, subscriber_id: UUID) -> Dict[str, Any]:
        """
        Executa o caso de uso - cria uma nova conta a receber
        
        Args:
            data: Dados da conta a receber
            subscriber_id: ID do assinante (segurança multi-tenant)
            
        Returns:
            Dict[str, Any]: Dicionário representando a conta a receber criada
            
        Raises:
            ValueError: Se houver erro na validação ou criação
        """
        try:
            entity = self.repo.create_receivable(data, subscriber_id)
            return entity.to_dict()
        except Exception as e:
            raise ValueError(f"Erro ao criar conta a receber: {str(e)}")


class GetReceivableUseCase:
    """
    Caso de uso para recuperar um registro de conta a receber por ID
    """
    
    def __init__(self, repo: IFinanceRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repo: Implementação de IFinanceRepository
        """
        self.repo = repo

    def execute(self, id: UUID, subscriber_id: UUID) -> Dict[str, Any]:
        """
        Executa o caso de uso - busca uma conta a receber por ID
        
        Args:
            id: ID da conta a receber
            subscriber_id: ID do assinante (segurança multi-tenant)
            
        Returns:
            Dict[str, Any]: Dicionário representando a conta a receber
            
        Raises:
            ValueError: Se a conta a receber não for encontrada
        """
        try:
            entity = self.repo.get_receivable(id, subscriber_id)
            if not entity:
                raise ValueError(f"Conta a receber com ID {id} não encontrada")
            return entity.to_dict()
        except Exception as e:
            raise ValueError(f"Erro ao buscar conta a receber: {str(e)}")


class ListReceivablesUseCase:
    """
    Caso de uso para listar registros de contas a receber com filtros
    """
    
    def __init__(self, repo: IFinanceRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repo: Implementação de IFinanceRepository
        """
        self.repo = repo

    def execute(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        received: bool = None,
        due_from: date = None,
        due_to: date = None,
    ) -> List[Dict[str, Any]]:
        """
        Executa o caso de uso - lista contas a receber com filtros
        
        Args:
            subscriber_id: ID do assinante (segurança multi-tenant)
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros para retornar
            received: Filtro pelo status de recebimento (opcional)
            due_from: Data de vencimento inicial para filtro (opcional)
            due_to: Data de vencimento final para filtro (opcional)
            
        Returns:
            List[Dict[str, Any]]: Lista de dicionários representando contas a receber
            
        Raises:
            ValueError: Se houver erro na listagem
        """
        try:
            entities = self.repo.list_receivables(
                subscriber_id=subscriber_id,
                skip=skip,
                limit=limit,
                received=received,
                due_from=due_from,
                due_to=due_to
            )
            return [entity.to_dict() for entity in entities]
        except Exception as e:
            raise ValueError(f"Erro ao listar contas a receber: {str(e)}")


class UpdateReceivableUseCase:
    """
    Caso de uso para atualizar um registro de conta a receber
    """
    
    def __init__(self, repo: IFinanceRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repo: Implementação de IFinanceRepository
        """
        self.repo = repo

    def execute(self, id: UUID, data: ReceivableUpdate, subscriber_id: UUID) -> Dict[str, Any]:
        """
        Executa o caso de uso - atualiza uma conta a receber
        
        Args:
            id: ID da conta a receber
            data: Dados a serem atualizados
            subscriber_id: ID do assinante (segurança multi-tenant)
            
        Returns:
            Dict[str, Any]: Dicionário representando a conta a receber atualizada
            
        Raises:
            ValueError: Se a conta a receber não for encontrada ou houver erro na validação
        """
        try:
            entity = self.repo.update_receivable(id, data, subscriber_id)
            if not entity:
                raise ValueError(f"Conta a receber com ID {id} não encontrada")
            return entity.to_dict()
        except Exception as e:
            raise ValueError(f"Erro ao atualizar conta a receber: {str(e)}")


class DeleteReceivableUseCase:
    """
    Caso de uso para excluir (logicamente) um registro de conta a receber
    """
    
    def __init__(self, repo: IFinanceRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repo: Implementação de IFinanceRepository
        """
        self.repo = repo

    def execute(self, id: UUID, subscriber_id: UUID) -> bool:
        """
        Executa o caso de uso - exclui logicamente uma conta a receber
        
        Args:
            id: ID da conta a receber
            subscriber_id: ID do assinante (segurança multi-tenant)
            
        Returns:
            bool: True se a exclusão foi bem-sucedida
            
        Raises:
            ValueError: Se a conta a receber não for encontrada
        """
        try:
            self.repo.delete_receivable(id, subscriber_id)
            return True
        except Exception as e:
            raise ValueError(f"Erro ao excluir conta a receber: {str(e)}")


# --- Cash Flow & Profit Use Cases ---
class GetCashFlowUseCase:
    """
    Caso de uso para calcular o fluxo de caixa de um período
    """
    
    def __init__(self, repo: IFinanceRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repo: Implementação de IFinanceRepository
        """
        self.repo = repo

    def execute(self, subscriber_id: UUID, from_date: date, to_date: date) -> Dict[str, Any]:
        """
        Executa o caso de uso - calcula o fluxo de caixa em um período
        
        Args:
            subscriber_id: ID do assinante (segurança multi-tenant)
            from_date: Data inicial do período
            to_date: Data final do período
            
        Returns:
            Dict[str, Any]: Dicionário representando o resumo do fluxo de caixa
            
        Raises:
            ValueError: Se houver erro no cálculo
        """
        try:
            cash_flow = self.repo.get_cashflow(subscriber_id, from_date, to_date)
            return cash_flow.to_dict()
        except Exception as e:
            raise ValueError(f"Erro ao calcular fluxo de caixa: {str(e)}")


class CalculateProfitUseCase:
    """
    Caso de uso para calcular o lucro de um período
    """
    
    def __init__(self, repo: IFinanceRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repo: Implementação de IFinanceRepository
        """
        self.repo = repo

    def execute(self, subscriber_id: UUID, period_from: date, period_to: date) -> Dict[str, Any]:
        """
        Executa o caso de uso - calcula o lucro em um período
        
        Args:
            subscriber_id: ID do assinante (segurança multi-tenant)
            period_from: Data inicial do período
            period_to: Data final do período
            
        Returns:
            Dict[str, Any]: Dicionário representando o cálculo de lucro
            
        Raises:
            ValueError: Se houver erro no cálculo
        """
        try:
            profit = self.repo.calculate_profit(subscriber_id, period_from, period_to)
            return profit.to_dict()
        except Exception as e:
            raise ValueError(f"Erro ao calcular lucro: {str(e)}")