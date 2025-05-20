"""
Value object para representar a associação entre um insumo e um módulo.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class ModuloAssociation:
    """
    Value Object para associação entre um insumo e um módulo.
    Representa a relação de uso de um insumo por um módulo funcional,
    incluindo a quantidade padrão utilizada.
    """
    module_id: UUID
    quantidade_padrao: int = 1
    observacao: Optional[str] = None
    module_nome: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """
        Validação pós-inicialização.
        """
        if self.quantidade_padrao <= 0:
            raise ValueError("Quantidade padrão deve ser um número positivo")