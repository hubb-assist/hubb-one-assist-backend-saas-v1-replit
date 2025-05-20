from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class CostFixedEntity:
    """Entidade de domínio para custos fixos."""
    
    nome: str
    valor: Decimal
    data: date
    subscriber_id: UUID
    observacoes: Optional[str] = None
    id: UUID = uuid4()
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    def __post_init__(self):
        """Valida os dados após a inicialização."""
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
        self.__post_init__()
        
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