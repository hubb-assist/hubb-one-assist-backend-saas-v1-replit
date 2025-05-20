from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4


class CostFixedEntity:
    """Entidade de domínio para custos fixos."""
    
    def __init__(
        self,
        nome: str,
        valor: Decimal,
        data: date,
        subscriber_id: UUID,
        observacoes: Optional[str] = None,
        id: Optional[UUID] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id if id is not None else uuid4()
        self.nome = nome
        self.valor = valor
        self.data = data
        self.subscriber_id = subscriber_id
        self.observacoes = observacoes
        self.is_active = is_active
        self.created_at = created_at if created_at is not None else datetime.utcnow()
        self.updated_at = updated_at if updated_at is not None else datetime.utcnow()
        
        self._validate()
    
    def _validate(self):
        """Valida os dados da entidade."""
        if not self.nome or len(self.nome.strip()) == 0:
            raise ValueError("O nome não pode estar vazio")
        
        if self.valor <= 0:
            raise ValueError("O valor deve ser maior que zero")
            
        # Valida que o valor tem no máximo 2 casas decimais
        if self.valor.quantize(Decimal('0.01')) != self.valor:
            raise ValueError("O valor deve ter no máximo 2 casas decimais")
            
    def update(self, **kwargs):
        """Atualiza os atributos da entidade."""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'subscriber_id', 'created_at']:
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
        
        # Valida novamente após as atualizações
        self._validate()
        
        return self
        
    def deactivate(self):
        """Desativa o custo fixo (exclusão lógica)."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
        return self
        
    def reactivate(self):
        """Reativa o custo fixo."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
        return self