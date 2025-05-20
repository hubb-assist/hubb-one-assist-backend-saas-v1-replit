"""
Value Object para representar associações entre insumos e módulos.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID


class ModuloAssociation:
    """
    Value Object que representa a associação entre um insumo e um módulo.
    
    Esta classe permite que um insumo seja associado a diferentes módulos
    do sistema, com informações adicionais como quantidade padrão de uso.
    """
    
    def __init__(
        self,
        module_id: UUID,
        quantidade_padrao: int,
        observacao: Optional[str] = None,
        module_nome: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Inicializa uma nova associação entre insumo e módulo.
        
        Args:
            module_id: ID do módulo associado
            quantidade_padrao: Quantidade padrão que o módulo consome deste insumo
            observacao: Observação opcional sobre a associação
            module_nome: Nome do módulo associado (para exibição)
            created_at: Data de criação
            updated_at: Data da última atualização
        """
        self.module_id = module_id
        self.quantidade_padrao = quantidade_padrao
        self.observacao = observacao
        self.module_nome = module_nome
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        # Validações
        if self.quantidade_padrao <= 0:
            raise ValueError("Quantidade padrão deve ser maior que zero")
    
    def __eq__(self, other):
        """
        Comparação de igualdade entre associações.
        
        Args:
            other: Outra instância para comparação
            
        Returns:
            bool: True se os module_id são iguais
        """
        if not isinstance(other, ModuloAssociation):
            return False
        return self.module_id == other.module_id
    
    def atualizar_quantidade(self, quantidade: int) -> None:
        """
        Atualiza a quantidade padrão da associação.
        
        Args:
            quantidade: Nova quantidade
            
        Raises:
            ValueError: Se a quantidade for negativa ou zero
        """
        if quantidade <= 0:
            raise ValueError("Quantidade padrão deve ser maior que zero")
        
        self.quantidade_padrao = quantidade
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """
        Converte a associação para um dicionário.
        
        Returns:
            dict: Dicionário representando a associação
        """
        return {
            "module_id": str(self.module_id),
            "quantidade_padrao": self.quantidade_padrao,
            "observacao": self.observacao,
            "module_nome": self.module_nome,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }