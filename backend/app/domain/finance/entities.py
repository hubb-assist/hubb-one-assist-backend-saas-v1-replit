from uuid import UUID, uuid4
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict, Any


class PayableEntity:
    """
    Entidade de domínio para representar contas a pagar
    """
    
    def __init__(
        self,
        subscriber_id: UUID,
        description: str,
        amount: Decimal,
        due_date: date,
        paid: bool = False,
        payment_date: Optional[datetime] = None,
        notes: Optional[str] = None,
        id: Optional[UUID] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id or uuid4()
        self.subscriber_id = subscriber_id
        self.description = description
        self.amount = amount
        self.due_date = due_date
        self.paid = paid
        self.payment_date = payment_date
        self.notes = notes
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        self._validate()
    
    def _validate(self) -> None:
        """
        Valida as regras de negócio da entidade
        """
        if not self.description or len(self.description.strip()) < 3:
            raise ValueError("A descrição deve ter pelo menos 3 caracteres")
            
        if self.amount <= Decimal("0"):
            raise ValueError("O valor deve ser maior que zero")
            
        if self.paid and not self.payment_date:
            raise ValueError("Data de pagamento é obrigatória quando marcado como pago")
    
    def mark_as_paid(self, payment_date: Optional[datetime] = None) -> None:
        """
        Marca a conta como paga na data especificada ou atual
        
        Args:
            payment_date: Data do pagamento (opcional, padrão: datetime atual)
        """
        self.paid = True
        self.payment_date = payment_date or datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update(self, data: Dict[str, Any]) -> None:
        """
        Atualiza os atributos da entidade
        
        Args:
            data: Dicionário com os dados a serem atualizados
        """
        if "description" in data and data["description"] is not None:
            self.description = data["description"]
            
        if "amount" in data and data["amount"] is not None:
            self.amount = data["amount"]
            
        if "due_date" in data and data["due_date"] is not None:
            self.due_date = data["due_date"]
            
        if "paid" in data and data["paid"] is not None:
            was_not_paid = not self.paid
            self.paid = data["paid"]
            
            # Se foi marcado como pago e não tinha data de pagamento, defina a data atual
            if was_not_paid and self.paid and not self.payment_date:
                self.payment_date = data.get("payment_date") or datetime.utcnow()
            
        if "payment_date" in data and data["payment_date"] is not None:
            self.payment_date = data["payment_date"]
            
        if "notes" in data and data["notes"] is not None:
            self.notes = data["notes"]
            
        if "is_active" in data and data["is_active"] is not None:
            self.is_active = data["is_active"]
            
        self.updated_at = datetime.utcnow()
        self._validate()
    
    def deactivate(self) -> None:
        """
        Desativa a conta (exclusão lógica)
        """
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a entidade para um dicionário
        
        Returns:
            Dict[str, Any]: Dicionário representando a entidade
        """
        return {
            "id": self.id,
            "subscriber_id": self.subscriber_id,
            "description": self.description,
            "amount": self.amount,
            "due_date": self.due_date,
            "paid": self.paid,
            "payment_date": self.payment_date,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class ReceivableEntity:
    """
    Entidade de domínio para representar contas a receber
    """
    
    def __init__(
        self,
        subscriber_id: UUID,
        patient_id: UUID,
        description: str,
        amount: Decimal,
        due_date: date,
        received: bool = False,
        receive_date: Optional[datetime] = None,
        notes: Optional[str] = None,
        id: Optional[UUID] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id or uuid4()
        self.subscriber_id = subscriber_id
        self.patient_id = patient_id
        self.description = description
        self.amount = amount
        self.due_date = due_date
        self.received = received
        self.receive_date = receive_date
        self.notes = notes
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        self._validate()
    
    def _validate(self) -> None:
        """
        Valida as regras de negócio da entidade
        """
        if not self.description or len(self.description.strip()) < 3:
            raise ValueError("A descrição deve ter pelo menos 3 caracteres")
            
        if self.amount <= Decimal("0"):
            raise ValueError("O valor deve ser maior que zero")
            
        if self.received and not self.receive_date:
            raise ValueError("Data de recebimento é obrigatória quando marcado como recebido")
    
    def mark_as_received(self, receive_date: Optional[datetime] = None) -> None:
        """
        Marca a conta como recebida na data especificada ou atual
        
        Args:
            receive_date: Data do recebimento (opcional, padrão: datetime atual)
        """
        self.received = True
        self.receive_date = receive_date or datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update(self, data: Dict[str, Any]) -> None:
        """
        Atualiza os atributos da entidade
        
        Args:
            data: Dicionário com os dados a serem atualizados
        """
        if "patient_id" in data and data["patient_id"] is not None:
            self.patient_id = data["patient_id"]
            
        if "description" in data and data["description"] is not None:
            self.description = data["description"]
            
        if "amount" in data and data["amount"] is not None:
            self.amount = data["amount"]
            
        if "due_date" in data and data["due_date"] is not None:
            self.due_date = data["due_date"]
            
        if "received" in data and data["received"] is not None:
            was_not_received = not self.received
            self.received = data["received"]
            
            # Se foi marcado como recebido e não tinha data de recebimento, defina a data atual
            if was_not_received and self.received and not self.receive_date:
                self.receive_date = data.get("receive_date") or datetime.utcnow()
            
        if "receive_date" in data and data["receive_date"] is not None:
            self.receive_date = data["receive_date"]
            
        if "notes" in data and data["notes"] is not None:
            self.notes = data["notes"]
            
        if "is_active" in data and data["is_active"] is not None:
            self.is_active = data["is_active"]
            
        self.updated_at = datetime.utcnow()
        self._validate()
    
    def deactivate(self) -> None:
        """
        Desativa a conta (exclusão lógica)
        """
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a entidade para um dicionário
        
        Returns:
            Dict[str, Any]: Dicionário representando a entidade
        """
        return {
            "id": self.id,
            "subscriber_id": self.subscriber_id,
            "patient_id": self.patient_id,
            "description": self.description,
            "amount": self.amount,
            "due_date": self.due_date,
            "received": self.received,
            "receive_date": self.receive_date,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class CashFlowSummary:
    """
    Value Object para representar um resumo de fluxo de caixa
    """
    
    def __init__(
        self,
        total_inflows: Decimal,
        total_outflows: Decimal,
        net_flow: Decimal,
    ):
        self.total_inflows = total_inflows
        self.total_outflows = total_outflows
        self.net_flow = net_flow
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o Value Object para um dicionário
        
        Returns:
            Dict[str, Any]: Dicionário representando o Value Object
        """
        return {
            "total_inflows": self.total_inflows,
            "total_outflows": self.total_outflows,
            "net_flow": self.net_flow
        }


class ProfitCalculation:
    """
    Value Object para representar um cálculo de lucro
    """
    
    def __init__(
        self,
        total_revenue: Decimal,
        total_costs: Decimal,
        gross_profit: Decimal,
        net_profit: Decimal,
    ):
        self.total_revenue = total_revenue
        self.total_costs = total_costs
        self.gross_profit = gross_profit
        self.net_profit = net_profit
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o Value Object para um dicionário
        
        Returns:
            Dict[str, Any]: Dicionário representando o Value Object
        """
        return {
            "total_revenue": self.total_revenue,
            "total_costs": self.total_costs,
            "gross_profit": self.gross_profit,
            "net_profit": self.net_profit
        }