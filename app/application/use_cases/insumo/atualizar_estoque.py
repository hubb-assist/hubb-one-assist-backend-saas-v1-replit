"""
Caso de uso para atualizar o estoque de um insumo (entrada ou saída).
"""

from typing import Optional
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface


class AtualizarEstoqueUseCase:
    """
    Caso de uso para atualizar o estoque de um insumo (entrada ou saída).
    
    Responsável por registrar movimentações de estoque, como entradas
    de novos produtos ou saídas para uso em procedimentos.
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
        tipo_movimento: str
    ) -> Optional[InsumoEntity]:
        """
        Executa o caso de uso para atualizar o estoque de um insumo.
        
        Args:
            insumo_id: ID do insumo a atualizar
            quantidade: Quantidade a ser movimentada (sempre positiva)
            tipo_movimento: Tipo de movimento ('entrada' ou 'saida')
            
        Returns:
            Optional[InsumoEntity]: Entidade atualizada ou None se não encontrada
            
        Raises:
            ValueError: Se a quantidade for negativa ou tipo de movimento inválido
            ValueError: Se a retirada resultar em estoque negativo
        """
        # Validações básicas
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero")
            
        if tipo_movimento not in ['entrada', 'saida']:
            raise ValueError("Tipo de movimento deve ser 'entrada' ou 'saida'")
        
        # Atualizar estoque via repositório
        try:
            return self.repository.update_stock(
                insumo_id=insumo_id,
                quantidade=quantidade,
                tipo_movimento=tipo_movimento
            )
        except ValueError as e:
            # Propagar erro de estoque insuficiente ou outras validações
            raise ValueError(str(e))