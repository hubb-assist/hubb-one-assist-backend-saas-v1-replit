from abc import ABC, abstractmethod
from uuid import UUID
from datetime import date
from typing import List, Optional

from app.domain.finance.entities import (
    PayableEntity,
    ReceivableEntity,
    CashFlowSummary,
    ProfitCalculation
)
from app.schemas.finance_schema import (
    PayableCreate, 
    PayableUpdate,
    ReceivableCreate,
    ReceivableUpdate
)


class IFinanceRepository(ABC):
    """
    Interface do repositório para operações financeiras
    """
    
    # Payables (Contas a Pagar)
    @abstractmethod
    def create_payable(self, data: PayableCreate, subscriber_id: UUID) -> PayableEntity:
        """
        Cria uma nova conta a pagar para o assinante
        
        Args:
            data: Dados da conta a pagar
            subscriber_id: ID do assinante (segurança multi-tenant)
            
        Returns:
            PayableEntity: Entidade de conta a pagar criada
            
        Raises:
            ValueError: Se houver erro na validação dos dados
        """
        pass
    
    @abstractmethod
    def get_payable(self, id: UUID, subscriber_id: UUID) -> Optional[PayableEntity]:
        """
        Recupera uma conta a pagar pelo ID
        
        Args:
            id: ID da conta a pagar
            subscriber_id: ID do assinante (segurança multi-tenant)
            
        Returns:
            Optional[PayableEntity]: Entidade de conta a pagar ou None se não encontrada
            
        Raises:
            ValueError: Se houver erro na recuperação dos dados
        """
        pass
    
    @abstractmethod
    def update_payable(self, id: UUID, data: PayableUpdate, subscriber_id: UUID) -> PayableEntity:
        """
        Atualiza uma conta a pagar existente
        
        Args:
            id: ID da conta a pagar
            data: Dados a serem atualizados
            subscriber_id: ID do assinante (segurança multi-tenant)
            
        Returns:
            PayableEntity: Entidade de conta a pagar atualizada
            
        Raises:
            ValueError: Se a conta não for encontrada ou houver erro na validação
        """
        pass
    
    @abstractmethod
    def delete_payable(self, id: UUID, subscriber_id: UUID) -> None:
        """
        Exclui logicamente uma conta a pagar
        
        Args:
            id: ID da conta a pagar
            subscriber_id: ID do assinante (segurança multi-tenant)
            
        Raises:
            ValueError: Se a conta não for encontrada
        """
        pass
    
    @abstractmethod
    def list_payables(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        paid: Optional[bool] = None,
        due_from: Optional[date] = None,
        due_to: Optional[date] = None,
    ) -> List[PayableEntity]:
        """
        Lista contas a pagar com filtros opcionais
        
        Args:
            subscriber_id: ID do assinante (segurança multi-tenant)
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros a retornar
            paid: Filtro por status de pagamento (True/False/None)
            due_from: Data de vencimento inicial para filtro
            due_to: Data de vencimento final para filtro
            
        Returns:
            List[PayableEntity]: Lista de entidades de contas a pagar
        """
        pass
    
    # Receivables (Contas a Receber)
    @abstractmethod
    def create_receivable(self, data: ReceivableCreate, subscriber_id: UUID) -> ReceivableEntity:
        """
        Cria uma nova conta a receber para o assinante
        
        Args:
            data: Dados da conta a receber
            subscriber_id: ID do assinante (segurança multi-tenant)
            
        Returns:
            ReceivableEntity: Entidade de conta a receber criada
            
        Raises:
            ValueError: Se houver erro na validação dos dados
        """
        pass
    
    @abstractmethod
    def get_receivable(self, id: UUID, subscriber_id: UUID) -> Optional[ReceivableEntity]:
        """
        Recupera uma conta a receber pelo ID
        
        Args:
            id: ID da conta a receber
            subscriber_id: ID do assinante (segurança multi-tenant)
            
        Returns:
            Optional[ReceivableEntity]: Entidade de conta a receber ou None se não encontrada
            
        Raises:
            ValueError: Se houver erro na recuperação dos dados
        """
        pass
    
    @abstractmethod
    def update_receivable(self, id: UUID, data: ReceivableUpdate, subscriber_id: UUID) -> ReceivableEntity:
        """
        Atualiza uma conta a receber existente
        
        Args:
            id: ID da conta a receber
            data: Dados a serem atualizados
            subscriber_id: ID do assinante (segurança multi-tenant)
            
        Returns:
            ReceivableEntity: Entidade de conta a receber atualizada
            
        Raises:
            ValueError: Se a conta não for encontrada ou houver erro na validação
        """
        pass
    
    @abstractmethod
    def delete_receivable(self, id: UUID, subscriber_id: UUID) -> None:
        """
        Exclui logicamente uma conta a receber
        
        Args:
            id: ID da conta a receber
            subscriber_id: ID do assinante (segurança multi-tenant)
            
        Raises:
            ValueError: Se a conta não for encontrada
        """
        pass
    
    @abstractmethod
    def list_receivables(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        received: Optional[bool] = None,
        due_from: Optional[date] = None,
        due_to: Optional[date] = None,
    ) -> List[ReceivableEntity]:
        """
        Lista contas a receber com filtros opcionais
        
        Args:
            subscriber_id: ID do assinante (segurança multi-tenant)
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros a retornar
            received: Filtro por status de recebimento (True/False/None)
            due_from: Data de vencimento inicial para filtro
            due_to: Data de vencimento final para filtro
            
        Returns:
            List[ReceivableEntity]: Lista de entidades de contas a receber
        """
        pass
    
    # Cashflow & Profit
    @abstractmethod
    def get_cashflow(
        self,
        subscriber_id: UUID,
        from_date: date,
        to_date: date,
    ) -> CashFlowSummary:
        """
        Calcula o fluxo de caixa para um período
        
        Args:
            subscriber_id: ID do assinante (segurança multi-tenant)
            from_date: Data inicial do período
            to_date: Data final do período
            
        Returns:
            CashFlowSummary: Resumo do fluxo de caixa
        """
        pass
    
    @abstractmethod
    def calculate_profit(
        self,
        subscriber_id: UUID,
        period_from: date,
        period_to: date,
    ) -> ProfitCalculation:
        """
        Calcula o lucro para um período
        
        Args:
            subscriber_id: ID do assinante (segurança multi-tenant)
            period_from: Data inicial do período
            period_to: Data final do período
            
        Returns:
            ProfitCalculation: Cálculo de lucro
        """
        pass