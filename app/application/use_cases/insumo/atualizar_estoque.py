"""
Caso de uso para atualizar o estoque de um insumo.
"""

from typing import Optional
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface


class AtualizarEstoqueInsumoUseCase:
    """
    Caso de uso especializado para atualizar o estoque de um insumo.
    
    Permite adicionar ou remover quantidades do estoque de um insumo,
    respeitando as regras de negócio como validação de estoque disponível.
    """
    
    def __init__(self, repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            repository: Implementação do repositório de insumos
        """
        self.repository = repository
    
    def execute(
        self,
        insumo_id: UUID,
        quantidade: int,
        tipo_movimento: str,
        observacao: Optional[str] = None
    ) -> Optional[InsumoEntity]:
        """
        Executa o caso de uso para atualizar o estoque de um insumo.
        
        Args:
            insumo_id: ID do insumo a ser atualizado
            quantidade: Quantidade a adicionar ou remover (deve ser positiva)
            tipo_movimento: Tipo do movimento ('entrada' ou 'saida')
            observacao: Observação opcional sobre o movimento
            
        Returns:
            Optional[InsumoEntity]: Entidade atualizada ou None se não encontrada
            
        Raises:
            ValueError: Se os parâmetros forem inválidos ou estoque insuficiente
        """
        # Validar tipo de movimento
        if tipo_movimento not in ["entrada", "saida"]:
            raise ValueError("Tipo de movimento deve ser 'entrada' ou 'saida'")
            
        # Validar quantidade
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
            
        # Atualizar estoque utilizando o repositório
        return self.repository.update_estoque(
            insumo_id=insumo_id,
            quantidade=quantidade,
            tipo_movimento=tipo_movimento,
            observacao=observacao
        )