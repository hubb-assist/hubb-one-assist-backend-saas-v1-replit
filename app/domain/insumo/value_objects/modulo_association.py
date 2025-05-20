"""
Value object que representa a associação entre um insumo e um módulo funcional.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class ModuloAssociation:
    """
    Value object que representa a associação entre um insumo e um módulo funcional.
    
    Esta classe imutável representa a relação entre um insumo e um módulo, 
    contendo informações sobre a quantidade padrão utilizada e observações.
    """
    module_id: UUID
    quantidade_padrao: int = 1
    observacao: Optional[str] = None
    module_nome: Optional[str] = None
    
    def __post_init__(self):
        """
        Validações dos dados após inicialização.
        """
        if self.quantidade_padrao <= 0:
            raise ValueError("A quantidade padrão deve ser maior que zero")