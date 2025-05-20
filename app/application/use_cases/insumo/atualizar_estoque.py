"""
Caso de uso para atualização de estoque de insumo.
"""

from typing import Optional, Dict, Any
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface


class AtualizarEstoqueInsumoUseCase:
    """
    Caso de uso para atualização de estoque de um insumo.
    
    Implementa a lógica de negócio para atualizar o estoque de um insumo,
    permitindo entrada ou saída de itens e mantendo histórico.
    """
    
    def __init__(self, insumo_repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com o repositório de insumos.
        
        Args:
            insumo_repository: Repositório de insumos que segue a interface definida
        """
        self.insumo_repository = insumo_repository
    
    def execute(self, insumo_id: UUID, quantidade: int, tipo_movimento: str, 
                observacao: Optional[str] = None) -> Optional[InsumoEntity]:
        """
        Executa o caso de uso para atualizar o estoque de um insumo.
        
        Args:
            insumo_id: UUID do insumo a atualizar
            quantidade: Quantidade a ser adicionada ou removida (sempre positiva)
            tipo_movimento: Tipo de movimento ("entrada" ou "saida")
            observacao: Observação sobre o movimento (opcional)
            
        Returns:
            Optional[InsumoEntity]: Entidade de insumo atualizada ou None se não encontrado
            
        Raises:
            ValueError: Se os dados de atualização forem inválidos
        """
        # Validar entrada de dados
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero")
            
        if tipo_movimento not in ["entrada", "saida"]:
            raise ValueError("Tipo de movimento deve ser 'entrada' ou 'saida'")
        
        # Buscar insumo existente
        insumo = self.insumo_repository.get_by_id(insumo_id)
        if not insumo:
            return None
            
        # Preparar dados para atualização
        update_data = {}
        
        # Calcular novo estoque com base no tipo de movimento
        if tipo_movimento == "entrada":
            update_data["estoque_atual"] = insumo.estoque_atual + quantidade
        else:  # saida
            if insumo.estoque_atual < quantidade:
                raise ValueError(f"Estoque insuficiente. Disponível: {insumo.estoque_atual}, Solicitado: {quantidade}")
            update_data["estoque_atual"] = insumo.estoque_atual - quantidade
        
        # Executar atualização
        insumo_atualizado = self.insumo_repository.update(insumo_id, update_data)
        
        # TODO: Em uma implementação mais completa, registrar o histórico de movimentação
        # em uma tabela específica para rastreabilidade.
        
        return insumo_atualizado