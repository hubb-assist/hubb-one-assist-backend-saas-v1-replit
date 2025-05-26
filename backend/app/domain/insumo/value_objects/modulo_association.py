"""
Value Object para representar a associação entre um Insumo e um Módulo.
"""

from typing import Optional
from uuid import UUID


class ModuloAssociation:
    """
    Value Object que representa a associação entre um Insumo e um Módulo.
    
    Esta classe encapsula os dados e regras da associação, garantindo
    a integridade e consistência dos dados.
    """
    
    def __init__(
        self,
        module_id: UUID,
        quantidade_padrao: int = 1,
        observacao: Optional[str] = None,
        module_nome: Optional[str] = None
    ):
        """
        Inicializa uma nova associação entre Insumo e Módulo.
        
        Args:
            module_id: ID do módulo associado
            quantidade_padrao: Quantidade padrão do insumo utilizada pelo módulo
            observacao: Observação sobre a utilização (opcional)
            module_nome: Nome do módulo, apenas para exibição (opcional)
        """
        self._validar_parametros(module_id, quantidade_padrao)
        
        self.module_id = module_id
        self.quantidade_padrao = quantidade_padrao
        self.observacao = observacao
        self.module_nome = module_nome
    
    def _validar_parametros(self, module_id: UUID, quantidade_padrao: int):
        """
        Valida os parâmetros fornecidos.
        
        Args:
            module_id: ID do módulo a ser validado
            quantidade_padrao: Quantidade padrão a ser validada
            
        Raises:
            ValueError: Se algum parâmetro for inválido
        """
        if not module_id:
            raise ValueError("ID do módulo é obrigatório")
            
        if quantidade_padrao <= 0:
            raise ValueError("Quantidade padrão deve ser maior que zero")
            
    def __eq__(self, other):
        """
        Compara duas associações para verificar igualdade.
        
        Args:
            other: Outra instância de ModuloAssociation
            
        Returns:
            bool: True se forem iguais, False caso contrário
        """
        if not isinstance(other, ModuloAssociation):
            return False
            
        return self.module_id == other.module_id
        
    def __hash__(self):
        """
        Retorna o hash da associação.
        
        Returns:
            int: Hash baseado no ID do módulo
        """
        return hash(self.module_id)